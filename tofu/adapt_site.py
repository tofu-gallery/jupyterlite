"""Make the output of `jupyter lite build` importable and servable by Tofu. Run by tofu/build-site.sh.

Tofu's GitHub import drops every path that has a folder named `build` in it, and its static lane reads a
package.json with a build script as a site it has to build. JupyterLite's output has both: the app's
JavaScript lives in `build/`, each app's bundle sources sit in `<app>/build/`, and the rspack project
that made the bundles (package.json, rspack.config*.js) sits at the top. This script:

1. renames `build/` to `built/` (same length, so the source maps of the patched chunks stay aligned);
2. points each app page's bundle link and the `fullStaticUrl`/`settingsUrl`/`themesUrl` settings at it;
3. patches the one URL the bundles build by hand (the Help > Licenses data file);
4. removes the bundle sources and the rspack project files, which the running site never loads;
5. copies the licences of the packages whose files the site ships into `LICENSE` and `LICENSES/`.

Usage: python -I tofu/adapt_site.py site   (with the Python environment that ran the build)
"""
import pathlib
import re
import shutil
import sys
from importlib import metadata

OLD, NEW = 'build', 'built'
site = pathlib.Path(sys.argv[1])
repo = pathlib.Path(__file__).resolve().parent.parent
if not (site / OLD).is_dir() or (site / NEW).exists():
    sys.exit(f'{site}: expected a fresh `jupyter lite build` output with {OLD}/ and no {NEW}/')

# 1. the app bundles
(site / OLD).rename(site / NEW)

# 2. each app's page preloads ../build/<app>/bundle.js; the settings name the folder too
for page in sorted(site.glob('*/index.html')):
    text = page.read_text(encoding='utf-8')
    new, n = re.subn(r'(<link id="jupyter-lite-main"[^>]*href="\.\./)' + OLD + '/', r'\g<1>' + NEW + '/', text)
    if n:
        page.write_text(new, encoding='utf-8')
        print(f'page     {page.relative_to(site)}')
setting = re.compile(r'("(?:fullStaticUrl|settingsUrl|themesUrl)"\s*:\s*"(?:\.\.?/)?)' + OLD + r'(?=[/"])')
for cfg in sorted([*site.glob('jupyter-lite.*'), *site.glob('*/jupyter-lite.*')]):
    if cfg.suffix not in ('.json', '.ipynb'):
        continue
    text = cfg.read_text(encoding='utf-8')
    new, n = setting.subn(r'\g<1>' + NEW, text)
    if n:
        cfg.write_text(new, encoding='utf-8')
        print(f'settings {cfg.relative_to(site)} ({n})')

# 3. the licences client fetches URLExt.join(baseUrl, "build", "third-party-licenses.json")
licences_url = '.getBaseUrl(),"' + OLD + '",'
patched = 0
for chunk in sorted([*(site / NEW).glob('*.js'), *(site / 'extensions').rglob('*.js')]):
    text = chunk.read_text(encoding='utf-8')
    if licences_url in text:
        chunk.write_text(text.replace(licences_url, '.getBaseUrl(),"' + NEW + '",'), encoding='utf-8')
        patched += 1
        print(f'chunk    {chunk.relative_to(site)}')
if not any(licences_url.replace(OLD, NEW) in c.read_text(encoding='utf-8') for c in (site / NEW).glob('*.js')):
    sys.exit('the licences URL was not found in the app bundles: check the JupyterLite version')

# 4. bundle sources (<app>/build/) and the rspack project at the top
for folder in sorted(p for p in site.rglob(OLD) if p.is_dir()):
    shutil.rmtree(folder)
    print(f'removed  {folder.relative_to(site)}/')
for name in ('package.json', 'rspack.config.js', 'rspack.config.analyze.js', 'rspack.config.watch.js'):
    if (site / name).exists():
        (site / name).unlink()
        print(f'removed  {name}')

# 5. licences: this repository's, then each package that puts files into the site
shutil.copyfile(repo / 'LICENSE', site / 'LICENSE')
shipped = []
for dist in metadata.distributions():
    name = dist.metadata['Name']
    files = [str(f) for f in (dist.files or [])]
    if not (any('share/jupyter/labextensions/' in f for f in files)
            or name.lower() in ('jupyterlite-core', 'jupyterlab')
            or name.lower().startswith('jupyterlab-language-pack-')):
        continue
    for f in files:
        base = f.split('/')[-1]
        if '.dist-info/' in f and re.match(r'(LICEN[CS]E|COPYING|NOTICE)', base, re.I):
            dest = site / 'LICENSES' / f'{name}-{dist.version}' / base
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(dist.locate_file(f), dest)
    shipped.append(f'{name} {dist.version}')
print('licences', ', '.join(sorted(shipped, key=str.lower)))
