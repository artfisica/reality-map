// Project the world once into assets/map.json, so the site build stays pure
// Python and the repository carries no runtime JavaScript dependency.
//
//   npm install world-atlas topojson-client d3-geo
//   node scripts/make_map.mjs
//
// Equal Earth projection: areas are comparable, which matters when the subject
// is who bears the consequences of decisions taken elsewhere. Mercator would
// inflate the metropolitan north and shrink every territory in this atlas.

import { writeFileSync } from "node:fs";
import { geoEqualEarth, geoPath, geoGraticule } from "d3-geo";
import { feature, merge } from "topojson-client";
import world from "world-atlas/countries-110m.json" with { type: "json" };

const W = 1600;
const H = 780;

// Places the atlas examines. Coordinates are the point the study is about, not
// a capital. Cases that collide at world scale are merged into one marker and
// named together in the legend.
const PLACES = {
  levant: [35.2, 32.7],
  mesopotamia: [41.0, 34.3],
  afghanistan: [67.7, 34.0],
  "puerto-rico": [-66.4, 18.2],
  guam: [144.8, 13.4],
  "new-caledonia": [165.6, -21.3],
  "french-guiana": [-53.1, 4.0],
  caribbean: [-73.5, 15.5],
  "eastern-pacific": [-91.0, 5.0],
  venezuela: [-66.5, 7.5],
};

// One landmass, no internal borders. Natural Earth has to take a position on
// every disputed boundary; this atlas does not, and a drawn line through Gaza,
// Western Sahara or Kashmir would be the map asserting what the prose has to
// argue. Antarctica is dropped for composition.
const all = feature(world, world.objects.countries);
const keep = world.objects.countries.geometries.filter(
  (g) => g.properties.name !== "Antarctica",
);
const land = merge(world, keep);
console.log(`merged ${keep.length} of ${all.features.length} countries`);

const projection = geoEqualEarth().fitExtent(
  [[24, 24], [W - 24, H - 24]],
  land,
);
// Integer precision. At 1600px wide the sub-pixel detail is invisible and
// costs a third of the payload, which readers on slow connections pay for.
const path = geoPath(projection);
const round = (d) => d.replace(/(-?\d+)\.\d+/g, "$1");

const out = {
  viewBox: `0 0 ${W} ${H}`,
  land: round(path(land)),
  graticule: round(path(geoGraticule().step([30, 30])())),
  sphere: round(path({ type: "Sphere" })),
  points: Object.fromEntries(
    Object.entries(PLACES).map(([id, lonlat]) => {
      const xy = projection(lonlat);
      return [id, [Math.round(xy[0] * 10) / 10, Math.round(xy[1] * 10) / 10]];
    }),
  ),
};

writeFileSync("assets/map.json", JSON.stringify(out));
console.log(
  `assets/map.json: ${Object.keys(out.points).length} points, ` +
    `${out.land.length} path chars`,
);
