import aiofiles.os
import asyncio
import os
import shutil
import sys
from resemble.cli import terminal
from resemble.cli.detect_partitions import detect_partitions
from resemble.cli.dev import (
    add_application_options,
    check_docker_status,
    try_and_become_child_subreaper_on_linux,
)
from resemble.cli.directories import (
    add_working_directory_options,
    use_working_directory,
)
from resemble.cli.rc import ArgumentParser, ArgumentParserFactory
from resemble.cli.subprocesses import Subprocesses
from resemble.controller.exceptions import InputError
from resemble.controller.plan_makers import validate_num_consensuses
from resemble.settings import (
    ENVOY_VERSION,
    ENVVAR_LOCAL_ENVOY_MODE,
    ENVVAR_LOCAL_ENVOY_TLS_CERTIFICATE_PATH,
    ENVVAR_LOCAL_ENVOY_TLS_KEY_PATH,
    ENVVAR_LOCAL_ENVOY_USE_TLS,
    ENVVAR_RESEMBLE_LOCAL_ENVOY,
    ENVVAR_RESEMBLE_LOCAL_ENVOY_PORT,
    ENVVAR_RSM_DIRECTORY,
    ENVVAR_RSM_EFFECT_VALIDATION,
    ENVVAR_RSM_NAME,
    ENVVAR_RSM_PARTITIONS,
    ENVVAR_RSM_SECRETS_DIRECTORY,
    ENVVAR_RSM_SERVE,
)


async def _pick_envoy_mode(
    subprocesses: Subprocesses,
    env: dict[str, str],
) -> None:
    # Will we run Envoy inside a new Docker container, or can we run it as a
    # stand-alone program? Note that it's entirely possible that we are
    # already inside a Docker container, inside which we might run 'envoy'
    # as a stand-alone process.
    envoy_mode = 'docker' if shutil.which('envoy') is None else 'executable'
    env[ENVVAR_LOCAL_ENVOY_MODE] = envoy_mode

    if envoy_mode == 'docker':
        return await check_docker_status(subprocesses)

    async with subprocesses.exec(
        'envoy',
        '--version',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    ) as process:
        stdout, _ = await process.communicate()
        if process.returncode != 0:
            terminal.fail(
                f"Could not use Envoy:\n"
                "\n"
                f"{stdout.decode() if stdout is not None else '<no output>'}"
            )

        # 'envoy --version' outputs something like:
        #  envoy  version:
        #  d79f6e8d453ee260e9094093b8dd31af0056e67b/1.30.2/Clean/RELEASE/BoringSSL
        if ENVOY_VERSION not in stdout.decode():
            terminal.fail(
                f"Expecting Envoy version '{ENVOY_VERSION}', but found "
                f"'{stdout.decode()}'. Are you using the right Resemble "
                "base image in Docker?"
            )


def register_serve(parser: ArgumentParser):
    add_working_directory_options(parser.subcommand('serve'))

    add_application_options(parser.subcommand('serve'))

    parser.subcommand('serve').add_argument(
        '--directory',
        type=str,
        help='path to directory for durably storing application state',
        required=True,
    )

    parser.subcommand('serve').add_argument(
        '--partitions',
        type=int,
        help=(
            'the number of partitioned serving processes to spawn. Defaults to '
            'the number of cores available. Note that changing this value '
            'currently requires a backup and restore, but that restriction will '
            'be lifted in the near future.'
        ),
    )

    parser.subcommand('serve').add_argument(
        '--name',
        type=str,
        help="name of application, used to differentiate within '--directory'",
        required=True,
    )

    parser.subcommand('serve').add_argument(
        '--port',
        type=int,
        help='port to listen on',
        required=True,
    )

    parser.subcommand('serve').add_argument(
        '--tls',
        type=str,
        choices=['own-certificate', 'external'],
        required=True,
        help="how your application will provide secure TLS connections. Set "
        "'own-certificate' if you'd like to provide your own TLS certificate, "
        "or set 'external' if this `rsm serve` is deployed behind an external "
        "load balancer that already does TLS termination.",
    )

    parser.subcommand('serve').add_argument(
        '--tls-certificate',
        type=str,
        help=
        "path to TLS certificate to use when setting '--tls=own-certificate'",
    )

    parser.subcommand('serve').add_argument(
        '--tls-key',
        type=str,
        help="path to TLS key to use when setting '--tls=own-certificate'",
    )


async def serve(
    args,
    parser: ArgumentParser,
    parser_factory: ArgumentParserFactory,
) -> int:
    """Invokes `serve` with the arguments passed to 'rsm serve'."""

    # Determine the working directory and move into it.
    with use_working_directory(args, parser, verbose=True):

        # If on Linux try and become a child subreaper so that we can
        # properly clean up all processes descendant from us!
        try_and_become_child_subreaper_on_linux()

        # Use `Subprocesses` to manage all of our subprocesses for us.
        subprocesses = Subprocesses()

        application = os.path.abspath(args.application)

        # TODO: run `rsm protoc` once.

        # Set all the environment variables that
        # 'resemble.aio.Application' will be looking for.
        #
        # We make a copy of the environment so that we don't change
        # our environment variables which might cause an issue.
        env = os.environ.copy()

        env[ENVVAR_RSM_SERVE] = 'true'

        assert args.name is not None

        env[ENVVAR_RSM_NAME] = args.name

        env[ENVVAR_RSM_DIRECTORY] = args.directory

        if args.secrets_directory is not None:
            env[ENVVAR_RSM_SECRETS_DIRECTORY] = args.secrets_directory

        # Pick the mode we'll run Envoy in: either as a stand-alone
        # program or inside a Docker container.
        await _pick_envoy_mode(subprocesses, env)

        env[ENVVAR_RESEMBLE_LOCAL_ENVOY] = 'true'

        env[ENVVAR_RESEMBLE_LOCAL_ENVOY_PORT] = str(args.port)

        # NOTE: We call detect_partitions lazily so that a user has the recourse
        # of explicitly setting `--partitions` if it fails.
        partitions = (
            args.partitions if args.partitions is not None else
            detect_partitions(flag_name='--partitions')
        )
        try:
            validate_num_consensuses(partitions, "partitions")
        except InputError as e:
            terminal.fail(f"Invalid `--partitions` value: {e}")
        env[ENVVAR_RSM_PARTITIONS] = str(partitions)

        # Check that the TLS configuration they gave us is valid and set the
        # `LocalEnvoy` environment variables.
        if args.tls == 'own-certificate':
            if not args.tls_key or not args.tls_certificate:
                terminal.fail(
                    "When setting '--tls=own-certificate', flags "
                    "'--tls-certificate' and '--tls-key' must also be set"
                )

            if not await aiofiles.os.path.isfile(args.tls_certificate):
                terminal.fail(
                    f"Expecting file at --tls-certificate='{args.tls_certificate}'"
                )
            with open(args.tls_certificate) as f:
                first_line = f.readline().strip('\n')
                if first_line != "-----BEGIN CERTIFICATE-----":
                    terminal.fail(
                        f"The file at --tls-certificate='{args.tls_key}' does not "
                        "seem to contain a TLS certificate"
                    )

            if not await aiofiles.os.path.isfile(args.tls_key):
                terminal.fail(f"Expecting file at --tls-key='{args.tls_key}'")
            with open(args.tls_key) as f:
                first_line = f.readline().strip('\n')
                if first_line != "-----BEGIN PRIVATE KEY-----":
                    terminal.fail(
                        f"The file at --tls-key='{args.tls_key}' does not seem to "
                        "contain a TLS key"
                    )

            env[ENVVAR_LOCAL_ENVOY_USE_TLS] = "True"
            # We don't check the certificate and key for being None, because in
            # that case LocalEnvoy will use localhost.direct certificate.
            env[ENVVAR_LOCAL_ENVOY_TLS_CERTIFICATE_PATH] = args.tls_certificate
            env[ENVVAR_LOCAL_ENVOY_TLS_KEY_PATH] = args.tls_key

        else:
            assert args.tls == 'external'
            if args.tls_key or args.tls_certificate:
                terminal.fail(
                    "When setting '--tls=external', flags '--tls-certificate' "
                    "and '--tls-key' cannot be set"
                )
            env[ENVVAR_LOCAL_ENVOY_USE_TLS] = "False"

        env[ENVVAR_RSM_EFFECT_VALIDATION] = 'DISABLED'

        # Also include all environment variables from '--env='.
        for (key, value) in args.env or []:
            env[key] = value

        # If 'PYTHONPATH' is not explicitly set, we'll set it to the
        # specified generated code directory. We want to get the directory from
        # 'rsm protoc' flags, which user might have specified in '.rsmrc'.
        if 'PYTHONPATH' not in env and parser.dot_rc is not None:
            protoc_parser = parser_factory(['rsm', 'protoc'])
            protoc_args, _ = protoc_parser.parse_args()
            if protoc_args.python is not None:
                env['PYTHONPATH'] = protoc_args.python

        if not await aiofiles.os.path.isfile(application):
            terminal.fail(f"Missing application at '{application}'")

        # Expect an executable if we haven't been asked to use
        # `python`.
        if (
            args.python is None and
            not await aiofiles.os.access(application, os.X_OK)
        ):
            terminal.fail(
                f"Expecting executable application at '{application}'. "
                "Specify '--python' if you want to run a Python application."
            )

        launcher = sys.executable if args.python is not None else None

        args = [application] if launcher is None else [launcher, application]

        async with subprocesses.exec(*args, env=env) as process:
            return await process.wait()
