# spider-frontend

## Install
```bash
npm install
```

## Local development
This will automatically run the development server and the Tailwind CSS watching:
```bash
npm run dev
```

Then navigate to http://localhost:3002/.

## Configuring a model
The model structure looks as follows:
```
dist/
├── config
│   ├── fish.yml
│   └── ...
├── data
│   ├── fish.geojson
│   └── ...
├── models
│   ├── fish.py
│   └── ...
```

To add a model, the following steps are needed:
1. Create a new `GeoJSON` hexagon file, eg `dist/data/mining.geojson`.
Use the instructions under [prep](../[prep/) to do this.
2. Write your `Python` model code and save it to eg `dist/models/mining.python`.
3. Create a new `YAML` config, eg `dist/config/mining.yml`.
You can base this on the [dist/config/example.yml](./dist/config/example.yml) file, and follow the instructions there for the necessary fields.
Make sure it correctly points to the hexagon and model files you just created.

### Notes on the hexagon file
There are a few `properties` that must be included on every `Feature` in the hexagons `GeoJSON` file:
1. An integer `index` field as one of the `properties`, that must match the `id`.
2. Integer fields `n0` through `n5` that refer to neighbouring hexagons.
(This is only needed if any drawing will be used.)

The snippet below shows example properties for a single hexagon Feature:
```json
"properties": {
    "index": 0,
    "n0": 450,
    "n1": 307,
    "n2": 270,
    "n3": 2004,
    "n4": 1695,
    "n5": 1289
}
```
