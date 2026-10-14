<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# OpenAirInterface5G Documentation Website (MkDocs)

The Duranta OpenAirInterface5G documentation is written in Markdown
and maintained throughout the repository, from `doc/` to README files
alongside the source code in directories such as `radio/`, `common/`, and `openair1/`.

This directory brings the documentation together into a single, searchable website
using [MkDocs](https://www.mkdocs.org/) and the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
theme, customized with the Duranta branding.

The original Markdown files remain unchanged, preserving their readability and
rendering on GitHub while making the documentation accessible through a unified website.

## Prerequisites

- [Python 3.9 or newer](https://www.python.org/downloads/)
- [pip](https://pypi.org/project/pip/)

## Virtual environment (optional)

To keep the documentation tools separate from your system Python, create and
activate a virtual environment from the repository root before the Quick start:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

All Quick start commands then run inside it. When finished, leave it with
`deactivate`.

The `.venv/` directory is local to your environment and must not be committed
to Git. The site build skips hidden directories, so it is not published either.

## Quick start

From the repository root, install the dependencies:

```bash
pip install -r doc/mkdocs/requirements.txt
```

Start the development server to preview the documentation locally.
The site rebuilds automatically when files change.

```bash
mkdocs serve
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) to view the site.

If the `mkdocs` command is not found (pip may install it in `~/.local/bin`,
which is not always in `PATH`), run `python3 -m mkdocs serve` instead.

To use a different port for the preview, replace `<PORT_NUMBER>` with your preferred port (e.g., `8005`):

```bash
mkdocs serve -a 127.0.0.1:<PORT_NUMBER>
```

To build the static site for deployment, run:

```bash
mkdocs build
```

The generated site is written to `build/mkdocs-site/`.
To serve the generated static files locally, run:

```bash
python3 -m http.server 8000 --directory build/mkdocs-site
```

For more details, run `mkdocs --help`.

## Validation

Before submitting a pull request, run a strict build to check for warnings and
errors:

```bash
mkdocs build --strict
```

The strict build fails if MkDocs reports any warning, such as a link to a
missing file or to a missing section (`page.md#section`). This catches broken
documentation before it is merged.

Unlike `mkdocs serve`, which only prints warnings and keeps serving the site,
`mkdocs build --strict` stops with an error code, so it can also be used in CI.

## Files and directories

```text
.
├── mkdocs.yml                              # Site configuration, theme, and Markdown extensions
└── doc/
    └── mkdocs/
        ├── README.md                       # Overview and usage instructions
        ├── requirements.txt                # Pinned Python dependencies
        ├── hooks.py                        # Integrates docs_site with MkDocs build events
        ├── docs_site/                      # Python modules for documentation site logic
        │   ├── __init__.py                 # Package overview
        │   ├── repo.py                     # Repository paths and documentation file discovery
        │   ├── nav.py                      # Navigation generation from doc/README.md
        │   ├── transforms.py               # Markdown transformations for MkDocs
        │   └── labels.py                   # GitHub label badges and colors
        └── overrides/                      # Custom theme templates and styles
            ├── assets/
            │   └── stylesheets/
            │       └── duranta-theme.css   # Duranta colors and layout
            └── partials/
                └── copyright.html          # Custom footer with logo and issue link
```

## Troubleshooting

- **`mkdocs: command not found`**: activate the virtual environment, or run
  `python3 -m mkdocs` instead of `mkdocs`.
- **Port already in use** (`Address already in use`): another server is
  running on that port; pick another one with `mkdocs serve -a 127.0.0.1:8005`.
- **Missing dependencies** (`ModuleNotFoundError`, unknown theme or
  extension): reinstall them with `pip install -r doc/mkdocs/requirements.txt`.
- **Build errors**: check the terminal output for invalid configuration in
  `mkdocs.yml`, missing files, or errors in `hooks.py` and the `docs_site/`
  modules.
- **`Could not fetch GitHub label colors`**: harmless. It happens offline or
  when the GitHub API rate limit is reached. The label pills (e.g. in
  `doc/TESTBenches.md`) then use the last colors cached in
  `build/mkdocs-cache/`, or a default color. To raise the rate limit, run with
  a token: `GITHUB_TOKEN=<token> mkdocs serve`.
