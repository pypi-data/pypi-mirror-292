import typer
from rockai.server.http import start_server
from rockai.server.utils import is_valid_name
from pathlib import Path
from rockai.parser.config_util import parse_config_file
from typing_extensions import Annotated
from rockai.docker.docker_util import build_final_image
import os
import shutil
import requests
import subprocess
import logging
import sys

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)

app = typer.Typer()

APP_NAME = "rockai"


def download_file(url: str, save_path: str):
    try:
        # Send a GET request to the URL
        response = requests.get(url, stream=True)
        # Check if the request was successful
        response.raise_for_status()

        # Open the file in binary write mode and write the content
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"File downloaded successfully and saved to {save_path}")

    except requests.exceptions.RequestException as e:
        print(f"Failed to download the file: {str(e)}")


@app.command()
def init():
    download_file(
        "https://rockai-web-resouce-bucket.s3.ap-northeast-1.amazonaws.com/rock.yaml",
        Path.cwd() / "rock.yaml",
    )
    download_file(
        "https://rockai-web-resouce-bucket.s3.ap-northeast-1.amazonaws.com/predictor.py",
        Path.cwd() / "predictor.py",
    )
    download_file(
        "https://rockai-web-resouce-bucket.s3.ap-northeast-1.amazonaws.com/dockerignore",
        Path.cwd() / ".dockerignore",
    )
    print("Init success")


@app.command(name="build")
def build(port: Annotated[int, typer.Option(help="Port of the API server")] = 8000):
    """
    Build the image
    """
    if not os.path.exists(Path.cwd() / ".rock_temp"):
        os.makedirs(Path.cwd() / ".rock_temp")
        print(f"Folder '{Path.cwd() / '.rock_temp'}' created.")
    else:
        print(f"Folder '{Path.cwd() / '.rock_temp'}' already exists.")

    config_path: Path = Path.cwd() / "rock.yaml"
    if not config_path.is_file():
        raise Exception("rock.yaml config file doesn't exist in the current directory")
    else:
        print("rock.yaml config file exist")

    config_map = parse_config_file(config_path)
    logger.debug(config_map)
    if not is_valid_name(config_map["image"].split("/")[-1]):
        print(
            "Invalid model name, please rename your model accordingly to the following rules"
        )
        print(
            "1. contain no more than 140 characters\n2. contain only lowercase alphanumeric characters,and '-'\n3. start with an alphanumeric character\n4. end with an alphanumeric character"
        )
        raise Exception(
            "Invalid model name: {}".format(config_map["image"].split("/")[-1])
        )
    try:
        # Copy the content of file_1 to file_2
        if "python_requirements" in config_map["build"]:
            shutil.copyfile(
                Path.cwd() / config_map["build"]["python_requirements"],
                Path.cwd() / ".rock_temp" / "requirements.txt",
            )
            config_map["build"]["python_requirements"] = ".rock_temp/requirements.txt"

    except FileNotFoundError as e:
        raise FileNotFoundError("Source file not found") from e
    except Exception as e:
        raise Exception(f"An error occurred: {e}") from e
    if "build" in config_map and "python_version" not in config_map["build"]:
        config_map["build"][
            "python_version"
        ] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    build_final_image(config_map=config_map, port=port)


@app.command()
def start(
    auth: Annotated[
        str, typer.Option(help="Bearer auth token of the API server")
    ] = None,
    port: Annotated[int, typer.Option(help="Port of the API server")] = 8000,
):
    """
    start local development server
    """
    start_server(port, auth)


@app.command("push")
def push_model():
    """
    Push the model to the RockAI platform
    """
    build()
    config_path: Path = Path.cwd() / "rock.yaml"
    if not config_path.is_file():
        raise Exception("rock.yaml config file doesn't exist in the current directory")
    else:
        print("rock.yaml config file exist")

    config_map = parse_config_file(config_path)
    subprocess.run(["docker", "image", "push", "{}".format(config_map["image"])])


@app.command(name="login")
def login_to_docker(
    api_token: Annotated[str, typer.Argument(help="Your API token")],
    debug: Annotated[bool, typer.Option(help="enable debug mode")] = False,
):
    url = "https://api.rockai.online/v1/user/docker_token"
    if debug:
        print("Debug mode is enabled")
        url = "https://api-dev.rockai.online:9090/v1/user/docker_token"
    headers = {"Authorization": "Bearer {}".format(api_token)}

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    subprocess.run(
        [
            "docker",
            "login",
            "r.18h.online",
            "-u",
            response.json()["data"]["docker_robot_account"],
            "-p",
            response.json()["data"]["docker_token"],
        ]
    )
