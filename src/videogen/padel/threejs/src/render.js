// render.js — puppeteer runner que lanza scene.html, captura frames y los
// concatena a mp4 con ffmpeg. Usado desde Python padel/render.py cuando
// PADEL_FORMAT=threejs.
//
// Variables de entorno:
//   SCENE          nombre de la táctica (lob/back_wall/bandeja/...)
//   FPS            default 30
//   OUT_MP4        ruta mp4 destino (si no, output/<scene>.mp4)
//   HEADLESS       'new' (default) o 'false' para debug local
//
// Chrome del sistema (no el chromium bundled) para evitar bugs crashpad en
// macOS. En Linux CI puppeteer usa su bundled.
import puppeteer from 'puppeteer';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';
import { promises as fs } from 'fs';
import { spawn } from 'child_process';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, '..');

const SCENE = process.env.SCENE || 'lob';
const MODEL = process.env.MODEL || '';  // 'michelle' override, default Soldier
const FPS = parseInt(process.env.FPS || '30', 10);
const OUT_MP4 = process.env.OUT_MP4 || resolve(ROOT, 'output', `${SCENE}.mp4`);
const CHROME_PATH = process.env.CHROME_PATH ||
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

async function run() {
  const framesDir = resolve(ROOT, 'output', `${SCENE}_frames`);
  await fs.rm(framesDir, { recursive: true, force: true });
  await fs.mkdir(framesDir, { recursive: true });

  const launchOpts = {
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-dev-shm-usage',
      '--no-first-run',
      '--no-default-browser-check',
      '--allow-file-access-from-files',
      // Chrome 130+: software WebGL via ANGLE+SwiftShader (reemplaza al viejo --use-gl=swiftshader)
      '--use-angle=swiftshader',
      '--enable-unsafe-swiftshader',
    ],
  };
  // Si existe Chrome del sistema (macOS bridge), usarlo. Si no (Linux CI),
  // puppeteer usa su chromium bundled.
  try {
    await fs.access(CHROME_PATH);
    launchOpts.executablePath = CHROME_PATH;
    console.log('[render.js] usando Chrome del sistema:', CHROME_PATH);
  } catch { console.log('[render.js] usando Chromium bundled de puppeteer'); }

  const browser = await puppeteer.launch(launchOpts);
  const page = await browser.newPage();
  page.on('console', msg => console.log('[page]', msg.text()));
  page.on('pageerror', err => console.error('[pageerror]', err.message));
  await page.setViewport({ width: 1080, height: 1920, deviceScaleFactor: 1 });

  let url = 'file://' + resolve(ROOT, 'src', 'scene.html') + '?scene=' + SCENE;
  if (MODEL) url += '&model=' + MODEL;
  console.log('[render.js] navigate →', url);
  await page.goto(url, { waitUntil: 'networkidle0', timeout: 60_000 });
  await page.waitForFunction(() => window.__ready === true, { timeout: 60_000 });

  const duration = await page.evaluate(() => window.getDuration());
  const totalFrames = Math.floor(duration * FPS);
  console.log(`[render.js] scene=${SCENE} duration=${duration}s @${FPS}fps → ${totalFrames} frames`);

  const t0 = Date.now();
  for (let i = 0; i < totalFrames; i++) {
    const t = i / FPS;
    await page.evaluate((t) => window.renderFrame(t), t);
    const buf = await page.screenshot({ type: 'png', omitBackground: false });
    await fs.writeFile(
      resolve(framesDir, `f_${String(i).padStart(5, '0')}.png`),
      buf
    );
    if (i % 30 === 0 || i === totalFrames - 1) {
      const elapsed = ((Date.now() - t0) / 1000).toFixed(1);
      console.log(`  frame ${i+1}/${totalFrames}  (t=${t.toFixed(2)}s, elapsed=${elapsed}s)`);
    }
  }
  await browser.close();
  console.log('[render.js] captura completa — mux ffmpeg');

  // ffmpeg: PNG seq → mp4 vertical 1080x1920
  await fs.mkdir(dirname(OUT_MP4), { recursive: true });
  await new Promise((resolveP, reject) => {
    const ff = spawn('ffmpeg', [
      '-y',
      '-framerate', String(FPS),
      '-i', resolve(framesDir, 'f_%05d.png'),
      '-c:v', 'libx264',
      '-pix_fmt', 'yuv420p',
      '-crf', '20',
      '-preset', 'fast',
      '-movflags', '+faststart',
      OUT_MP4
    ], { stdio: 'inherit' });
    ff.on('exit', code => code === 0 ? resolveP() : reject(new Error('ffmpeg exit ' + code)));
    ff.on('error', reject);
  });

  // Limpieza de frames (ocupan ~100MB por escena)
  if (process.env.KEEP_FRAMES !== '1') {
    await fs.rm(framesDir, { recursive: true, force: true });
  }
  console.log('[render.js] OK →', OUT_MP4);
}

run().catch(e => { console.error('[render.js] FAIL', e); process.exit(1); });
