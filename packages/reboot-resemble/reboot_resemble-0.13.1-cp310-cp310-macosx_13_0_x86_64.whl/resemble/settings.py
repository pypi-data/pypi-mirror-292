# The settings below must match their equivalents, if applicable, in:
# * resemble/settings.h
# * <possibly other languages by the time you read this>

# gRPC max message size to transmit large state data.
MAX_SIDECAR_GRPC_MESSAGE_LENGTH_BYTES = 100 * 1024 * 1024

DOCS_BASE_URL = "https://docs.reboot.dev"

# The path to the directory where Resemble state is stored.
RESEMBLE_STATE_DIRECTORY = '/var/run/resemble/state'

# The name of the admin secret that is used to authenticate admin requests,
# e.g., for inspect.
ADMIN_SECRET_NAME = 'rsm-admin-secret'

# The names of environment variables that are present both in `rsm dev run` and
# in Kubernetes.
#
# TODO: The API key should likely be provided by a file in production, to allow
# for rotation.
ENVVAR_RSM_CLOUD_API_KEY = 'RSM_CLOUD_API_KEY'
ENVVAR_RSM_CLOUD_GATEWAY_ADDRESS = 'RSM_CLOUD_GATEWAY_ADDRESS'
ENVVAR_RSM_CLOUD_GATEWAY_SECURE_CHANNEL = 'RSM_CLOUD_GATEWAY_SECURE_CHANNEL'

# The names of environment variables that are only present when running in `rsm
# dev run`.
ENVVAR_RSM_DEV = 'RSM_DEV'
ENVVAR_RSM_SERVE = 'RSM_SERVE'
ENVVAR_RSM_NAME = 'RSM_NAME'
ENVVAR_RSM_EFFECT_VALIDATION = 'RSM_EFFECT_VALIDATION'
ENVVAR_RSM_SECRETS_DIRECTORY = 'RSM_SECRETS_DIRECTORY'
ENVVAR_RSM_DIRECTORY = 'RSM_DIRECTORY'
ENVVAR_RSM_NODEJS = 'RSM_NODEJS'
ENVVAR_RSM_PARTITIONS = 'RSM_PARTITIONS'

# The names of environment variables that are only present when configuring a
# local Envoy.
ENVVAR_RESEMBLE_LOCAL_ENVOY = 'RESEMBLE_LOCAL_ENVOY'
ENVVAR_RESEMBLE_LOCAL_ENVOY_PORT = 'RESEMBLE_LOCAL_ENVOY_PORT'

# The name of an environment variable that indicates that we are
# running from within `node`. Not to be confused with
# `ENVVAR_RSM_NODEJS` which implies the `--nodejs` flag was set when
# using `rsm`.
ENVVAR_RESEMBLE_NODEJS = 'RESEMBLE_NODEJS'

# The name of an environment variable that's only present when running on
# Kubernetes.
ENVVAR_KUBERNETES_SERVICE_HOST = 'KUBERNETES_SERVICE_HOST'

# When we set up servers we often need to listen on every addressable
# interface on the local machine. This is especially important in some
# circumstances where networks may be rather convoluted, e.g., when we
# have local Docker containers.
EVERY_LOCAL_NETWORK_ADDRESS = '0.0.0.0'
ONLY_LOCALHOST_NETWORK_ADDRESS = '127.0.0.1'

# Ports that Resemble is, by default, reachable on for gRPC and HTTP traffic
# from clients running outside the Resemble cluster. These are the ports that
# users will use in their configuration/code when they choose how to connect to
# a Resemble cluster.
#
# Note that these are defaults; some environments may override these settings.
# Furthermore, many environments may only have one of these ports exposed.
#
# The insecure port serves unencrypted traffic. The secure port serves traffic
# that uses TLS.
DEFAULT_INSECURE_PORT = 9990
DEFAULT_SECURE_PORT = 9991

# Normally, application IDs are not very human-readable - they're hashes derived
# from a human-readable name. However, we choose a hardcoded human-readable ID
# here, for two reasons:
# 1. We want a human-readable endpoint for the Resemble Cloud; e.g.:
#      cloud.some-cluster.resemble.cloud
# 2. If we need to debug a Kubernetes cluster, we're likely to need to interact
#    with the cloud app. Giving it a human-readable ID makes that easier.
CLOUD_APPLICATION_ID = "cloud"
CLOUD_USER_ID = "cloud"
CLOUD_SPACE_NAME = "cloud"

# The length bounds of user inputs that will be encoded into headers. The
# values are chosen to be larger than any value we've observed in reasonable use
# cases, but small enough that the gRPC maximum metadata size (8 KiB, see [1])
# will not be exceeded.
#   [1]: https://grpc.io/docs/guides/metadata/#be-aware)
MIN_ACTOR_ID_LENGTH = 1
MAX_ACTOR_ID_LENGTH = 128
MAX_IDEMPOTENCY_KEY_LENGTH = 128
MAX_BEARER_TOKEN_LENGTH = 4096

# The suffix given to sidecar state directories.
SIDECAR_SUFFIX = "-sidecar"

# Local envoy specific environment variables that impact how it gets
# configured.
ENVOY_VERSION = '1.30.2'
ENVOY_PROXY_IMAGE = f'envoyproxy/envoy:v{ENVOY_VERSION}'
ENVVAR_LOCAL_ENVOY_USE_TLS = 'RESEMBLE_LOCAL_ENVOY_USE_TLS'
ENVVAR_LOCAL_ENVOY_TLS_CERTIFICATE_PATH = 'RESEMBLE_LOCAL_ENVOY_TLS_CERTIFICATE_PATH'
ENVVAR_LOCAL_ENVOY_TLS_KEY_PATH = 'RESEMBLE_LOCAL_ENVOY_TLS_KEY_PATH'
# The name of the environment variable, which should be set by 'rsm serve' or
# 'rsm dev run', that contains the mode in which the Envoy should run
# (executable/docker).
ENVVAR_LOCAL_ENVOY_MODE = 'RESEMBLE_LOCAL_ENVOY_MODE'
ENVVAR_LOCAL_ENVOY_DEBUG = 'RESEMBLE_LOCAL_ENVOY_DEBUG'

# Whether or not signal manipulation is available.
ENVVAR_SIGNALS_AVAILABLE = 'RESEMBLE_SIGNALS_AVAILABLE'

# Args for launching a nodejs based consensus.
ENVVAR_NODEJS_CONSENSUS = 'RESEMBLE_NODEJS_CONSENSUS'
ENVVAR_NODEJS_CONSENSUS_BASE64_ARGS = 'RESEMBLE_NODEJS_CONSENSUS_BASE64_ARGS'
