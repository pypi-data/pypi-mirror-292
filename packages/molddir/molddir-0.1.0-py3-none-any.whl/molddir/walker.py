import logging
import os
from copy import deepcopy
from fnmatch import fnmatch
from typing import List, Optional

logger = logging.getLogger(__name__)


ESCAPE: List[str] = [
    ".git",
    "poetry.lock",
    ".vscode",
    ".idea",
    ".pytest_cache",
    ".mypy_cache",
    ".tox",
    ".ruff_cache",
    "node_modules",
    "package-lock.json",
    "yarn.lock",
    ".venv",
    ".cache",
    ".env",
]


class FolderWalker:
    _codebase_path: str

    def __init__(self, codebase_path: str, escape: Optional[str] = None):
        if not os.path.exists(codebase_path):
            raise FileNotFoundError(f"Path {codebase_path} does not exist")
        self._codebase_path = codebase_path
        escape_ = None if escape is None else escape.split(",")
        self._ignore_list = set(deepcopy(ESCAPE)) if escape_ is None else set(deepcopy(ESCAPE + escape_))
        self._current_paths = []
        self._index = 0
        self._populate_gitignore()
        self._populate_paths()

    def _populate_gitignore(self):
        gitignore_path = os.path.join(self._codebase_path, ".gitignore")
        if not os.path.exists(gitignore_path):
            logger.info(f"Gitignore file not found at {self._codebase_path}")
            return
        lines = []
        with open(gitignore_path, "r") as file:
            lines = file.readlines()

        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                self._ignore_list.add(line)

    def _populate_paths(self):
        for root, dirs, files in os.walk(self._codebase_path):
            dirs_t = []
            for item in dirs:
                item_path = os.path.normpath(os.path.join(root, item))
                if self._should_ignore(item_path):
                    logger.info(f"Ignoring directory: {item}")
                else:
                    dirs_t.append(item)
            dirs[:] = dirs_t
            if self._should_ignore(root):
                logger.info(f"Ignoring file: {root}")
                continue
            for item in files:
                file_path = os.path.normpath(os.path.join(root, item))
                if self._should_ignore(file_path):
                    logger.info(f"Ignoring file: {file_path}")
                else:
                    self._current_paths.append(file_path)

    def _should_ignore(self, path: str) -> bool:
        relative_path = os.path.relpath(path, self._codebase_path)
        for pattern in self._ignore_list:
            if self._match_pattern(relative_path, pattern):
                return True
        return False

    def _match_pattern(self, relative_path: str, pattern: str) -> bool:
        if pattern.endswith("/"):
            return fnmatch(relative_path, f"*{pattern}*")
        if "*" in pattern:
            return fnmatch(relative_path, pattern)
        return relative_path == pattern

    def should_ignore(self, item: str) -> bool:
        return self._should_ignore(item)

    def is_git_enabled(self) -> bool:
        return os.path.exists(os.path.join(self._codebase_path, ".git"))

    def has_gitignore(self) -> bool:
        return os.path.exists(os.path.join(self._codebase_path, ".gitignore"))

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index < len(self._current_paths):
            result = self._current_paths[self._index]
            self._index += 1
            return result
        else:
            raise StopIteration


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # codebase_path_ = "C:/Users/rahul.das05/OneDrive - Infosys Limited/workspace/aiforui/agentnet/"
    codebase_path_ = "/Users/mac_admin/rahul/agent_net"
    ignore = FolderWalker(codebase_path_)
    # print(ignore._ignore_list)
    for item in ignore:
        print(item)
