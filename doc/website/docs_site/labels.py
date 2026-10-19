# SPDX-License-Identifier: MIT
"""
GitHub label pills.

GitHub renders a bare label URL (e.g. .../openairinterface5g/labels/5G-NR) as a
colored label, whereas the site would show the raw URL. Such URLs are replaced by an
<a class="gh-label"> styled in duranta-theme.css, using the label color from
GitHub when available.
"""

import json
import logging
import os
import re
import time
import urllib.parse
import urllib.request

from .repo import REPO_ROOT

log = logging.getLogger("docs_site")

# Label colors are cached so that the preview server, which rebuilds on every save,
# stays within the GitHub API rate limit (60 requests per hour without a token).
LABEL_CACHE = os.path.join(REPO_ROOT, "build", "website-cache", "label-colors.json")
LABEL_CACHE_MAX_AGE = 24 * 3600  # seconds

# Label name -> hex color (e.g. "5G-NR" -> "68e09e"), filled by load_colors().
_colors = {}


def load_colors(repo_url):
  """Load the label colors used by render_labels(), once per build."""
  _colors.clear()
  _colors.update(_fetch_colors(repo_url))


def render_labels(markdown, repo_url):
  """Replace bare label URLs by label pills. URLs already inside a link "(...)", "<...>" or "[...]" are left as is."""
  label_re = re.compile(rf"(?<![(<\[\w/])({re.escape(repo_url.rstrip('/'))}/labels/([\w%.-]+))")
  return label_re.sub(lambda m: _label_html(m.group(1), m.group(2)), markdown)


def _fetch_colors(repo_url):
  """
  Label colors of the GitHub repository, from the cache or the GitHub API.

  The API is only queried if the cache is older than LABEL_CACHE_MAX_AGE, with
  the GITHUB_TOKEN environment variable if set. If the API is not reachable
  (offline build, rate limit), the cache is used even if outdated; without a
  cache, labels use the default color of the stylesheet. The build never fails.
  """
  m = re.match(r"https://github\.com/([^/]+/[^/]+?)/?$", repo_url or "")
  if not m:
    return {}
  cached = {}
  try:
    with open(LABEL_CACHE, encoding="utf-8") as f:
      cached = json.load(f)
    if time.time() - os.path.getmtime(LABEL_CACHE) < LABEL_CACHE_MAX_AGE:
      return cached
  except (OSError, ValueError):
    pass
  request = urllib.request.Request(f"https://api.github.com/repos/{m.group(1)}/labels?per_page=100")
  if os.environ.get("GITHUB_TOKEN"):
    request.add_header("Authorization", f"Bearer {os.environ['GITHUB_TOKEN']}")
  try:
    with urllib.request.urlopen(request, timeout=5) as r:
      colors = {l["name"]: l["color"] for l in json.load(r)}
  except Exception as e:
    log.info("Could not fetch GitHub label colors (%s), using %s", e, "cached colors" if cached else "default color")
    return cached
  os.makedirs(os.path.dirname(LABEL_CACHE), exist_ok=True)
  with open(LABEL_CACHE, "w", encoding="utf-8") as f:
    json.dump(colors, f)
  return colors


def _text_color(bg):
  """Black or white, whichever has the higher WCAG contrast on the hex color bg (e.g. "68e09e")."""
  channels = (int(bg[i:i + 2], 16) / 255 for i in (0, 2, 4))
  r, g, b = ((c / 12.92) if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels)
  luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
  contrast_black = (luminance + 0.05) / 0.05
  contrast_white = 1.05 / (luminance + 0.05)
  return "#1f2328" if contrast_black > contrast_white else "#ffffff"


def _label_html(url, name):
  """HTML pill for one label URL; name may be URL-encoded (e.g. "help%20wanted")."""
  name = urllib.parse.unquote(name)
  color = _colors.get(name)
  style = f' style="background-color:#{color};color:{_text_color(color)}"' if color else ""
  return f'<a class="gh-label" href="{url}"{style}>{name}</a>'
