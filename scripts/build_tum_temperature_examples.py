import copy
import json
import shutil
import textwrap
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "examples" / "DEBY_LOD2_4959457.original.city.json"
SCHEMA = ROOT / "dynamizer.ext.json"
PACKAGE = ROOT / "generated_tum_temperature_examples_v2.0.0"
EXAMPLES = PACKAGE / "examples"
DATA = PACKAGE / "data"
BUILDING_ID = "DEBY_LOD2_4959457"
EXTENSION_URL = "https://raw.githubusercontent.com/JEDDOUB/cityjson-dynamizer-extension/refs/tags/v2.0.0/dynamizer.ext.json"
FROST_BASE = "https://gi3.gis.lrg.tum.de/frost/v1.1"

OBSERVATIONS = [
    ("2025-08-27T06:58:22.758Z", 19.8),
    ("2025-08-27T07:03:28.020Z", 20.0),
    ("2025-08-27T07:08:33.278Z", 20.1),
    ("2025-08-27T07:13:38.538Z", 20.1),
]


def base_document(dynamizer_id):
    data = copy.deepcopy(json.loads(SOURCE.read_text(encoding="utf-8")))
    data.setdefault("extensions", {})["dynamizer"] = {
        "url": EXTENSION_URL,
        "version": "2.0.0",
    }
    attrs = data["CityObjects"][BUILDING_ID].setdefault("attributes", {})
    attrs["temperature"] = OBSERVATIONS[0][1]
    attrs["temperatureMetadata"] = {
        "observationProperty": "Temperature",
        "uom": "Cel",
        "sourceDatastream": f"{FROST_BASE}/Datastreams(1)",
        "thingID": "1",
        "locationID": "1",
        "locationName": "TUM Room 0126",
    }
    attrs["+dynamizer"] = [dynamizer_id]
    return data


def dynamizer(dynamizer_id, dynamic_data=None, sensor_connection=None):
    attrs = {
        "target": BUILDING_ID,
        "attributeRef": "/attributes/temperature",
    }
    if dynamic_data is not None:
        attrs.update({
            "startTime": OBSERVATIONS[0][0],
            "endTime": OBSERVATIONS[-1][0],
            "dynamicData": dynamic_data,
        })
    if sensor_connection is not None:
        attrs["sensorConnection"] = sensor_connection
    return {"type": "+Dynamizer", "attributes": attrs}


def generic_series(points):
    return {
        "type": "+GenericTimeseries",
        "attributes": {
            "firstTimestamp": points[0][0],
            "lastTimestamp": points[-1][0],
            "observationProperty": "Temperature",
            "uom": "Cel",
            "valueType": "double",
            "timeValuePair": [
                {"timestamp": timestamp, "doubleValue": value}
                for timestamp, value in points
            ],
        },
    }


def write_example(name, data):
    EXAMPLES.mkdir(parents=True, exist_ok=True)
    (EXAMPLES / name).write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def build():
    if PACKAGE.exists():
        shutil.rmtree(PACKAGE)
    EXAMPLES.mkdir(parents=True)
    DATA.mkdir(parents=True)

    # 1. GenericTimeseries: independent series; TimeValuePair records embedded.
    data = base_document("dyn-temperature-generic")
    data["CityObjects"]["dyn-temperature-generic"] = dynamizer(
        "dyn-temperature-generic", "series-temperature-generic"
    )
    data["CityObjects"]["series-temperature-generic"] = generic_series(OBSERVATIONS)
    write_example("01-generic-embedded-time-value-pairs.city.json", data)

    # 2. TabulatedFileTimeseries: values reside in a CSV table.
    data = base_document("dyn-temperature-tabulated")
    data["CityObjects"]["dyn-temperature-tabulated"] = dynamizer(
        "dyn-temperature-tabulated", "series-temperature-tabulated"
    )
    data["CityObjects"]["series-temperature-tabulated"] = {
        "type": "+TabulatedFileTimeseries",
        "attributes": {
            "firstTimestamp": OBSERVATIONS[0][0],
            "lastTimestamp": OBSERVATIONS[-1][0],
            "observationProperty": "Temperature",
            "uom": "Cel",
            "fileLocation": "../data/temperature.csv",
            "fileType": "CSV",
            "mimeType": "text/csv",
            "valueType": "double",
            "numberOfHeaderLines": 1,
            "fieldSeparator": ",",
            "decimalSymbol": ".",
            "timeColumnName": "timestamp",
            "valueColumnName": "temperature",
        },
    }
    write_example("02-tabulated-file-timeseries.city.json", data)

    # 3. StandardFileTimeseries: values reside in OGC TimeseriesML 1.2 XML.
    data = base_document("dyn-temperature-standard")
    data["CityObjects"]["dyn-temperature-standard"] = dynamizer(
        "dyn-temperature-standard", "series-temperature-standard"
    )
    data["CityObjects"]["series-temperature-standard"] = {
        "type": "+StandardFileTimeseries",
        "attributes": {
            "firstTimestamp": OBSERVATIONS[0][0],
            "lastTimestamp": OBSERVATIONS[-1][0],
            "observationProperty": "Temperature",
            "uom": "Cel",
            "fileLocation": "../data/temperature-timeseriesml.xml",
            "fileType": {
                "code": "TimeseriesML-1.2",
                "codeSpace": "https://docs.ogc.org/is/15-042r5/15-042r5.html",
            },
            "mimeType": "application/xml",
        },
    }
    write_example("03-standard-file-timeseries.city.json", data)

    # 4. CompositeTimeseries: two concrete embedded series form one series.
    data = base_document("dyn-temperature-composite")
    data["CityObjects"]["dyn-temperature-composite"] = dynamizer(
        "dyn-temperature-composite", "series-temperature-composite"
    )
    data["CityObjects"]["series-temperature-part-a"] = generic_series(OBSERVATIONS[:2])
    data["CityObjects"]["series-temperature-part-b"] = generic_series(OBSERVATIONS[2:])
    data["CityObjects"]["series-temperature-composite"] = {
        "type": "+CompositeTimeseries",
        "attributes": {
            "firstTimestamp": OBSERVATIONS[0][0],
            "lastTimestamp": OBSERVATIONS[-1][0],
            "component": [
                {"repetitions": 1, "timeseries": "series-temperature-part-a"},
                {"repetitions": 1, "timeseries": "series-temperature-part-b"},
            ],
        },
    }
    write_example("04-composite-timeseries.city.json", data)

    # 5. SensorConnection: observations remain remote in FROST.
    data = base_document("dyn-temperature-sensor")
    data["CityObjects"]["dyn-temperature-sensor"] = dynamizer(
        "dyn-temperature-sensor",
        sensor_connection={
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
    )
    write_example("05-sensor-connection.city.json", data)

    (DATA / "temperature.csv").write_text(
        "timestamp,temperature\n" + "".join(
            f"{timestamp},{value:.1f}\n" for timestamp, value in OBSERVATIONS
        ),
        encoding="utf-8",
    )

    points = "\n".join(
        f"""  <tsml:point>
    <tsml:MeasurementTVP>
      <tsml:time>{timestamp}</tsml:time>
      <tsml:value>{value:.1f}</tsml:value>
    </tsml:MeasurementTVP>
  </tsml:point>"""
        for timestamp, value in OBSERVATIONS
    )
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<tsml:TimeseriesTVP
  xmlns:tsml="http://www.opengis.net/timeseriesml/1.2"
  xmlns:gml="http://www.opengis.net/gml/3.2"
  xmlns:xlink="http://www.w3.org/1999/xlink"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.opengis.net/timeseriesml/1.2 https://schemas.opengis.net/tsml/1.2/timeseriesML.xsd"
  gml:id="temperature-series-1">
  <gml:description>Temperature observations copied from FROST Datastream 1 for encoding comparison.</gml:description>
  <tsml:metadata>
    <tsml:TimeseriesMetadata>
      <tsml:temporalExtent>
        <gml:TimePeriod gml:id="temperature-period-1">
          <gml:beginPosition>{OBSERVATIONS[0][0]}</gml:beginPosition>
          <gml:endPosition>{OBSERVATIONS[-1][0]}</gml:endPosition>
        </gml:TimePeriod>
      </tsml:temporalExtent>
    </tsml:TimeseriesMetadata>
  </tsml:metadata>
  <tsml:defaultPointMetadata>
    <tsml:PointMetadata>
      <tsml:uom code="Cel"/>
      <tsml:interpolationType
        xlink:href="http://www.opengis.net/def/timeseries/InterpolationCode/Continuous"
        xlink:title="continuous"/>
    </tsml:PointMetadata>
  </tsml:defaultPointMetadata>
{points}
</tsml:TimeseriesTVP>
"""
    (DATA / "temperature-timeseriesml.xml").write_text(xml, encoding="utf-8")

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    schema["url"] = EXTENSION_URL
    (PACKAGE / "dynamizer.ext.json").write_text(
        json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    readme = """# Comparable temperature encodings with the CityJSON Dynamizer Extension

This package applies Dynamizer Extension 2.0.0 to the Munich TUM building
`DEBY_LOD2_4959457` and, where applicable, to the same four historical
observations from TUM FROST Datastream 1.

The FROST location for Thing 1 is TUM Room 0126, Arcisstr. 21, at
`11.568095, 48.149132`. That point falls inside the building's published 2D
extent. This is strong spatial evidence for the association, but it is not a
formal asset-management assertion about the sensor's exact mounting point.

## What “embedded” means

There is no concrete `EmbeddedTimeseries` class in the CityGML Dynamizer UML.
The embedded case is represented by `+GenericTimeseries`: the series is an
independent CityObject, while its small `TimeValuePair` records are embedded in
the series attributes.

## Comparison

| File | Encoding | Where the values live | Main use |
|---|---|---|---|
| `01-generic-embedded-time-value-pairs.city.json` | `+GenericTimeseries` | Inside embedded `timeValuePair` records | Self-contained exchange |
| `02-tabulated-file-timeseries.city.json` | `+TabulatedFileTimeseries` | `data/temperature.csv` | Existing CSV/table data |
| `03-standard-file-timeseries.city.json` | `+StandardFileTimeseries` | `data/temperature-timeseriesml.xml` | Standards-based XML exchange |
| `04-composite-timeseries.city.json` | `+CompositeTimeseries` | Two referenced `+GenericTimeseries` components | Joining/repeating series sections |
| `05-sensor-connection.city.json` | `SensorConnection` in `+Dynamizer` | Remotely in FROST Datastream 1 | Live or on-demand access |

Every file retains the original geometry, vertices, semantics, transform,
metadata, and attributes. The dynamic target is the numeric property
`/attributes/temperature`. The `target` relation is authoritative; the target
building's `+dynamizer` array is the optional derived inverse.

## Validation

From this directory, run:

```text
cjvalext dynamizer.ext.json
cjval examples/01-generic-embedded-time-value-pairs.city.json -e dynamizer.ext.json
cjval examples/02-tabulated-file-timeseries.city.json -e dynamizer.ext.json
cjval examples/03-standard-file-timeseries.city.json -e dynamizer.ext.json
cjval examples/04-composite-timeseries.city.json -e dynamizer.ext.json
cjval examples/05-sensor-connection.city.json -e dynamizer.ext.json
```

`cjval` checks the CityJSON and extension structures. Operational validation
must additionally open the CSV/XML/FROST resource, resolve IDs and the JSON
Pointer, check temporal ordering, and verify units.

## Python scripts

Create only the live SensorConnection example from an original building:

```text
python apply_frost_temperature.py DEBY_LOD2_4959457.original.city.json building_frost_temperature.city.json
```

The included `build_tum_temperature_examples.py` is the reproducible builder
for all five encodings. Its source paths are defined at the top of the script.

## Publication note

The examples reference the immutable `v2.0.0` release URL. The repository must
therefore publish tag `v2.0.0` before automatic remote schema retrieval is used.
"""
    (PACKAGE / "README.md").write_text(textwrap.dedent(readme), encoding="utf-8")

    shutil.copy2(SOURCE, PACKAGE / "DEBY_LOD2_4959457.original.city.json")
    shutil.copy2(ROOT / "scripts" / "apply_frost_temperature.py", PACKAGE / "apply_frost_temperature.py")
    shutil.copy2(Path(__file__), PACKAGE / "build_tum_temperature_examples.py")

    archive = ROOT / f"{PACKAGE.name}.zip"
    if archive.exists():
        archive.unlink()
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(PACKAGE.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(ROOT))
    print(archive)


if __name__ == "__main__":
    build()
