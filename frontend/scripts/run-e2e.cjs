const { spawn, spawnSync } = require('node:child_process');
const path = require('node:path');

const PORT = 4201;
const URL = `http://127.0.0.1:${PORT}`;
const root = path.join(__dirname, '..');

const server = spawn(
  process.execPath,
  [path.join(root, 'node_modules/@angular/cli/bin/ng.js'), 'serve', '--port', String(PORT), '--host', '127.0.0.1'],
  { cwd: root, stdio: ['ignore', 'pipe', 'pipe'] }
);
let serverOutput = '';
server.stdout.on('data', (chunk) => { serverOutput += chunk; });
server.stderr.on('data', (chunk) => { serverOutput += chunk; });

function stopServer() {
  if (server.exitCode !== null) return;
  if (process.platform === 'win32') spawnSync('taskkill', ['/pid', String(server.pid), '/T', '/F']);
  else server.kill('SIGTERM');
}

async function waitForServer(timeoutMs = 180000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (server.exitCode !== null) throw new Error('Angular dev server stopped:\n' + serverOutput);
    try {
      if ((await fetch(URL)).ok) return;
    } catch {
    }
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }
  throw new Error('Angular dev server did not start in time:\n' + serverOutput);
}

(async () => {
  try {
    await waitForServer();
    const env = { ...process.env, E2E_HEADED: process.argv.includes('--prikazi') ? '1' : '0' };
    const test = spawnSync(process.execPath, [path.join(__dirname, 'check-chart.cjs')], { cwd: root, stdio: 'inherit', env });
    process.exitCode = test.status ?? 1;
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  } finally {
    stopServer();
  }
})();
