import os
import glob
from typing import Optional

def find_latest_transect_file(base_dir: Optional[str] = None,
                              pattern: str = "TRANSECT DATA SUMMARY *.xlsx") -> Optional[str]:
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    search_dirs = []
    if base_dir:
        search_dirs.append(base_dir)
    search_dirs += [os.path.join(repo_dir, "data"), repo_dir]

    candidates = []
    for d in search_dirs:
        if not os.path.isdir(d):
            continue
        candidates += glob.glob(os.path.join(d, pattern))
    if not candidates:
        return None
    return os.path.abspath(max(candidates, key=os.path.getmtime))