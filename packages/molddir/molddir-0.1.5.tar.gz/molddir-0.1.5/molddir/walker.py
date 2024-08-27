from contextlib import contextmanager
import logging
import os
from copy import deepcopy
from fnmatch import fnmatch
import platform
import re
import subprocess
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

    def __init__(self, codebase_path: str, escape: Optional[str] = None, incremental: bool = False):
        if not os.path.exists(codebase_path):
            raise FileNotFoundError(f"Path {codebase_path} does not exist")
        self._codebase_path = codebase_path
        self._incremental = incremental
        escape_ = None if escape is None else escape.split(",")
        self._ignore_list = set(deepcopy(ESCAPE)) if escape_ is None else set(deepcopy(ESCAPE + escape_))
        self._current_paths = []
        self._index = 0
        self._populate_gitignore()
        self._populate_paths()

    def _populate_gitignore(self):
        gitignore_path = os.path.join(self._codebase_path, ".gitignore")
        if not os.path.exists(gitignore_path):
            logger.debug(f"Gitignore file not found at {self._codebase_path}")
            return
        lines = []
        with open(gitignore_path, "r") as file:
            lines = file.readlines()

        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                self._ignore_list.add(line)

    def _get_all_files(self):
        for root, dirs, files in os.walk(self._codebase_path):
            dirs_t = []
            for item in dirs:
                item_path = os.path.normpath(os.path.join(root, item))
                if self._should_ignore(item_path):
                    logger.debug(f"Ignoring directory: {item}")
                else:
                    dirs_t.append(item)
            dirs[:] = dirs_t
            if self._should_ignore(root):
                logger.debug(f"Ignoring directory: {root}")
                continue
            for item in files:
                file_path = os.path.normpath(os.path.join(root, item))
                if self._should_ignore(file_path):
                    logger.debug(f"Ignoring file: {item}")
                else:
                    self._current_paths.append(file_path)

    @contextmanager
    def _cd_to_codebase(self):
        previous_path = os.getcwd()
        os.chdir(self._codebase_path)
        try:
            yield
        finally:
            os.chdir(previous_path)

    def _get_incremenal_path(self):
        if not self.is_git_enabled():
            return
        cmd = ["git", "diff", "--name-only", "HEAD"]
        with self._cd_to_codebase():
            result = subprocess.run(
                cmd,
                shell=True if platform.system().lower() == "windows" else False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
            )
            stdout_ = result.stdout.strip() if isinstance(result.stdout, str) else result.stdout
            stderr_ = result.stderr.strip() if isinstance(result.stderr, str) else result.stderr
            if stderr_:
                logger.error("Error While excuting the Git Command")
                logger.error(stderr_)
            pattern = re.compile(r"^(.*)$", re.MULTILINE)
            for match in pattern.findall(stdout_):
                filename = os.path.join(self._codebase_path, match.strip())
                if self._should_ignore(filename):
                    logger.debug(f"Ignoring file: {match.strip()}")
                else:
                    self._current_paths.append(filename)

    def _populate_paths(self):
        if self._incremental:
            self._get_incremenal_path()
        else:
            self._get_all_files()

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
