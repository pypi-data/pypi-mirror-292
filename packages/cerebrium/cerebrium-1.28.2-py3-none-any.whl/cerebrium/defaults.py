from sys import version_info

# Deployment
PYTHON_VERSION = f"{version_info.major}.{version_info.minor}"
DOCKER_BASE_IMAGE_URL = "debian:bookworm-slim"
INCLUDE = "[./*, main.py, cerebrium.toml]"
EXCLUDE = "[.*]"
SHELL_COMMANDS = []

# Hardware
CPU = 2
MEMORY = 12.0
COMPUTE = "CPU"
GPU_COUNT = 1
PROVIDER = "aws"
REGION = "us-east-1"

# Scaling
MIN_REPLICAS = 0
MAX_REPLICAS = 5
COOLDOWN = 30
