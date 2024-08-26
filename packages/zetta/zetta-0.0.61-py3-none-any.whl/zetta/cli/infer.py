# Copyright ZettaBlock Labs 2024
import openai
import typer
import requests
import json
from zetta._utils.async_utils import synchronizer

from openai import OpenAI

API_SERVER = "http://ec2-3-222-116-93.compute-1.amazonaws.com:8000"

infer_cli = typer.Typer(
    name="infer",
    help="Send inference requests to Zetta AI network.",
    no_args_is_help=True,
)


@infer_cli.command(
    name="list",
    help="List all the visible inference endpoints for a network.",
)
@synchronizer.create_blocking
async def list(model: str = "all"):
    url = f"{API_SERVER}/infer/list"
    response = requests.get(url, params={"model": model})
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
    else:
        response.raise_for_status()


@infer_cli.command(
    name="status", help="Show the stats information of the inference endpoints."
)
@synchronizer.create_blocking
async def status(endpoint: str = "all"):
    url = f"{API_SERVER}/infer/status"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
    else:
        response.raise_for_status()


@infer_cli.command(name="shell", help="Open a shell to chat with model")
@synchronizer.create_blocking
async def shell(model: str = "", endpoint: str = "any"):
    pass


@infer_cli.command(name="chat", help=" chat with model")
@synchronizer.create_blocking
async def chat(
    model: str = "", msg: str = "", endpoint: str = "any", stream: bool = False
):
    if model == "":
        print(
            "Please specify a model to deploy. a valid model should start with 'model_' and contain repo-name and version, such as model_3VMYpHF2IN7YrnBPj133xBYo@fb-opt-125m@latest"
        )
        return
    if msg == "":
        print("Please input a message to chat.")
        return
    client = OpenAI(
        base_url="http://ec2-3-222-116-93.compute-1.amazonaws.com:8888/v1",
        api_key="token-abc123",
    )
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "you are an english people, always speak in english",
                },
                {
                    "role": "user",
                    "content": msg,
                },
            ],
            stream=stream,
        )
    except openai.APIConnectionError as e:
        print("The server could not be reached")
        print(e.__cause__)  # an underlying Exception, likely raised within httpx.
        return
    except openai.APIStatusError as e:
        print("Another non-200-range status code was received")
        print(e.status_code)
        print(e.response)
        return
    if stream:
        for chunk in completion:
            print(chunk.choices[0].delta.content)
    else:
        res = completion.choices[0].message.content.split("\n")
        print(res[0])


@infer_cli.command(
    name="history",
    help="Check the inference history. ",
)
@synchronizer.create_blocking
async def history(
    model: str = "", endpoint: str = "any", inputs: str = "", delimiter: str = ""
):
    pass
