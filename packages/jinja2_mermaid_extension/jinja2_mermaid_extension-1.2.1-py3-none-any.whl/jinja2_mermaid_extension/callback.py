"""
## This module defines a callback function for generating mermaid diagrams.
"""

import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory


def mermaid(
    inp: Path | str,
    out: Path,
    theme: str = "default",
    scale: int = 3,
    width: int = 800,
    height: int | None = None,
    background: str = "white",
    temp_dir: Path | None = None,
    delete_temp_dir: bool = True,
    mermaid_docker_image: str = "minlag/mermaid-cli",
    mermaid_volume_mount: str = "/data",
) -> None:
    """
    Generate a mermaid diagram from a mermaid code block or input file.

    Parameters:
        inp: A raw mermaid code block or a path to a file containing mermaid code.
        out: The path to the output file.
        theme: The theme to use for the diagram.
        scale: A scaling factor for the diagram.
        width: The width of the diagram in pixels.
        height: The height of the diagram in pixels.
        background: The background color of the generated diagram.
        temp_dir: A temporary directory to use for intermediate files.
        delete_temp_dir: Whether to delete the temporary directory after execution.
        mermaid_docker_image: The docker image containing the mermaid-cli tool.
        mermaid_volume_mount: The directory in the docker container to mount the temporary directory to.
    """
    out = Path(out)

    with temp_dir or TemporaryDirectory(
        dir=None if temp_dir is None else str(temp_dir), delete=delete_temp_dir
    ) as tmp_root:
        tmp_root = Path(str(tmp_root))

        if isinstance(inp, str):
            tmp_inp = tmp_root / out.with_suffix(".mmd").name
            with tmp_inp.open("w") as stream:
                stream.write(inp)
        else:
            if not inp.exists():
                raise FileNotFoundError(f"input file does not exist!: {inp}")

            tmp_inp = tmp_root / inp.name
            shutil.copy(inp, tmp_inp)

        if not out.parent.exists():
            raise FileNotFoundError(f"output directory does not exist!: {out.parent}")

        if out.is_dir():
            raise IsADirectoryError(out)

        tmp_out = tmp_root / out.name
        if tmp_out.exists():
            raise FileExistsError(tmp_out)

        if tmp_out.suffix.lower() not in {".svg", ".png", ".pdf"}:
            raise ValueError(f"Expected output file to have a .svg, .png, or .pdf extension, got {tmp_out.suffix}")

        if tmp_inp.suffix.lower() not in {".mmd"}:
            raise ValueError(f"Expected input file to have a .mmd extension, got {tmp_inp.suffix}")

        # noinspection SpellCheckingInspection
        command = [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{tmp_root}:{mermaid_volume_mount}",
            mermaid_docker_image,
            "-t",
            theme,
            "-b",
            background,
            "-s",
            str(scale),
            "-w",
            str(width),
            *(() if height is None else ("-H", str(height))),
            "-i",
            tmp_inp.name,
            "-o",
            tmp_out.name,
        ]

        try:
            subprocess.check_call(command)
        except subprocess.CalledProcessError:
            raise RuntimeError("Failed to execute mermaid command") from None

        if not tmp_out.exists():
            raise FileNotFoundError(tmp_out)

        shutil.copy(tmp_out, out)
