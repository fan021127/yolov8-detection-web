// ========== 历史记录页面逻辑 ==========

let currentPage = 1;
const pageSize = 10;
let editingRecordId = null;

const tableBody = document.getElementById('recordTableBody');
const pagination = document.getElementById('pagination');
const toast = document.getElementById('toast');
const remarkModal = document.getElementById('remarkModal');
const detailModal = document.getElementById('detailModal');

// ========== 退出登录 ==========
document.getElementById('logoutBtn').addEventListener('click', async () => {
    await fetch('/logout');
    window.location.href = '/';
});

// ========== Toast ==========
function showToast(msg, type = '') {
    toast.textContent = msg;
    toast.className = `toast ${type}`;
    toast.classList.remove('hidden');
    setTimeout(() => toast.classList.add('hidden'), 3000);
}

// ========== 加载记录 ==========
async function loadRecords(page = 1) {
    currentPage = page;
    tableBody.innerHTML = '<tr><td colspan="9" class="loading-cell">加载中...</td></tr>';

    try {
        const res = await fetch(`/api/history?page=${page}&page_size=${pageSize}`);
        const data = await res.json();

        if (!data.success) {
            tableBody.innerHTML = '<tr><td colspan="9" class="empty-cell">加载失败</td></tr>';
            return;
        }

        renderTable(data.records);
        renderPagination(data.pagination);
    } catch (e) {
        tableBody.innerHTML = '<tr><td colspan="9" class="empty-cell">网络错误</td></tr>';
    }
}

function renderTable(records) {
    if (records.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="9" class="empty-cell">暂无检测记录，去上传一张图片试试吧~</td></tr>';
        return;
    }

    tableBody.innerHTML = records.map(r => `
        <tr>
            <td>${r.id}</td>
            <td class="file-name-cell" title="${r.file_name}">${r.file_name}</td>
            <td><span class="type-tag ${r.file_type === 'image' ? 'type-image' : 'type-video'}">
                ${r.file_type === 'image' ? '图片' : '视频'}
            </span></td>
            <td><strong>${r.total_objects}</strong></td>
            <td>${r.conf_threshold}</td>
            <td class="remark-cell" title="${r.remark || ''}">${r.remark || '-'}</td>
            <td><span class="status-tag status-${r.status}">${statusText(r.status)}</span></td>
            <td>${r.created_at}</td>
            <td>
                <button class="action-btn btn-view" onclick="viewDetail(${r.id})">查看</button>
                <button class="action-btn btn-edit" onclick="editRemark(${r.id}, '${(r.remark || '').replace(/'/g, "\\'")}')">备注</button>
                <button class="action-btn btn-delete" onclick="deleteRecord(${r.id})">删除</button>
            </td>
        </tr>
    `).join('');
}

function statusText(status) {
    const map = { completed: '已完成', processing: '处理中', failed: '失败', pending: '等待中' };
    return map[status] || status;
}

function renderPagination(pg) {
    if (pg.total_pages <= 1) {
        pagination.innerHTML = `<span class="page-info">共 ${pg.total} 条记录</span>`;
        return;
    }

    let html = `<button class="page-btn" onclick="loadRecords(${currentPage - 1})" ${currentPage <= 1 ? 'disabled' : ''}>上一页</button>`;

    const maxShow = 7;
    let start = Math.max(1, currentPage - 3);
    let end = Math.min(pg.total_pages, start + maxShow - 1);
    if (end - start < maxShow - 1) start = Math.max(1, end - maxShow + 1);

    for (let i = start; i <= end; i++) {
        html += `<button class="page-btn ${i === currentPage ? 'active' : ''}" onclick="loadRecords(${i})">${i}</button>`;
    }

    html += `<button class="page-btn" onclick="loadRecords(${currentPage + 1})" ${currentPage >= pg.total_pages ? 'disabled' : ''}>下一页</button>`;
    html += `<span class="page-info">第 ${currentPage}/${pg.total_pages} 页，共 ${pg.total} 条</span>`;

    pagination.innerHTML = html;
}

// ========== 查看详情 ==========
async function viewDetail(recordId) {
    try {
        const res = await fetch(`/api/history/${recordId}`);
        const data = await res.json();
        if (!data.success) {
            showToast('获取详情失败', 'error');
            return;
        }
        const r = data.record;
        const det = r.detection_json || {};
        const classCounts = det.class_counts || {};

        let classHtml = '';
        if (Object.keys(classCounts).length > 0) {
            classHtml = '<div class="detail-class-list">' +
                Object.entries(classCounts).map(([k, v]) =>
                    `<span class="class-tag"><span class="tag-name">${k}</span><span class="tag-count">${v}</span></span>`
                ).join('') + '</div>';
        } else {
            classHtml = '<span style="color:#999">无</span>';
        }

        document.getElementById('detailContent').innerHTML = `
            <div class="detail-section">
                <h4>基本信息</h4>
                <div class="detail-grid">
                    <div class="detail-item"><span class="label">记录ID：</span><span class="value">${r.id}</span></div>
                    <div class="detail-item"><span class="label">文件名：</span><span class="value">${r.file_name}</span></div>
                    <div class="detail-item"><span class="label">类型：</span><span class="value">${r.file_type === 'image' ? '图片' : '视频'}</span></div>
                    <div class="detail-item"><span class="label">状态：</span><span class="value">${statusText(r.status)}</span></div>
                    <div class="detail-item"><span class="label">置信度：</span><span class="value">${r.conf_threshold}</span></div>
                    <div class="detail-item"><span class="label">物体总数：</span><span class="value">${r.total_objects}</span></div>
                    <div class="detail-item" style="grid-column:1/-1"><span class="label">检测时间：</span><span class="value">${r.created_at}</span></div>
                    <div class="detail-item" style="grid-column:1/-1"><span class="label">备注：</span><span class="value">${r.remark || '无'}</span></div>
                </div>
            </div>
            <div class="detail-section">
                <h4>检测到的物体类别</h4>
                ${classHtml}
            </div>
            ${r.result_path ? `
            <div class="detail-section">
                <h4>结果文件</h4>
                <a href="/static/${r.result_path}" target="_blank" style="color:#667eea">点击查看 /下载结果</a>
            </div>` : ''}
        `;
        detailModal.classList.remove('hidden');
    } catch (e) {
        showToast('网络错误', 'error');
    }
}

document.getElementById('closeDetail').addEventListener('click', () => {
    detailModal.classList.add('hidden');
});

// ========== 编辑备注 ==========
function editRemark(recordId, currentRemark) {
    editingRecordId = recordId;
    document.getElementById('remarkText').value = currentRemark || '';
    remarkModal.classList.remove('hidden');
}

document.getElementById('cancelRemark').addEventListener('click', () => {
    remarkModal.classList.add('hidden');
    editingRecordId = null;
});

document.getElementById('saveRemark').addEventListener('click', async () => {
    const remark = document.getElementById('remarkText').value.trim();
    if (!editingRecordId) return;

    try {
        const res = await fetch(`/api/history/${editingRecordId}/remark`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ remark }),
        });
        const data = await res.json();
        if (data.success) {
            showToast('备注已更新', 'success');
            remarkModal.classList.add('hidden');
            editingRecordId = null;
            loadRecords(currentPage);
        } else {
            showToast(data.message || '更新失败', 'error');
        }
    } catch (e) {
        showToast('网络错误', 'error');
    }
});

// ========== 删除记录 ==========
async function deleteRecord(recordId) {
    if (!confirm('确定要删除这条记录吗？此操作不可恢复。')) return;

    try {
        const res = await fetch(`/api/history/${recordId}`, { method: 'DELETE' });
        const data = await res.json();
        if (data.success) {
            showToast('已删除', 'success');
            loadRecords(currentPage);
        } else {
            showToast(data.message || '删除失败', 'error');
        }
    } catch (e) {
        showToast('网络错误', 'error');
    }
}

// ========== 导出 Excel ==========
document.getElementById('exportBtn').addEventListener('click', () => {
    window.location.href = '/api/export/excel';
});

// 点击遮罩关闭弹窗
remarkModal.addEventListener('click', (e) => {
    if (e.target === remarkModal) remarkModal.classList.add('hidden');
});
detailModal.addEventListener('click', (e) => {
    if (e.target === detailModal) detailModal.classList.add('hidden');
});

// 初始化
loadRecords(1);
