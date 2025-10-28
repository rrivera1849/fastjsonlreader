import json
import os
from typing import List, Optional

def default_cache_dir() -> str:
    return os.path.join(os.path.expanduser("~"), ".fastjsoncache")

def _cache_filename(file_path: str, cache_dir: str, num_lines: Optional[int]) -> str:
    name = os.path.basename(file_path)
    if num_lines is not None:
        return os.path.join(cache_dir, f"{name}.bcl.{num_lines}")
    return os.path.join(cache_dir, f"{name}.bcl")

def build_cache(
    file_path: str,
    cache_dir: Optional[str] = None,
    num_lines: Optional[int] = None,
    force: bool = False,
) -> str:
    """
    Build the BCL (byte-count lookup) cache for `file_path`.

    Returns the path to the cache file.
    """
    cache_dir = cache_dir or default_cache_dir()
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = _cache_filename(file_path, cache_dir, num_lines)

    if (not force) and os.path.exists(cache_path):
        return cache_path

    bcl: List[int] = []
    ii = 0
    with open(file_path, "r", encoding="utf-8") as fin:
        for line in fin:
            bcl.append(len(line.encode("utf-8")))
            ii += 1
            if num_lines is not None and ii >= num_lines:
                break
    with open(cache_path, "w", encoding="utf-8") as fout:
        fout.writelines(f"{x}\n" for x in bcl)

    return cache_path


class FastJSONLReader(object):
    """
    JSONL reader with a cached per-line byte count (.bcl) to enable fast random access.

    NOTE: For simplicity, this keeps per-line byte counts and computes the seek
    offset as sum(bcl[:index]). For huge files, we may consider switching to cumulative
    offsets stored on disk (one extra pass; O(1) seek).
    """

    def __init__(
        self,
        file_path: str,
        cache_dir: Optional[str] = None,
        num_lines: Optional[int] = None,
    ):
        self.file_path = file_path
        self.cache_dir = cache_dir or default_cache_dir()
        os.makedirs(self.cache_dir, exist_ok=True)

        # Prefer an existing cache; otherwise build it
        cache_path = _cache_filename(self.file_path, self.cache_dir, num_lines)
        if not os.path.exists(cache_path):
            build_cache(self.file_path, self.cache_dir, num_lines=num_lines)

        self._read_bcl(num_lines)

    def _get_cache_filename(self, num_lines: Optional[int]) -> str:
        return _cache_filename(self.file_path, self.cache_dir, num_lines)

    def _read_bcl(self, num_lines: Optional[int]) -> List[int]:
        self.bcl: List[int] = []
        with open(self._get_cache_filename(num_lines), "r", encoding="utf-8") as fin:
            for line in fin:
                self.bcl.append(int(line.strip()))
        return self.bcl

    def __getitem__(self, index: int):
        if index < 0 or index >= len(self.bcl):
            raise IndexError("Index out of bounds")
        # Compute byte offset by summing previous line byte lengths
        bytes_to_seek = sum(self.bcl[:index])
        with open(self.file_path, "r", encoding="utf-8") as fin:
            fin.seek(bytes_to_seek)
            line = fin.readline()
        return json.loads(line)

    def __len__(self) -> int:
        return len(self.bcl)

