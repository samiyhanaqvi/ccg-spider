/* global mapboxgl Vue */

mapboxgl.accessToken =
  "pk.eyJ1IjoiY2FyZGVybmUiLCJhIjoiY2puMXN5cnBtNG53NDN2bnhlZ3h4b3RqcCJ9.eNjrtezXwvM7Ho1VSxo06w";

const map = new mapboxgl.Map({
  container: "map",
  style: "mapbox://styles/mapbox/light-v10",
  center: [37.7, 0.31],
  zoom: 6,
});

var app = new Vue({
  el: "#sidebar",
  data: {
    message: "Hello Vue!",
  },
});

map.on("load", () => {
  map.addSource("earthquakes", {
    type: "geojson",
    // Use a URL for the value for the `data` property.
    data: "https://docs.mapbox.com/mapbox-gl-js/assets/earthquakes.geojson",
  });

  map.addLayer({
    id: "earthquakes-layer",
    type: "circle",
    source: "earthquakes",
    paint: {
      "circle-radius": 8,
      "circle-stroke-width": 2,
      "circle-color": "red",
      "circle-stroke-color": "white",
    },
  });
});
