import express from 'express';
import ffmpegPath from 'ffmpeg-static';
import multer from 'multer';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const port = Number(process.env.PORT || 5177);
const uploadDir = path.join(__dirname, 'uploads');
const outputDir = path.join(__dirname, 'exports');

fs.mkdirSync(uploadDir, { recursive: true });
fs.mkdirSync(outputDir, { recursive: true });

const storage = multer.diskStorage({
  destination: uploadDir,
  filename: (_req, file, cb) => {
    const safeBase = path.basename(file.originalname).replace(/[^\w.\-\u4e00-\u9fa5]/g, '_');
    cb(null, `${Date.now()}-${safeBase}`);
  }
});

const upload = multer({ storage });

app.use(express.json({ limit: '1mb' }));
app.use('/uploads', express.static(uploadDir));
app.use('/exports', express.static(outputDir));
app.use(express.static(path.join(__dirname, 'public')));

function assertInside(root, candidate) {
  const resolved = path.resolve(root, candidate);
  if (!resolved.startsWith(path.resolve(root))) {
    throw new Error('Invalid path');
  }
  return resolved;
}

function toSeconds(value) {
  const number = Number(value);
  if (!Number.isFinite(number) || number < 0) return 0;
  return number;
}

app.post('/api/upload', upload.single('video'), (req, res) => {
  if (!req.file) {
    res.status(400).json({ error: '请选择视频文件' });
    return;
  }

  res.json({
    fileName: req.file.filename,
    originalName: req.file.originalname,
    url: `/uploads/${encodeURIComponent(req.file.filename)}`
  });
});

app.post('/api/export', (req, res) => {
  try {
    const { fileName, start, end, vertical } = req.body;
    if (!fileName) {
      res.status(400).json({ error: '请先上传视频' });
      return;
    }

    const inputPath = assertInside(uploadDir, fileName);
    if (!fs.existsSync(inputPath)) {
      res.status(404).json({ error: '找不到原视频' });
      return;
    }

    const startSec = toSeconds(start);
    const endSec = toSeconds(end);
    const duration = Math.max(0, endSec - startSec);
    if (duration < 0.3) {
      res.status(400).json({ error: '片段太短，请至少选择0.3秒以上' });
      return;
    }

    const stamp = new Date().toISOString().replace(/[:.]/g, '-');
    const outputName = `clip-${stamp}-${Math.round(startSec * 1000)}-${Math.round(endSec * 1000)}.mp4`;
    const outputPath = path.join(outputDir, outputName);

    const args = [
      '-y',
      '-ss', String(startSec),
      '-i', inputPath,
      '-t', String(duration)
    ];

    if (vertical) {
      args.push(
        '-vf',
        'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920',
        '-c:v',
        'libx264',
        '-preset',
        'veryfast',
        '-crf',
        '20',
        '-c:a',
        'aac',
        '-b:a',
        '160k'
      );
    } else {
      args.push('-c', 'copy');
    }

    args.push(outputPath);

    const child = spawn(ffmpegPath, args);
    let stderr = '';
    child.stderr.on('data', chunk => {
      stderr += chunk.toString();
    });

    child.on('close', code => {
      if (code !== 0) {
        res.status(500).json({
          error: '导出失败',
          detail: stderr.slice(-2000)
        });
        return;
      }

      res.json({
        fileName: outputName,
        url: `/exports/${encodeURIComponent(outputName)}`,
        outputPath
      });
    });
  } catch (error) {
    res.status(500).json({ error: error.message || '导出失败' });
  }
});

app.get('/api/clips', (_req, res) => {
  const clips = fs.readdirSync(outputDir)
    .filter(fileName => fileName.toLowerCase().endsWith('.mp4'))
    .map(fileName => {
      const fullPath = path.join(outputDir, fileName);
      const stat = fs.statSync(fullPath);
      return {
        fileName,
        url: `/exports/${encodeURIComponent(fileName)}`,
        createdAt: stat.birthtimeMs || stat.mtimeMs
      };
    })
    .sort((a, b) => b.createdAt - a.createdAt);

  res.json({ clips });
});

app.get('/api/health', (_req, res) => {
  res.json({ ok: true, ffmpeg: Boolean(ffmpegPath) });
});

app.listen(port, () => {
  console.log(`Basketball Quick Cut running at http://localhost:${port}`);
});
