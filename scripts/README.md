# Additional scripts

The examples in this repository are complete and can be used without running
these scripts. The scripts document how the examples were produced and add
checks that cannot be expressed by Draft-07 JSON Schema alone.

## `apply_frost_temperature.py`

Adds one sensor-connected `+Dynamizer` to the supplied TUM CityJSON building.
The source geometry, vertices, semantics, transform, metadata, and existing
attributes are preserved.

```bash
python scripts/apply_frost_temperature.py \
  examples/DEBY_LOD2_4959457.original.city.json \
  building_frost_temperature.city.json
```

Input: a CityJSON 2.0 file containing `DEBY_LOD2_4959457`.  
Output: a CityJSON 2.0 file containing the original building and a
sensor-connected `+Dynamizer`.

## `build_tum_temperature_examples.py`

Regenerates all five comparison examples from the same source building and
four temperature observations. Use this script when changing the extension
schema or example-generation logic.

```bash
python scripts/build_tum_temperature_examples.py
```

The script writes a separate generated package. It does not need to be run to
use the examples already committed to this repository.

## `validate_references.py`

Checks relationships and resources that JSON Schema cannot validate across the
whole document:

- existence of the CityObjects identified by `target`, `dynamicData`,
  component `timeseries`, and `sensorLocation`;
- resolution of target-relative RFC 6901 JSON Pointers;
- consistency of a Dynamizer with the target-side `+dynamizer` list when that
  optional list is present;
- cycles in composite-series graphs;
- existence and basic structure of the bundled CSV and XML resources.

The checker verifies that referenced IDs exist, but it does not currently
verify the CityObject type of every referenced series. Its inverse-link check
is also performed from each Dynamizer towards its target; it does not
independently validate every ID found in every `+dynamizer` array.

```bash
python scripts/validate_references.py
```

This checker complements `cjval`; it does not replace CityJSON schema
validation or application specific checks of units and remote services.
