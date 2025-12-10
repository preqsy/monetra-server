from sqlalchemy.inspection import inspect
import json
from pathlib import Path


def read_from_config_json(json_key):
    path = Path.cwd() / "config.json"
    json_data = path.read_text()
    data_dict = json.loads(json_data)
    return data_dict[json_key]


def get_default_categories():
    return read_from_config_json("default_categories")


def convert_sql_models_to_dict(obj, visited=None) -> dict:
    """Convert a SQLAlchemy model instance to a dictionary, including relationships."""
    if visited is None:
        visited = set()

    obj_id = id(obj)
    if obj_id in visited:
        return None
    visited.add(obj_id)

    result = {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}

    for relationship in inspect(obj).mapper.relationships:
        # Check if the relationship is already loaded
        if relationship.key in obj.__dict__:
            related_obj = getattr(obj, relationship.key)
            if related_obj is not None:
                if relationship.uselist:
                    result[relationship.key] = [
                        convert_sql_models_to_dict(item, visited)
                        for item in related_obj
                    ]
                else:
                    result[relationship.key] = convert_sql_models_to_dict(
                        related_obj, visited
                    )

    return result


def extract_beneficiary(narration: str) -> str:
    """
    Extracts the beneficiary from Mono bank transaction narration.
    Example narration: "NIP/KUDA/SAMUEL OLAMIDE/TRANSFER 14"
    Returns: "SAMUEL OLAMIDE"
    """
    # print("***********Narration:", narration)
    try:
        parts = narration.split("/")
        if len(parts) >= 3:
            return parts[2].strip().lower()
    except Exception:
        pass
    # print("***********Narration:", narration)
    return narration


# print(extract_beneficiary("NIP/KUDA/SAMUEL/TRANSFER 14"))
