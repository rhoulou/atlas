# Lions Addon — Project Workflow

Kodi addon repo. Addon root: `plugin.video.lions/`. Repo served from `repo/`.

## Release workflow (vX.Y.Z)

Never asked twice — when site fixes are done, run the full release automatically.

1. **Bump version**: `plugin.video.lions/addon.xml` — set `version` to the next patch (e.g. 1.0.98 → 1.0.99).
2. **Changelog**: `plugin.video.lions/changelog.txt` — add a new `====` block at the very top:
   ```
   =====================================================
   version="1.0.99"
   -<one terse line per fix>
   =====================================================
   ```
3. **Build zip** (exclude pyc/`__pycache__`):
   ```
   cp -r plugin.video.lions /tmp/opencode/lions_build/plugin.video.lions
   cd /tmp/opencode/lions_build
   find . -name __pycache__ -type d -exec rm -rf {} +
   find . -name '*.pyc' -delete
   zip -rq <repo>/repo/zips/plugin.video.lions/plugin.video.lions-<ver>.zip plugin.video.lions
   ```
   Verify: no `__pycache__`/`.pyc` in zip; `addon.xml` inside zip has the new version.
4. **Repo files**:
   - `repo/addons.xml`: bump the `version=` attribute on the `plugin.video.lions` `<addon>` line only.
   - `repo/addons.xml.md5`: `md5sum repo/addons.xml > repo/addons.xml.md5`.
   - `repo/index.html`: insert the new zip as the first item under `<h3>plugin.video.lions</h3>` and mark it `(latest)` (previous one loses `(latest)`).
5. **Commit twice** (matches repo history pattern):
   - Commit 1: all `plugin.video.lions/**` changes — message `v<ver> - <summary of fixes>`.
   - Commit 2: `repo/addons.xml`, `repo/addons.xml.md5`, `repo/index.html`, new zip — message `v<ver> - rebuild repo zip for auto-update`.
   - NEVER stage `repo/zips/repository.atlas/repository.atlas-1.0.0.zip`.
6. **Push** to `origin main` (remote: `rhoulou/atlas`).

## Site fix conventions

- Sites live in `plugin.video.lions/resources/sites/<site>.py`; config in `plugin.video.lions/resources/sites.json` (key = module filename without `.py`); icons in `plugin.video.lions/resources/art/sites/<site>.png`.
- Global search calls `URL_SEARCH[0] + str(term)` then invokes `URL_SEARCH[1]` with that URL. To build the search URL from the term inside the module instead, set `URL_SEARCH = ('', 'showSearch')` and define `showSearch(sSearchText='')`.
- Double-slash URLs (`//recherche/`, `//?s=`) are fixed with `.rstrip('/')` on `URL_MAIN`.
- Newline-broken HTML parsing: `re.sub(r'\r?\n', '', sHtmlContent)` before matching, and prefer tolerant patterns (`[^>]*>.*?`).
- Dead sites: remove the sites.json entry, the module, and the icon; keep unrelated hosters (`resources/hosters/`) and the `supported_player` list untouched.
- Verify: `python3 -m py_compile` on touched modules, JSON parse of sites.json, and a live HTTP 200 sweep of the changed URLs.
