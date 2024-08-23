import json
from typing import Any, Dict, List, Union
from ..server.http import create_app
from pathlib import Path


def remove_title_next_to_ref(
    schema_node: Union[Dict[str, Any], List[Any]],
) -> Union[Dict[str, Any], List[Any]]:
    """
    Recursively remove 'title' from schema components that have a '$ref'.
    This function addresses a non-compliance issue in FastAPI's OpenAPI schema generation, where
    'title' fields adjacent to '$ref' fields can cause validation problems with some OpenAPI tools.
    """
    if isinstance(schema_node, dict):
        if "$ref" in schema_node and "title" in schema_node:
            del schema_node["title"]
        for _key, value in schema_node.items():
            remove_title_next_to_ref(value)
    elif isinstance(schema_node, list):  # type: ignore[reportUnnecessaryIsInstance]
        for i, item in enumerate(schema_node):
            schema_node[i] = remove_title_next_to_ref(item)
    return schema_node


if __name__ == "__main__":
    schema = {}
    app = create_app(path=Path.cwd(),auth=None)
    print(json.dumps(app.openapi(), indent=2))
