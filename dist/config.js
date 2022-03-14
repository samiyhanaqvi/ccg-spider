export const pars = [
  {
    var: "grid",
    label: "Grid cost per km",
    min: 1,
    max: 1000,
    val: 200,
    unit: "$",
  },
  {
    var: "road",
    label: "Road cost per km",
    min: 1,
    max: 1000,
    val: 500,
    unit: "$",
  },
  {
    var: "pop",
    label: "Cost per person",
    min: 0,
    max: 10,
    val: 3,
    unit: "$",
  },
];

export const filts = [
  {
    var: "water_dist",
    label: "Max water dist",
    min: 0,
    max: 10,
    val: 5,
    op: "<",
    unit: "km",
  },
];

export const attrs = [
  {
    var: "profit",
    min: 0,
    max: 40000,
    minCol: "hsl(0, 29%, 93%)",
    maxCol: "hsl(0, 100%, 23%)",
  },
  {
    var: "grid_dist",
    min: 0,
    max: 100,
    minCol: "hsl(90, 29%, 93%)",
    maxCol: "hsl(90, 100%, 23%)",
  },
  {
    var: "lake_dist",
    min: 0,
    max: 20,
    minCol: "hsl(150, 29%, 93%)",
    maxCol: "hsl(150, 100%, 23%)",
  },
];
