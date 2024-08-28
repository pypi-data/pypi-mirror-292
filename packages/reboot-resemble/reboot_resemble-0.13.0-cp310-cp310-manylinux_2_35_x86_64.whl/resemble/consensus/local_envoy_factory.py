import os
from pathlib import Path
from resemble.aio.servicers import Routable
from resemble.aio.types import ConsensusId
from resemble.consensus.docker_local_envoy import DockerLocalEnvoy
from resemble.consensus.executable_local_envoy import ExecutableLocalEnvoy
from resemble.consensus.local_envoy import ConsensusAddress, LocalEnvoy
from resemble.helpers import (
    base64_serialize_proto_descriptor_set,
    generate_proto_descriptor_set,
)
from resemble.settings import (
    ENVVAR_LOCAL_ENVOY_DEBUG,
    ENVVAR_LOCAL_ENVOY_MODE,
    ENVVAR_LOCAL_ENVOY_TLS_CERTIFICATE_PATH,
    ENVVAR_LOCAL_ENVOY_TLS_KEY_PATH,
    ENVVAR_LOCAL_ENVOY_USE_TLS,
)

RESEMBLE_LOCAL_ENVOY_DEBUG: bool = os.environ.get(
    ENVVAR_LOCAL_ENVOY_DEBUG,
    'false',
).lower() == 'true'


class LocalEnvoyFactory:

    @staticmethod
    def create(
        *,
        published_port: int,
        application_id: str,
        routables: list[Routable],
        address_by_consensus: dict[ConsensusId, ConsensusAddress],
        stopped_consensuses: set[ConsensusId],
    ) -> LocalEnvoy:
        proto_descriptor_set = generate_proto_descriptor_set(routables)

        base64_encoded_proto_desc_set = base64_serialize_proto_descriptor_set(
            proto_descriptor_set
        )

        use_tls = os.environ.get(ENVVAR_LOCAL_ENVOY_USE_TLS) == "True"

        certificate_path = os.environ.get(
            ENVVAR_LOCAL_ENVOY_TLS_CERTIFICATE_PATH, None
        )
        certificate = (
            Path(certificate_path) if certificate_path is not None else None
        )
        key_path = os.environ.get(ENVVAR_LOCAL_ENVOY_TLS_KEY_PATH, None)
        key = Path(key_path) if key_path is not None else None

        assert certificate is None or key is not None

        if os.environ.get(ENVVAR_LOCAL_ENVOY_MODE) == 'docker':
            return DockerLocalEnvoy(
                published_port=published_port,
                application_id=application_id,
                routables=routables,
                address_by_consensus=address_by_consensus,
                stopped_consensuses=stopped_consensuses,
                base64_encoded_proto_desc_set=base64_encoded_proto_desc_set,
                use_tls=use_tls,
                certificate=certificate,
                key=key,
                debug_mode=RESEMBLE_LOCAL_ENVOY_DEBUG,
            )

        return ExecutableLocalEnvoy(
            published_port=published_port,
            application_id=application_id,
            routables=routables,
            address_by_consensus=address_by_consensus,
            base64_encoded_proto_desc_set=base64_encoded_proto_desc_set,
            use_tls=use_tls,
            certificate=certificate,
            key=key,
            debug_mode=RESEMBLE_LOCAL_ENVOY_DEBUG,
        )
