from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

try:
    import rich_click as click
except ImportError:
    import click  # type: ignore[no-redef]

from click import Path as ClickPath

from ._utils import LitestarEnv, LitestarExtensionGroup, validate_mutually_exclusive_env_options
from .commands import core, schema, sessions

if TYPE_CHECKING:
    from typing import Sequence

__all__ = ("litestar_group",)


@click.group(cls=LitestarExtensionGroup, context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--app", "app_path", help="Module path to a Litestar application")
@click.option(
    "--app-dir",
    help="Look for APP in the specified directory, by adding this to the PYTHONPATH. Defaults to the current working directory.",
    default=None,
    type=ClickPath(dir_okay=True, file_okay=False, path_type=Path),
    show_default=False,
)
@click.option(
    "--env-file",
    "env_files",
    help="Path to a .env file to load environment variables from. Defaults to `./.env`",
    default=None,
    type=ClickPath(dir_okay=False, file_okay=True, path_type=Path),
    show_default=False,
    multiple=True,
    callback=validate_mutually_exclusive_env_options,
)
@click.option(
    "--ignore-env-files",
    "ignore_env_files",
    is_flag=True,
    default=False,
    callback=validate_mutually_exclusive_env_options,
)
@click.pass_context
def litestar_group(
    ctx: click.Context,
    app_path: str | None,
    app_dir: Path | None = None,
    env_files: Sequence[Path] = (Path(".env"),),
    ignore_env_files: bool = False,
) -> None:
    """Litestar CLI.

    The application to will be automatically discovered if it's in one of these
    canonical paths: 'app.py', 'asgi.py', 'application.py' or 'app/__init__.py'.
    When auto-discovering application factories, functions with the name 'create_app'
    are considered, or functions that are annotated as returning a 'Litestar'
    instance.

    Alternatively, the application can be specified explicitly via the '--app' option
    ('litestar --app=<module name>.<submodule>:<app instance or factory>') or the
    'LITESTAR_APP' environment variable of the same name.
    """
    if ctx.obj is None:  # env has not been loaded yet, so we can lazy load it
        implicit_load = not env_files
        if ignore_env_files:
            env_files = ()
            implicit_load = False
        ctx.obj = lambda: LitestarEnv.from_env(
            app_path,
            app_dir=app_dir,
            env_files=env_files,
            implicit_load=implicit_load,
        )


# add sub commands here

litestar_group.add_command(core.info_command)  # pyright: ignore
litestar_group.add_command(core.run_command)  # pyright: ignore
litestar_group.add_command(core.routes_command)  # pyright: ignore
litestar_group.add_command(core.version_command)  # pyright: ignore
litestar_group.add_command(sessions.sessions_group)  # pyright: ignore
litestar_group.add_command(schema.schema_group)  # pyright: ignore
