import json
import os
import sys
import traceback
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Optional
from urllib.parse import urlparse

import pytimeparse
import typer
import websockets
from loguru import logger
from tabulate import tabulate
from typer_config.decorators import use_toml_config

from trainwave_cli.api import Api
from trainwave_cli.config.config import config
from trainwave_cli.io import create_tarball
from trainwave_cli.utils import async_command, ensure_api_key, truncate_string

app = typer.Typer()


@app.command()
@async_command
@use_toml_config(default_value="trainwave.toml")
@ensure_api_key
async def launch(  # noqa
    # Basic job parameters
    name: Annotated[str, typer.Option()],
    project: Annotated[str, typer.Option()],
    setup_command: Annotated[str, typer.Option()],
    run_command: Annotated[str, typer.Option()],
    # Optional params
    expires: Annotated[str, typer.Option()] = "",
    env_vars={},  # dict[str, str]  not supported by typer yet
    exclude_gitignore: Annotated[bool, typer.Option()] = True,
    exclude_regex: Optional[Annotated[str, typer.Option()]] = None,
    # Harware parameters
    image: Annotated[str, typer.Option()] = "",
    hdd_size_mb: Annotated[int, typer.Option()] = 20,
    memory_mb: Annotated[int, typer.Option()] = 0,
    cpus: Annotated[int, typer.Option()] = 0,
    gpus: Annotated[int, typer.Option()] = 0,
    gpu_type: Annotated[str, typer.Option()] = "",
) -> None:
    api_client = Api(config.api_key, config.endpoint, project)
    # Interpolate environe variables
    env_vars = eval(env_vars)
    for k, v in env_vars.items():
        if v.startswith("${"):
            interpolated = os.getenv(v[2:-1])
            if interpolated is None:
                logger.warning(f"Environment variable {v} not found")
            else:
                env_vars[k] = interpolated

    conf = {
        "name": name,
        "image": image,
        "setup_command": setup_command,
        "run_command": run_command,
        "hdd_size_mb": hdd_size_mb,
        "memory_mb": memory_mb,
        "cpus": cpus,
        "gpus": gpus,
        "gpu_type": gpu_type,
        "env_vars": env_vars,
    }

    if expires != "":
        expires_time = pytimeparse.parse(expires)
        if expires_time is None:
            logger.warning(f"Expires cannot be used, defaulting to nothing")
        else:
            expires_at = int(datetime.now(timezone.utc).timestamp()) + int(expires_time)
            conf["expires_at"] = expires_at

    def render(k, v) -> str:
        match k:
            case "env_vars":
                return ",".join(v.keys())
            case "expires_at":
                return datetime.fromtimestamp(v).strftime("%Y-%m-%d %H:%M:%S")
            case _:
                return truncate_string(str(conf[k]), 50)

    tab_keys = list(conf.keys())
    tab_values = {
        "name": tab_keys,
        "value": [render(k, conf[k]) for k in tab_keys],
    }
    logger.info(tabulate(tab_values, headers="keys"))
    logger.info("\n")

    tarball = None
    try:
        job = await api_client.create_job(conf)
        tarball = create_tarball(Path().cwd(), exclude_gitignore, exclude_regex)
        await api_client.upload_code(Path(tarball.name), job.upload_url)
        await api_client.code_submission(job)

        co = asdict(job.cloud_offer)
        tab_keys = list(co.keys())
        tab_values = {
            "name": tab_keys,
            "value": [truncate_string(str(co[k]), 50) for k in tab_keys],
        }
        logger.info("\nMatched machine\n" + tabulate(tab_values, headers="keys") + "\n")
        logger.info(f"Job created: {job.rid} ({job.id})")
    except Exception as e:
        traceback.print_exc()
        logger.error(f"An error occurred: {e}")
    finally:
        if tarball:
            tarball.close()


@app.command()
@async_command
@use_toml_config(default_value="trainwave.toml")
@ensure_api_key
async def status(
    project: Annotated[str, typer.Option()],
    job_id: str,
) -> None:
    api_client = Api(config.api_key, config.endpoint, project)
    logger.info(await api_client.job_status(job_id))


@app.command()
@async_command
@use_toml_config(default_value="trainwave.toml")
@ensure_api_key
async def cancel(
    project: Annotated[str, typer.Option()],
    job_id: str,
):
    api_client = Api(config.api_key, config.endpoint, project)
    await api_client.cancel_job(job_id)
    logger.info(f"Cancelled job: {job_id}")


@app.command()
@async_command
@ensure_api_key
async def logs(
    job_id: str,
) -> None:
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{extra[log_time]}</green> | <white>{message}</white>",
        colorize=True,
        serialize=False,
        level="DEBUG",
        enqueue=True,
        catch=True,
    )
    parsed = urlparse(config.endpoint)
    scheme = "wss" if parsed.scheme == "https" else "ws"
    port = ""
    if parsed.port:
        port = f":{parsed.port}"
    uri = f"{scheme}://{parsed.hostname}{port}/ws/logs/{job_id}/?api_key={config.api_key}"

    def format_ts(ts: str | None) -> str:
        if ts is None:
            return ""
        timestamp = int(ts) / 1e9
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f")

    ssl_context = None
    if "trainwave.dev" in uri:
        import ssl

        ssl_context = ssl.SSLContext()
        ssl_context.verify_mode = ssl.CERT_NONE
    opts = {"ssl": ssl_context} if ssl_context else {}

    async with websockets.connect(uri, **opts) as websocket:
        try:
            while response := await websocket.recv():
                data = json.loads(response)
                logger.info(data["message"], log_time=format_ts(data.get("ts")))
        except websockets.exceptions.ConnectionClosedOK:
            pass
