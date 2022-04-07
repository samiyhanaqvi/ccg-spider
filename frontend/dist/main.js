/* global Vue _ mapboxgl MapboxDraw turf */

import * as models from "./models/index.js";
import {
  updateHex,
  reloadHex,
  resetProp,
  toObj,
  toObjSingle,
  toObjArr,
  fmt,
  zip,
  updatePaint,
  extendProp,
  getColorByMinMax,
  downloadHex,
  downloadLines,
  layerPaint,
} from "./funcs.js";

let path = window.location.pathname.split("/")[1];
if (!(path in models)) path = "fish";

const modelRoot = models[path];
let hex = modelRoot.hex;
const model = modelRoot.model;
const config = modelRoot.config;
const loc = config.loc;
const hexSize = config.hexSize;
const popup = config.popup;
const infra = config.infra;
const pars = config.pars;
const attrs = config.attrs;

let mapLoaded = false;

hex = updateHex(toObjSingle(pars, "val"), hex, model);

const app = Vue.createApp({
  data() {
    return {
      hex,
      path,
      pars,
      infra,
      idLabels: false,
      scaleColors: true,
      attrs: toObj(attrs),
      colorBy: attrs[0].col,
      drawing: null,
    };
  },
  computed: {
    idLabelsText: function () {
      return this.idLabels ? "visible" : "none";
    },
    parVals: function () {
      return toObjSingle(this.pars, "val");
    },
    colorByObj: function () {
      return this.attrs[this.colorBy];
    },
    colorByMinMax: function () {
      const minMax = getColorByMinMax(this.colorByObj, this.scaleColors, this.hex);
      return { min: fmt(minMax.min), max: fmt(minMax.max) };
    },
    colorBarStyle: function () {
      const from = this.colorByObj.minCol;
      const to = this.colorByObj.maxCol;
      return `linear-gradient(to right, ${from}, ${to})`;
    },
  },
  watch: {
    idLabels: function () {
      map.setLayoutProperty("hex_label", "visibility", this.idLabelsText);
    },
    scaleColors: function () {
      updatePaint(this.colorByObj, map, this.scaleColors, this.hex);
    },
    parVals: function () {
      this.debouncedUpdate();
    },
    colorBy: function () {
      updatePaint(this.colorByObj, map, this.scaleColors, this.hex);
    },
  },
  created: function () {
    this.debouncedUpdate = _.debounce(this.update, 500);
  },
  methods: {
    zip: function (a, b) {
      return zip(a, b);
    },
    draw: function (col) {
      if (this.drawing == col) {
        this.drawing = null;
      } else {
        this.drawing = col;
      }
      setDrawing(this.drawing);
    },
    deleteDraw: function (col) {
      deleteDrawing(col);
      this.drawing = null;
    },
    update: function () {
      this.hex = updateHex(this.parVals, this.hex, model);
      reloadHex(map, this.hex, mapLoaded);
    },
    downloadHex: function () {
      downloadHex(this.hex, path);
    },
    downloadLines: function () {
      downloadLines(drawnLines, path);
    },
  },
}).mount("#sidebar");

mapboxgl.accessToken =
  "pk.eyJ1IjoiY2FyZGVybmUiLCJhIjoiY2puMXN5cnBtNG53NDN2bnhlZ3h4b3RqcCJ9.eNjrtezXwvM7Ho1VSxo06w";
const map = new mapboxgl.Map({
  container: "map",
  style: "mapbox://styles/carderne/cl0rvsxn200ce14jz3q5j5hco?fresh=true",
  center: loc.center,
  zoom: loc.zoom,
});

const drawModes = {
  line: "draw_line_string",
  point: "draw_point",
};

const setDrawing = (drawing) => {
  if (drawing) {
    draw.changeMode(drawModes[toObj(infra)[drawing].type]);
  } else {
    draw.changeMode("static");
  }
};

infra.forEach((obj) => {
  hex.features.forEach((ft) => {
    ft.properties[`${obj.col}_orig`] = ft.properties[obj.col];
  });
});


const deleteDrawing = (col) => {
  map.getSource(`drawn_${col}`).setData(turf.featureCollection([]));
  draw.deleteAll();
  drawnLines[col] = [];
  app.hex = resetProp(col, app.hex);
  app.hex = updateHex(app.parVals, app.hex, model);
  reloadHex(map, app.hex, mapLoaded);
};

const StaticMode = {};
StaticMode.onSetup = function () {
  this.setActionableState();
  return {};
};
StaticMode.toDisplayFeatures = function (state, geojson, display) {
  display(geojson);
};

const draw = new MapboxDraw({
  displayControlsDefault: false,
  modes: { ...MapboxDraw.modes, static: StaticMode },
  styles: [
    {
      id: "gl-draw",
      type: "line",
      filter: ["==", "$type", "LineString"],
      layout: {
        "line-cap": "round",
        "line-join": "round",
      },
      paint: {
        "line-color": "#000000",
        "line-width": 2,
        "line-opacity": 1,
      },
    },
    {
      id: "highlight-active-points",
      type: "circle",
      filter: ["all", ["==", "$type", "Point"], ["==", "meta", "feature"]],
      paint: {
        "circle-radius": 7,
        "circle-color": "#000000",
      },
    },
  ],
});
map.addControl(draw);

const getPointsFromGeom = (newGeom) => {
  if (newGeom.type === "Point") {
    return turf.featureCollection([turf.point(newGeom.coordinates)]);
  } else {
    const length = Math.floor(turf.lineDistance(newGeom, "km"));
    const features = [];
    for (let step = 0; step < length + 6; step += 5) {
      features.push(turf.along(newGeom, step, "km"));
    }
    return turf.featureCollection(features);
  }
};

const joinLineToHex = (newGeom) => {
  const points = getPointsFromGeom(newGeom);
  const tagged = turf
    .tag(points, hex, "index", "hexId")
    .features.map((f) => f.properties.hexId);
  const ids = [...new Set(tagged)].filter(Number);
  return ids;
};

const drawnLines = toObjArr(infra);

const updateLine = (e) => {
  const drawing = app.drawing;
  if (drawing) {
    drawnLines[drawing] = drawnLines[drawing].concat(e.features);
    map
      .getSource(`drawn_${drawing}`)
      .setData(turf.featureCollection(drawnLines[drawing]));
    const ids = e.features.map((f) => joinLineToHex(f.geometry)).flat(1);
    extendProp(ids, 0, drawing, app.hex, hexSize);
    app.hex = updateHex(app.parVals, app.hex, model);
    reloadHex(map, app.hex, mapLoaded);
  }
};


map.on("draw.create", updateLine);
map.on("draw.modechange", (e) => {
  if (e.mode === "simple_select" && app.drawing)
    setTimeout(() => {
      draw.changeMode(drawModes[toObj(infra)[app.drawing].type]);
    }, 100);
});


map.on("load", () => {
  mapLoaded = true;

  infra.forEach((i) => {
    const id = `drawn_${i.col}`;
    map.addSource(id, {
      type: "geojson",
      data: turf.featureCollection([]),
    });

    const layerType = i.type === "line" ? "line" : "circle";
    map.addLayer({
      id: id,
      type: layerType,
      source: id,
      paint: layerPaint(i),
    });
  });

  map.addSource("hex", {
    type: "geojson",
    data: hex,
  });

  const filt = ["!=", ["get", "tech"], "none"];

  map.addLayer({
    id: "hex",
    type: "fill",
    source: "hex",
    filter: filt,
    paint: {
      "fill-color": "rgba(0, 0, 0, 0)",
      "fill-opacity": ["interpolate", ["linear"], ["zoom"], 5, 0.6, 13, 0.2],
      "fill-outline-color": [
        "interpolate",
        ["linear"],
        ["zoom"],
        5,
        "hsla(0, 0%, 11%, 0)",
        13,
        "hsl(0, 0%, 11%)",
      ],
    },
  });
  map.addLayer({
    id: "hex_label",
    type: "symbol",
    source: "hex",
    filter: filt,
    layout: {
      "text-field": "{index}",
      "text-size": 10,
      "visibility": app.idLabelsText,
    },
    paint: {
      "text-halo-width": 1,
      "text-halo-color": "#fff",
      "text-halo-blur": 1,
      "text-color": "#000",
    },
  });
  app.hex = updateHex(app.parVals, app.hex, model);
  reloadHex(map, app.hex, mapLoaded);
  updatePaint(app.colorByObj, map, app.scaleColors, app.hex);

  const pointer = () => {
    if (!app.drawing) map.getCanvas().style.cursor = "pointer";
  };
  const nopointer = () => {
    if (!app.drawing) map.getCanvas().style.cursor = "";
  };

  map.on("mouseenter", "hex", pointer);
  map.on("mouseleave", "hex", nopointer);

  const addPopup = (e) => {
    if (!app.drawing) {
      const props = e.features[0].properties;
      const rows = popup.map((p) => {
        const val = p.fmt ? fmt(props[p.col]) : props[p.col];
        const unit = p.unit ? ` ${p.unit}` : "";
        return `<div>${p.label}: ${val} ${unit}</div>`;
      });
      const description =
        `<div><strong>ID: ${props.index}</strong></div>` + rows.join("");
      new mapboxgl.Popup().setLngLat(e.lngLat).setHTML(description).addTo(map);
    }
  };
  map.on("click", "hex", (e) => addPopup(e));
});
