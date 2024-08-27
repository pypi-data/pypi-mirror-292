import os
import json
import re
from typing import Any, Dict, List, Union

JSONType = Union[Dict[str, Any], List[Any]]


def remove_comments_from_json(content: str) -> str:
    cleaned_content = re.sub(r"//.*?(?=\n)|/\*.*?\*/", "", content, flags=re.DOTALL)
    return cleaned_content


def get_path_level(path: str) -> int:
    return path.count(os.sep)


def load_safe_json(file_path: str) -> JSONType:
    with open(file_path, "r") as file:
        content = file.read()
        content = remove_comments_from_json(content)
        return json.loads(content)
