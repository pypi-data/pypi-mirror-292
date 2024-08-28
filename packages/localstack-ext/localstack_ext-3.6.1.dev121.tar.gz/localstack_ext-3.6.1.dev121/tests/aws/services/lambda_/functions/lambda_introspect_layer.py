import re
import stat
from pathlib import Path


def handler(event, context):
    paths = [
        # Layers directory
        "/opt",
        "/opt/bin",
        "/opt/bin/true",
        "/opt/somedir",
        "/opt/somedir/somefile",
        "/opt/somefile-600",
        "/opt/somefile-755",
        "/opt/somefile-777",
        # Lambda code directory (affected by the presence of layers!)
        "/var/task",
        "/var/task/handler.py",
    ]
    path_details = {}
    for p in paths:
        path_label = re.sub("/", "_", p)
        path = Path(p)
        mode = None
        if path.exists():
            mode = stat.filemode(path.stat().st_mode)
        path_details[f"{path_label}_mode"] = mode

    return {
        "paths": path_details,
    }
