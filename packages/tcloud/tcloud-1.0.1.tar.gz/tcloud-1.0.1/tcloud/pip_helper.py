import os
import subprocess
import sys
import typing as t


def install(
    name: str,
    *,
    version: t.Optional[str] = None,
    extra_index_url: t.Optional[str] = None,
    upgrade: bool = True,
    extras: t.Optional[t.List[str]] = None,
) -> None:
    pip_executable = os.path.join(os.path.dirname(sys.executable), "pip")
    pip_command = [pip_executable, "install"]
    if upgrade:
        pip_command.append("--upgrade")
    package = name
    if extras:
        package += f"[{','.join(sorted(extras))}]"
    if version:
        package += f"=={version}"
    pip_command.append(package)
    if extra_index_url:
        pip_command += ["--extra-index-url", extra_index_url]
    try:
        subprocess.run(
            pip_command,
            check=True,
        )
    except subprocess.CalledProcessError:
        sys.exit(1)
