#!/usr/bin/env python3
"""Operational checks that complement cjval and JSON Schema validation.

For the repository examples, the script checks whether referenced IDs exist,
whether target-relative JSON Pointers resolve, whether composite-series cycles
are present, whether a Dynamizer is listed in its target-side inverse index
when that optional index exists, and whether bundled file resources can be
read. It does not verify the CityObject type of every referenced series or
perform network requests.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


def decode_pointer_token(token: str) -> str:
    return token.replace("~1", "/").replace("~0", "~")


def resolve_pointer(value, pointer: str):
    if pointer == "":
        return value
    if not pointer.startswith("/"):
        raise ValueError(f"JSON Pointer must be empty or start with '/': {pointer}")
    current = value
    for raw in pointer[1:].split("/"):
        token = decode_pointer_token(raw)
        if isinstance(current, list):
            current = current[int(token)]
        elif isinstance(current, dict):
            current = current[token]
        else:
            raise KeyError(f"Cannot descend through scalar at token {token!r}")
    return current


def referenced_series(obj: dict) -> list[str]:
    if obj.get("type") != "+CompositeTimeseries":
        return []
    return [
        component["timeseries"]
        for component in obj.get("attributes", {}).get("component", [])
        if "timeseries" in component
    ]


def check_cycles(cityobjects: dict) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(identifier: str) -> None:
        if identifier in visiting:
            raise ValueError(f"Composite timeseries cycle detected at {identifier}")
        if identifier in visited:
            return
        visiting.add(identifier)
        for child in referenced_series(cityobjects[identifier]):
            visit(child)
        visiting.remove(identifier)
        visited.add(identifier)

    for identifier, obj in cityobjects.items():
        if obj.get("type") == "+CompositeTimeseries":
            visit(identifier)


def check_external_resource(example: Path, obj: dict) -> None:
    attrs = obj.get("attributes", {})
    location = attrs.get("fileLocation")
    if not location:
        return
    resource = (example.parent / location).resolve()
    if not resource.is_file():
        raise FileNotFoundError(f"Missing resource: {resource}")
    if obj.get("type") == "+TabulatedFileTimeseries":
        separator = attrs.get("fieldSeparator", ",")
        with resource.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream, delimiter=separator)
            fields = set(reader.fieldnames or [])
            for key in ("timeColumnName", "valueColumnName"):
                column = attrs.get(key)
                if column and column not in fields:
                    raise ValueError(f"Column {column!r} not found in {resource}")
            if not list(reader):
                raise ValueError(f"No data rows in {resource}")
    elif obj.get("type") == "+StandardFileTimeseries":
        ET.parse(resource)


def validate(example: Path) -> None:
    document = json.loads(example.read_text(encoding="utf-8"))
    cityobjects = document["CityObjects"]

    for identifier, obj in cityobjects.items():
        attrs = obj.get("attributes", {})
        if obj.get("type") == "+Dynamizer":
            target_id = attrs["target"]
            if target_id not in cityobjects:
                raise KeyError(f"{identifier}: target does not resolve: {target_id}")
            resolve_pointer(cityobjects[target_id], attrs["attributeRef"])
            dynamic_id = attrs.get("dynamicData")
            if dynamic_id and dynamic_id not in cityobjects:
                raise KeyError(f"{identifier}: dynamicData does not resolve: {dynamic_id}")
            sensor = attrs.get("sensorConnection", {})
            location_id = sensor.get("sensorLocation")
            if location_id and location_id not in cityobjects:
                raise KeyError(f"{identifier}: sensorLocation does not resolve: {location_id}")
            inverse = cityobjects[target_id].get("attributes", {}).get("+dynamizer", [])
            if inverse and identifier not in inverse:
                raise ValueError(f"{identifier}: target inverse does not contain Dynamizer ID")

        for series_id in referenced_series(obj):
            if series_id not in cityobjects:
                raise KeyError(f"{identifier}: component does not resolve: {series_id}")
        check_external_resource(example, obj)

    check_cycles(cityobjects)


def main() -> None:
    examples = sorted(EXAMPLES.glob("0*.city.json"))
    if not examples:
        raise SystemExit("No numbered examples found.")
    for example in examples:
        validate(example)
        print(f"PASS {example.relative_to(ROOT)}")
    print(f"PASS {len(examples)} examples")


if __name__ == "__main__":
    main()
