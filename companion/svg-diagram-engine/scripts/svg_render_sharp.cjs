#!/usr/bin/env node
"use strict";

const sharp = require("sharp");

const [input, output, widthText, heightText] = process.argv.slice(2);
if (!input || !output || !widthText || !heightText) {
  console.error("usage: svg_render_sharp.cjs INPUT.svg OUTPUT.png WIDTH HEIGHT");
  process.exit(2);
}

sharp(input, { density: 144 })
  .resize(Number(widthText), Number(heightText), { fit: "fill" })
  .png()
  .toFile(output)
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
