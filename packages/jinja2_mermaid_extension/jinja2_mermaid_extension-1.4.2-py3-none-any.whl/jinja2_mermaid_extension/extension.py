"""
## This module defines a jinja2 extension for generating mermaid diagrams.
"""

import inspect
from collections.abc import Generator
from pathlib import Path
from typing import Any

from jinja2 import Environment

from jinja2_mermaid_extension.base import GenImageExtension
from jinja2_mermaid_extension.callback import MermaidOptions, TikZOptions, mermaid, tikz


class TikZExtension(GenImageExtension):
    """
    A Jinja2 extension for generating tikz diagrams.
    """

    tags: set[str] = {"tikz"}  # noqa: RUF012
    input_root_key: str | None = "tikz_input_root"
    output_root_key: str | None = "tikz_output_root"

    def __init__(self, environment: Environment):
        super().__init__(environment)

    @property
    def _valid_keys(self) -> Generator[str]:
        yield from TikZOptions.__annotations__.keys()
        yield from inspect.signature(tikz).parameters

    @staticmethod
    def modify(**kwargs: Any) -> Generator[tuple[str, Any], None, None]:
        """
        Intercept and modify the keyword arguments before passing them to the callback function.
        """
        for key, value in kwargs.items():
            if key == "diagram":
                if "inp" in kwargs:
                    raise RuntimeError("Cannot have both 'diagram' and 'inp' in kwargs")
                yield "inp", value
            else:
                yield key, value

    def callback(
        self,
        inp: Path | str,
        out: Path,
        inp_root: Path,
        out_root: Path,
        **kwargs: Any,
    ) -> None:
        """
        The function to call to generate an image.
        """
        if isinstance(inp, str) and inp.endswith(".tex"):
            inp = Path(inp)
            if not inp.is_absolute():
                inp = inp_root / inp

        return tikz(inp=inp, out=out, **kwargs)


class MermaidExtension(GenImageExtension):
    """
    A Jinja2 extension for generating mermaid diagrams.
    """

    tags: set[str] = {"mermaid"}  # noqa: RUF012
    input_root_key: str | None = "mermaid_input_root"
    output_root_key: str | None = "mermaid_output_root"

    def __init__(self, environment: Environment):
        super().__init__(environment)

    @property
    def _valid_keys(self) -> Generator[str]:
        yield from MermaidOptions.__annotations__.keys()
        yield from inspect.signature(mermaid).parameters

    @staticmethod
    def modify(**kwargs: Any) -> Generator[tuple[str, Any], None, None]:
        """
        Intercept and modify the keyword arguments before passing them to the callback function.
        """
        for key, value in kwargs.items():
            if key == "diagram":
                if "inp" in kwargs:
                    raise RuntimeError("Cannot have both 'diagram' and 'inp' in kwargs")
                yield "inp", value
            else:
                yield key, value

    def callback(
        self,
        inp: Path | str,
        out: Path,
        inp_root: Path,
        out_root: Path,
        **kwargs: Any,
    ) -> None:
        """
        The function to call to generate an image.
        """
        if isinstance(inp, str) and inp.endswith(".mmd"):
            inp = Path(inp)
            if not inp.is_absolute():
                inp = inp_root / inp

        return mermaid(inp=inp, out=out, **kwargs)
