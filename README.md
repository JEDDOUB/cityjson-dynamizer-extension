# CityJSON Dynamizer Extension

CityJSON Extension 2.0.0 for representing the operational core of
the [CityGML 3.0 Dynamizer module](https://docs.ogc.org/is/20-010/20-010.html#dynamizer-uml)
in CityJSON 2.0.

The extension provides a practical encoding for time-varying CityObject
properties, embedded and file-based time series, composite series, and live or
remote sensor connections.

**Extension version:** 2.0.0  
**Target CityJSON version:** 2.0  
**Schema baseline used for testing:** CityJSON 2.0.2

## Why version 2.0.0?

An earlier CityJSON 1.1 proposal used extension version 1.0 and embedded a
Dynamizer directly in a Building attribute. This repository is a redesigned,
incompatible representation for CityJSON 2.0: Dynamizers and concrete series
have stable CityObject identities, the target relation is explicit, and the
temporal and file encodings are substantially revised. Version 2.0.0 therefore
indicates a new major extension design; it must not be confused with the
`versionCityJSON` value, which separately identifies the compatible CityJSON
minor version.

## Core representation

- `+Dynamizer` is an independent extension CityObject.
- `target` identifies the CityObject whose property changes.
- `attributeRef` is an RFC 6901 JSON Pointer evaluated relative to that target.
- `dynamicData` identifies a concrete time-series CityObject.
- Concrete series are `+GenericTimeseries`, `+CompositeTimeseries`,
  `+StandardFileTimeseries`, and `+TabulatedFileTimeseries`.
- `SensorConnection`, `TimeValuePair`, and `TimeseriesComponent` are embedded
  records because they do not need independent identity.
- The target-side `+dynamizer` attribute is an optional derived inverse index;
  `target` remains authoritative.

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

| CityGML concept | CityJSON encoding |
|---|---|
| Dynamizer | `+Dynamizer` CityObject |
| GenericTimeseries | `+GenericTimeseries` CityObject |
| CompositeTimeseries | `+CompositeTimeseries` CityObject |
| StandardFileTimeseries | `+StandardFileTimeseries` CityObject |
| TabulatedFileTimeseries | `+TabulatedFileTimeseries` CityObject |
| SensorConnection | Embedded in `+Dynamizer` |
| TimeValuePair | Embedded typed record |
| TimeseriesComponent | Embedded reference record |
| Scalar values | `int`, `double`, `string`, `uri`, and `bool` branches |

Geometry-, implicit-geometry-, and appearance-valued Dynamizers are not
included in version 2.0.0. Their CityGML meaning is documented in the report,
but no stable CityJSON encoding is claimed for them.

## Repository contents

```text
.
├── dynamizer.ext.json
├── README.md
├── CITATION.cff
├── CONTRIBUTING.md
├── LICENSE
├── VALIDATION_REPORT.md
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

All examples use the same TUM LoD2 building and target the same property,
`/attributes/temperature`. Only the source and organisation of the temporal
values change.

| Example | Representation | Values are stored |
|---|---|---|
| `01-generic-embedded-time-value-pairs.city.json` | Generic series | In embedded typed pairs |
| `02-tabulated-file-timeseries.city.json` | Tabulated-file series | In `data/temperature.csv` |
| `03-standard-file-timeseries.city.json` | Standard-file series | In a TimeseriesML file |
| `04-composite-timeseries.city.json` | Composite series | In referenced component series |
| `05-sensor-connection.city.json` | Sensor connection | Remotely in TUM FROST |

## Validation

Install [`cjval`](https://github.com/cityjson/cjval), then run from the
repository root:

```bash
cjvalext dynamizer.ext.json
cjval examples/01-generic-embedded-time-value-pairs.city.json -e dynamizer.ext.json
cjval examples/02-tabulated-file-timeseries.city.json -e dynamizer.ext.json
cjval examples/03-standard-file-timeseries.city.json -e dynamizer.ext.json
cjval examples/04-composite-timeseries.city.json -e dynamizer.ext.json
cjval examples/05-sensor-connection.city.json -e dynamizer.ext.json
python scripts/validate_references.py
```

`cjval` checks CityJSON and extension structure. The included reference checker
adds local ID resolution, JSON Pointer resolution, composite-cycle checks, and
checks of the bundled CSV/XML resources. Unit compatibility, network
availability, authentication, and application behaviour require additional
semantic or operational validation.

## Why are scripts included?

The CityJSON examples are ready to use; running the scripts is not required.
The scripts are included for transparency and reproducibility:

- `apply_frost_temperature.py` shows how a normal CityJSON 2.0 building can be
  enriched with a sensor-connected `+Dynamizer` without changing its geometry;
- `build_tum_temperature_examples.py` regenerates the five equivalent examples
  from the same source building and observations;
- `validate_references.py` performs cross-object and external-file checks that
  JSON Schema alone cannot express.

See [`scripts/README.md`](scripts/README.md) for inputs, outputs, and usage.

## Publishing this release

After uploading the repository contents, create the Git tag/release `v2.0.0`.
The schema and examples deliberately use the immutable raw URL associated with
that tag. Until the tag exists, validate with the local schema by passing
`-e dynamizer.ext.json` to `cjval`.

## Documentation

The mapping specification in `docs/` describes:

- the mapping of each supported CityGML Dynamizer concept;
- the rationale for the hybrid identity model;
- temporal, pointer, unit, code-list, file, and sensor encodings;
- structural, semantic, and resource-validation boundaries;
- known limitations and future work.

## References

- [OGC CityGML 3.0 Part 1: Conceptual Model](https://docs.ogc.org/is/20-010/20-010.html)
- [OGC CityGML 3.0 Part 2: GML Encoding](https://docs.ogc.org/is/21-006r2/21-006r2.html)
- [CityJSON 2.0.2 specification](https://www.cityjson.org/specs/2.0.2/)
- [CityJSON Extension mechanism](https://www.cityjson.org/specs/2.0.2/#extensions)
- [RFC 6901 JSON Pointer](https://www.rfc-editor.org/rfc/rfc6901)
- [RFC 3339 Date and Time](https://www.rfc-editor.org/rfc/rfc3339)

## Licence

MIT. See [`LICENSE`](LICENSE).
