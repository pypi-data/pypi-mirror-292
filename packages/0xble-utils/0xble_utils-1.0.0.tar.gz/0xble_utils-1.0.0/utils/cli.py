import os
import subprocess
from termcolor import colored
from rich.console import Console
from rich.pretty import pprint as _pprint
from rich.status import Status
from utils.strings import truncate
from pyfzf import FzfPrompt
import click
import re

console = Console()


def spinner(
    status,
    *,
    progress: float = None,
    spinner: str = "dots",
    spinner_style: str = "status.spinner",
    speed: float = 1.0,
    refresh_per_second: float = 12.5,
):
    status = f"[dim]{status}[/]"

    if progress:
        progress = round(progress, 2) * 100
        progress = int(progress)
        status = f"[not dim]{progress}%[/] {status}"

    # Below copied from rich.status
    return Status(
        status,
        console=console,
        spinner=spinner,
        spinner_style=spinner_style,
        speed=speed,
        refresh_per_second=refresh_per_second,
    )


def print(text="\n", **kwargs):
    if "highlight" not in kwargs:
        kwargs["highlight"] = False

    console.print(text, **kwargs)


def pprint(text, **kwargs):
    _pprint(text, **kwargs)


def prompt(
    text: str = "Enter input",
    type=str,
    default: str = None,
    required=False,
    initial_text: str = None,
    exit_on_interrupt=True,
):
    text.strip()

    # Escape any double quotes and backticks
    text = text.replace('"', '\\"')
    text = text.replace("`", "\\`")

    if initial_text:
        initial_text = initial_text.replace('"', '\\"')
        initial_text = initial_text.replace("`", "\\`")

    if default and isinstance(default, str):
        default = default.replace('"', '\\"')
        default = default.replace("`", "\\`")

    command = f'prompt "{text}"'

    if default is not None:
        command += f' --default "{default}"'

    if initial_text:
        command += f' --initial-text "{initial_text}"'

    response = None
    while not response:
        response = run(command, exit_on_interrupt=exit_on_interrupt)

        if response is None:
            return None

        if not required:
            break

    if response:
        return type(response)
    else:
        if type == str:
            return ""
        elif type == int:
            return 0
        elif type == float:
            return 0.0
        elif type == bool:
            return False
        elif type == list:
            return []
        elif type == dict:
            return {}
        else:
            return None


def confirm(text: str, default=True, exit_on_interrupt=True):
    text.strip()

    # Escape any double quotes and backticks
    text = text.replace('"', '\\"')
    text = text.replace("`", "\\`")

    command = f'confirm "{text}"'

    if not default:
        command += " --no"

    res = os.system(command)

    if res == 0:
        return True
    elif res == 2:
        if exit_on_interrupt:
            exit()
        else:
            return None
    else:
        return False


def select(
    choices: list,
    prompt: str = None,
    multi: bool | int = False,
    report=True,
    format_choices=True,
):
    options = "--ansi --no-bold --print-query --cycle --no-sort"

    options += f" --prompt="
    options += '"'
    options += colored("?", "yellow", attrs=["dark"])

    if prompt:
        prompt = prompt.replace('"', '\\"')
        prompt = prompt.strip()

        options += " "
        options += colored(prompt, attrs=["bold"])

    options += colored(" › ", attrs=["dark"])
    options += '"'

    if multi:
        options += " --multi"

        if multi >= 2:
            options += f"={multi}"

        options += f" --bind ctrl-a:select-all,ctrl-d:deselect-all,ctrl-t:toggle-all"

    if format_choices:
        choices = [colored(choice, attrs=["dark"]) for choice in choices]

    try:
        fzf = FzfPrompt()
        response = fzf.prompt(choices, options)
    except KeyboardInterrupt:
        return None

    if response:
        input = response[0]
        response = response[1:]

        if not response:
            response = [input]

        for i, item in enumerate(response):
            # Remove any ANSI escape sequences
            item = re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", item)

            # Remove all text after separator
            item = re.sub(r"\s{4}.*", "", item)

            # Remove any trailing whitespace
            item = item.strip()

            response[i] = item

        if report:
            statement = "[green]✔ [/]"
            statement += f"[bold]{prompt if prompt else 'Selected'}[/]"
            statement += " [dim]·[/dim] "

            if multi:
                limit = 20
                response_str = ", ".join(response[:limit]) + (
                    f", and {len(response) - limit} more..."
                    if len(response) > limit
                    else ""
                )
            else:
                response = response[0]
                response_str = response

            statement += f"[green]{response_str}[/]"

            console.print(statement)

    return response


def edit(text: str = "", prompt: str = None, type=str, report=True):
    try:
        response = click.edit(text, editor='vim "+norm G$" "+startinsert!"')
    except KeyboardInterrupt:
        return None

    if response is not None:
        text = type(response)

        if isinstance(text, str):
            text = text.strip()
    else:
        return text

    if report:
        statement = "[green]✔ [/]"
        statement += f"[bold]{prompt if prompt else 'Edited'}[/]"
        statement += " [dim]·[/dim] "
        statement += f"[green]{truncate(text)}[/]"

        console.print(statement)

    return text


def run(command, exit_on_interrupt=True, report=True, **kwargs):
    try:
        response = (
            subprocess.check_output(command, shell=True, **kwargs)
            .decode("utf-8")
            .strip()
        )

        if "\n" in response:
            response = "\n".join([f"{line.strip()}" for line in response.split("\n")])

        if response and report:
            print(response)
    except subprocess.CalledProcessError or KeyboardInterrupt:
        if exit_on_interrupt:
            exit()
        else:
            return None

    return response


# For testing purposes
if __name__ == "__main__":
    pass
