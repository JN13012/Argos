import { readFile, writeFile } from "node:fs/promises";
import { mesh } from "topojson-client";

const atlas = JSON.parse(await readFile(new URL("../node_modules/world-atlas/land-110m.json", import.meta.url), "utf8"));
const outlines = mesh(atlas, atlas.objects.land).coordinates.map((line) =>
  line.map(([longitude, latitude]) => [Number(longitude.toFixed(3)), Number(latitude.toFixed(3))]),
);
await writeFile(new URL("../src/features/home/scene/land-outlines.json", import.meta.url), JSON.stringify(outlines) + "\n");
process.stdout.write(`Prepared ${outlines.length} land outlines for the globe.\n`);
