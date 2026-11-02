/*
  打卡机前端逻辑
  流程：打开摄像头 → 每 120ms 采样一帧算质量 → 连续达标后自动抓拍
       → POST /api/v1/kiosk/verify（1:1 比对桩）→ 显示结果 → 自动进入下一位

  为什么质量判定放前端：只做「亮度 / 清晰度 / 是否乱动」这类像素级判断，
  不需要人脸模型，浏览器就能算；「有没有人脸」由后端人脸检测负责（返回 3001 提示重拍），
  这样前端零模型依赖，教室断网也能跑。
*/
(function () {
  'use strict';

  // ---------- DOM ----------
  const $ = (id) => document.getElementById(id);
  const video = $('video');
  const progressEl = $('progress');
  const nameEl = $('stu-name');
  const noEl = $('stu-no');
  const lampEl = $('quality');
  const hintEl = $('hint');
  const bannerEl = $('banner');
  const summaryEl = $('summary');
  const summaryTextEl = $('summary-text');
  const resetBtn = $('reset-btn');

  // ---------- 采样参数 ----------
  const SAMPLE_W = 160;         // 采样画布宽（小尺寸即可判断质量）
  const SAMPLE_H = 120;
  const TICK_MS = 120;          // 采样间隔
  const STABLE_FRAMES = 8;      // 连续达标帧数，约 1 秒
  const BRIGHT_MIN = 60;        // 过暗
  const BRIGHT_MAX = 205;       // 过曝
  const SHARP_MIN = 40;         // 拉普拉斯方差下限（越低越模糊）
  const STILL_MAX = 4;          // 相邻帧平均灰度差上限（越大说明在乱动）

  const work = document.createElement('canvas');
  work.width = SAMPLE_W;
  work.height = SAMPLE_H;
  const workCtx = work.getContext('2d', { willReadFrequently: true });

  let lastGray = null;    // 上一帧灰度，用于判断是否保持不动
  let stableCount = 0;    // 连续达标帧数
  let busy = false;       // 正在上传/比对
  let cameraReady = false;
  let finished = false;   // 名单已走完

  // ---------- 摄像头 ----------
  async function startCamera() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setLamp('bad', '浏览器不支持摄像头');
      setHint('请用 Chrome / Edge 100+ 打开本页面');
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: 'user' },
        audio: false,
      });
      video.srcObject = stream;
      await video.play();
      cameraReady = true;
      setHint('请把面部放进虚线框内，保持不动会自动抓拍');
    } catch (error) {
      // NotAllowedError：拒绝了权限；NotFoundError：没有摄像头；SecurityError：非安全上下文
      const tips = {
        NotAllowedError: '已拒绝摄像头权限，请点地址栏的相机图标重新允许',
        NotFoundError: '没有检测到摄像头设备',
        SecurityError: '必须用 http://127.0.0.1:5000 打开，局域网 IP 下浏览器不给摄像头',
      };
      setLamp('bad', tips[error.name] || ('摄像头启动失败：' + error.name));
      setHint('提示：打卡机就跑在这台笔记本上，用 localhost 访问');
    }
  }

  // ---------- 图像质量 ----------
  function sampleGray() {
    workCtx.drawImage(video, 0, 0, SAMPLE_W, SAMPLE_H);
    const data = workCtx.getImageData(0, 0, SAMPLE_W, SAMPLE_H).data;
    const gray = new Uint8ClampedArray(SAMPLE_W * SAMPLE_H);
    let sum = 0;
    for (let i = 0, j = 0; i < data.length; i += 4, j += 1) {
      const g = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
      gray[j] = g;
      sum += g;
    }
    return { gray, brightness: sum / (SAMPLE_W * SAMPLE_H) };
  }

  // 拉普拉斯算子方差：值越小说明画面越模糊
  function laplacianVariance(gray) {
    let sum = 0;
    let sumSq = 0;
    let count = 0;
    for (let y = 1; y < SAMPLE_H - 1; y += 1) {
      for (let x = 1; x < SAMPLE_W - 1; x += 1) {
        const i = y * SAMPLE_W + x;
        const v = 4 * gray[i] - gray[i - 1] - gray[i + 1] - gray[i - SAMPLE_W] - gray[i + SAMPLE_W];
        sum += v;
        sumSq += v * v;
        count += 1;
      }
    }
    const mean = sum / count;
    return sumSq / count - mean * mean;
  }

  // 相邻两帧的平均灰度差：用来判断学生是否站稳
  function frameDiff(a, b) {
    let sum = 0;
    for (let i = 0; i < a.length; i += 1) sum += Math.abs(a[i] - b[i]);
    return sum / a.length;
  }

  // ---------- 采样主循环 ----------
  function tick() {
    if (!cameraReady || busy || finished || video.videoWidth === 0) return;

    const { gray, brightness } = sampleGray();
    const sharpness = laplacianVariance(gray);
    const diff = lastGray ? frameDiff(gray, lastGray) : 999;
    lastGray = gray;

    const lightOk = brightness > BRIGHT_MIN && brightness < BRIGHT_MAX;
    const sharpOk = sharpness > SHARP_MIN;
    const stillOk = diff < STILL_MAX;

    if (lightOk && sharpOk && stillOk) {
      stableCount += 1;
      setLamp('good', '质量良好，保持不动');
      if (stableCount >= STABLE_FRAMES) {
        stableCount = 0;
        capture();
      }
      return;
    }

    stableCount = 0;
    if (!lightOk) {
      setLamp('bad', brightness <= BRIGHT_MIN ? '光线太暗，请面向光源' : '画面过亮，请避开强光');
    } else if (!sharpOk) {
      setLamp('bad', '画面模糊，请靠近一点或擦一下镜头');
    } else {
      setLamp('bad', '请站稳，不要晃动');
    }
  }

  // ---------- 抓拍并上传 ----------
  async function capture(mockFail) {
    if (busy || finished || !cameraReady) return;
    busy = true;
    setLamp('busy', '正在比对，请稍候…');

    // 用原始分辨率抓一帧，转 jpeg 上传
    const full = document.createElement('canvas');
    full.width = video.videoWidth;
    full.height = video.videoHeight;
    full.getContext('2d').drawImage(video, 0, 0, full.width, full.height);
    const blob = await new Promise((resolve) => full.toBlob(resolve, 'image/jpeg', 0.9));

    const form = new FormData();
    form.append('file', blob, 'capture.jpg');

    const url = '/api/v1/kiosk/verify' + (mockFail ? '?mock=fail' : '');
    try {
      const response = await fetch(url, { method: 'POST', body: form });
      const payload = await response.json();
      if (payload.code !== 0) {
        showBanner('bad', payload.message || '比对失败');
        setLamp('bad', '请重试');
      } else {
        const result = payload.data;
        const similarity = Number(result.similarity).toFixed(4);
        showBanner(result.passed ? 'good' : 'bad',
          (result.passed ? '签到成功 · ' : '未通过 · ') + result.suggestion);
        setLamp(result.passed ? 'good' : 'bad',
          '相似度 ' + similarity + '（阈值 ' + Number(result.threshold).toFixed(2) + '，当前为桩结果）');
        renderState(result.next);
      }
    } catch (error) {
      showBanner('bad', '上传失败，请检查服务是否还在运行');
      setLamp('bad', '上传失败：' + error.message);
    } finally {
      // 结果条停留 1.2 秒再恢复采样
      setTimeout(() => {
        hideBanner();
        busy = false;
      }, 1200);
    }
  }

  // ---------- 缺勤 / 重置 ----------
  async function skip() {
    if (busy || finished) return;
    busy = true;
    try {
      const response = await fetch('/api/v1/kiosk/skip', { method: 'POST' });
      const payload = await response.json();
      if (payload.code === 0) {
        showBanner('bad', '已记为缺勤');
        renderState(payload.data.next);
      } else {
        showBanner('bad', payload.message);
      }
    } finally {
      setTimeout(() => { hideBanner(); busy = false; }, 900);
    }
  }

  async function reset() {
    await fetch('/api/v1/kiosk/reset', { method: 'POST' });
    summaryEl.hidden = true;
    busy = false;
    finished = false;
    await loadState();
  }

  // ---------- 状态渲染 ----------
  function renderState(state) {
    if (!state) return;
    finished = Boolean(state.done);
    progressEl.textContent = state.done
      ? '已完成 ' + state.total + ' / ' + state.total
      : '第 ' + (state.index + 1) + ' / ' + state.total + ' 位';

    if (state.done) {
      nameEl.textContent = '名单已走完';
      noEl.textContent = '出勤 ' + state.present + ' / ' + state.total;
      summaryTextEl.textContent =
        '出勤 ' + state.present + ' 人　待核实 ' +
        state.records.filter((r) => r.status === '待核实').length + ' 人　缺勤 ' +
        state.records.filter((r) => r.status === '缺勤').length + ' 人';
      summaryEl.hidden = false;
      return;
    }

    nameEl.textContent = state.current.name;
    noEl.textContent = '学号 ' + state.current.student_no;
  }

  async function loadState() {
    try {
      const response = await fetch('/api/v1/kiosk/current');
      const payload = await response.json();
      if (payload.code === 0) renderState(payload.data);
      else setLamp('bad', payload.message);
    } catch (error) {
      setLamp('bad', '无法连接服务：' + error.message);
    }
  }

  // ---------- 小工具 ----------
  function setLamp(kind, text) {
    lampEl.className = 'lamp ' + kind;
    lampEl.textContent = text;
  }
  function setHint(text) { hintEl.textContent = text; }
  function showBanner(kind, text) {
    bannerEl.className = 'banner ' + kind;
    bannerEl.textContent = text;
  }
  function hideBanner() { bannerEl.className = 'banner'; bannerEl.textContent = ''; }

  // ---------- 键盘：Enter 抓拍、空格缺勤、R 重置 ----------
  document.addEventListener('keydown', (event) => {
    if (event.code === 'Enter') { event.preventDefault(); capture(false); }
    else if (event.code === 'Space') { event.preventDefault(); skip(); }
    else if (event.key === 'r' || event.key === 'R') { event.preventDefault(); reset(); }
  });

  resetBtn.addEventListener('click', reset);

  // ---------- 启动 ----------
  loadState().then(startCamera);
  setInterval(tick, TICK_MS);
})();
