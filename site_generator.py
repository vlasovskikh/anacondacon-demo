import os
import re
from logging import info
from pprint import pprint
from typing import Iterable, Dict, Any, Callable, Optional
from urllib.request import pathname2url

loaders = []


def merge(x1, x2):
    if isinstance(x1, dict) and isinstance(x2, dict):
        res = x1.copy()
        for k, v in x2.items():
            if k in res:
                res[k] = merge(res[k], v)
            else:
                res[k] = v
        return res
    elif isinstance(x1, list) and isinstance(x2, list):
        res = list(x1)
        res.extend(x2)
        return res
    elif x1 == x2:
        return x1
    else:
        raise ValueError(f"Cannot merge '{x1!r}' and '{x2!r}'")


def write_greeting(path: str) -> None:
    with open(path, mode='wb') as fd:
        # TODO: Write the actual greeting to the file
        pass


def load_site_files(paths: Iterable[str],
                    config: Dict[str, Any]) -> Dict[str, Any]:
    source = config['source']
    info('Loading source files...')
    site = config.copy()
    n = 0
    for path in paths:
        rel_path = os.path.relpath(path, source)
        for f in loaders:
            data = f(rel_path, site)
            if data:
                n += 1
                site = merge(site, data)
                break
    info(f'Loaded {n} files')
    return site


def load_site(config: Dict[str, Any]) -> Dict[str, Any]:
    paths = all_source_files(config['source'], config['destination'])
    return load_site_files(paths, config)


def all_source_files(source: str, destination: str) -> Iterable[str]:
    dst_base, dst_name = os.path.split(os.path.realpath(destination))
    for source, dirs, files in os.walk(source):
        if os.path.realpath(source) == dst_base and dst_name in dirs:
            dirs.remove(dst_name)
        for filename in files:
            yield os.path.join(source, filename)


def loader(f: Callable[[str, dict], dict]) -> Any:
    """Register a site source content loader."""
    loaders.insert(0, f)
    return f


@loader
def load_file(path: str, _config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    return {
        'files': [{'url': path2url(path), 'path': path}],
    }


def path2url(path: str) -> str:
    m = re.match(r'(.*)[/\\]index.html?$', path)
    if m:
        path = m.group(1) + os.path.sep
    path = os.path.sep + path
    return pathname2url(path.encode('utf-8'))


def main():
    pprint(load_site({'source': '.', 'destination': '.'}))


if __name__ == '__main__':
    main()
