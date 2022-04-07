/* global turf */

export const reloadHex = (map, hex, mapLoaded) => {
  if (mapLoaded) {
    map.getSource("hex").setData(hex);
  }
};

export const updateHex = (parVals, hex, model) => {
  return {
    ...hex,
    features: hex.features.map((f) => ({
      ...f,
      properties: { ...f.properties, ...model(f.properties, parVals) },
    })),
  };
};

export const resetProp = (prop, hex) => {
  return {
    ...hex,
    features: hex.features.map((f) => ({
      ...f,
      properties: {
        ...f.properties,
        [prop]: f.properties[`${prop}_orig`],
      },
    })),
  };
};

export const getColorByMinMax = (attr, scaleColors, hex) => {
  let min = attr.min;
  let max = attr.max;
  if (scaleColors) {
    const hexVals = hex.features.map((f) => f.properties[attr.col]);
    min = Math.min(...hexVals);
    max = Math.max(...hexVals);
  }
  return { min, max };
};

export const toObj = (arr) =>
  arr.reduce((acc, el) => ((acc[el.col] = el), acc), {});

export const toObjSingle = (arr, key) =>
  arr.reduce((acc, el) => ((acc[el.col] = el[key]), acc), {});

export const toObjArr = (arr) =>
  arr.reduce((acc, el) => ((acc[el.col] = []), acc), {});

export const fmt = (val) => val && Math.round(val).toLocaleString("en");

export const zip = (a, b) => a.map((k, i) => [k, b[i]]);

const zipflat = (a, b) =>
  zip(a, b)
    .reduce((k, i) => k.concat(i))
    .concat(b.slice(-1));

export const updatePaint = (attr, map, scaleColors, hex) => {
  if ("cats" in attr) {
    map.setPaintProperty(
      "hex",
      "fill-color",
      ["match"]
        .concat([["get", attr.col]])
        .concat(zipflat(attr.cats, attr.colors))
    );
  } else {
    const minMax = getColorByMinMax(attr, scaleColors, hex);
    map.setPaintProperty("hex", "fill-color", [
      "interpolate",
      ["linear"],
      ["get", attr.col],
      minMax.min,
      attr.minCol,
      minMax.max,
      attr.maxCol,
    ]);
  }
};

export const extendProp = (ids, dist, col, hexOrig, hexSize) => {
  let hex = hexOrig;
  const neis = [];
  ids.forEach((i) => {
    try {
      if (hex.features[i].properties[col] > dist) {
        hex.features[i].properties[col] = dist;
        const p = hex.features[i].properties;
        const nei = [p.n0, p.n1, p.n2, p.n3, p.n4, p.n5];
        neis.push(nei);
      }
    } catch (e) {} // eslint-disable-line
  });
  if (neis.length > 0) {
    const idsSet = new Set(ids);
    const newIds = [...new Set(neis.flat(1))].filter((x) => !idsSet.has(x));
    hex = extendProp(newIds, dist + hexSize, col, hex, hexSize);
  }
  return hex;
};

export const layerPaint = (i) =>
  i.type === "line"
    ? {
        "line-color": i.color,
        "line-width": 3,
        "line-opacity": 0.9,
      }
    : {
        "circle-radius": 7,
        "circle-color": i.color,
      };

export const downloadHex = (hex, path) => {
  downloadFc(hex, path, "spider_hex");
};

export const downloadLines = (drawnLines, path) => {
  const lines = Object.entries(drawnLines).map(([type, arr]) => {
    const feats = arr.map((ft) => {
      ft.properties.type = type;
      return ft;
    });
    return feats;
  });
  const fc = turf.featureCollection(lines.flat());
  downloadFc(fc, path, "spider_lines");
};

const downloadFc = (fc, path, name) => {
  const str = JSON.stringify(fc);
  const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(str);
  const downloadAnchorNode = document.createElement("a");
  downloadAnchorNode.setAttribute("href", dataStr);
  downloadAnchorNode.setAttribute("download", name + "_" + path + ".geojson");
  document.body.appendChild(downloadAnchorNode);
  downloadAnchorNode.click();
  downloadAnchorNode.remove();
};
