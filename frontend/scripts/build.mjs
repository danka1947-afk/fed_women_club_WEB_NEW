import { mkdir, copyFile, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, '..');
const dist = join(root, 'dist');

await mkdir(join(dist, 'src'), { recursive: true });
await copyFile(join(root, 'index.html'), join(dist, 'index.html'));
await copyFile(join(root, 'src', 'main.js'), join(dist, 'src', 'main.js'));
await copyFile(join(root, 'src', 'styles.css'), join(dist, 'src', 'styles.css'));
await writeFile(join(dist, 'build-info.json'), JSON.stringify({ builtAt: new Date().toISOString() }, null, 2));
console.log('frontend build completed');
