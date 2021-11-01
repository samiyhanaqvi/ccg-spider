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
  },
});

hex.features.forEach((ft, i) => {
  const props = ft.properties;
  hex.features[i].properties.Cost = props.Grid;
});

map.on("load", () => {
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
      "fill-outline-color": "hsl(0, 0%, 11%)",
    },
  });

  setTimeout(() => {
    hex.features.forEach((ft, i) => {
      const props = ft.properties;
      hex.features[i].properties.Cost = props.Cost + 200;
    });
    map.getSource("hex").setData(hex);
  }, 1000);
});
