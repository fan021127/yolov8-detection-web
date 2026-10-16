// ========== 目标检测页面逻辑 ==========

let selectedFile = null;
let currentResultUrl = null;
let chartInstance = null;

const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const fileIcon = document.getElementById('fileIcon');
const detectBtn = document.getElementById('detectBtn');
const confSlider = document.getElementById('confSlider');
const confValue = document.getElementById('confValue');
const resultPreview = document.getElementById('resultPreview');
const resultActions = document.getElementById('resultActions');
const statsSection = document.getElementById('statsSection');
const loading = document.getElementById('loading');
const progressContainer = document.getElementById('progressContainer');
const progressFill = document.getElementById('progressFill');
const progressPercent = document.getElementById('progressPercent');
const toast = document.getElementById('toast');

// ========== 退出登录 ==========
document.getElementById('logoutBtn').addEventListener('click', async () => {
    await fetch('/logout');
    window.location.href = '/';
});

// ========== Toast 提示 ==========
function showToast(msg, type = '') {
    toast.textContent = msg;
    toast.className = `toast ${type}`;
    toast.classList.remove('hidden');
    setTimeout(() => toast.classList.add('hidden'), 3000);
}

// ========== 置信度滑块 ==========
confSlider.addEventListener('input', () => {
    confValue.textContent = confSlider.value;
});

// ========== 文件上传 ==========
uploadArea.addEventListener('click', () => fileInput.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
        handleFile(e.dataTransfer.files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

function handleFile(file) {
    selectedFile = file;
    const isVideo = file.type.startsWith('video/');
    fileIcon.textContent = isVideo ? '🎬' : '🖼️';
    fileName.textContent = file.name;
    fileSize.textContent = formatSize(file.size);
    fileInfo.classList.remove('hidden');
    detectBtn.disabled = false;

    // 重置结果区
    resetResults();
}

function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
}

document.getElementById('removeFile').addEventListener('click', () => {
    selectedFile = null;
    fileInput.value = '';
    fileInfo.classList.add('hidden');
    detectBtn.disabled = true;
    resetResults();
});

function resetResults() {
    resultPreview.innerHTML = `
        <div class="placeholder">
            <div class="placeholder-icon">🔍</div>
            <p>上传文件并点击"开始检测"查看结果</p>
        </div>`;
    resultActions.classList.add('hidden');
    statsSection.classList.add('hidden');
    progressContainer.classList.add('hidden');
    currentResultUrl = null;
}

// ========== 开始检测 ==========
detectBtn.addEventListener('click', () => {
    if (!selectedFile) return;

    const isVideo = selectedFile.type.startsWith('video/');
    if (isVideo) {
        detectVideo();
    } else {
        detectImage();
    }
});

// ---------- 图片检测 ----------
async function detectImage() {
    detectBtn.disabled = true;
    loading.classList.remove('hidden');

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('conf_threshold', confSlider.value);

    try {
        const res = await fetch('/api/detect/image', {
            method: 'POST',
            body: formData,
        });
        const data = await res.json();

        if (data.success) {
            showResult(data.result_url, 'image', data.detection);
            showToast('检测完成！', 'success');
        } else {
            showToast(data.message || '检测失败', 'error');
        }
    } catch (e) {
        console.error('检测出错:', e);
        showToast('检测出错: ' + (e.message || e), 'error');
    } finally {
        loading.classList.add('hidden');
        detectBtn.disabled = false;
    }
}

// ---------- 视频检测 ----------
async function detectVideo() {
    detectBtn.disabled = true;
    progressContainer.classList.remove('hidden');
    progressFill.style.width = '0%';
    progressPercent.textContent = '0%';

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('conf_threshold', confSlider.value);

    try {
        const res = await fetch('/api/detect/video', {
            method: 'POST',
            body: formData,
        });
        const data = await res.json();

        if (!data.success) {
            showToast(data.message || '上传失败', 'error');
            detectBtn.disabled = false;
            progressContainer.classList.add('hidden');
            return;
        }

        const taskId = data.task_id;
        const recordId = data.record_id;

        // 轮询进度
        const poll = setInterval(async () => {
            try {
                const progRes = await fetch(`/api/video/progress/${taskId}`);
                const progData = await progRes.json();
                const task = progData.task;

                progressFill.style.width = task.progress + '%';
                progressPercent.textContent = task.progress + '%';

                if (task.status === 'done') {
                    clearInterval(poll);
                    // 通知后端完成
                    const completeRes = await fetch(`/api/video/complete/${taskId}/${recordId}`, { method: 'POST' });
                    const completeData = await completeRes.json();

                    if (completeData.success) {
                        showResult(completeData.result_url, 'video', {
                            class_counts: completeData.class_counts,
                            total_objects: completeData.total_objects,
                            detections: [],
                        });
                        showToast('视频检测完成！', 'success');
                    } else {
                        showToast('视频处理完成但保存失败', 'error');
                    }
                    detectBtn.disabled = false;
                } else if (task.status === 'failed') {
                    clearInterval(poll);
                    showToast(task.error || '视频处理失败', 'error');
                    detectBtn.disabled = false;
                    progressContainer.classList.add('hidden');
                }
            } catch (e) {
                // 忽略轮询错误
            }
        }, 1500);

    } catch (e) {
        console.error('视频检测出错:', e);
        showToast('出错: ' + (e.message || e), 'error');
        detectBtn.disabled = false;
        progressContainer.classList.add('hidden');
    }
}

// ========== 展示结果 ==========
function showResult(url, type, detection) {
    currentResultUrl = url;

    if (type === 'image') {
        resultPreview.innerHTML = `<img src="${url}" alt="检测结果">`;
    } else {
        resultPreview.innerHTML = `<video src="${url}" controls autoplay loop></video>`;
    }

    resultActions.classList.remove('hidden');
    statsSection.classList.remove('hidden');

    // 统计数字
    document.getElementById('totalObjects').textContent = detection.total_objects;
    const classCounts = detection.class_counts || {};
    document.getElementById('classCount').textContent = Object.keys(classCounts).length;

    // 类别标签
    const classList = document.getElementById('classList');
    classList.innerHTML = '';
    Object.entries(classCounts).sort((a, b) => b[1] - a[1]).forEach(([name, count]) => {
        const tag = document.createElement('span');
        tag.className = 'class-tag';
        tag.innerHTML = `<span class="tag-name">${name}</span><span class="tag-count">${count}</span>`;
        classList.appendChild(tag);
    });

    // ECharts 饼图
    renderChart(classCounts);
}

function renderChart(classCounts) {
    // 容错：如果 ECharts 库未加载，跳过图表渲染，不影响其他结果展示
    if (typeof echarts === 'undefined') {
        console.warn('ECharts 未加载，跳过图表渲染');
        const chartDom = document.getElementById('chartContainer');
        chartDom.innerHTML = '<div style="text-align:center;color:#999;padding:40px 0;font-size:13px">图表库加载失败，请检查网络后刷新</div>';
        return;
    }

    try {
        const chartDom = document.getElementById('chartContainer');
        if (chartInstance) {
            chartInstance.dispose();
        }
        chartInstance = echarts.init(chartDom);

        const data = Object.entries(classCounts).map(([name, value]) => ({ name, value }));
        if (data.length === 0) {
            chartDom.innerHTML = '<div style="text-align:center;color:#999;padding:40px 0;font-size:13px">未检测到目标物体</div>';
            return;
        }

        const option = {
            tooltip: {
                trigger: 'item',
                formatter: '{b}: {c} ({d}%)',
            },
            legend: {
                orient: 'vertical',
                right: 10,
                top: 'center',
                textStyle: { fontSize: 12 },
            },
            series: [{
                name: '物体类别分布',
                type: 'pie',
                radius: ['40%', '70%'],
                center: ['38%', '50%'],
                avoidLabelOverlap: true,
                itemStyle: {
                    borderRadius: 6,
                    borderColor: '#fff',
                    borderWidth: 2,
                },
                label: { show: false },
                emphasis: {
                    label: { show: true, fontSize: 14, fontWeight: 'bold' },
                },
                data: data,
                color: ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b',
                        '#fa709a', '#fee140', '#30cfd0', '#ff9a9e', '#a18cd1'],
            }],
        };

        chartInstance.setOption(option);
        window.addEventListener('resize', () => { if (chartInstance) chartInstance.resize(); });
    } catch (err) {
        console.error('图表渲染失败:', err);
        document.getElementById('chartContainer').innerHTML =
            '<div style="text-align:center;color:#999;padding:40px 0;font-size:13px">图表渲染失败</div>';
    }
}

// ========== 下载结果 ==========
document.getElementById('downloadBtn').addEventListener('click', () => {
    if (currentResultUrl) {
        const filename = currentResultUrl.split('/').pop();
        window.location.href = `/api/download/${filename}`;
    }
});
