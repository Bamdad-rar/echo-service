import code

import typer

from configuration.databases import (
    init_mongo,
    disconnect_mongo,
    init_redis,
    disconnect_redis
)

try:
    from IPython import embed

    IPYTHON_AVAILABLE = True
except ImportError:
    IPYTHON_AVAILABLE = False

cli = typer.Typer()


@cli.command()
def shell():

    init_mongo()
    init_redis()
    typer.echo("MongoDB and Redis initialized.\n")

    # Prepare local context for the shell
    # You can import models, app, or anything else here:
    from scheduler.domain.schedule import OneOff, Recurring
    from scheduler.domain.task import Task
    # ... etc.

    local_context = {
        "Task": Task,
        "OneOff": OneOff,
        "Recurring": Recurring,
        # etc...
    }

    banner = (
        r"""
         _____     _             ____                  _          
        | ____|___| |__   ___   / ___|  ___ _ ____   _(_) ___ ___ 
        |  _| / __| '_ \ / _ \  \___ \ / _ \ '__\ \ / / |/ __/ _ \
        | |__| (__| | | | (_) |  ___) |  __/ |   \ V /| | (_|  __/
        |_____\___|_| |_|\___/  |____/ \___|_|    \_/ |_|\___\___|

        """
        "Welcome to the Echo Service shell!\n"
        "Type commands here. Press Ctrl+D to exit.\n"
    )

    try:
        if IPYTHON_AVAILABLE:
            typer.echo("Launching IPython...\n")
            embed(user_ns=local_context, banner1=banner)
        else:
            typer.echo("IPython not installed; falling back to basic Python shell...\n")
            code.interact(banner, local=local_context)
    finally:
        typer.echo("\nClosing MongoDB and Redis connections.")
        disconnect_mongo()
        disconnect_redis()
        typer.echo("\nBye!")


if __name__ == "__main__":
    cli()
