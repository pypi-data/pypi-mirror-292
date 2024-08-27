import os.path
import re
from os import getcwd, walk

WIKI_PATTERN = re.compile(r"\[\[ *(.+?) *\| *(.+?) *\]\]")


def get_links(content: str):
    links = WIKI_PATTERN.findall(content)
    return [l for l, _ in links]


def fetch_context(filename: str) -> list[tuple[str, str]]:
    all_files = get_all_files()
    result = []
    visited = set()

    def DFS(name: str):
        if name in visited:
            return
        visited.add(name)
        with open(name) as f:
            content = f.read()
            links = get_links(content)
            for link in links:
                if link in all_files:
                    DFS(all_files[link])
        result.append((name, content))

    DFS(filename)
    return result


def get_all_files():
    result = {}
    for root, _, filenames in walk(getcwd()):
        for name in filenames:
            result[name] = os.path.join(root, name)

    return result
