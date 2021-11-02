/* global mapboxgl Vue hex */

import hex from "./hex.js";

mapboxgl.accessToken =
  "pk.eyJ1IjoiY2FyZGVybmUiLCJhIjoiY2puMXN5cnBtNG53NDN2bnhlZ3h4b3RqcCJ9.eNjrtezXwvM7Ho1VSxo06w";

const map = new mapboxgl.Map({
  container: "map",
  style: "mapbox://styles/mapbox/light-v10",
  center: [37.7, 0.31],
  zoom: 6,
});

// eslint-disable-next-line no-unused-vars
const app = new Vue({
  el: "#sidebar",
  data: {
    message: "Hello Vue!",
    pars: {
      grid: { name: "Grid", min: 1, max: 100, val: 20 },
      road: { name: "Road", min: 1, max: 100, val: 50 },
      pop: { name: "Pop", min: 0, max: 10, val: 3 },
    },
  },
  watch: {
    vals: function () {
      this.debouncedUpdate();
    },
  },
  computed: {
    vals: function () {
      return Object.keys(this.pars).reduce(
        (acc, key) => ((acc[key] = this.pars[key].val), acc),
        {}
      );
    },
  },
  created: function () {
    this.debouncedUpdate = _.debounce(this.update, 500);
  },
  methods: {
    update: function () {
      updateHex(this.vals);
    },
  },
});

let mapLoaded = false;
map.on("load", () => {
  mapLoaded = true;
  map.addSource("hex", {
    type: "geojson",
    data: hex,
  });

  map.addLayer({
    id: "hex",
    type: "fill",
    source: "hex",
    paint: {
      "fill-color": [
        "interpolate",
        ["linear"],
        ["get", "Cost"],
        0,
        "hsl(0, 29%, 93%)",
        40000,
        "hsl(0, 100%, 23%)",
      ],
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
  updateHex(app.vals);
});

const updateHex = (vals) => {
  if (mapLoaded) {
    const keys = Object.keys(vals);
    hex.features.forEach((ft, i) => {
      const props = ft.properties;
      let cost = 0;
      keys.forEach((k) => (cost += props[k] * vals[k]));
      hex.features[i].properties.Cost = cost;
    });
    map.getSource("hex").setData(hex);
  }
};
