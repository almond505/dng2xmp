// Builds dng2xmp-offline.html: index.html with JSZip embedded, so the page
// makes no network requests. Verifies the vendored JSZip against the same
// SRI hash the online page pins.
//
//   node tools/build-offline.mjs
import { readFileSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const html = readFileSync(join(root, 'index.html'), 'utf8');
const lib = readFileSync(join(root, 'vendor', 'jszip-3.10.1.min.js'));

const pinned = /const JSZIP_SRI = '(sha384-[^']+)'/.exec(html)?.[1];
const actual = 'sha384-' + createHash('sha384').update(lib).digest('base64');
if (pinned !== actual) {
  console.error(`JSZip hash mismatch.\n  pinned: ${pinned}\n  vendor: ${actual}`);
  process.exit(1);
}
const code = lib.toString('utf8');
if (/<\/script/i.test(code)) { console.error('Vendored script contains </script; refusing to inline.'); process.exit(1); }

const marker = '<!-- OFFLINE_JSZIP -->';
if (!html.includes(marker)) { console.error('Marker not found in index.html'); process.exit(1); }
let out = html.replace(marker, () => `<script>\n${code}\n</script>`);
// No remote origins needed any more.
out = out.replace("script-src 'unsafe-inline' https://cdnjs.cloudflare.com;", "script-src 'unsafe-inline';");
writeFileSync(join(root, 'dng2xmp-offline.html'), out);
console.log(`dng2xmp-offline.html written (${(out.length / 1024).toFixed(0)} KB), JSZip ${actual}`);
