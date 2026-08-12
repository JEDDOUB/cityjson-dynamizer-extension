# Validation Report - Dynamizer Extension 2.0.0

**Validation date:** 11 August 2026  
**Status:** All reported checks passed.

## 1. Extension schema validation

The `dynamizer.ext.json` document was checked against the official CityJSON 2.0 Extension schema.

The extension defines the following five CityObject types:

- `+Dynamizer`
- `+GenericTimeseries`
- `+CompositeTimeseries`
- `+StandardFileTimeseries`
- `+TabulatedFileTimeseries`

The schema supports time series containing integer, double, string, URI and Boolean values.

Geometry, implicit geometry and appearance values are not included in version 2.0.0. 

## 2. CityJSON example validation

The following example files were successfully validated with `cjval` and the local extension schema:

1. `examples/01-generic-embedded-time-value-pairs.city.json`
2. `examples/02-tabulated-file-timeseries.city.json`
3. `examples/03-standard-file-timeseries.city.json`
4. `examples/04-composite-timeseries.city.json`
5. `examples/05-sensor-connection.city.json`

These examples cover embedded time-value pairs, tabulated files, standard time-series files, composite time series and sensor connections.

## 3. Additional reference checks

The following command was also executed successfully:

```bash
python scripts/validate_references.py
```

This script performs additional checks that cannot be expressed completely by
JSON Schema. For the five included examples, it verifies that:

- every `target` ID identifies an existing CityObject;
- every `dynamicData` ID identifies an existing CityObject;
- every `timeseries` ID used by a composite-series component identifies an
  existing CityObject;
- every `sensorLocation` ID identifies an existing CityObject when it is used;
- every `attributeRef` resolves to an existing property inside its target
  CityObject;
- when a target contains a `+dynamizer` list, the corresponding Dynamizer ID is
  present in that list;
- composite time series do not contain direct or indirect reference cycles;
- the CSV and XML resources used by the file-based examples exist;
- the named CSV time and value columns exist and the CSV file contains data;
- the TimeseriesML example is well-formed XML.

The script checks whether the referenced IDs exist. It does not currently
verify that every `dynamicData` or component `timeseries` reference points to
one of the four supported time-series CityObject types. It also does not
perform a complete reverse check of every ID listed in a target-side
`+dynamizer` array. These more detailed semantic checks remain the
responsibility of an application profile or a future version of the reference
validator.

## 4. Preservation of the source building

The five examples are based on the same TUM LoD2 building. The building geometry, vertices, semantic surfaces, transform, metadata and existing attributes were preserved when the Dynamizer objects were added.

## 5. Reproducibility checks

The included Python scripts were checked for syntax errors. The example-generation script successfully reproduced the five example datasets, and the FROST script produced a CityJSON 2.0 dataset containing the expected sensor-connected `+Dynamizer`.

All JSON files included in the repository were also checked to confirm that they are valid JSON documents.

## 6. Scope of the validation

Successful validation confirms that the files follow the CityJSON structure and the rules expressed by the Dynamizer extension schema. It also confirms the local references and bundled data resources checked by `validate_references.py`.

Validation does not confirm that:

- a remote sensor service is currently available;
- authentication information is valid;
- units are physically compatible or can be converted automatically;
- external code-list values belong to their stated vocabularies;
- an application will display or process the changing values in a particular way.

These points depend on external services or application-specific rules and must be checked separately when required.

## 7. Repeating the validation

From the repository root, run:

```bash
cjvalext dynamizer.ext.json
cjval examples/01-generic-embedded-time-value-pairs.city.json -e dynamizer.ext.json
cjval examples/02-tabulated-file-timeseries.city.json -e dynamizer.ext.json
cjval examples/03-standard-file-timeseries.city.json -e dynamizer.ext.json
cjval examples/04-composite-timeseries.city.json -e dynamizer.ext.json
cjval examples/05-sensor-connection.city.json -e dynamizer.ext.json
python scripts/validate_references.py
```

When the local extension file is supplied with `-e dynamizer.ext.json`, validation does not depend on downloading the extension schema from the internet.
