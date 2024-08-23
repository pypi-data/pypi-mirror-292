import ast
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from cleo.io.io import IO
from poetry.core.utils.helpers import module_name
from poetry.plugins.plugin import Plugin
from poetry.poetry import Poetry

from . import strtobool


class VersionPlugin(Plugin):
    def activate(self, poetry: Poetry, io: IO) -> None:
        disable_log = strtobool(os.environ.get('POETRY_PLUGIN_PRIVATE_DISABLE_LOG', 'false'))

        poetry_version_config: Optional[Dict[str, Any]] = poetry.pyproject.data.get(
            "tool", {}
        ).get("poetry-version-plugin")
        if poetry_version_config is None:
            return
        version_source = poetry_version_config.get("source")
        if not version_source:
            message = (
                "<b>poetry-plugin-private</b>: No <b>source</b> configuration found in "
                "[tool.poetry-version-plugin] in pyproject.toml, not extracting "
                "dynamic version"
            )
            io.write_error_line(message)
            raise RuntimeError(message)

        if not disable_log:
            io.write_line('\033[38;5;192m[Plugin]: Dynamic version plugin is enabled.\033[0m')

        if version_source == "init":
            # Check if version is set in environment variables? If present, the version number in the environment variable is used.
            version = os.environ.get('VERSION', None)

            if version:
                if not disable_log:
                    io.write_line(
                        f'[Plugin]: The version number has been dynamically set to \033[38;5;119m{version}\033[0m based on the environment variable <VERSION>.'
                    )
                poetry.package.version = version
                return

            packages = poetry.local_config.get("packages")
            if packages:
                if len(packages) == 1:
                    package_name = packages[0]["include"]
                else:
                    message = (
                        "<b>poetry-plugin-private</b>: More than one package set, "
                        "cannot extract dynamic version"
                    )
                    io.write_error_line(message)
                    raise RuntimeError(message)
            else:
                package_name = module_name(poetry.package.name)
            init_path = Path(package_name) / "__init__.py"
            if not init_path.is_file():
                message = (
                    "<b>poetry-plugin-private</b>: __init__.py file not found at "
                    f"{init_path} cannot extract dynamic version"
                )
                io.write_error_line(message)
                raise RuntimeError(message)
            else:
                if not disable_log:
                    io.write_line(
                        f'\033[38;5;240m[Plugin]: Using __init__.py file at {init_path} for dynamic version\033[0m'
                    )
            tree = ast.parse(init_path.read_text(encoding='utf-8'))
            for el in tree.body:
                if isinstance(el, ast.Assign):
                    if len(el.targets) == 1:
                        target = el.targets[0]
                        if isinstance(target, ast.Name):
                            if target.id == "__version__":
                                value_node = el.value
                                if isinstance(value_node, ast.Constant):
                                    version = value_node.value
                                elif isinstance(value_node, ast.Str):
                                    version = value_node.s
                                else:  # pragma: nocover
                                    # This is actually covered by tests, but can't be
                                    # reported by Coverage
                                    # Ref: https://github.com/nedbat/coveragepy/issues/198
                                    continue
                                if not disable_log:
                                    io.write_line(
                                        f'[Plugin]: Setting package dynamic version to __version__ variable from __init__.py: \033[38;5;119m{version}\033[0m'
                                    )
                                poetry.package.version = version
                                return
            message = (
                "<b>poetry-plugin-private</b>: No valid __version__ variable found "
                "in __init__.py, cannot extract dynamic version"
            )
            io.write_error_line(message)
            raise RuntimeError(message)
        elif version_source == "git-tag":
            result = subprocess.run(
                ["git", "describe", "--exact-match", "--tags", "HEAD"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                universal_newlines=True,
            )
            if result.returncode == 0:
                tag = result.stdout.strip()

                if not disable_log:
                    io.write_line(
                        "<b>poetry-plugin-private</b>: Git tag found, setting "
                        f"dynamic version to: \033[38;5;119m{tag}\033[0m"
                    )
                poetry.package.version = tag
                return
            else:
                message = (
                    "<b>poetry-plugin-private</b>: No Git tag found, not "
                    "extracting dynamic version"
                )
                io.write_error_line(message)
                raise RuntimeError(message)
        elif version_source == 'env':
            version = os.environ.get('VERSION', '0.0.1')

            if not disable_log:
                io.write_line(
                    "<b>poetry-plugin-private</b>: Setting package "
                    "dynamic version to __version__ "
                    f"variable from System/User environment variables: \033[38;5;119m{version}\033[0m"
                )
            poetry.package.version = version
