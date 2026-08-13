#!/usr/bin/env python3
"""Enrich a CityJSON 2.0 file with a Dynamizer SensorConnection.

The input geometry, vertices, semantics, metadata, and existing attributes are
preserved. Only the Dynamizer extension declaration, one target attribute, one
inverse link, and one +Dynamizer CityObject are added.
"""

import argparse
import json
from pathlib import Path


BUILDING_ID = "DEBY_LOD2_4959457"
DYNAMIZER_ID = "dynamizer-frost-temperature-datastream-1"
EXTENSION_URL = (
    "https://raw.githubusercontent.com/JEDDOUB/cityjson-dynamizer-extension/refs/tags/v2.0.0/dynamizer.ext.json"
)
FROST_BASE = "https://gi3.gis.lrg.tum.de/frost/v1.1"


def enrich(data: dict) -> dict:
    if data.get("type") != "CityJSON" or data.get("version") != "2.0":
        raise ValueError("The input must be a CityJSON 2.0 document.")
    cityobjects = data.get("CityObjects")
    if not isinstance(cityobjects, dict) or BUILDING_ID not in cityobjects:
        raise KeyError(f"Target building not found: {BUILDING_ID}")

    extensions = data.setdefault("extensions", {})
    extensions["dynamizer"] = {
        "url": EXTENSION_URL,
        "version": "2.0.0",
    }

    building = cityobjects[BUILDING_ID]
    attributes = building.setdefault("attributes", {})
    attributes["temperature"] = 19.8
    attributes["temperatureMetadata"] = {
        "uom": "Cel",
        "observationProperty": "Temperature",
        "source": f"{FROST_BASE}/Datastreams(1)",
        "accessMode": "live-sensor-connection",
        "thingID": "1",
        "locationID": "1",
        "locationName": "TUM Room 0126",
    }
    inverse = attributes.setdefault("+dynamizer", [])
    if DYNAMIZER_ID not in inverse:
        inverse.append(DYNAMIZER_ID)

    cityobjects[DYNAMIZER_ID] = {
        "type": "+Dynamizer",
        "attributes": {
            "target": BUILDING_ID,
            "attributeRef": "/attributes/temperature",
            "sensorConnection": {
                "connectionType": {
                    "code": "OGC.SensorThings",
                    "codeSpace": "https://www.ogc.org/standard/sensorthings/",
                },
                "observationProperty": (
                    "http://www.qudt.org/qudt/owl/1.0.0/quantity/"
                    "Instances.html#ThermodynamicTemperature"
                ),
                "uom": "Cel",
                "sensorID": "5",
                "sensorName": "Grove BME680",
                "datastreamID": "1",
                "baseURL": FROST_BASE,
                "authType": "none",
                "linkToObservation": f"{FROST_BASE}/Datastreams(1)/Observations",
                "linkToSensorDescription": f"{FROST_BASE}/Sensors(5)",
                "sensorLocation": BUILDING_ID,
            },
        },
    }
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="Original CityJSON file")
    parser.add_argument("output", type=Path, help="Enriched CityJSON file")
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    enriched = enrich(data)
    args.output.write_text(
        json.dumps(enriched, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
