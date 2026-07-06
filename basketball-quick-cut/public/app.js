const fileInput = document.querySelector('#videoFile');
const player = document.querySelector('#player');
const markStartButton = document.querySelector('#markStart');
const exportButton = document.querySelector('#exportClip');
const startTimeEl = document.querySelector('#startTime');
const currentTimeEl = document.querySelector('#currentTime');
const clipLengthEl = document.querySelector('#clipLength');
const statusEl = document.querySelector('#status');
const resultEl = document.querySelector('#result');
const downloadLink = document.querySelector('#downloadLink');
const outputPathEl = document.querySelector('#outputPath');
const verticalMode = document.querySelector('#verticalMode');
const clipsGrid = document.querySelector('#clipsGrid');
const refreshClipsButton = document.querySelector('#refreshClips');

let uploadedFileName = '';
let startTime = 0;
let isExporting = false;

function formatTime(seconds) {
  const safe = Math.max(0, Number(seconds) || 0);
  const minutes = Math.floor(safe / 60);
  const wholeSeconds = Math.floor(safe % 60);
  const millis = Math.floor((safe - Math.floor(safe)) * 1000);
  return `${String(minutes).padStart(2, '0')}:${String(wholeSeconds).padStart(2, '0')}.${String(millis).padStart(3, '0')}`;
}

function updateReadout() {
  const current = player.currentTime || 0;
  startTimeEl.textContent = formatTime(startTime);
  currentTimeEl.textContent = formatTime(current);
  clipLengthEl.textContent = `${Math.max(0, current - startTime).toFixed(1)}s`;
}

function setStatus(message) {
  statusEl.textContent = message;
}

async function loadClips() {
  try {
    const response = await fetch('/api/clips');
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || '读取片段失败');

    clipsGrid.innerHTML = '';
    if (!data.clips.length) {
      clipsGrid.innerHTML = '<p class="empty-state">还没有保存片段。</p>';
      return;
    }

    data.clips.forEach(clip => {
      const card = document.createElement('article');
      card.className = 'clip-card';
      card.innerHTML = `
        <video controls playsinline preload="metadata" src="${clip.url}"></video>
        <div class="clip-meta">
          <strong title="${clip.fileName}">${clip.fileName}</strong>
          <a href="${clip.url}" download="${clip.fileName}">下载</a>
        </div>
      `;
      clipsGrid.appendChild(card);
    });
  } catch (error) {
    clipsGrid.innerHTML = `<p class="empty-state">${error.message || '读取片段失败'}</p>`;
  }
}

fileInput.addEventListener('change', async () => {
  const file = fileInput.files?.[0];
  if (!file) return;

  resultEl.hidden = true;
  setStatus('正在导入视频...');

  const formData = new FormData();
  formData.append('video', file);

  try {
    const response = await fetch('/api/upload', {
      method: 'POST',
      body: formData
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || '导入失败');

    uploadedFileName = data.fileName;
    player.src = data.url;
    startTime = 0;
    setStatus(`已导入：${data.originalName}`);
    updateReadout();
  } catch (error) {
    setStatus(error.message || '导入失败');
  }
});

player.addEventListener('timeupdate', updateReadout);
player.addEventListener('loadedmetadata', updateReadout);

markStartButton.addEventListener('click', () => {
  markStart();
});

function markStart() {
  startTime = player.currentTime || 0;
  resultEl.hidden = true;
  setStatus(`起点已标记：${formatTime(startTime)}`);
  updateReadout();
}

document.querySelectorAll('[data-nudge]').forEach(button => {
  button.addEventListener('click', () => {
    const delta = Number(button.dataset.nudge);
    player.currentTime = Math.max(0, (player.currentTime || 0) + delta);
    updateReadout();
  });
});

exportButton.addEventListener('click', () => {
  exportClip();
});

async function exportClip() {
  if (isExporting) return;

  if (!uploadedFileName) {
    setStatus('请先选择比赛视频。');
    return;
  }

  const endTime = player.currentTime || 0;
  if (endTime <= startTime) {
    setStatus('当前时间要在起点之后。先播放到片段结束位置，再点导出。');
    return;
  }

  isExporting = true;
  exportButton.disabled = true;
  resultEl.hidden = true;
  setStatus('正在导出片段...');

  try {
    const response = await fetch('/api/export', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        fileName: uploadedFileName,
        start: startTime,
        end: endTime,
    vertical: verticalMode.checked
      })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || '导出失败');

    downloadLink.href = data.url;
    downloadLink.download = data.fileName;
    outputPathEl.textContent = data.outputPath;
    resultEl.hidden = false;
    setStatus(verticalMode.checked ? '竖屏片段导出完成。' : '横屏片段导出完成。');
    await loadClips();
  } catch (error) {
    setStatus(error.message || '导出失败');
  } finally {
    isExporting = false;
    exportButton.disabled = false;
  }
}

document.addEventListener('keydown', event => {
  const target = event.target;
  const isTyping = target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement;
  if (isTyping) return;

  if (event.key.toLowerCase() === 's') {
    event.preventDefault();
    markStart();
  }

  if (event.key.toLowerCase() === 'e') {
    event.preventDefault();
    exportClip();
  }
});

refreshClipsButton.addEventListener('click', loadClips);

updateReadout();
loadClips();
