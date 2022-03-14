export const pars = [
  {
    name: "grid",
    label: "Grid cost per km",
    min: 1,
    max: 1000,
    val: 200,
    unit: "$",
  },
  {
    name: "road",
    label: "Road cost per km",
    min: 1,
    max: 1000,
    val: 500,
    unit: "$",
  },
  {
    name: "pop",
    label: "Cost per person",
    min: 0,
    max: 10,
    val: 3,
    unit: "$",
  },
];

export const filts = [
  {
    name: "water_dist",
    label: "Max water dist",
    min: 0,
    max: 10,
    val: 5,
    op: "<",
    unit: "km",
  },
];
