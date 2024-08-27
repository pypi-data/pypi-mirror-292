"""
## This module defines a base class for jinja2 extensions that generate images.
"""

import enum
import functools
import inspect
import json
import logging
from collections.abc import Generator, Hashable
from concurrent.futures import Executor, Future, ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, cast
from uuid import UUID, uuid5

import yaml
from jinja2 import Environment, nodes, pass_context
from jinja2.ext import Extension
from jinja2.parser import Parser
from jinja2.runtime import Context, Macro

logger = logging.getLogger(__name__)

namespace = UUID("b5db653c-cc06-466c-9b39-775db782a06f")


class Mode(enum.Enum):
    MD: str = "md"
    OUT: str = "out"
    RST: str = "rst"
    MYST: str = "myst"


LOOKUP_MODE = {
    "md": Mode.MD,
    "markdown": Mode.MD,
    "out": Mode.OUT,
    "path": Mode.OUT,
    "output": Mode.OUT,
    "output_only": Mode.OUT,
    "output_path": Mode.OUT,
    "rst": Mode.RST,
    "restructuredtext": Mode.RST,
    "myst": Mode.MYST,
    "myst_parser": Mode.MYST,
    "myst_markdown": Mode.MYST,
}


@dataclass
class Runner:
    running: set[Hashable] = field(default_factory=set)
    futures: dict[Future, Hashable] = field(default_factory=dict)

    def run(self, key: Hashable, fn: Callable, *args: Any, **kwargs: Any) -> None:
        if key in self.futures or key in self.running:
            raise KeyError(key)

        future = self.executor().submit(fn, *args, **kwargs)
        self.futures[future] = key
        self.running.add(key)

    def wait(self) -> None:
        for future in as_completed(self.futures.keys()):
            key = self.futures[future]
            self.running.remove(key)
            self.futures.pop(future)
            future.result()

        if self.futures:
            raise RuntimeError("Not all futures completed")

        if self.running:
            self.running.clear()

    @classmethod
    @functools.lru_cache(maxsize=1)
    def executor(cls) -> Executor:
        return ThreadPoolExecutor(max_workers=None)

    def __contains__(self, key: Hashable) -> bool:
        return key in self.running


@functools.lru_cache(maxsize=1)
def runner() -> Runner:
    return Runner()


class GenImageExtension(Extension):
    tags: set[str] = {"yaml"}  # noqa: RUF012
    input_root_key: str | None = None
    output_root_key: str | None = None

    def __init__(self, environment: Environment):
        super().__init__(environment)

    def parse(self, parser: Parser) -> nodes.Node:
        """
        The logic to parse the jinja2 block as yaml.
        """
        line = next(parser.stream).lineno
        block = parser.parse_statements((f"name:end{next(iter(self.tags))}",), drop_needle=True)
        kwargs = yaml.safe_load(cast(nodes.TemplateData, cast(nodes.Output, block[0]).nodes[0]).data)
        callback = self.call_method("_render", [nodes.Const(json.dumps(kwargs))])
        return nodes.CallBlock(callback, [], [], block).set_lineno(line)

    @staticmethod
    def modify(**kwargs: Any) -> Generator[tuple[str, Any], None, None]:
        """
        Intercept and modify the keyword arguments before passing them to the callback function.
        """
        yield from kwargs.items()

    def callback(self, inp: Path | str, out: Path, inp_root: Path, out_root: Path, **kwargs: Any) -> None:
        """
        The function to call to generate an image.
        """
        raise NotImplementedError

    @property
    def _valid_keys(self) -> Generator[str]:
        yield from ()

    @pass_context
    def _render(self, context: Context, kwargs_json: str, caller: Macro) -> str:
        kwargs = dict(self.modify(**json.loads(kwargs_json)))
        valid_keys = set(inspect.signature(self._gen_markdown_lines).parameters) | set(self._valid_keys)
        valid_keys = valid_keys - {"context", "output_name_salt", "out"}
        unknown_keys = set(kwargs.keys()) - valid_keys
        if any(unknown_keys):
            raise TypeError(f"callback got unexpected keyword arguments: {', '.join(unknown_keys)}")

        return "\n".join(self._gen_markdown_lines(context, output_name_salt=kwargs_json, **kwargs))

    def _gen_markdown_lines(  # noqa: C901
        self,
        context: Context,
        inp: Path | str,
        ext: str = ".png",
        name: str | None = None,
        mode: str | Mode = Mode.OUT,
        width: int | str | None = None,
        height: int | str | None = None,
        align: str = "center",
        caption: str | None = None,
        full_path: bool = False,
        just_name: bool = False,
        use_cached: bool = True,
        parallel: bool = False,
        output_name_salt: str = "...",
        **kwargs: Any,
    ) -> Generator[str, None, None]:
        """
        Run callback and yield a series of markdown commands to include it .
        """
        if isinstance(mode, str):
            mode = LOOKUP_MODE[mode.strip().lower()]

        out_root = self._get_output_root(context)
        if name is None:
            name = str(uuid5(namespace, str(inp) + output_name_salt))

        out = out_root.joinpath(name).with_suffix("." + ext.lower().lstrip("."))

        if not out.exists() or not use_cached:
            if out in runner():
                logger.warning("ignore: %s", out)
            else:
                if parallel:
                    logger.warning("submit: %s", out)
                    runner().run(
                        key=out,
                        fn=self.callback,
                        inp=inp,
                        out=out,
                        inp_root=self._get_input_root(context),
                        out_root=out_root,
                        **kwargs,
                    )
                else:
                    logger.warning("create: %s", out)
                    self.callback(
                        inp=inp,
                        out=out,
                        inp_root=self._get_input_root(context),
                        out_root=self._get_output_root(context),
                        **kwargs,
                    )
                    runner().running.add(out)
        else:
            logger.warning("cached: %s", out)

        if just_name:
            stem = out.name
        elif not full_path:
            stem = str(out.relative_to(Path(out_root)))
        else:
            stem = str(out)

        if mode == Mode.OUT:
            yield stem
        elif mode == Mode.MD:
            yield from self._render_md(out, stem, caption)
        elif mode == Mode.RST:
            yield from self._render_rst(stem, caption)
        elif mode == Mode.MYST:
            yield from self._render_myst(stem, align, caption, width, height)
        else:
            raise ValueError(f"Unknown mode: {mode}")

    @classmethod
    def _get_input_root(cls, context: Context) -> Path:
        if cls.input_root_key is None:
            return Path.cwd()

        if (root := context.parent.get(str(cls.input_root_key))) is None:
            return Path.cwd()

        return Path(cast(Path, root))

    @classmethod
    def _get_output_root(cls, context: Context) -> Path:
        if cls.output_root_key is None:
            return Path.cwd()

        if (root := context.parent.get(str(cls.output_root_key))) is None:
            return Path.cwd()

        return Path(cast(Path, root))

    @staticmethod
    def _render_md(out: Path, stem: str, caption: str | None) -> Generator[str, None, None]:
        if caption is not None:
            caption = caption.rstrip()
            yield f"![{caption}]({stem})"
        else:
            yield f"![{out.name}]({stem})"

    @staticmethod
    def _render_rst(stem: str, caption: str | None) -> Generator[str, None, None]:
        if caption is not None:
            yield f".. image:: {stem}\n   :alt: {caption.rstrip()}"
        else:
            yield f".. image:: {stem}"

    @staticmethod
    def _render_myst(
        stem: str, align: str, caption: str | None, width: int | str | None, height: int | str | None
    ) -> Generator[str, None, None]:
        if caption is not None:
            yield f":::{{figure}} {stem}"
        else:
            yield f":::{{image}} {stem}"
        if width is not None:
            yield f":width: {width}"
        if height is not None:
            yield f":height: {height}"
        if align is not None:
            yield f":align: {align}"
        if caption is not None:
            yield f"\n{caption.rstrip()}"
        yield r":::"
