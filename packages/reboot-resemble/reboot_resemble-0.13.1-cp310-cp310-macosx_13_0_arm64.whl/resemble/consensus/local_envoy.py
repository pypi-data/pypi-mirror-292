from __future__ import annotations

import asyncio
import grpc
import math
import os
import shutil
from dataclasses import dataclass
from grpc_health.v1 import health_pb2, health_pb2_grpc
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from resemble.aio.headers import CONSENSUS_ID_HEADER
from resemble.aio.types import ConsensusId, ServiceName
from typing import Optional

LOCALHOST_DIRECT_CRT = os.path.join(
    os.path.dirname(__file__), 'localhost.direct.crt'
)

# We open an admin port for Envoy to facilitate debugging. We pick 9901 since
# it's a typical choice (AWS uses it) that's similar to the ports Resemble
# already uses.
ENVOY_ADMIN_PORT = 9901

ENVOY_CONFIG_TEMPLATE_NAME = 'local_envoy_config.yaml.j2'

if not os.path.isfile(LOCALHOST_DIRECT_CRT):
    raise FileNotFoundError(
        "Expecting 'localhost.direct.crt' at path "
        f"'{LOCALHOST_DIRECT_CRT}'"
    )

LOCALHOST_DIRECT_KEY = os.path.join(
    os.path.dirname(__file__), 'localhost.direct.key'
)

if not os.path.isfile(LOCALHOST_DIRECT_KEY):
    raise FileNotFoundError(
        "Expecting 'localhost.direct.key' at path "
        f"'{LOCALHOST_DIRECT_KEY}'"
    )


@dataclass
class ConsensusAddress:
    host: str
    grpc_port: int
    websocket_port: int


@dataclass
class RouteMapEntry:
    # The start of this shard's key range. Conceptually this represents a single
    # `byte`, but we store it as an `int` for easier embedding in Lua source
    # code.
    shard_keyrange_start: int
    # The consensus ID that traffic matching this entry should get sent to.
    consensus_id: ConsensusId


class LocalEnvoy:
    """
    Wrapper class for setting up a local Envoy outside of Kubernetes. Depending
    on the chosen subclass this may run Envoy in a Docker container, or as a
    standalone process.

    The user of this class is responsible for calling .start() and .stop().
    """

    @property
    def port(self) -> int:
        raise NotImplementedError

    async def start(self) -> None:
        raise NotImplementedError

    async def stop(self) -> None:
        raise NotImplementedError

    @staticmethod
    def _write_envoy_dir(
        *,
        # The path at which this function should write the Envoy configuration.
        output_dir: str,
        # The path at which Envoy will observe the written configuration to be.
        # This may be different, e.g. when Envoy is running in a Docker
        # container that has mounted the config directory elsewhere.
        observed_dir: str,
        envoy_port: int,
        application_id: str,
        service_names: list[ServiceName],
        address_by_consensus: dict[ConsensusId, ConsensusAddress],
        proto_descriptor_bin: bytes,
        use_tls: bool,
        certificate: Optional[Path],
        key: Optional[Path],
    ) -> Path:
        """
        Generates a directory with all the required config needed to run
        Envoy.

        Returns the path the the generated 'envoy.yaml' file that should be
        passed to Envoy as a parameter.
        """

        # Compute the route map.
        shard_keyrange_starts = _shard_keyrange_starts(
            len(address_by_consensus)
        )
        route_map = [
            RouteMapEntry(
                # To safely embed an arbitrary byte in textual Lua source
                # code, we represent it as an int.
                shard_keyrange_start=int(shard_keyrange_start),
                consensus_id=consensus_id
            ) for shard_keyrange_start, consensus_id in
            zip(shard_keyrange_starts, address_by_consensus.keys())
        ]

        # Inject the Lua filter that handles "mangled" HTTP paths that need to
        # be translated into something that can be routed.
        #
        # TODO: instead of mashing this into the `envoy.yaml` this can now be
        #       left in its file and imported like we do with the 'sha1'
        #       library, below.
        mangled_http_path_filter_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'controller',
            'mangled_http_path_filter.lua',
        )

        with open(
            mangled_http_path_filter_path, 'r'
        ) as mangled_http_path_filter_file:
            mangled_http_path_filter = mangled_http_path_filter_file.read()

        # Our config depends on the appropriate SSL certificate being
        # available in the Envoy's config directory.
        certificate_in_output_dir = Path(os.path.join(output_dir), 'tls.crt')
        certificate_in_observed_dir = Path(
            os.path.join(observed_dir), 'tls.crt'
        )
        key_in_output_dir = Path(os.path.join(output_dir), 'tls.key')
        key_in_observed_dir = Path(os.path.join(observed_dir), 'tls.key')
        if use_tls:
            shutil.copyfile(
                certificate or LOCALHOST_DIRECT_CRT,
                certificate_in_output_dir,
            )
            shutil.copyfile(
                key or LOCALHOST_DIRECT_KEY,
                key_in_output_dir,
            )

        # Our config depends on the Lua SHA1 library being available at `sha1/`.
        source_dir = os.path.dirname(__file__)
        sha1_source_dir = os.path.join(source_dir, "sha1", "src", "sha1")
        sha1_in_output_dir = os.path.join(output_dir, "sha1")
        shutil.copytree(sha1_source_dir, sha1_in_output_dir)

        # Now we're ready to start assembling our `envoy.yaml`.
        template_input = {
            'envoy_port': envoy_port,
            'address_by_consensus': address_by_consensus,
            'route_map': route_map,
            'application_id': application_id,
            'service_names': service_names,
            # We have to turn the base64 encoded proto descriptor into a string
            # using .decode() because Jinja can only handle str types.
            'proto_descriptor_bin': proto_descriptor_bin.decode(),
            'envoy_admin_port': ENVOY_ADMIN_PORT,
            'use_tls': use_tls,
            'tls_certificate_path': certificate_in_observed_dir,
            'tls_key_path': key_in_observed_dir,
            'mangled_http_path_filter': mangled_http_path_filter,
        }

        # Define a Jinja2 environment to allow Jinja's `include` to find other
        # template files in the same directory.
        env = Environment(loader=FileSystemLoader(source_dir))
        template = env.get_template(ENVOY_CONFIG_TEMPLATE_NAME)
        envoy_yaml_contents = template.render(template_input)

        envoy_yaml_in_output = Path(os.path.join(output_dir, "envoy.yaml"))
        envoy_yaml_in_output.write_text(envoy_yaml_contents)

        envoy_yaml_in_observed = Path(os.path.join(observed_dir, "envoy.yaml"))

        # If the files we've just created are bind-mounted into a Docker
        # container, they may be accessed by a different user than our current
        # one. Make sure they're readable. To not block ourselves from deleting
        # these files after Envoy is done, keep them writable for ourselves.
        #
        # TODO(rjh): rather than doing this work here, perhaps it would be less
        # brittle (i.e. no local fs changes) to use `docker create`+`docker cp`+
        # `docker start` instead of `docker run` in the Docker-specific local
        # envoy class.
        for root, dirs, files in os.walk(output_dir):
            os.chmod(root, 0o755)
            for dir_ in dirs:
                os.chmod(os.path.join(root, dir_), 0o755)
            for file_ in files:
                os.chmod(os.path.join(root, file_), 0o755)

        return envoy_yaml_in_observed

    async def _wait_for_grpc_health_check(self, consensus_id: ConsensusId):
        # Using the 'dev' subdomain as a workaround for a gRPC
        # bug that produces log message error about not
        # matching the entry (*.localhost.direct) in the
        # certificate if we just use 'localhost.direct'. See
        # https://github.com/reboot-dev/respect/issues/2305
        target = f'dev.localhost.direct:{self.port}'
        metadata = ((CONSENSUS_ID_HEADER, consensus_id),)
        while True:
            async with grpc.aio.secure_channel(
                target,
                grpc.ssl_channel_credentials(),
            ) as channel:
                stub = health_pb2_grpc.HealthStub(channel)
                request = health_pb2.HealthCheckRequest()
                try:
                    response = await stub.Check(request, metadata=metadata)
                    if response.status == health_pb2.HealthCheckResponse.SERVING:
                        break
                except grpc.aio.AioRpcError:
                    await asyncio.sleep(0.05)


def _shard_keyrange_starts(num_shards: int) -> list[int]:
    NUM_BYTE_VALUES = 256
    if num_shards > NUM_BYTE_VALUES:
        raise ValueError(
            f"'num_shards' must be less than or equal to "
            f"{NUM_BYTE_VALUES}; got {num_shards}."
        )
    if not math.log2(num_shards).is_integer():
        raise ValueError(
            f"'num_shards' must be a power of 2; got {num_shards}."
        )
    shard_size = NUM_BYTE_VALUES // num_shards
    # The first shard always begins at the very beginning of the key range.
    return [i * shard_size for i in range(0, num_shards)]
