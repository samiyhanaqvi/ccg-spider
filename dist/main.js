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
    grid: 20,
    road: 50,
    pop: 3,
  },
  watch: {
    grid: function (val) {
      this.debouncedUpdate();
    },
    road: function (val) {
      this.debouncedUpdate();
    },
    pop: function (val) {
      this.debouncedUpdate();
    },
  },
  created: function () {
    this.debouncedUpdate = _.debounce(this.update, 500);
  },
  methods: {
    update: function () {
      updateHex({ grid: this.grid, road: this.road, pop: this.pop });
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
        400,
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
  updateHex({ grid: app.grid, road: app.road, pop: app.pop });
});

const updateHex = ({ grid, road, pop }) => {
  if (mapLoaded) {
    hex.features.forEach((ft, i) => {
      const props = ft.properties;
      hex.features[i].properties.Cost =
        (props.Grid * grid + props.Roads * road + props.Pop * pop) / 100;
    });
    map.getSource("hex").setData(hex);
  }
};
