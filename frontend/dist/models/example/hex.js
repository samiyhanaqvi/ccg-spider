export default {
  type: "FeatureCollection",
  features: [
    {
      id: 0,                                  // this must be here and must be an int
      type: "Feature",
      properties: {
        index: 0,                             // this must be here and must match the "id"
        n0: 450,                              // these n0-n5 must be here and must be ints matching ids
        n1: 307,
        n2: 270,
        n3: 2004,
        n4: 1695,
        n5: 1289,
        city_dist: 153.130065,
        farm_type: "pond",
      },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [37.61610735846944, 0.06579072760081736],
            [37.61769861332583, 0.15690190421744965],
            [37.53818148010392, 0.20655820064066732],
            [37.457011954584715, 0.16514134029325656],
            [37.45535858172872, 0.07399816931651684],
            [37.53493686951643, 0.02430377388329065],
            [37.61610735846944, 0.06579072760081736],
          ],
        ],
      },
    },
  ],
};
