import json
import requests
from pathlib import Path
import logging
from rich.progress import Progress, SpinnerColumn, TextColumn
import subprocess
import uuid
from rockai.docker.torch_version import torch_version_list
import importlib.metadata

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("docker").setLevel(logging.WARNING)


def remove_some_libs(file_name, lib_to_be_deleted):
    try:
        # Open the file in read mode
        with open(file_name, "r") as file:
            lines = file.readlines()

        # Open the file in write mode
        with open(file_name, "w") as file:
            for line in lines:
                if lib_to_be_deleted not in line:
                    file.write(line)

        print("Successfully removed {} from {}".format(lib_to_be_deleted, file_name))
    except FileNotFoundError:
        print("{} not found".format(file_name))


def get_tensorflow_version(filename: str) -> str:
    """
    Reads a pip's requirements.txt file and returns the TensorFlow version specified in it.
    """
    try:
        with open(filename, "r") as file:
            for line in file:
                if line.startswith("tensorflow=="):
                    # Split the line at '==' to get the package and version
                    parts = line.strip().split("==")
                    if len(parts) == 2:
                        return parts[1]
                    else:
                        return "No specific version specified"
        return None
    except FileNotFoundError:
        return "File not found"


def run_command_and_get_output():
    # Run the command and capture the output
    result = subprocess.run(
        ["python", "-m", "rockai.command.openapi_schema"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Check if the command was successful
    if result.returncode == 0:
        # Store the output in a string
        output = result.stdout
    else:
        # Handle the error
        output = f"Error: {result.stderr}"

    return "'{}'".format(
        str(json.dumps(json.dumps(json.loads(output)), separators=(",", ":")))
    )


def build_docker_image(
    image_tag,
    config_map,
    tag,
    platform="linux/amd64",
    port=8000,
    is_tensorflow=False,
    install_cmd=None,
):
    docker_list = []
    docker_list.append(add_base(image_tag))
    docker_list.append(add_env("DEBIAN_FRONTEND=noninteractive"))
    # docker_list.append(add_env("HF_ENDPOINT=https://hf-mirror.com"))
    docker_list.append(add_work_dir("/src"))
    docker_list.append(copy_files(".", "/src"))
    docker_list.append(
        add_run(
            "sed -i 's/http:\/\/archive.ubuntu.com\/ubuntu\//http:\/\/mirrors.tuna.tsinghua.edu.cn\/ubuntu\//g' /etc/apt/sources.list"
        )
    )
    docker_list.append(add_run("apt clean"))
    docker_list.append(add_run("apt-get clean"))
    docker_list.append(add_run("apt update && apt-get update"))
    docker_list.append(add_env('PATH="/root/.pyenv/shims:/root/.pyenv/bin:$PATH"'))
    docker_list.append(
        add_run(
            """--mount=type=cache,target=/var/cache/apt apt-get update -qq && apt-get install -qqy --no-install-recommends \
	make \
	build-essential \
	libssl-dev \
	zlib1g-dev \
	libbz2-dev \
	libreadline-dev \
	libsqlite3-dev \
	wget \
	curl \
	llvm \
	libncurses5-dev \
	libncursesw5-dev \
	xz-utils \
	tk-dev \
	libffi-dev \
	liblzma-dev \
	git \
	ca-certificates \
	&& rm -rf /var/lib/apt/lists/*
"""
        )
    )
    docker_list.append(
        add_run(
            """curl -s -S -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash && \
	git clone https://github.com/momo-lab/pyenv-install-latest.git "$(pyenv root)"/plugins/pyenv-install-latest && \
	pyenv install-latest {} && \
	pyenv global $(pyenv install-latest --print {}) && \
	pip install "wheel<1"
""".format(
                config_map["build"]["python_version"],
                config_map["build"]["python_version"],
            )
        )
    )
    docker_list.append(add_expose(port))
    if "system_packages" in config_map["build"]:
        for package in config_map["build"]["system_packages"]:
            docker_list.append(add_run("apt install -y {}".format(package)))

    docker_list.append(
        add_run(f"pip install rockai=={importlib.metadata.version('rockai')}")
    )
    if "python_requirements" not in config_map["build"]:
        logging.info("No python requirements.txt file found in rock.yaml")
    else:
        docker_list.append(
            copy_files("{}".format(config_map["build"]["python_requirements"]), "/src")
        )
        if is_tensorflow:  # building tensorflow
            remove_some_libs(
                config_map["build"]["python_requirements"], "tensorflow-metal"
            )
            remove_some_libs(
                config_map["build"]["python_requirements"], "tensorflow-macos"
            )
            docker_list.append(
                add_run(
                    "pip install -r {} {}".format(
                        "requirements.txt",
                        "-i https://pypi.tuna.tsinghua.edu.cn/simple --extra-index-url https://pypi.org/simple/",
                    )
                )
            )

            tf_version = get_tensorflow_version(
                config_map["build"]["python_requirements"]
            )
            docker_list.append(
                add_run(
                    "pip install tensorflow[and-cuda]=={} -i https://pypi.tuna.tsinghua.edu.cn/simple".format(
                        tf_version
                    )
                )
            )
        else:  # building torch
            remove_some_libs(config_map["build"]["python_requirements"], "torch")
            remove_some_libs(config_map["build"]["python_requirements"], "torchvision")
            remove_some_libs(config_map["build"]["python_requirements"], "torchaudio")
            if install_cmd is not None:
                docker_list.append(add_run(install_cmd))
                docker_list.append(
                    add_run(
                        "pip install -r {} {}".format(
                            "requirements.txt",
                            "-i https://pypi.tuna.tsinghua.edu.cn/simple --extra-index-url https://pypi.org/simple/",
                        )
                    )
                )

    docker_list.append(
        add_labels("run.cog.openapi_schema", run_command_and_get_output())
    )
    docker_list.append(add_cmd("rockai start --port {}".format(port)))

    save_docker_file(docker_list)
    subprocess.run(
        [
            "docker",
            "build",
            "--platform",
            platform,
            "-t",
            tag,
            "-f",
            Path.cwd() / ".rock_temp/Dockerfile",
            Path.cwd(),
        ]
    )


def build_cpu_image(
    image_tag, config_map, tag, platform="linux/amd64", port=8000, framework=None
):
    docker_list = []
    docker_list.append(add_base(image_tag))
    docker_list.append(add_env("DEBIAN_FRONTEND=noninteractive"))
    docker_list.append(add_run("apt update && apt-get update"))
    docker_list.append(add_work_dir("/src"))
    docker_list.append(copy_files(".", "/src"))
    docker_list.append(
        add_run(f"pip install rockai=={importlib.metadata.version('rockai')}")
    )
    if "python_requirements" in config_map["build"]:

        if framework is not None:
            if framework == "tensorflow":  # Build TF
                tf_version = get_tensorflow_version(
                    config_map["build"]["python_requirements"]
                )
                remove_some_libs(
                    config_map["build"]["python_requirements"], "tensorflow-metal"
                )
                remove_some_libs(
                    config_map["build"]["python_requirements"], "tensorflow-macos"
                )
                docker_list.append(
                    copy_files(
                        "{}".format(config_map["build"]["python_requirements"]), "/src"
                    )
                )

                docker_list.append(
                    add_run(
                        "pip install -r {} {}".format(
                            "requirements.txt",
                            "-i https://pypi.tuna.tsinghua.edu.cn/simple --extra-index-url https://pypi.org/simple/",
                        )
                    )
                )
                docker_list.append(
                    add_run(
                        "pip install tensorflow=={} -i https://pypi.tuna.tsinghua.edu.cn/simple".format(
                            tf_version
                        )
                    )
                )

            else:  # Build Torch
                docker_list.append(
                    copy_files(
                        "{}".format(config_map["build"]["python_requirements"]), "/src"
                    )
                )
                docker_list.append(
                    add_run(
                        "pip install -r {} {}".format(
                            "requirements.txt",
                            "-i https://pypi.tuna.tsinghua.edu.cn/simple --extra-index-url https://download.pytorch.org/whl/cpu",
                        )
                    )
                )

    else:
        logging.info("No python requirements.txt file found in rock.yaml")

    docker_list.append(add_expose(port))
    if "system_packages" in config_map["build"]:
        for package in config_map["build"]["system_packages"]:
            docker_list.append(add_run("apt install -y {}".format(package)))
    docker_list.append(
        add_labels("run.cog.openapi_schema", run_command_and_get_output())
    )
    docker_list.append(add_cmd("rockai start --port {}".format(port)))
    save_docker_file(docker_list)
    subprocess.run(
        [
            "docker",
            "build",
            "--platform",
            platform,
            "-t",
            tag,
            "-f",
            Path.cwd() / ".rock_temp/Dockerfile",
            Path.cwd(),
        ]
    )


def tf_compat_matrix():
    json_data = [
        {
            "tf_version": "tensorflow-2.16.1",
            "python": "3.9-3.11",
            "cuDNN": "8.9",
            "CUDA": "12.3",
        },
        {
            "tf_version": "tensorflow-2.15.0",
            "python": "3.9-3.11",
            "cuDNN": "8.9",
            "CUDA": "12.2",
        },
        {
            "tf_version": "tensorflow-2.14.0",
            "python": "3.9-3.11",
            "cuDNN": "8.7",
            "CUDA": "11.8",
        },
        {
            "tf_version": "tensorflow-2.13.0",
            "python": "3.8-3.11",
            "cuDNN": "8.6",
            "CUDA": "11.8",
        },
        {
            "tf_version": "tensorflow-2.12.0",
            "python": "3.8-3.11",
            "cuDNN": "8.6",
            "CUDA": "11.8",
        },
        {
            "tf_version": "tensorflow-2.11.0",
            "python": "3.7-3.10",
            "cuDNN": "8.1",
            "CUDA": "11.2",
        },
        {
            "tf_version": "tensorflow-2.10.0",
            "python": "3.7-3.10",
            "cuDNN": "8.1",
            "CUDA": "11.2",
        },
        {
            "tf_version": "tensorflow-2.9.0",
            "python": "3.7-3.10",
            "cuDNN": "8.1",
            "CUDA": "11.2",
        },
        {
            "tf_version": "tensorflow-2.8.0",
            "python": "3.7-3.10",
            "cuDNN": "8.1",
            "CUDA": "11.2",
        },
        {
            "tf_version": "tensorflow-2.7.0",
            "python": "3.7-3.9",
            "cuDNN": "8.1",
            "CUDA": "11.2",
        },
        {
            "tf_version": "tensorflow-2.6.0",
            "python": "3.6-3.9",
            "cuDNN": "8.1",
            "CUDA": "11.2",
        },
        {
            "tf_version": "tensorflow-2.5.0",
            "python": "3.6-3.9",
            "cuDNN": "8.1",
            "CUDA": "11.2",
        },
        {
            "tf_version": "tensorflow-2.4.0",
            "python": "3.6-3.8",
            "cuDNN": "8.0",
            "CUDA": "11.0",
        },
        {
            "tf_version": "tensorflow-2.3.0",
            "python": "3.5-3.8",
            "cuDNN": "7.6",
            "CUDA": "10.1",
        },
        {
            "tf_version": "tensorflow-2.2.0",
            "python": "3.5-3.8",
            "cuDNN": "7.6",
            "CUDA": "10.1",
        },
    ]
    return json_data


def find_correct_image_by_torch_gpu_only(torch_version):
    if torch_version.startswith("1.") and "+" in torch_version:
        parts = torch_version.split("+")
        torch_version = parts[0]

    for each_version in torch_version_list:
        if torch_version == each_version["version"]:
            return each_version["image"], each_version["install"]

    raise Exception(
        "Rock can't find a suppported Cuda or cuDNN version for torch version: {}".format(
            torch_version
        )
    )


def parse_data(result):
    r_list = result["results"]
    result = []
    for item in r_list:
        if (
            "ubuntu" in item["name"]
            and "devel" in item["name"]
            and "cudnn" in item["name"]
        ):
            result.append(item["name"])
    return result


def get_image_tag_from_docker():

    result = []
    page = 1
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(
            description="Downloading image list...(should take around 10-15 seconds)",
            total=None,
        )
        while True:
            url = "https://hub.docker.com/v2/namespaces/nvidia/repositories/cuda/tags?page={}&page_size=100".format(
                page
            )
            response = requests.request("GET", url)

            if response.status_code == 200:
                result += parse_data(response.json())
            elif response.status_code == 404:
                break
            else:
                raise Exception()
            page += 1
        with open("nvidia_docker_cuda_image.json", "w") as file:
            json.dump(result, file)
        return result


def process_requirements(filename):
    with open(filename, "r") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            line_spl = line.split("==")
            if "tensorflow" == line_spl[0]:
                return "tensorflow", line_spl[1]
            if "torch" == line_spl[0]:
                return "torch", line_spl[1]
    return None, None


def build_final_image(config_map, port=8000):

    if "gpu" in config_map["build"] and config_map["build"]["gpu"] is True:
        if "python_requirements" in config_map["build"]:

            # Build GPU image
            framework, version = process_requirements(
                Path.cwd() / config_map["build"]["python_requirements"]
            )
            if framework == "tensorflow":
                print("Building an TensorFlow image")
                image_tag = "nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04"
                build_docker_image(
                    image_tag,
                    config_map,
                    config_map["image"],
                    port=port,
                    install_cmd=None,
                    is_tensorflow=True,
                )
            elif framework == "torch":
                print("Building an PyTorch image {}".format(version))
                image_tag, install_cmd = find_correct_image_by_torch_gpu_only(version)
                build_docker_image(
                    image_tag,
                    config_map,
                    config_map["image"],
                    port=port,
                    install_cmd=install_cmd,
                    is_tensorflow=False,
                )
        else:
            image_tag = "nvidia/cuda:12.5.0-devel-ubuntu22.04"
            build_docker_image(
                image_tag,
                config_map,
                config_map["image"],
                port=port,
                install_cmd=None,
                is_tensorflow=False,
            )
    else:
        py_version = config_map["build"]["python_version"]
        # build CPU image
        if "python_requirements" in config_map["build"]:
            framework, version = process_requirements(
                Path.cwd() / config_map["build"]["python_requirements"]
            )

            py_version = config_map["build"]["python_version"]
            if framework == "tensorflow":
                build_cpu_image(
                    "python:{}".format(py_version),
                    config_map,
                    config_map["image"],
                    port=port,
                    framework="tensorflow",
                )
            elif framework == "torch":
                build_cpu_image(
                    "python:{}".format(py_version),
                    config_map,
                    config_map["image"],
                    port=port,
                    framework="torch",
                )
            else:
                build_cpu_image(
                    "python:{}".format(py_version),
                    config_map,
                    config_map["image"],
                    port=port,
                    framework=None,
                )
        else:
            build_cpu_image(
                "python:{}".format(py_version),
                config_map,
                config_map["image"],
                port=port,
                framework=None,
            )


def add_base(base):
    return "FROM {}\n".format(base)


def add_cmd(cmd_list):
    return "CMD {}\n".format(cmd_list)


def add_expose(port):
    return "EXPOSE {}\n".format(port)


def add_work_dir(dir):
    return "WORKDIR {}\n".format(dir)


def add_run(cmd):
    return "RUN {}\n".format(cmd)


def copy_files(src, dest):
    return "COPY {} {}\n".format(src, dest)


def add_env(env):
    return "ENV {}\n".format(env)


def add_labels(key, value):
    return "LABEL {}={}\n".format(key, value)


def save_docker_file(cmd_list):
    result = "".join(cmd_list)
    # Define the directory path
    directory_path = Path(str(Path.cwd() / ".rock_temp"))

    # Check if the directory exists
    if not directory_path.exists():
        # If it does not exist, create the directory
        directory_path.mkdir(parents=True, exist_ok=True)
        print(f"Directory created: {directory_path}")
    else:
        print(f"Directory already exists: {directory_path}")
    try:
        suffix = uuid.uuid4().hex
        with open(Path.cwd() / ".rock_temp/Dockerfile".format(suffix), "w") as file:
            file.write(result)
    except Exception as e:
        print("An error occurred while writing to the file. Error: ", str(e))
