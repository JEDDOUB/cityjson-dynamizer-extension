# CityJSON Dynamizer Extension

CityJSON Extension 2.0.0 for representing concepts from the [CityGML 3.0 Dynamizer module](https://docs.ogc.org/is/20-010/20-010.html#dynamizer-uml) in CityJSON 2.0.

The extension provides a practical encoding for time-varying CityObject properties, embedded and file-based time series, composite series, and live or remote sensor connections.

* **Extension version:** 2.0.0
* **Target CityJSON version:** 2.0
* **Schema baseline used for testing:** CityJSON 2.0.2

## Version and relationship to earlier work

This extension builds on an [earlier Dynamizer extension proposal for CityJSON 1.1](https://github.com/1khawla/CityJSON-Dynamizer).

Version 2.0.0 introduces a redesigned encoding for CityJSON 2.0. Dynamizers and concrete time series are represented as identifiable CityObjects, the relation to the affected CityObject is explicitly represented through `target`, and the temporal and file-based encodings have been revised.

## Core representation

* `+Dynamizer` is an independent extension CityObject.
* `target` identifies the CityObject whose property changes.
* `attributeRef` is an RFC 6901 JSON Pointer evaluated relative to that target.
* `dynamicData` identifies a concrete time-series CityObject.
* Concrete series are `+GenericTimeseries`, `+CompositeTimeseries`, `+StandardFileTimeseries`, and `+TabulatedFileTimeseries`.
* `SensorConnection`, `TimeValuePair`, and `TimeseriesComponent` are embedded records because they do not need independent identities.
* The target-side `+dynamizer` attribute is an optional inverse reference provided for convenience. The `target` member remains the main relation from the Dynamizer to the affected CityObject.

```json
"dyn-temperature": {
  "type": "+Dynamizer",
  "attributes": {
    "target": "building-01",
    "attributeRef": "/attributes/temperature",
    "dynamicData": "series-temperature"
  }
}
```

## Supported concepts

| CityGML concept         | CityJSON encoding                                                      |
| ----------------------- | ---------------------------------------------------------------------- |
| Dynamizer               | `+Dynamizer` CityObject                                                |
| GenericTimeseries       | `+GenericTimeseries` CityObject                                        |
| CompositeTimeseries     | `+CompositeTimeseries` CityObject                                      |
| StandardFileTimeseries  | `+StandardFileTimeseries` CityObject                                   |
| TabulatedFileTimeseries | `+TabulatedFileTimeseries` CityObject                                  |
| SensorConnection        | Embedded in `+Dynamizer`                                               |
| TimeValuePair           | Embedded typed record                                                  |
| TimeseriesComponent     | Embedded reference record                                              |
| Scalar values           | Typed representations for `int`, `double`, `string`, `uri`, and `bool` |

Geometry-, implicit-geometry-, and appearance-valued Dynamizers are not included in version 2.0.0. Their CityGML meaning and the related CityJSON encoding difficulties are documented in the mapping specification, but no stable CityJSON encoding is currently proposed for them.

## Repository contents

```text
.
├── dynamizer.ext.json
├── README.md
├── CITATION.cff
├── CONTRIBUTING.md
├── LICENSE
├── extension.toml
├── docs/
│   └── Dynamizer_Mapping_Specification_v2.0.0.pdf
├── examples/
│   ├── README.md
│   ├── 01-generic-embedded-time-value-pairs.city.json
│   ├── 02-tabulated-file-timeseries.city.json
│   ├── 03-standard-file-timeseries.city.json
│   ├── 04-composite-timeseries.city.json
│   ├── 05-sensor-connection.city.json
│   └── DEBY_LOD2_4959457.original.city.json
├── data/
│   ├── temperature.csv
│   └── temperature-timeseriesml.xml
└── scripts/
    ├── README.md
    ├── apply_frost_temperature.py
    ├── build_tum_temperature_examples.py
    └── validate_references.py
```

## Examples

All examples use the same TUM LoD2 building and target the same property, `/attributes/temperature`. Only the source and organisation of the temporal values change.

| Example                                          | Representation        | Values are stored              |
| ------------------------------------------------ | --------------------- | ------------------------------ |
| `01-generic-embedded-time-value-pairs.city.json` | Generic series        | In embedded typed pairs        |
| `02-tabulated-file-timeseries.city.json`         | Tabulated-file series | In `data/temperature.csv`      |
| `03-standard-file-timeseries.city.json`          | Standard-file series  | In a TimeseriesML file         |
| `04-composite-timeseries.city.json`              | Composite series      | In referenced component series |
| `05-sensor-connection.city.json`                 | Sensor connection     | Remotely in TUM FROST          |

## Validation

Install [`cjval`](https://github.com/cityjson/cjval), then run the following commands from the repository root:

```bash
cjvalext dynamizer.ext.json
cjval examples/01-generic-embedded-time-value-pairs.city.json -e dynamizer.ext.json
cjval examples/02-tabulated-file-timeseries.city.json -e dynamizer.ext.json
cjval examples/03-standard-file-timeseries.city.json -e dynamizer.ext.json
cjval examples/04-composite-timeseries.city.json -e dynamizer.ext.json
cjval examples/05-sensor-connection.city.json -e dynamizer.ext.json
python scripts/validate_references.py
```

`cjval` checks the CityJSON structure and its conformance with the extension schema.

The included reference checker performs additional checks that JSON Schema cannot express, including:

* resolution of referenced CityObject IDs;
* resolution of `attributeRef` JSON Pointers;
* detection of cycles in composite time series;
* existence of the bundled external files;
* verification of the CSV time and value columns; and
* well-formedness of the bundled XML file.

Successful validation does not automatically prove that units are compatible, remote services are available, authentication is valid, or application-specific behaviour is correct. These aspects require additional semantic or operational checks.

## Additional scripts

The CityJSON examples are ready to use, and running the scripts is not required. The scripts are included to document how the examples were generated and to make the results reproducible.

* `apply_frost_temperature.py` shows how a CityJSON 2.0 building can be enriched with a sensor-connected `+Dynamizer` without modifying its geometry.
* `build_tum_temperature_examples.py` regenerates the five examples from the same source building and temperature observations.
* `validate_references.py` performs cross-object and external-resource checks that JSON Schema alone cannot express.

See [`scripts/README.md`](scripts/README.md) for the required inputs, generated outputs, and usage instructions.

## Documentation

The complete mapping specification is available in the [`docs`](docs/) directory.

It describes:

* the mapping of the supported CityGML Dynamizer concepts;
* the reasons behind the selected CityJSON representations;
* the hybrid representation of independent CityObjects and embedded records;
* temporal values and timestamps;
* JSON Pointer target addressing;
* units of measure and code values;
* embedded, composite, file-based, and sensor-connected time series;
* structural, semantic, and external-resource validation;
* known limitations; and
* possible future developments.

## Contact

This extension is developed within [GeoScITY](https://www.geoscity.uliege.be/), University of Liège.

Questions, suggestions, and feedback can be submitted through the repository’s [GitHub Issues](https://github.com/JEDDOUB/cityjson-dynamizer-extension/issues).

## References

* [OGC CityGML 3.0 Part 1: Conceptual Model](https://docs.ogc.org/is/20-010/20-010.html)
* [OGC CityGML 3.0 Part 2: GML Encoding](https://docs.ogc.org/is/21-006r2/21-006r2.html)
* [CityJSON 2.0.2 specification](https://www.cityjson.org/specs/2.0.2/)
* [CityJSON Extension mechanism](https://www.cityjson.org/specs/2.0.2/#extensions)
* [Earlier Dynamizer extension proposal for CityJSON 1.1](https://github.com/1khawla/CityJSON-Dynamizer)
* [RFC 6901: JSON Pointer](https://www.rfc-editor.org/rfc/rfc6901)
* [RFC 3339: Date and Time on the Internet](https://www.rfc-editor.org/rfc/rfc3339)

## Licence

This project is licensed under the MIT License. See [`LICENSE`](LICENSE).
