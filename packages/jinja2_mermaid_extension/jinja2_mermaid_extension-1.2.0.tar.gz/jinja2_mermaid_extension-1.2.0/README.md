# jinja2-mermaid-extension

[![Release](https://img.shields.io/github/v/release/AdamGagorik/jinja2-mermaid-extension)](https://img.shields.io/github/v/release/AdamGagorik/jinja2-mermaid-extension)
[![Build status](https://img.shields.io/github/actions/workflow/status/AdamGagorik/jinja2-mermaid-extension/main.yml?branch=main)](https://github.com/AdamGagorik/jinja2-mermaid-extension/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/AdamGagorik/jinja2-mermaid-extension/branch/main/graph/badge.svg)](https://codecov.io/gh/AdamGagorik/jinja2-mermaid-extension)
[![Commit activity](https://img.shields.io/github/commit-activity/m/AdamGagorik/jinja2-mermaid-extension)](https://img.shields.io/github/commit-activity/m/AdamGagorik/jinja2-mermaid-extension)
[![License](https://img.shields.io/github/license/AdamGagorik/jinja2-mermaid-extension)](https://img.shields.io/github/license/AdamGagorik/jinja2-mermaid-extension)

A jinja2 block to render a mermaid diagram.

1. The diagram is rendered using the `mermaid-cli` tool in a `Docker` container.
2. The diagram is saved to the current directory or `mermaid_output_root` (if defined).
3. The block is then replaced with a configurable string (markdown, etc).

## Setup

- `Docker` must be installed to run the `mermaid` command line tool.
- The extension should be installed in your `Python` environment.

```bash
pip install jinja2-mermaid-extension
```

- The extension should be added to the `jinja2` environment.

```python
from jinja2 import Environment
from jinja2_mermaid_extension import MermaidExtension

env = Environment(extensions=[MermaidExtension])
```

- You should pass the `mermaid_output_root` to the render method.

```python
out_path = Path().cwd() / "example.md"
template = env.get_template("example.md.jinja2")
rendered = template.render(mermaid_output_root=out_path.parent)
out_path.write_text(rendered)
```

## Usage

The following `jinaj2` block will render a mermaid diagram.

```jinja2
{% mermaid -%}
ext: .png
mode: myst
scale: 3
width: 75
align: center
caption: |
    An example mermaid diagram!
diagram: |
    graph TD
        A --> B
        B --> C
        A --> C
{% endmermaid %}
```

The following arguments are available:

| Argument                 | Kind               | Description                                                                | Default                |
| ------------------------ | ------------------ | -------------------------------------------------------------------------- | ---------------------- |
| **diagram** or **inp**   | Input              | The raw mermaid diagram code or the path to an `mmd` file.                 | `None`                 |
| **ext**                  | Output             | The file extension of the generated diagram.                               | `".png"`               |
| **mode**                 | Replacement Option | How to render the output after processing.                                 | `"path"`               |
| **theme**                | Mermaid CLI Option | The theme to use for the diagram.                                          | `"default"`            |
| **scale**                | Mermaid CLI Option | A scaling factor for the diagram.                                          | `3`                    |
| **width**                | Mermaid CLI Option | The width of the diagram in pixels.                                        | `800 `                 |
| **height**               | Mermaid CLI Option | The height of the diagram in pixels.                                       | `None`                 |
| **background**           | Mermaid CLI Option | The background color of the generated diagram.                             | `"white"`              |
| **alt_text**             | Replacement Option | The alt text of the diagram.                                               | `None`                 |
| **align**                | Replacement Option | The alignment of the diagram only valid for MyST output)                   | `"center"`             |
| **caption**              | Replacement Option | A caption to add to the diagram only valid for MyST output).               | `None`                 |
| **just_name**            | Replacement Option | Whether to only output the name of the generated diagram.                  | `False`                |
| **relative_to**          | Replacement Option | The directory to make the path of the generated diagram relative to.       | `None`                 |
| **use_cached**           | Processing Option  | Whether to use a cached version of the diagram.                            | `True`                 |
| **parallel**             | Processing Option  | Whether to render the diagram in parallel.                                 | `True`                 |
| **temp_dir**             | Processing Option  | A temporary directory to use for intermediate files.                       | `None`                 |
| **delete_temp_dir**      | Processing Option  | Whether to delete the temporary directory after execution.                 | `True`                 |
| **mermaid_docker_image** | Processing Option  | The docker image containing the mermaid-cli tool.                          | `"minlag/mermaid-cli"` |
| **mermaid_volume_mount** | Processing Option  | The directory in the docker container to mount the temporary directory to. | `"/data"`              |

The block will be replaced by a string based on the `mode` argument.

- `"path"`: Output the path to the generated image.
- `"markdown"`: Output a simple markdown image link.
- `"restructured"`: Output a restructured text image link.
- `"myst_markdown"`: Output a MyST formatted markdown image.

---

- **Github repository**: <https://github.com/AdamGagorik/jinja2-mermaid-extension/>
- **Documentation** <https://AdamGagorik.github.io/jinja2-mermaid-extension/>
