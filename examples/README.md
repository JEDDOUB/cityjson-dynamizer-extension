# CityJSON example datasets

This directory contains five CityJSON 2.0 datasets based on the same
TUM LoD2 building. Each file includes the building geometry, the Dynamizer
extension declaration, and the CityObjects needed by the illustrated encoding.

| File | Demonstrated encoding | CityObjects |
|---|---|---:|
| `01-generic-embedded-time-value-pairs.city.json` | Embedded generic time series | 3 |
| `02-tabulated-file-timeseries.city.json` | External tabulated CSV series | 3 |
| `03-standard-file-timeseries.city.json` | External TimeseriesML file | 3 |
| `04-composite-timeseries.city.json` | Composite time series | 5 |
| `05-sensor-connection.city.json` | FROST SensorThings connection | 2 |
| `DEBY_LOD2_4959457.original.city.json` |  Source building | 1 |

The files can be validated with `cjval`.

From the repository root, run:

```bash
cjval examples/01-generic-embedded-time-value-pairs.city.json -e dynamizer.ext.json
```

Repeat the command with the other example filenames as required.

## Sensor-location note

In example 05, the FROST location at longitude 11.568095 and latitude
48.149132 lies inside the published two-dimensional extent of the TUM building.
This spatial match supports the use of the building ID as `sensorLocation`, but
it does not prove the sensor's exact physical mounting point.
