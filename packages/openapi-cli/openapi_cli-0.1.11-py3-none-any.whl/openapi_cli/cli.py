import copy
import functools
import importlib.util
import inspect
import json
import os
import pkgutil
import re
import sys
import typing
from enum import Enum
from functools import cached_property
from http import HTTPStatus
from json import JSONDecodeError, JSONEncoder
from pathlib import Path
from types import ModuleType
from typing import Any, ForwardRef, ParamSpec, Self, TypeVar
from textwrap import dedent
from plumbum.machines import local

import attrs
import click
from attr import AttrsInstance
from click import Argument, Context, Group, UsageError, pass_context
from plumbum import ProcessExecutionError
from pydantic import BaseModel, Field, HttpUrl
from plumbum.colors import red, green, blue, yellow, white
from plumbum.cmd import grep, head, echo, cp, mv


T = TypeVar("T")

CONFIG_FOLDER = Path(".openapi_cli").absolute()
CONFIG_FILE = CONFIG_FOLDER.joinpath("config.json")

F = typing.Callable[..., Any]
R = TypeVar("R")
P = ParamSpec("P")

OK = "✅ " | green
BAD = "❌ " | red
INFO = "ℹ️ " | blue
WARN = "⚠️ " | yellow

MAGNIFIER = "🔍 " | blue
FILE = "📄 " | blue
BACKUP = "🗄️ " | blue
WRITE = "📝 " | blue
BULLET = "\u2022 "

TYPE_MAP = {
    str: click.STRING,
    int: click.INT,
    float: click.FLOAT,
    bool: click.BOOL,
}


def echo(text: str, prefix: str = ""):
    """Print text with a prefix."""

    click.echo(f"{f"{prefix} " if prefix else ""}{text}")


class CliConfig(BaseModel):
    """CLI configuration file model."""

    client_module_name: Path | str | None = Field(
        None, description="Python module containing the " "client"
    )
    base_url: HttpUrl | None = Field(None, description="Base URL of the API")
    token: str | None = Field(None, description="API token")
    editor: str | None = Field(None, description="Text editor to use for editing JSON")

    @classmethod
    def load(cls) -> Self:
        if not CONFIG_FILE.exists():
            return cls()

        with open(CONFIG_FILE, "r") as f:
            return cls.model_validate_json(f.read())

    def save(self):
        """Save the configuration to disk."""

        CONFIG_FOLDER.mkdir(exist_ok=True, parents=True)
        CONFIG_FILE.write_text(
            self.model_dump_json(
                by_alias=True,
                exclude_none=True,
                exclude={"state"},
            )
        )

    @cached_property
    def client_models(self) -> ModuleType:
        return importlib.import_module(f"{self.client_module_name}.models")

    @cached_property
    def client_types(self) -> ModuleType:
        return importlib.import_module(f"{self.client_module_name}.types")

    @cached_property
    def json_encoder(self) -> type[JSONEncoder]:
        def default(encoder, obj):
            if isinstance(obj, Enum):
                return obj.value
            if isinstance(obj, self.client_types.Unset):
                return None
            return obj

        return type("JSONEncoder", (JSONEncoder,), {"default": default})


@click.group(no_args_is_help=True, invoke_without_command=True)
@pass_context
def cli(ctx: Context):
    ctx.obj = CliConfig.load()

    module_err = f"Use `{ctx.info_name} client install` to set the client module first!" | red

    if ctx.obj.client_module_name is None and ctx.invoked_subcommand != "client":
        raise click.UsageError(module_err)


@cli.group("client")
def client_group():
    """Client configuration commands."""

    pass


@cli.group(
    "action",
    help="List of API actions",
    invoke_without_command=True,
    no_args_is_help=True,
)
@click.pass_obj
def action_group(config: CliConfig):
    pass


def print_result(f: F) -> F:
    """Print the result of the function."""

    def list_items_to_dict(items: list) -> list:
        result = []

        for item in items:
            if hasattr(item, "to_dict"):
                result.append(item.to_dict())
            else:
                result.append(item)

        return result

    @functools.wraps(f)
    @click.pass_obj
    def wrapper(config: CliConfig, *args: P.args, **kwargs: P.kwargs) -> R:
        """Print the result of the function."""

        orig_result = f(*args, **kwargs)
        result = copy.deepcopy(orig_result)
        if result is None:
            return

        if (
            hasattr(result, "status_code")
            and getattr(result, "parsed", None) is None
            and not getattr(result, "content", None)
        ):
            status: HTTPStatus = result.status_code
            result = f"{status.value} {status.name}: {status.description}"

        if getattr(result, "parsed", None) is not None:
            result = result.parsed

        elif getattr(result, "content") is not None:
            try:
                result = json.loads(result.content)
            except json.JSONDecodeError:
                result = f"{orig_result.status_code}: {result.content.decode()}"

        if isinstance(result, list):
            result = list_items_to_dict(result)

        if hasattr(result, "to_dict"):
            result = result.to_dict()

        result = json.dumps(result, indent=2, cls=config.json_encoder)

        click.echo(result)

    return wrapper


def with_client(f, client_cls):
    """Initialize the API client."""

    @functools.wraps(f)
    def wrapper(_: Context, *args, **kwargs):
        try:
            return f(
                *args,
                **kwargs,
                client=get_api_client(client_cls),
            )
        except TypeError as e:
            raise click.UsageError(f"Use `configure` to set the client url and token: {e}")

    return wrapper


def as_json(f: F) -> F:
    """Parse body as json."""

    @click.option("--json-file", type=Path, help="Input JSON file")
    @click.option("--json", "payload", type=str, help="JSON payload")
    @click.option("--edit", is_flag=True, help="Open text in editor")
    @functools.wraps(f)
    @click.pass_context
    def wrapper(
        ctx: Context,
        *args: P.args,
        json_file: Path | None = None,
        payload: str | None = None,
        edit: bool = False,
        **kwargs: P.kwargs,
    ) -> R:

        if not ctx.args and not json_file and not payload and not edit:
            click.echo(ctx.get_help())
            return

        if json_file is not None:
            with open(json_file, "r") as file:
                payload = file.read()

        if edit:
            payload = click.edit(payload, editor=ctx.obj.editor)

        if payload is not None:
            try:
                kwargs["body"] = json.loads(payload)
            except JSONDecodeError as e:
                raise click.UsageError(f"Invalid JSON payload: {e}" | red)
        else:
            raise click.UsageError("JSON payload required" | red)

        return f(*args, **kwargs)

    w = WARN
    b = BULLET | yellow

    wrapper.__doc__ += "\b\n"
    wrapper.__doc__ += inspect.cleandoc(
        f"""
        {w} {"JSON payload required" | green} {w}
        {b} {"to pass a JSON payload use --json flag." | blue}
        {b} {"to pass a JSON file use --json-file flag." | blue}
        {b} {"to edit a JSON payload in a text editor use --edit flag." | blue}
    """
    )

    return wrapper


def add_to_click(config: CliConfig, func: T, value, name) -> T:
    """Add function as command to click."""

    name = name.replace("_", "-")

    value_type = TYPE_MAP.get(value.annotation, click.STRING)
    default_value = (
        value.default if not isinstance(value.default, config.client_types.Unset) else None
    )

    is_list = False
    if isinstance(typing.get_origin(value.annotation), list):
        is_list = True

    if isinstance(typing.get_args(value.annotation), tuple):
        for arg in typing.get_args(value.annotation):
            orig = typing.get_origin(arg)
            if isinstance(orig, type) and issubclass(orig, list):
                is_list = True

    value_default = value.default

    if value_default == inspect.Parameter.empty and not is_list:
        func.__doc__ += f"{name}: {value_type}\n" | green
        func = click.argument(name)(func)
    else:
        func = click.option(
            f"--{name}",
            default=default_value,
            multiple=is_list,
            help=f"{name}" | blue,
            type=(
                click.Choice([e.value for e in value.annotation])
                if isinstance(value.annotation, Enum)
                else None
            ),
        )(func)

    return func


def iter_api(config: CliConfig, module: str, group: Group) -> None:
    """Iterate over all API classes in a module."""

    module = importlib.import_module(module)
    for sub_module in pkgutil.iter_modules(module.__path__):
        sub_module_name = sub_module.name.replace("_", "-")
        if sub_module.ispkg:
            iter_api(
                config,
                f"{module.__name__}.{sub_module.name}",
                group.group(
                    sub_module_name,
                    help=f"Actions tagged with `{sub_module_name}` tag",
                    no_args_is_help=True,
                    invoke_without_command=True,
                )(lambda: None),
            )
        else:
            full_name = f"{module.__name__}.{sub_module.name}"

            func = getattr(importlib.import_module(full_name), "sync_detailed")

            func.__doc__ = inspect.cleandoc(func.__doc__.split("Args:")[0])
            func.__doc__ = f"{func.__doc__}"
            func.__doc__ += "\n\nArguments:\n\n\b\n"

            if inspect.signature(func).parameters.get("client"):
                client_cls = inspect.signature(func).parameters.get("client").annotation
                func = with_client(func, client_cls)

            for name, value in inspect.signature(func).parameters.items():
                if name == "client":
                    continue

                elif name == "body":
                    func = as_json(func)

                else:
                    func = add_to_click(config, func, value, name)

            args_required = False
            if hasattr(func, "__click_params__"):
                args_required = bool([o for o in func.__click_params__ if isinstance(o, Argument)])

            cmd = group.command(sub_module_name, no_args_is_help=args_required)

            cmd(click.pass_context(print_result(func)))


@click.pass_obj
def get_api_client(config: CliConfig, client_cls: type[T] | tuple[type[T]]) -> T:
    """Get an API client instance."""

    if isinstance(client_cls, tuple):
        client_cls = client_cls[0]

    if isinstance(client_cls, type):
        return client_cls(
            base_url=str(config.base_url),
            token=str(config.token),
        )


def validate_client_module(config: CliConfig) -> bool:
    """Validate that the client module exists and has all the necessary submodules."""

    required_submodules = ["api", "models", "client", "errors", "types"]

    for submodule in required_submodules:
        try:
            importlib.import_module(f"{config.client_module_name}.{submodule}")
        except (AttributeError, ModuleNotFoundError) as e:
            raise click.UsageError(str(e) | red) from None

    return True


@client_group.command("api-config", no_args_is_help=True)
@click.option("--base-url", help="Base API URL")
@click.pass_obj
def configure(
    config: CliConfig,
    base_url: HttpUrl | None = None,
) -> None:
    """Configure basic OpenAPI Client options.

    \b
    BASE_URL: Base URL of the API.
    """

    if base_url is not None:
        config.base_url = base_url

    config.save()

    click.echo("Client module configured successfully")


@client_group.command(
    "auth",
    no_args_is_help=True,
)
@click.argument("token", type=str)
@click.pass_obj
def auth(config: CliConfig, token: str) -> None:
    """Authenticate the user with a token.

    \b
    TOKEN: API token.

    """

    config.token = token
    config.save()


GIT_URL_HELP = f"""
    \b
    {"Git URL to the client module" | green}
    {"[add --module if the package is a submodule]" | blue}
"""


@client_group.command("install", no_args_is_help=True)
@click.option("--module", type=str, help="Module name to install" | green)
@click.option("--git", help=GIT_URL_HELP)
@click.pass_obj
def install_client(
    config: CliConfig,
    module: str | None,
    git: str | None,
):
    """Install a client module from git URL or module name.

    \b
    You can install the client module from a git URL or a module name.
    If you provide a module name, the module will be installed from PyPI.
    If you provide a git URL, the module will be installed from the git repository.
    If the client module is a submodule, provide the module name with --module.
    """

    try:
        from plumbum.cmd import poetry

        pip = poetry["run", "pip"]
    except ImportError:
        from plumbum.cmd import pip

    install_cmd = pip["install"]

    if module is not None and git is None:
        try:
            importlib.import_module(module)
        except ModuleNotFoundError:
            install_cmd = install_cmd[module]
        else:
            config.client_module_name = module
            install_cmd = None

    elif git is not None:
        if sys.prefix == sys.base_prefix:
            if not click.confirmation_option(
                prompt="Install in system Python?" | warn,
                default=False,
            ):
                return click.echo("Aborted")

        install_cmd = install_cmd[f"git+{git}"]
    else:
        raise click.UsageError("Provide either a module name or git URL" | red)

    if install_cmd is not None:
        try:
            result = install_cmd()
        except ProcessExecutionError as e:
            click.echo(e, color=True)
            return
        else:
            result = (grep["(from"] << result)()
            result = (head["-n", 1] << result)()

            if module is not None:
                config.client_module_name = module
            else:
                config.client_module_name = re.findall(r"\(from (?P<module>.*)==", result)[
                    0
                ].replace("-", "_")

    try:
        validate_client_module(config)
    except UsageError as e:
        if module is None:
            message = f"""
                {"Failed to find the client module name: {e.message}\n" | red}
                {"If the client package is under different name specify it with --module" | yellow}
            """

            click.echo(message, color=True)
            return
        else:
            raise e

    click.echo("Client module installed successfully" | green, color=True)
    config.save()


@cli.group("completions")
def completions_group():
    """Terminal completion commands."""


def get_shell_info(script_name, shell="autodetect") -> tuple[Path, str, Path, str]:
    """Detect the current shell and source file and competion command."""

    supported_shells = ["bash", "zsh", "fish"]

    script_name = script_name.replace("-", "_")
    command_name = script_name.upper()

    if shell == "autodetect":
        echo("Detecting shell..." | blue, MAGNIFIER)

        shell = os.environ.get("SHELL", "").split("/")[-1]

        echo(f"Detected shell: {shell}" | blue, OK if shell in supported_shells else BAD)

    rc_path = None
    rc_command = None

    if shell == "bash":
        rc_path = Path("~/.bashrc")
        sript_rc_command = f'eval "$(_{command_name}_COMPLETE=zsh_source {script_name})"'
    elif shell == "zsh":
        rc_path = Path("~/.zshrc")
        script_rc_command = f'eval "$(_{command_name}_COMPLETE=zsh_source {script_name})"'
    elif shell == "fish":
        srcipt_rc_path = Path(f"~/.config/fish/completions/{script_name}.fish")
        script_rc_command = f"_{command_name}_COMPLETE=fish_source {script_name} | source"
    else:
        raise click.UsageError(f"Unsupported shell {shell}" | red)

    script_rc_command = f"""
        # {script_name} completion
        if command -v {script_name} &>/dev/null; then {script_rc_command}; fi
    """

    if shell in ["bash", "zsh"]:
        script_rc_path = Path(f"{rc_path}_{script_name}_completions")
        rc_command = f"source {script_rc_path}"

    return rc_path, rc_command, script_rc_path, script_rc_command


@completions_group.command("enable")
@click.argument(
    "shell",
    type=click.Choice(["bash", "zsh", "fish", "autodetect"]),
    default="autodetect",
)
@click.pass_context
def enable_completions(ctx: Context, shell: str):
    """Generate bash completions for the CLI."""

    script_name = ctx.parent.parent.info_name

    rc_path, rc_command, script_rc_path, script_rc_command = get_shell_info(
        script_name, shell=shell
    )

    echo(f"Creating completions script for `{script_name}`..." | blue, WRITE)

    with open(script_rc_path.expanduser(), "w") as f:
        f.write(script_rc_command)

    echo(f"Completions script created for `{script_name}` at {script_rc_path}" | green, FILE)

    if rc_path is not None and rc_command is not None:
        with open(rc_path.expanduser(), "r") as f:
            rc_text = f.read()

            if rc_command in rc_text:
                echo(f"Completions already enabled for `{script_name}` in {rc_path}" | yellow, OK)
            else:
                with open(rc_path.expanduser(), "a") as f:
                    f.write(f"\n{rc_command}\n")

                echo(f"Completions enabled for {script_name}" | green, OK)

    help = "To enable competions use `{cmd}`" | blue
    cmd = f"source {rc_path}" | white

    echo(f"{help.format(cmd=cmd)}", INFO)


@completions_group.command("disable")
@click.argument(
    "shell",
    type=click.Choice(["bash", "zsh", "fish", "autodetect"]),
    default="autodetect",
)
@click.pass_context
def completions_disable(ctx: Context, shell: str):
    """Disable completions for the CLI."""

    rc_path, rc_command, script_rc_path, script_command = get_shell_info(
        ctx.parent.parent.info_name, shell=shell
    )

    if script_rc_path.exists():
        echo("Removing completions script..." | blue, FILE)
        mv[script_rc_path.expanduser(), f"{script_rc_path.expanduser()}.backup"]()
        echo(f"Complitions file moved to {script_rc_path}.backup" | green, BACKUP)

    echo("Looking for completions in shell configuration..." | blue, MAGNIFIER)

    if rc_path is not None and rc_command is not None:
        echo("Creating backup file..." | blue, BACKUP)
        cp[rc_path.expanduser(), f"{rc_path.expanduser()}.backup"]()
        echo(f"Shell configuration backed up to `{rc_path}.backup`" | blue, OK)

        with open(rc_path.expanduser(), "r") as rc_read_file:
            text = ""

            for line in rc_read_file.readlines():
                if script_command in line:
                    echo("Found completions command in shell configuration" | green, INFO)
                else:
                    text += line

            with open(rc_path.expanduser(), "w") as rc_write_file:
                rc_write_file.write(text)

    echo("Completions disabled in shell configuration" | green, OK)


@cli.command("set-editor", no_args_is_help=True)
@click.argument("editor", type=str)
@click.pass_obj
def set_editor(config: CliConfig, editor: str):
    """Set the text editor to use for editing JSON.

    \b
    EDITOR: Text editor to use. Example: vim, nano, code.
    """

    config.editor = editor
    config.save()

    echo(f"Editor set to {editor}" | green, OK)


def main():
    return cli()


# Add API actions to the CLI completions
__conf = CliConfig.load()
if __conf.client_module_name is not None:
    iter_api(__conf, f"{__conf.client_module_name}.api", action_group)

if __name__ == "__main__":
    cli()
