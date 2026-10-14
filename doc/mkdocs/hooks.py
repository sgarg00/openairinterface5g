# SPDX-License-Identifier: MIT
"""
MkDocs hooks for the Duranta OpenAirInterface 5G documentation site, registered in `mkdocs.yml`.

Documentation is distributed throughout the repository, with READMEs in `doc/`
and alongside source code in directories such as `radio/`, `common/`, and `openair1/`.
Since MkDocs uses a single `docs_dir`, these hooks adapt the repository layout to make
the Markdown files available to the documentation build.

- on_config: generate the navigation bar from doc/README.md (the source of
  truth), and load the GitHub label colors (cached) used to render label pills.
- on_files: publish every git-tracked markdown/image file of the repository
  under its repo-relative path, so that existing relative links such as
  `../radio/rfsimulator/README.md` work unchanged.
- on_page_markdown: adapt each page to MkDocs before rendering: remove table of
  contents markers, render GitHub alerts (`> [!NOTE]`, ...) as admonitions, point links
  to non-documentation files (sources, configs, directories) to GitHub, and
  render bare GitHub label URLs as label pills.

The work is done by the docs_site package next to this file; this file only
connects it to MkDocs.
"""

import importlib
import os

from mkdocs.structure.files import File, Files

from docs_site import labels, nav, repo, transforms


def on_config(config):
  """Generate the navigation bar and load the label colors, once per build."""
  # "mkdocs serve" loads this file only once but calls on_config on every
  # rebuild: reload docs_site so that edits to it apply without a restart
  # (edits to this file itself still need one).
  for module in (repo, nav, transforms, labels):
    importlib.reload(module)
  config["nav"] = nav.build_nav()
  labels.load_colors(config["repo_url"])
  return config


def on_files(files, config):
  """
  Replace the files found in docs_dir by all documentation files of the repository.

  Pages keep their repo-relative path (doc/BUILD.md, radio/USRP/README.md,
  ...). Theme files (Material assets and doc/mkdocs/overrides) are kept.
  """
  docs_dir = os.path.abspath(config["docs_dir"])
  theme_files = [f for f in files if os.path.abspath(f.src_dir) != docs_dir]
  repo_files = [File(path, repo.REPO_ROOT, config["site_dir"], config["use_directory_urls"]) for path in repo.tracked_files()]
  return Files(repo_files + theme_files)


def on_page_markdown(markdown, page, config, files):
  """Adapt the markdown of one page to MkDocs before it is rendered."""
  # The overview page lists every page itself: hide its (nearly empty) navigation sidebar.
  if page.file.src_uri == repo.NAV_SOURCE:
    page.meta.setdefault("hide", []).append("navigation")

  markdown = transforms.remove_toc_markers(markdown)
  markdown = transforms.github_alerts(markdown)
  markdown = transforms.link_unpublished_files(markdown, page.file.src_uri, files, config["repo_url"])
  return labels.render_labels(markdown, config["repo_url"])
