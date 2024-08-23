# Copyright ZettaBlock Labs 2024
import configparser
import os
import requests
import typer
from zetta._utils.async_utils import synchronizer

model_cli = typer.Typer(
    name="model",
    help="Manage your models in Zetta AI Network.",
    no_args_is_help=True,
)

SERVICE_CREATE_MODEL_URL = "https://neo-dev.prod.zettablock.com/v1/api/asset"
SERVICE_GITEA_URL = "https://gitea.stag-vxzy.zettablock.com"

@model_cli.command(name="create", help="create a new model repo.")
@synchronizer.create_blocking
async def create(model_name: str = typer.Option(..., help="Name of the model"),
                    description: str = typer.Option("", help="Description of the model"),
                    license_type: str = typer.Option("MIT", help="License type of the model"),
                    modality_type: str = typer.Option("Text-to-Text", help="Modality of the model. E.g Text-to-Text, Text-to-Image etc"),
                    private: bool = typer.Option(False, help="Is the model private or not")):

    try:
        zetta_root = os.path.expanduser("~")
        secrets_path = os.path.join(zetta_root, ".zetta/secrets")
        config = configparser.ConfigParser()
        config.read(secrets_path)
        token = config.get('default', 'token', fallback=None)
    except FileNotFoundError:
        print(f"File not found: {secrets_path}")
    except IOError:
        print(f"An error occurred while reading the file: {secrets_path}")

    headers = {
        "Authorization": token
    }

    json_data = {
        "type": "Model",
        "name": model_name,
        "license": license_type,
        "description": description,
        "private": private,
        "modality": modality_type
    }

    response = requests.post(SERVICE_CREATE_MODEL_URL, headers=headers, json=json_data)
    if response.status_code == 200:
        print(f'Successfully created model {model_name}')
    else:
        response.raise_for_status()


@model_cli.command(name="delete", help="delete a model repo")
@synchronizer.create_blocking
async def delete(json: bool = False):
    pass


@model_cli.command(name="ownership", help="list model ownership.")
@synchronizer.create_blocking
async def ownership(json: bool = False):
    pass


@model_cli.command(
    name="lineage", help="list the lineage (with rewards info) for the model."
)
@synchronizer.create_blocking
async def lineage(json: bool = False):
    pass


@model_cli.command(name="logs", help="list the access logs for the model.")
@synchronizer.create_blocking
async def logs(json: bool = False):
    pass


@model_cli.command(name="history", help="list the git history for the model.")
@synchronizer.create_blocking
async def history(model_name: str = typer.Option(..., help="Name of the model"),
                    num_commits: int = typer.Option(10, help="Number of commits to display")):

    try:
        zetta_root = os.path.expanduser("~")
        profile_path = os.path.join(zetta_root, ".zetta/profile")
        config = configparser.ConfigParser()
        config.read(profile_path)
        user = config.get('default', 'user_name', fallback=None)
    except FileNotFoundError:
        print(f"File not found: {profile_path}")
    except IOError:
        print(f"An error occurred while reading the file: {profile_path}")

    GITEA_HISTORY_URL = f"{SERVICE_GITEA_URL}/api/v1/repos/{user}/{model_name}/commits"
    params = {
        "stat": "false",
        "verification": "false",
        "files": "false"
    }
    response = requests.get(GITEA_HISTORY_URL, params=params)

    if response.status_code == 200:
        commit_histories = response.json()[:num_commits]
        for commit in commit_histories:
            print(f"{commit['sha'][:7]} {commit['commit']['message'].strip()}")
    else:
        response.raise_for_status()


@model_cli.command(name="register", help="register model.")
@synchronizer.create_blocking
async def register(json: bool = False):
    pass
