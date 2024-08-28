from abc import abstractmethod

from atom.api import Atom

from cerebrium.defaults import (
    MIN_REPLICAS,
    MAX_REPLICAS,
    COOLDOWN,
    CPU,
    MEMORY,
    COMPUTE,
    GPU_COUNT,
    PROVIDER,
    REGION,
    PYTHON_VERSION,
    DOCKER_BASE_IMAGE_URL,
    INCLUDE,
    EXCLUDE,
    SHELL_COMMANDS,
)


class TOMLConfig(Atom):
    @abstractmethod
    def __toml__(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def __json__(self) -> dict:
        raise NotImplementedError


class ScalingConfig(TOMLConfig):
    min_replicas: int = MIN_REPLICAS
    max_replicas: int = MAX_REPLICAS
    cooldown: int = COOLDOWN

    def __toml__(self) -> str:
        return (
            "[cerebrium.scaling]\n"
            f"min_replicas = {self.min_replicas}\n"
            f"max_replicas = {self.max_replicas}\n"
            f"cooldown = {self.cooldown}\n\n"
        )

    def __json__(self) -> dict:
        return {
            "minReplicaCount": self.min_replicas,
            "maxReplicaCount": self.max_replicas,
            "cooldownPeriodSeconds": self.cooldown,
        }


class HardwareConfig(TOMLConfig):
    cpu: int = CPU
    memory: float = MEMORY
    compute: str = COMPUTE
    gpu_count: int = GPU_COUNT
    provider: str = PROVIDER
    region: str = REGION

    def __toml__(self) -> str:
        gpu_count_line = f"gpu_count = {self.gpu_count}\n" if self.compute != "CPU" else ""
        return (
            "[cerebrium.hardware]\n"
            f"cpu = {self.cpu}\n"
            f"memory = {self.memory}\n"
            f'compute = "{self.compute}"\n' + gpu_count_line + "\n"
        )

    def __json__(self) -> dict:
        return {
            "cpu": self.cpu,
            "memory": self.memory,
            "compute": self.compute,
            "gpuCount": self.gpu_count,
            "provider": self.provider,
            "region": self.region,
        }


class DeploymentConfig(TOMLConfig):
    name: str
    python_version: str = PYTHON_VERSION
    docker_base_image_url: str = DOCKER_BASE_IMAGE_URL
    include: str = INCLUDE
    exclude: str = EXCLUDE
    shell_commands: list[str] = SHELL_COMMANDS

    def __toml__(self) -> str:
        shell_commands_line = (
            f"shell_commands = {self.shell_commands}\n" if self.shell_commands else ""
        )
        return (
            "[cerebrium.deployment]\n"
            f'name = "{self.name}"\n'
            f'python_version = "{self.python_version}"\n'
            f'docker_base_image_url = "{self.docker_base_image_url}"\n'
            f'include = "{self.include}"\n'
            f'exclude = "{self.exclude}"\n' + shell_commands_line + "\n"
        )

    def __json__(self) -> dict:
        return {
            "name": self.name,
            "pythonVersion": self.python_version,
            "baseImage": self.docker_base_image_url,
            "include": self.include,
            "exclude": self.exclude,
            "shellCommands": self.shell_commands,
        }


class DependencyConfig(Atom):
    pip: dict[str, str] = {}
    conda: dict[str, str] = {}
    apt: dict[str, str] = {}

    def __toml__(self) -> str:
        pip_strings = (
            "[cerebrium.dependencies.pip]\n"
            + "\n".join(f'"{key}" = "{value}"' for key, value in self.pip.items())
            + "\n"
            if self.pip
            else ""
        )
        conda_strings = (
            "[cerebrium.dependencies.conda]\n"
            + "\n".join(f'"{key}" = "{value}"' for key, value in self.conda.items())
            + "\n"
            if self.conda != {}
            else ""
        )
        apt_strings = (
            "[cerebrium.dependencies.apt]\n"
            + "\n".join(f'"{key}" = "{value}"' for key, value in self.apt.items())
            + "\n"
            if self.apt != {}
            else ""
        )
        if pip_strings or conda_strings or apt_strings:
            return pip_strings + conda_strings + apt_strings + "\n"
        return ""

    def __json__(self) -> dict:
        return {"pip": self.pip, "conda": self.conda, "apt": self.apt}


class CerebriumConfig(Atom):
    deployment: DeploymentConfig
    hardware: HardwareConfig
    scaling: ScalingConfig
    dependencies: DependencyConfig

    def to_toml(self, file: str = "cerebrium.toml") -> None:
        with open(file, "w") as f:
            f.write(self.deployment.__toml__())
            f.write(self.hardware.__toml__())
            f.write(self.scaling.__toml__())
            f.write(self.dependencies.__toml__())

    def to_payload(self) -> dict:
        payload = {
            **self.deployment.__json__(),
            **self.hardware.__json__(),
            **self.scaling.__json__(),
        }
        return payload
