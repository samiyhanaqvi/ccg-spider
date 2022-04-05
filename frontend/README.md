# spider-frontend

## Install
```bash
npm install
```

## Local development
```bash
npm run tw

# in a separate terminal
npx lite-server --baseDir=dist --host=0.0.0.0
```

Then navigate to http://localhost:3002/.

## Configuring a model
**NB**: You can see the examples in [dist/models/example](dist/models/example).
These are incomplete, but have more comments than the other files.

The model structure looks as follows:
```
dist/models/
├── index.js
├── fish
│   ├── index.js
│   ├── config.js
│   ├── hex.js
│   └── model.js
└── irri
    └── as above...
```

To add a model, the following steps are needed:
1. Create a new directory for the model under `models`, such as `dist/models/protein`.
2. Edit [dist/models/index.js](dist/models/index.js) with a new line as follows:
```javascript
export {default as protein} from "./protein/index.js";
```
3. Recreate all the files (`index.js`, `config.js`, `hex.js`, `model.js`) from one of the existing models.
Place these in your new directory.
4. Navigate to http://localhost:3002/protein to see what it looks like.

### Notes on hex.js
There are a few requirements for the `hex.js` files.

The snippet below shows an example with only one hexagon.
Some parts are omitted with `...` for brevity.
Essential features:
1. An integer `id` field at the same level as `type` and `properties`.
2. An integer `index` field as one of the `properties`, that must match the `id`.
3. Integer fields `n0` through `n5` that refer to neighbouring hexagons.
(This is only needed if any drawing will be used.)

```javascript
export default {
  type: "FeatureCollection",
  features: [
    {
      id: 0,
      type: "Feature",
      properties: {
        index: 0,
        n0: 450,
        n1: 307,
        n2: 270,
        n3: 2004,
        n4: 1695,
        n5: 1289,
        city_dist: 153.130065,
        farm_type: "pond",
        ...
      },
      geometry: {
        type: "Polygon",
        coordinates: [...],
      },
    },
    ...
  ]
}
```
