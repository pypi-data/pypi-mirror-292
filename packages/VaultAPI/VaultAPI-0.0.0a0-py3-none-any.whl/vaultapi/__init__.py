import sys

import click
from cryptography.fernet import Fernet

from vaultapi.main import start  # noqa: F401

version = "0.0.0-a"


@click.command()
@click.argument("run", required=False)
@click.argument("start", required=False)
@click.argument("keygen", required=False)
@click.option("--version", "-V", is_flag=True, help="Prints the version.")
@click.option("--help", "-H", is_flag=True, help="Prints the help section.")
@click.option(
    "--env",
    "-E",
    type=click.Path(exists=True),
    help="Environment configuration filepath.",
)
def commandline(*args, **kwargs) -> None:
    """Starter function to invoke vaultapi via CLI commands.

    **Flags**
        - ``--version | -V``: Prints the version.
        - ``--help | -H``: Prints the help section.
        - ``--env | -E``: Environment configuration filepath.

    **Commands**
        ``encryptor | decryptor``: Initiates the API server.
    """
    assert sys.argv[0].lower().endswith("vaultapi"), "Invalid commandline trigger!!"
    options = {
        "--version | -V": "Prints the version.",
        "--help | -H": "Prints the help section.",
        "--env | -E": "Environment configuration filepath.",
        "start | run": "Initiates the API server.",
    }
    # weird way to increase spacing to keep all values monotonic
    _longest_key = len(max(options.keys()))
    _pretext = "\n\t* "
    choices = _pretext + _pretext.join(
        f"{k} {'·' * (_longest_key - len(k) + 8)}→ {v}".expandtabs()
        for k, v in options.items()
    )
    if kwargs.get("version"):
        click.echo(f"vaultapi {version}")
        sys.exit(0)
    if kwargs.get("help"):
        click.echo(
            f"\nUsage: vaultapi [arbitrary-command]\nOptions (and corresponding behavior):{choices}"
        )
        sys.exit(0)
    trigger = kwargs.get("start") or kwargs.get("run") or kwargs.get("keygen") or ""
    if trigger and trigger.lower() in ("start", "run"):
        # Click doesn't support assigning defaults like traditional dictionaries, so kwargs.get("max", 100) won't work
        start(env_file=kwargs.get("env"))
        sys.exit(0)
    elif trigger.lower() == "keygen":
        key = Fernet.generate_key()
        click.secho(
            f"\nStore this as 'secret' or pass it as kwargs\n\n{key.decode()}\n"
        )
        sys.exit(0)
    else:
        click.secho(f"\n{kwargs}\nNo command provided", fg="red")
    click.echo(
        f"Usage: vaultapi [arbitrary-command]\nOptions (and corresponding behavior):{choices}"
    )
    sys.exit(1)
