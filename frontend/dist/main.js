/* global Vue _ mapboxgl */

import * as models from "./models/index.js";
import {
  getHex,
  updateHex,
  reloadHex,
  deleteDrawing,
  toObj,
  toObjSingle,
  toObjArr,
  fmt,
  zip,
  updatePaint,
  getColorByMinMax,
  downloadHex,
  downloadLines,
  updateLine,
  keepDrawing,
  setDrawing,
} from "./funcs.js";

import { onMapLoaded, setupDrawing } from "./map.js";

let path = window.location.pathname.split("/")[1];
if (!(path in models)) path = "fish";

const modelRoot = models[path];
const model = modelRoot.model;
const config = modelRoot.config;
const loc = config.loc;
const hexSize = config.hexSize;
const popup = config.popup;
const infra = config.infra;
const pars = config.pars;
const attrs = config.attrs;

const drawnLines = toObjArr(infra);


const app = Vue.createApp({
  data() {
    return {
      hex: {},
      path,
      pars,
      infra,
      mapLoaded: false,
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
      const minMax = getColorByMinMax(
        this.colorByObj,
        this.scaleColors,
        this.hex
      );
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
  created: async function () {
    this.debouncedUpdate = _.debounce(this.update, 500);
    this.hex = await getHex(path, this.infra, this.parVals, model);
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
      setDrawing(this.drawing, draw, infra);
    },
    deleteDraw: function (col) {
      deleteDrawing(col, map, this, draw, drawnLines, this.mapLoaded, model);
      this.drawing = null;
    },
    update: function () {
      this.hex = updateHex(this.parVals, this.hex, model);
      reloadHex(map, this.hex, this.mapLoaded);
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

map.on("load", () => {
  app.mapLoaded = true;
  onMapLoaded(map, infra, popup, app, model);
});

const draw = setupDrawing();
map.addControl(draw);

map.on("draw.create", (e) =>
  updateLine(e.features, app, map, model, app.mapLoaded, hexSize, drawnLines)
);

map.on("draw.modechange", (e) => keepDrawing(e.mode, app, draw, infra));
