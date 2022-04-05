// The centerpoint and zoom for the map to start at
const center = [37.7, 0.31];
const zoom = 6;
const loc = {center, zoom};

// fields to add to the hexagon click popups
const popup = [
  {
    col: "grid_dist",    // field to use from the hex data
    label: "Grid dist",  // text label to add in the popup
    unit: "km",          // unit to add after the value (set to "" for no unit)
    fmt: true,           // whether to format the numerical value (set to false for categorical/text values)
  },
  {
    col: "road_dist",
    label: "Road dist",
    unit: "km",
    fmt: true,
  },
  // and so on
];

// fields to enable drawing
// when these are drawn, the specified column will be set to 0 under the drawing
// and propagated outwards
const infra = [
  {
    col: "grid_dist",    // the column that will be affected by the drawing
    label: "Grid",       // the label for the drawing button
    type: "line",        // currently only "line" is supported
    color: "#FF0000",    // color to make the drawn features
  },
  {
    col: "road_dist",
    label: "Road",
    type: "line",
    color: "#0000FF",
  },
  // and so on
];

// parameters that will be added to the list of sliders
// these modify the "pars" value that is passed to the modelling function
const pars = [
  {
    col: "duration",     // name by which the value can be referred to
    label: "Duration",   // label for the slider UI
    unit: "years",       // unit to add to the slider UI
    min: 5,              // min allowed value
    max: 20,             // max allowed value
    val: 10,             // starting value
  },
  {
    col: "interest_rate",
    label: "Interest rate",
    unit: "%",
    min: 0,
    max: 100,
    val: 6,
  },
  // and so on
];

// these are the options for colouring the hexagons
// that are displayed in the "Colour by" drop down
const attrs = [
  {
    col: "road_dist",              // the column to read for the colour
    label: "road distance",        // the label to use in the drop down
    min: 0,                        // bottom value for colour scale (currently ignored)
    max: 100,                      // top value for colour scale (ditto)
    minCol: "hsl(60, 29%, 93%)",   // colour for bottom of scale (any valid CSS colour)
    maxCol: "hsl(60, 100%, 23%)",  // colour for top of scale
  },
  {
    col: "tech",
    label: "technology type",
    cats: ["something", "else"],   // this is a categorical colouring scheme
                                   // pass a list of categorical values that appear
                                   // in the specified column
    colors: [
      "hsla(0, 60%, 60%, 1)",      // and pass a list of colours
      "hsla(100, 60%, 60%, 1)",
      "hsla(200, 60%, 60%, 0.2)",  // there must be one more colour than there are "cats"
                                   // the last colour will apply to the case with no match
    ],
  },
];

export default {loc, popup, infra, pars, attrs};
