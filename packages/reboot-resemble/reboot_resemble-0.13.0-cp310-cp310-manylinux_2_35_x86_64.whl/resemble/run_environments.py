import os
from dataclasses import dataclass
from enum import Enum
from resemble.settings import (
    ENVVAR_KUBERNETES_SERVICE_HOST,
    ENVVAR_NODEJS_CONSENSUS,
    ENVVAR_RSM_DEV,
    ENVVAR_RSM_SERVE,
)


class RunEnvironment(Enum):
    """Known run environments."""
    RSM_DEV = 1
    RSM_SERVE = 2
    RSM_CLOUD = 3


class TypescriptEnvironment(Enum):
    """Known typescript run environments."""
    DOES_NOT_EXIST = 0
    NODEJS_CONSENSUS = 1


@dataclass(
    kw_only=True,
    frozen=True,
)
class RunSettings:
    run_environment: RunEnvironment
    typescript_environment: TypescriptEnvironment


class InvalidRunEnvironment(RuntimeError):
    """Exception for when run environment cannot be determined."""
    pass


def _detect_run_environment() -> RunEnvironment:
    """Internal helper to determine what run environment we are in."""
    # NOTE: ordering matters here as we may have multiple environment
    # variables set but some take precedence to others.
    if os.environ.get(ENVVAR_RSM_DEV, 'false').lower() == 'true':
        return RunEnvironment.RSM_DEV
    elif os.environ.get(ENVVAR_RSM_SERVE, 'false').lower() == 'true':
        return RunEnvironment.RSM_SERVE
    elif os.environ.get(ENVVAR_KUBERNETES_SERVICE_HOST) is not None:
        return RunEnvironment.RSM_CLOUD

    raise InvalidRunEnvironment()


def _detect_typescript_environment() -> TypescriptEnvironment:
    """Internal helper to determine what typescript environment we are in."""
    if os.environ.get(ENVVAR_NODEJS_CONSENSUS, 'false').lower() == 'true':
        return TypescriptEnvironment.NODEJS_CONSENSUS

    return TypescriptEnvironment.DOES_NOT_EXIST


def _detect_run_settings() -> RunSettings:
    """Internal helper to determine what run environment we are in."""

    run_environment = _detect_run_environment()
    typescript_environment = _detect_typescript_environment()

    return RunSettings(
        run_environment=run_environment,
        typescript_environment=typescript_environment,
    )


def on_cloud() -> bool:
    """Helper for checking if we are running in a 'rsm cloud'
    cluster."""
    try:
        run_settings = _detect_run_settings()
        return run_settings.run_environment == RunEnvironment.RSM_CLOUD
    except InvalidRunEnvironment:
        return False


def running_rsm_dev() -> bool:
    """Helper for checking if we are running in a local development
    environment."""

    try:
        run_settings = _detect_run_settings()
        return run_settings.run_environment == RunEnvironment.RSM_DEV
    except InvalidRunEnvironment:
        return False
