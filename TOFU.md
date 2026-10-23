# JupyterLite on Tofu

JupyterLite is Jupyter running entirely in the web browser: JupyterLab and the Jupyter Notebook interface, with a Python kernel built on Pyodide (Python compiled to WebAssembly) and JavaScript and p5.js kernels. Code runs on the visitor's own computer. There is no server, no account and no database: the notebooks and files people create are kept in their own browser's storage (IndexedDB) for the app's address, so they should download anything they want to keep.

This is a fork of [jupyterlite/demo](https://github.com/jupyterlite/demo), Project Jupyter's official template for publishing a JupyterLite site. It comes with upstream's sample notebooks (Python basics, Matplotlib, Plotly, Altair, ipywidgets, ipyleaflet, ipycanvas, folium, pyb2d physics games, JavaScript and p5.js), sample data, two extra themes (Night, Miami Nights) and French and Simplified Chinese language packs.

## How Tofu runs it

- Framework preset: **static**.
- Root folder: **`site`**, the finished site. `site/index.html` sends visitors to JupyterLab at `/lab/index.html`; the Notebook interface is at `/tree/index.html` and `/notebooks/`, and there are `/repl/`, `/consoles/` and `/edit/` pages.
- Install command: none. Build command: none. Output directory: `site` itself, served as it is.
- Environment variables: none. Database: none.

`site/` is built here because Tofu cannot run the Python toolchain that builds it. To rebuild it for a new pin, from the repository root:

```sh
python3.11 -m venv ../jupyterlite-venv && . ../jupyterlite-venv/bin/activate
python -m pip install -r requirements.txt && python -m pip install -r tofu/requirements-tofu.txt
./tofu/build-site.sh
git add -f site   # upstream's .gitignore ignores a top-level site/ folder
```

## What we changed and why

Everything is on the `tofu` branch and lives in added files; no upstream file is edited.

1. **`site/`**: the output of `jupyter lite build`, the same build upstream's GitHub Pages workflow runs (`--contents content`, plus `README.md`, which the workflow copies into `content/`).
2. **`tofu/requirements-tofu.txt`**: raises `jupyterlite-core` from upstream's pinned 0.8.0 to 0.8.6, the newest release of the same 0.8 line. 0.8.0 ships the JupyterLab front end with three published advisories, all fixed in 0.8.4: GHSA-6966-vjj6-99xv (high: cross-site scripting through notebook cells pasted from the clipboard), GHSA-3jqq-pw4j-pqcj (cross-site scripting through a crafted language package) and GHSA-jwrc-gm9j-263p (command link trust prompt). Everything else is installed exactly as upstream's `requirements.txt` says (JupyterLab 4.6.4, Notebook 7.6.3, Pyodide kernel 0.8.0, JavaScript kernel 0.3.0, p5 kernel 0.3.0, the widget, plotting and map libraries). The site reports JupyterLite 0.8.6 and JupyterLab 4.6.4.
3. **`tofu/adapt_site.py`** (run by `tofu/build-site.sh`) makes the build importable:
   - Renames `build/` to `built/`. Tofu's GitHub import drops every path with a folder named `build`, and that is where JupyterLite keeps its whole app (about 600 files of JavaScript, settings schemas and themes). The new name has the same length, so the source maps stay aligned.
   - Points the six app pages' bundle links and the `fullStaticUrl`, `settingsUrl` and `themesUrl` settings in the `jupyter-lite.json` files at `built/`.
   - Changes the one place the bundles name the folder themselves, the address of the Help > Licenses data: `URLExt.join(baseUrl, "build", "third-party-licenses.json")` becomes `"built"` in `site/built/981.*.js` and in `site/extensions/@jupyterlite/pyodide-kernel-extension/static/854.*.js` (one word in each; both are BSD-3-Clause JupyterLite code).
   - Removes the bundle sources in `tree/build/`, `edit/build/`, `consoles/build/` and `notebooks/build/` and the rspack project at the top of the output (`package.json` with a `build` script, `rspack.config*.js`). The running site never loads them, and a top-level `package.json` with a build script would make Tofu treat the folder as one to build.
   - Copies this repository's `LICENSE` to `site/LICENSE`, and the licence files of the 21 Python packages whose files the site ships to `site/LICENSES/<package>-<version>/`.
4. **`tofu/build-site.sh`** rebuilds `site/` in one step, and this **`TOFU.md`**.

Kept unchanged: the JupyterLite name, logo, favicons, themes, and every upstream notebook and data file.

## What it connects to at runtime

No analytics, tracking or advertising (the built bundles were searched; the only matches were an icon name and unrelated words), no Tofu account and no key. The public services it calls:

- **cdn.jsdelivr.net**: when a Python kernel starts, Pyodide v314.0.0 loads from `https://cdn.jsdelivr.net/pyodide/v314.0.0/full/`, including the WebAssembly runtime, Python's standard library and Pyodide's prebuilt packages (NumPy, Matplotlib, pandas and others). None of these are in this site. The p5.js kernel loads p5.js 1.9.0 from cdn.jsdelivr.net.
- **pypi.org and files.pythonhosted.org**: `%pip install` and `piplite.install` in a notebook fetch packages that neither this site nor Pyodide bundles, and several sample notebooks do this. The site itself bundles only the kernel's own wheels (`site/extensions/@jupyterlite/pyodide-kernel-extension/static/pypi/`).
- **tile.openstreetmap.org**: map tiles for ipyleaflet, folium and the GeoJSON viewer.
- **cdn.plot.ly and unpkg.com**: Plotly's map charts load map outlines and icons from them.
- **raw.githubusercontent.com, httpbin.org and s3-eu-west-1.amazonaws.com**: some sample notebook cells read example data from these when someone runs them. The logo at the top of `python.ipynb` points to a raw.githubusercontent.com path that now answers 404, so it shows as a broken image (upstream content, left as is).

Without internet access the interface still opens and the JavaScript kernel works, but the Python kernel cannot start.

## Upstream and licence

- Upstream: <https://github.com/jupyterlite/demo>, branch `main`, commit `0b56844ad3965ecfc201eaa59de45831eed44334` ("Update to JupyterLite 0.8.0 (#167)", 2026-06-25).
- Fork: <https://github.com/tofu-gallery/jupyterlite>. `main` mirrors upstream; `tofu` holds the adaptation; tag `pin/2026-10-23` marks the pinned commit.
- Licence: BSD-3-Clause, Copyright (c) 2026, Project Jupyter. The root `LICENSE` is unchanged; `site/LICENSE` is a copy.
- The built site also contains JupyterLite, JupyterLab, Jupyter Notebook, the kernels, themes, language packs and widget extensions (BSD-3-Clause, MIT and similar; their licence files are in `site/LICENSES/`) and the npm packages they bundle. Those 300 packages are listed with their licences in `site/built/third-party-licenses.json`, which Help > Licenses shows, and each extension carries its own `static/third-party-licenses.json` or `*.LICENSE.txt`. Notable: Font Awesome Free 5.15.4 (icons CC-BY-4.0, fonts SIL OFL-1.1, code MIT); elkjs 0.9.3 under EPL-2.0, a weak copyleft licence, shipped unmodified, with its source at <https://github.com/kieler/elkjs>; DOMPurify 3.4.10 (MPL-2.0 or Apache-2.0).
- Pyodide (MPL-2.0) and the Python packages it loads are not in this repository; they come from jsDelivr and PyPI at runtime under their own licences.
- "Jupyter", "JupyterLab", "JupyterLite" and the Jupyter logo are Project Jupyter's trademarks. They appear unchanged as the app's own name and logo; a gallery listing should not suggest that Project Jupyter endorses Tofu.
- The sample notebooks and data files (`content/`, copied into `site/files/`) are upstream's, as is.

## Verification

Run on 2026-10-23 on macOS (arm64) with Python 3.11.15. Nothing was deployed.

1. `python3.11 -m venv /private/tmp/gallery-tools/jupyterlite/venv`, then `pip install -r requirements.txt` and `pip install -r tofu/requirements-tofu.txt`: installed; `pip check` found no broken requirements.
2. `./tofu/build-site.sh`: exit 0. `site/` has 1,068 files (80 MB), and a local scan with Tofu's import filter drops none of them.
3. Copied `site/` with `rsync -a --exclude node_modules --exclude dist --exclude build --exclude target --exclude .cache` (the copy is identical to `site/`) and served it with `python3 -I -m http.server 49359 --bind 127.0.0.1`. `curl` returned HTTP 200 for `/`, `/lab/index.html`, `/built/lab/bundle.js`, `/built/third-party-licenses.json`, `/tree/index.html` and `/notebooks/index.html`.
4. Browser check (a fresh tab on 127.0.0.1 only):
   - `/` redirected to `/lab/index.html`, and JupyterLab's launcher appeared in 4.0 s with the Python (Pyodide), JavaScript (Web Worker) and p5.js kernels.
   - A new Python (Pyodide) notebook ran `1+1` and printed `2` (prompt `[1]`), 11 s after Shift+Enter including Pyodide's download from jsDelivr.
   - Help > Licenses opened and loaded `/built/third-party-licenses.json` (HTTP 200).
   - `/notebooks/index.html?path=python.ipynb` opened the bundled sample notebook in the Notebook interface with the Python (Pyodide) kernel.
   - Console errors: none. Failed requests seen by the page: none.
   - The first build (jupyterlite-core 0.8.0) passed the same checks, plus the file list at `/tree/index.html` and every extension's licence file loading in Help > Licenses.
5. `python3 -I simulate_import.py --one tofu-gallery/jupyterlite tofu site yes` against the pushed `tofu` branch (commit `2d5e718`): 1,068 files kept, 0 dropped, no missing references.
6. GitHub's archive of that commit (`codeload.github.com/.../legacy.zip`): 20,130,804 bytes (limit 50 MB); 1,102 files in the tree (limit 20,000); 81.9 MB unpacked (limit 250 MB). Adding this file changes those numbers by a few kilobytes.
