"""
## This module defines a callback function for generating mermaid diagrams.
"""

import shutil
import subprocess
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, ClassVar


@dataclass
class Options:
    """
    Specific options for a callback function.
    """


@dataclass
class TikZOptions(Options):
    """
    Specific options for the tikz callback function.
    """

    #: The commands to run to generate the LaTeX output.
    latex_command: tuple[str, ...] = (
        "tectonic",
        "{inp_tex}",
    )


@dataclass
class MermaidOptions(Options):
    """
    Specific options for the mermaid callback function.
    """

    #: The theme to use for the diagram.
    theme: str = "default"
    #: A scaling factor for the diagram.
    scale: int = 3
    #: The width of the diagram in pixels.
    render_width: int = 800
    #: The height of the diagram in pixels.
    render_height: int | None = None
    #: The background color of the generated diagram.
    background: str = "white"
    #: The docker image containing the mermaid-cli tool.
    mermaid_docker_image: str = "minlag/mermaid-cli"
    #: The directory in the docker container to mount the temporary directory to.
    mermaid_volume_mount: str = "/data"
    #: Whether to use the docker image or a locally installed mermaid-cli tool named mmdc.
    use_local_mmdc_instead: bool = False


@contextmanager
def handle_temp_root(force: Path | None, delete_temp_dir: bool) -> Generator[Path, None, None]:
    """
    Handle the temporary root directory.

    Args:
        force: A forced temporary root directory.
        delete_temp_dir: Whether to delete the temporary directory after execution.

    Yields:
        Path: The temporary root directory.
    """
    try:
        if force:
            yield force
        else:
            with TemporaryDirectory(delete=delete_temp_dir) as tmp_root:
                yield Path(tmp_root)
    finally:
        pass


class RunCommandInTempDir:
    """
    A wrapper to run a command in a temporary directory.
    """

    #: The extension for raw input files.
    RAW_INPUT_EXT: ClassVar[str] = ""
    #: The valid extensions for output files.
    VALID_OUT_EXT: ClassVar[frozenset[str]] = frozenset(())

    def command(self, *, tmp_inp: Path, tmp_out: Path, tmp_root: Path, **kwargs: Any) -> Generator[str, None, None]:
        """
        Generate the command to run.

        Args:
            tmp_inp: The input file, located in the temporary directory.
            tmp_out: The output file, located in the temporary directory.
            tmp_root: The current temporary directory.
            kwargs: Additional keyword arguments.

        Yields:
            str: The command strings that were generated.
        """
        raise NotImplementedError

    def __call__(
        self, *, inp: Path | str, out: Path, temp_dir: Path | None = None, delete_temp_dir: bool = True, **kwargs: Any
    ) -> None:
        """
        Run the command in a temporary directory.

        Args:
            inp: The input file or a raw input string.
            out: The output file.
            temp_dir: A temporary directory to use for intermediate files.
            delete_temp_dir: Whether to delete the temporary directory after execution.
            **kwargs: Additional keyword arguments.
        """
        out = Path(out)

        with handle_temp_root(temp_dir, delete_temp_dir) as tmp_root:
            if isinstance(inp, str):
                tmp_inp = tmp_root / out.with_suffix(self.RAW_INPUT_EXT).name
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

            if tmp_out.suffix.lower() not in self.VALID_OUT_EXT:
                raise ValueError(
                    f"Expected output file to have a {', '.join(self.VALID_OUT_EXT)} extension, got {tmp_out.suffix}"
                )

            if tmp_inp.suffix.lower() not in {self.RAW_INPUT_EXT}:
                raise ValueError(f"Expected input file to have a .mmd extension, got {tmp_inp.suffix}")

            try:
                subprocess.check_call(list(self.command(tmp_inp=tmp_inp, tmp_out=tmp_out, tmp_root=tmp_root, **kwargs)))
            except subprocess.CalledProcessError:
                raise RuntimeError("Failed to execute command") from None

            if not tmp_out.exists():
                raise FileNotFoundError(tmp_out)

            shutil.copy(tmp_out, out)


class TikZCallback(RunCommandInTempDir):
    """
    A callback function for generating mermaid diagrams.
    """

    #: The extension for raw input files.
    RAW_INPUT_EXT: ClassVar[str] = ".tex"
    #: The valid extensions for output files.
    VALID_OUT_EXT: ClassVar[frozenset[str]] = frozenset((".pdf",))

    def command(self, *, tmp_inp: Path, tmp_out: Path, tmp_root: Path, **kwargs: Any) -> Generator[str, None, None]:
        """
        Generate the command to run.

        Args:
            tmp_inp: The input file, located in the temporary directory.
            tmp_out: The output file, located in the temporary directory.
            tmp_root: The current temporary directory.
            kwargs: Additional keyword arguments.

        Yields:
            str: The command strings that were generated.
        """
        opts = TikZOptions(**kwargs)

        for command in opts.latex_command:
            yield command.format(inp_tex=tmp_inp)


class MermaidCallback(RunCommandInTempDir):
    """
    A callback function for generating mermaid diagrams.
    """

    #: The extension for raw input files.
    RAW_INPUT_EXT: ClassVar[str] = ".mmd"
    #: The valid extensions for output files.
    VALID_OUT_EXT: ClassVar[frozenset[str]] = frozenset((".svg", ".png", ".pdf"))

    def command(self, *, tmp_inp: Path, tmp_out: Path, tmp_root: Path, **kwargs: Any) -> Generator[str, None, None]:
        """
        Generate the command to run.

        Args:
            tmp_inp: The input file, located in the temporary directory.
            tmp_out: The output file, located in the temporary directory.
            tmp_root: The current temporary directory.
            kwargs: Additional keyword arguments.

        Yields:
            str: The command strings that were generated.
        """
        opts = MermaidOptions(**kwargs)

        if opts.use_local_mmdc_instead:
            yield "mmdc"
        else:
            yield "docker"
            yield "run"
            yield "--rm"
            yield "-v"
            yield f"{tmp_root}:{opts.mermaid_volume_mount}"
            yield opts.mermaid_docker_image

        yield "-t"
        yield opts.theme
        yield "-b"
        yield opts.background
        yield "-s"
        yield str(opts.scale)
        yield "-w"
        yield str(opts.render_width)
        yield from (() if opts.render_height is None else ("-H", str(opts.render_height)))
        yield "-i"
        yield tmp_inp.name
        yield "-o"
        yield tmp_out.name


tikz = TikZCallback()
mermaid = MermaidCallback()
