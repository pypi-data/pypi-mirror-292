import os.path
import re
import sys
import tempfile
import time
from pathlib import Path
from typing import List, Optional, Any

import docker
from docker.errors import BuildError
from poetry.toml import TOMLFile

from dotenv import load_dotenv
load_dotenv()


class DockerizeConfiguration:
    name: str = ""
    tags: List[str] = []
    entrypoint_cmd: List[str] = []
    python: str = ""
    ports: List[int] = []
    envs: dict[str, str] = {}
    labels: dict[str, str] = {}
    apt_packages: List[str] = []
    build_apt_packages: List[str] = []
    build_poetry_install_args: List[str] = []
    base_image: str = ""
    extra_build_instructions: List[str] = []
    extra_runtime_instructions: List[str] = []


class ProjectConfiguration:
    image_name: str
    image_tags: List[str]
    entrypoint: List[str]
    ports: List[int] = []
    envs: dict[str, str] = {}
    labels: dict[str, str]
    build_apt_packages: List[str] = []
    build_poetry_install_args: List[str] = []
    runtime_apt_packages: List[str] = []
    base_image: str = ""
    extra_build_instructions: List[str] = []
    extra_runtime_instructions: List[str] = []
    deps_packages: List[str] = []
    app_packages: List[str] = []



def _parse_list_str(value: Any, split_by: Optional[str] = " ") -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if split_by is not None:
        return str(value).split(split_by)
    return [str(value)]


def parse_dockerize_toml(from_dict: dict) -> DockerizeConfiguration:
    config = DockerizeConfiguration()
    config.name = _from_env_or_dict_str("name", from_dict)
    config.tags = _from_env_or_dict_list_str("tags", from_dict)
    config.entrypoint_cmd = _from_env_or_dict_list_str("entrypoint", from_dict, split_by=" ")
    config.python = _from_env_or_dict_str("python", from_dict)
    config.ports = _from_env_or_dict_list_int("ports", from_dict)
    config.envs = _from_env_or_dict_to_dict("env", from_dict)
    config.labels = _from_env_or_dict_to_dict("labels", from_dict)
    config.apt_packages = _from_env_or_dict_list_str("apt-packages", from_dict)
    config.build_apt_packages = _from_env_or_dict_list_str("build-apt-packages", from_dict)
    config.build_poetry_install_args = _from_env_or_dict_list_str("build-poetry-install-args", from_dict)
    config.base_image = _from_env_or_dict_str("base-image", from_dict)
    config.extra_build_instructions = _from_env_or_dict_list_str("extra-build-instructions", from_dict)
    config.extra_runtime_instructions = _from_env_or_dict_list_str("extra-runtime-instructions", from_dict)
    return config


def _from_env_or_dict_str(key: str, from_dict: dict) -> str:
    raw_value = _from_env_or_dict_raw(from_dict, key)
    if raw_value is None:
        return ""
    return str(raw_value)

def _from_env_or_dict_list_str(key: str, from_dict: dict, split_by: Optional[str] = None) -> List[str]:
    raw_value = _from_env_or_dict_raw(from_dict, key)
    return _parse_list_str(raw_value, split_by)

def _from_env_or_dict_list_int(key: str, from_dict: dict) -> List[int]:
    raw_value = _from_env_or_dict_raw(from_dict, key)
    as_strings = _parse_list_str(raw_value)
    return [int(s) for s in as_strings]


def _from_env_or_dict_to_dict(key: str, from_dict: dict) -> dict[str, str]:
    to_dict = {}
    from_dict_value = from_dict.get(key)
    if from_dict_value is not None:
        to_dict.update(from_dict_value)

    env_key = _env_key(key)
    for env_var in os.environ:
        if env_var.startswith(env_key):
            key = env_var.replace(env_key + "_", "")
            value = os.environ[env_var]
            to_dict[key] = value
    return to_dict

def _from_env_or_dict_raw(from_dict, key) -> Any:
    env_key = _env_key(key)
    raw_value = os.environ.get(env_key) or from_dict.get(key)
    return raw_value


def _env_key(key):
    env_key = "DOCKERIZE_" + key.upper().replace("-", "_")
    return env_key


def extract_python_version(pyversion: str) -> Optional[str]:
    try:
        if pyversion == "*":
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
            print(f"Python version is too generic (*), using same as system: {python_version}")
        elif re.match("[\\^~]?(\\d\\.\\d+)(\\.\\d+)?", pyversion) is not None:
            python_version = re.match("[\\^~]?(\\d\\.\\d+)(\\.\\d+)?", pyversion).group(1)
        else:
            python_version = re.match("[\\^~]?(\\d)(\\.\\*)?", pyversion).group(1)
        return python_version
    except Exception:
        return None


def parse_pyproject_toml(pyproject_path) -> ProjectConfiguration:
    pyproject_file = os.path.join(pyproject_path, 'pyproject.toml')
    file = TOMLFile(Path(pyproject_file))
    doc = file.read()

    config = ProjectConfiguration()
    tool = doc.get('tool', dict())
    tool_poetry = tool.get('poetry', dict())

    dockerize_section = parse_dockerize_toml(tool.get('dockerize', dict()))

    config.image_name = dockerize_section.name or tool_poetry['name']
    config.image_tags = dockerize_section.tags or [tool_poetry["version"], "latest"]

    if dockerize_section.entrypoint_cmd:
        config.entrypoint = dockerize_section.entrypoint_cmd
    else:
        if 'packages' in tool_poetry:
            packages = tool_poetry['packages']
            if len(packages) > 1:
                raise ValueError(f"""Multiple 'packages' found in pyproject.toml, please specify 'entrypoint' in 'tool.dockerize' section.
[tool.dockerize] 
entrypoint = "python -m {packages[0]['include']}"
""")
            package = packages[0]
            name = package["include"]
            config.entrypoint = ["python", "-m", name]

    if not config.entrypoint:
        raise ValueError('No package found in pyproject.toml and no entrypoint specified in dockerize section')

    config.runtime_apt_packages = dockerize_section.apt_packages or []
    config.build_apt_packages = dockerize_section.build_apt_packages or []
    config.build_apt_packages.append("gcc")
    config.build_poetry_install_args = dockerize_section.build_poetry_install_args or []
    if 'packages' in tool_poetry:
        config.app_packages += [package["include"] for package in tool_poetry['packages']]

    if "dependencies" in tool_poetry:
        for dep in tool_poetry["dependencies"]:
            if isinstance(tool_poetry["dependencies"][dep], dict):
                if 'path' in tool_poetry["dependencies"][dep]:
                    config.deps_packages.append(tool_poetry["dependencies"][dep]['path'])
                if 'git' in tool_poetry["dependencies"][dep]:
                    config.build_apt_packages.append("git")

    if dockerize_section.base_image:
        config.base_image = dockerize_section.base_image
    elif not dockerize_section.python:
        if "dependencies" not in tool_poetry or "python" not in tool_poetry["dependencies"]:
            print("No python version specified in pyproject.toml, using 3.11")
            python_version = "3.11"
        else:
            declared_py_version = tool_poetry["dependencies"]["python"]
            python_version = extract_python_version(declared_py_version)
            if python_version is None:
                python_version = "3.11"
                print(f"Declared python version dependency is too complex, using default: {python_version}")
            else:
                print(f"Python version extracted from project configuration: {python_version}")
        config.base_image = f"python:{python_version}-slim-bookworm"
    else:
        config.base_image = f"python:{dockerize_section.python}-slim-buster"

    config.ports = dockerize_section.ports or []
    config.envs = dockerize_section.envs or {}
    license = tool_poetry["license"] if "license" in tool_poetry else ""
    repository = tool_poetry["repository"] if "repository" in tool_poetry else ""
    authors = tool_poetry["authors"] if "authors" in tool_poetry else ""

    labels = {"org.opencontainers.image.title": config.image_name,
              "org.opencontainers.image.version": tool_poetry["version"],
              "org.opencontainers.image.authors": authors,
              "org.opencontainers.image.licenses": license,
              "org.opencontainers.image.url": repository,
              "org.opencontainers.image.source": repository}
    if dockerize_section.labels:
        labels.update(dockerize_section.labels)
    config.labels = labels
    config.build_runtime_packages = dockerize_section.apt_packages or []
    config.extra_build_instructions = dockerize_section.extra_build_instructions or []
    config.extra_runtime_instructions = dockerize_section.extra_runtime_instructions or []

    return config


def generate_extra_instructions_str(instructions: List[str]) -> str:
    if not len(instructions):
        return ""
    return "\n".join(instructions)


def generate_apt_packages_str(apt_packages: List[str]) -> str:
    if not len(apt_packages):
        return ""
    apt_packages_str = " ".join(list(set(apt_packages)))
    return f"""
ARG DEBIAN_FRONTEND=noninteractive

RUN echo 'Acquire::http::Timeout "30";\\nAcquire::http::ConnectionAttemptDelayMsec "2000";\\nAcquire::https::Timeout "30";\\nAcquire::https::ConnectionAttemptDelayMsec "2000";\\nAcquire::ftp::Timeout "30";\\nAcquire::ftp::ConnectionAttemptDelayMsec "2000";\\nAcquire::Retries "15";' > /etc/apt/apt.conf.d/99timeout_and_retries \
     && apt-get update \
     && apt-get -y dist-upgrade \
     && apt-get -y install {apt_packages_str}"""


def generate_add_project_toml_str(config: ProjectConfiguration, real_context_path: str) -> str:
    add_str = "RUN mkdir /app\n"
    add_str += "COPY pyproject.toml poetry.lock* README* /app/\n"
    for package in list(set(config.deps_packages)):
        if os.path.exists(os.path.join(real_context_path, package)):
            add_str += f"COPY ./{package} /app/{package}\n"
        else:
            print(f"WARNING: {package} not found, skipping it")
    return add_str

def generate_add_packages_str(config: ProjectConfiguration, real_context_path: str) -> str:
    add_str = ""
    for package in list(set(config.app_packages)):
        if os.path.exists(os.path.join(real_context_path, package)):
            add_str += f"COPY ./{package} /app/{package}\n"
        else:
            print(f"WARNING: {package} not found, skipping it")
    return add_str

def generate_docker_file_content(config: ProjectConfiguration, real_context_path: str) -> str:
    ports_str = "\n".join([f"EXPOSE {port}" for port in config.ports])
    cmd_str = " ".join(config.entrypoint)
    envs_str = "\n".join([f"ENV {key}={value}" for key, value in config.envs.items()])
    labels_str = "\n".join([f"LABEL {key}={value}" for key, value in config.labels.items()])
    return f"""
FROM {config.base_image} as builder
RUN pip install poetry==1.7.1

ENV POETRY_VIRTUALENVS_IN_PROJECT=1
ENV POETRY_VIRTUALENVS_CREATE=1
ENV POETRY_CACHE_DIR=/tmp/poetry_cache

{generate_apt_packages_str(config.build_apt_packages)}
{generate_add_project_toml_str(config, real_context_path)}

{generate_add_packages_str(config, real_context_path)}
{generate_extra_instructions_str(config.extra_build_instructions)}

RUN cd /app && poetry install --no-interaction --no-ansi {" ".join(config.build_poetry_install_args)}

FROM {config.base_image} as runtime
{generate_apt_packages_str(config.runtime_apt_packages)}
{labels_str}

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
{envs_str}

WORKDIR /app
COPY --from=builder /app/ /app/

{ports_str}
{generate_extra_instructions_str(config.extra_runtime_instructions)}
CMD {cmd_str}"""


def build_image(path: str, verbose: bool = False, generate: bool = False) -> None:
    config = parse_pyproject_toml(path)
    build(config=config, root_path=path, verbose=verbose, generate=generate)


def build(
        root_path: str,
        config: ProjectConfiguration,
        verbose: bool = False,
        generate: bool = False
) -> None:
    """
    Build a docker image from a poetry project.
    """

    with tempfile.NamedTemporaryFile() as tmp:
        dockerfile = tmp.name
        real_context_path = os.path.realpath(root_path)
        content = generate_docker_file_content(config, real_context_path)
        if generate:
            generate_dockerfile_path = os.path.join(real_context_path, "Dockerfile")
            with open(generate_dockerfile_path, "w") as f:
                f.write(content)
            print(f"Stored Dockerfile to {generate_dockerfile_path} 📄")
            return
        tmp.write(content.encode("utf-8"))
        tmp.flush()
        if verbose:
            print("Building with dockerfile content: \n===[Dockerfile]==\n" + content + "\n===[/Dockerfile]==\n")

        dockerignore = os.path.join(real_context_path, ".dockerignore")
        dockerignore_created = write_dockerignore_if_needed(dockerignore)
        try:
            first_tag = config.image_tags[0]
            full_image_name = f"{config.image_name}:{first_tag}"
            print(f"Building image: {full_image_name} 🔨")
            docker_client = docker.from_env()
            start_time = time.time()
            try:
                _, decoder = docker_client.images.build(
                    path=real_context_path,
                    dockerfile=dockerfile,
                    tag=full_image_name,
                    rm=False
                )
                if verbose:
                    print_build_logs(decoder)
            except BuildError as e:
                iterable = iter(e.build_log)
                print("❌ Build failed, printing execution logs:\n\n")
                print_build_logs(iterable)
                print("Error: " + str(e))
                raise e

            for tag in config.image_tags:
                if tag == first_tag:
                    continue
                docker_client.images.get(full_image_name).tag(config.image_name, tag=tag)
            diff = time.time() - start_time
            print(f"Successfully built images: ✅ ({round(diff, 1)}s)")
            for tag in config.image_tags:
                print(f"  - {config.image_name}:{tag}")
        finally:
            if dockerignore_created:
                try:
                    os.remove(dockerignore)
                except:
                    pass


def print_build_logs(iterable):
    while True:
        try:
            item = next(iterable)
            if "stream" in item:
                print(item["stream"], end='')
            elif "error" in item:
                print(item["error"], end='')
            else:
                pass
        except StopIteration:
            break


def write_dockerignore_if_needed(dockerignore: str):
    dockerignore_created = False
    if not os.path.exists(dockerignore):
        print("No .dockerignore found, using a good default one 😉")
        with open(dockerignore, "w") as f:
            f.write("""
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis""")
        dockerignore_created = True
    return dockerignore_created
