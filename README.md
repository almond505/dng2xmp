# DNG → XMP Preset Converter

Turns Lightroom-edited DNG files into importable Lightroom preset (`.xmp`) files. Everything runs client-side: no server, no upload.

## Use

Open `index.html` (or `dng2xmp-offline.html` for zero network use) in a browser, drop `.dng` or `.zip` files, choose which setting groups to include, and download `.xmp` presets one by one or as a `.zip`. The UI uses a Lightroom-style dark theme by default; the header button switches to light or system theme.

| File | What it is |
|---|---|
| `index.html` | The app. Loads JSZip 3.10.1 from cdnjs (pinned version + SRI) only when a `.zip` is opened or created. |
| `dng2xmp-offline.html` | Same app with JSZip embedded; makes no network requests. Rebuild with `node tools/build-offline.mjs`. |
| `vendor/jszip-3.10.1.min.js` | Vendored JSZip (MIT / GPLv3 dual licence); the build checks it against the pinned SRI hash. |
| `tools/make-fixtures.py` | Generates synthetic test DNGs/ZIPs: `python3 tools/make-fixtures.py <out_dir>`. |

## How extraction works

1. Reads the TIFF header and IFD chain with `Blob.slice()` (classic TIFF, `II` and `MM`), finds tag 700 (XMLPacket), and validates every offset and length against the file size.
2. If the directory can't be used (no tag 700, BigTIFF, damaged IFD), it scans the bytes in 4 MB chunks with overlap, so markers that straddle a chunk boundary are still found. If more than one distinct packet carries develop settings, the user must pick one.
3. Packets are decoded as strict UTF-8. NUL bytes, invalid UTF-8, truncation and XML parse errors are reported. Nothing is repaired.
4. Properties are matched by namespace URI and `localName`, never by prefix. Only direct properties of top-level `rdf:Description` elements count, so values nested inside `crs:Look` stay inside it.
5. Output is built with `createElementNS` / `setAttributeNS` and `XMLSerializer`, then re-parsed and checked ("XML structure validated").

## Limits

16 MB XMP packet · ZIP: 2 GB archive, 1,000 entries, 1 GB per entry, 8 GB total uncompressed, no ZIP64, no encryption, no split archives. Entry sizes are checked against the central directory before extraction and again while streaming.

## Not verified yet

The presets have not been test-imported into Lightroom. Only the XML structure is validated. The groups `ConvertToGrayscale` (Basic tone) and `GrayMixer*` (HSL) were added to the allowlist so B&W edits carry over.
