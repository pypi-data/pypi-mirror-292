import sys

import typer
from loguru import logger

from trainwave_cli.cli import auth, jobs

app = typer.Typer()
app.add_typer(jobs.app, name="jobs")
app.add_typer(auth.app, name="auth")


def entrypoint() -> None:
    logger.remove()
    logger.add(sys.stdout, colorize=True, format="<level>{message}</level>")
    app()


if __name__ == "__main__":
    app()
