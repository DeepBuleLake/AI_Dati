/**
 * 智能答题助手(DatiAI) - 前端交互脚本
 * 处理UI交互、API调用和数据刷新
 */

// DOM 元素
const elements = {
    // 按钮
    btnStart: document.getElementById('btnStart'),
    btnStop: document.getElementById('btnStop'),
    btnScreenshot: document.getElementById('btnScreenshot'),
    btnRecognize: document.getElementById('btnRecognize'),
    btnClearHistory: document.getElementById('btnClearHistory'),
    
    // 显示区域
    currentScreenshot: document.getElementById('currentScreenshot'),
    resultContent: document.getElementById('resultContent'),
    statusMessages: document.getElementById('statusMessages'),
    historyList: document.getElementById('historyList'),
    serviceStatus: document.getElementById('serviceStatus'),
    currentTime: document.getElementById('currentTime'),
    
    // 模态框
    modal: document.getElementById('modal'),
    modalTitle: document.getElementById('modalTitle'),
    modalBody: document.getElementById('modalBody'),
    modalClose: document.getElementById('modalClose'),
    
    // 加载动画
    loadingOverlay: document.getElementById('loadingOverlay'),
    loadingText: document.getElementById('loadingText')
};

// 全局状态
const state = {
    isRunning: false,
    lastScreenshot: null,
    lastResult: null,
    refreshInterval: null,
    refreshRate: 2000, // 刷新间隔（毫秒）
};

// ===== 初始化 =====
function init() {
    // 绑定按钮事件
    elements.btnStart.addEventListener('click', startService);
    elements.btnStop.addEventListener('click', stopService);
    elements.btnScreenshot.addEventListener('click', takeScreenshot);
    elements.btnRecognize.addEventListener('click', recognizeImage);
    elements.btnClearHistory.addEventListener('click', clearHistory);
    elements.modalClose.addEventListener('click', closeModal);
    
    // 创建一个占位图像
    createPlaceholderImage();
    
    // 初始加载数据
    refreshStatus();
    loadHistory();
    
    // 设置自动刷新
    startAutoRefresh();
    
    console.log('应用初始化完成');
}

// 创建占位图像
function createPlaceholderImage() {
    const canvas = document.createElement('canvas');
    canvas.width = 400;
    canvas.height = 300;
    const ctx = canvas.getContext('2d');
    
    // 填充背景
    ctx.fillStyle = '#2d2d2d';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // 绘制文字
    ctx.fillStyle = '#707070';
    ctx.font = 'italic 16px "Segoe UI"';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('尚未进行截图', canvas.width / 2, canvas.height / 2);
    
    // 设置为占位图像
    try {
        const dataUrl = canvas.toDataURL('image/png');
        elements.currentScreenshot.src = dataUrl;
    } catch (error) {
        console.error('创建占位图像失败:', error);
    }
}

// ===== 自动刷新 =====
function startAutoRefresh() {
    if (state.refreshInterval) {
        clearInterval(state.refreshInterval);
    }
    
    state.refreshInterval = setInterval(() => {
        refreshStatus();
        updateCurrentTime();
    }, state.refreshRate);
}

function stopAutoRefresh() {
    if (state.refreshInterval) {
        clearInterval(state.refreshInterval);
        state.refreshInterval = null;
    }
}

// ===== API 调用 =====
// 获取当前状态
async function refreshStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        updateStatusUI(data);
    } catch (error) {
        console.error('获取状态失败:', error);
        addStatusMessage('获取状态失败: ' + error.message);
    }
}

// 启动服务
async function startService() {
    showLoading('正在启动服务...');
    
    try {
        const response = await fetch('/api/start', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            state.isRunning = true;
            updateServiceStatusUI(true);
            addStatusMessage('服务已启动');
        } else {
            addStatusMessage('启动服务失败: ' + data.error);
        }
    } catch (error) {
        console.error('启动服务失败:', error);
        addStatusMessage('启动服务失败: ' + error.message);
    } finally {
        hideLoading();
    }
}

// 停止服务
async function stopService() {
    showLoading('正在停止服务...');
    
    try {
        const response = await fetch('/api/stop', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            state.isRunning = false;
            updateServiceStatusUI(false);
            addStatusMessage('服务已停止');
        } else {
            addStatusMessage('停止服务失败: ' + data.error);
        }
    } catch (error) {
        console.error('停止服务失败:', error);
        addStatusMessage('停止服务失败: ' + error.message);
    } finally {
        hideLoading();
    }
}

// 手动截图
async function takeScreenshot() {
    showLoading('正在截图...');
    
    try {
        const response = await fetch('/api/screenshot', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            addStatusMessage('截图成功: ' + data.filepath);
            // 刷新状态以获取新的截图
            setTimeout(refreshStatus, 500);
        } else {
            addStatusMessage('截图失败: ' + data.error);
        }
    } catch (error) {
        console.error('截图失败:', error);
        addStatusMessage('截图失败: ' + error.message);
    } finally {
        hideLoading();
    }
}

// 识别图像
async function recognizeImage() {
    showLoading('正在识别图像...');
    
    try {
        const response = await fetch('/api/recognize', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            addStatusMessage('识别请求已发送，正在处理...');
            // 定期刷新状态以获取识别结果
            const checkResult = setInterval(() => {
                refreshStatus();
                if (state.lastResult) {
                    clearInterval(checkResult);
                    hideLoading();
                }
            }, 1000);
        } else {
            addStatusMessage('识别请求失败: ' + data.error);
            hideLoading();
        }
    } catch (error) {
        console.error('识别请求失败:', error);
        addStatusMessage('识别请求失败: ' + error.message);
        hideLoading();
    }
}

// 加载历史记录
async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        const data = await response.json();
        
        if (data.success) {
            updateHistoryUI(data.records);
        } else {
            console.error('加载历史记录失败:', data.error);
        }
    } catch (error) {
        console.error('加载历史记录失败:', error);
    }
}

// 清空历史记录
async function clearHistory() {
    if (!confirm('确定要清空所有历史记录吗？')) {
        return;
    }
    
    showLoading('正在清空历史记录...');
    
    try {
        const response = await fetch('/api/history/clear', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            addStatusMessage('历史记录已清空');
            loadHistory();  // 重新加载历史（应该为空）
        } else {
            addStatusMessage('清空历史记录失败: ' + data.error);
        }
    } catch (error) {
        console.error('清空历史记录失败:', error);
        addStatusMessage('清空历史记录失败: ' + error.message);
    } finally {
        hideLoading();
    }
}

// ===== UI 更新 =====
// 更新状态 UI
function updateStatusUI(data) {
    // 更新服务状态
    state.isRunning = data.is_running;
    updateServiceStatusUI(data.is_running);
    
    // 更新截图
    if (data.last_screenshot && data.last_screenshot !== state.lastScreenshot) {
        state.lastScreenshot = data.last_screenshot;
        const timestamp = new Date().getTime();  // 添加时间戳防止缓存
        elements.currentScreenshot.src = `/screenshots/${data.last_screenshot}?t=${timestamp}`;
        elements.btnRecognize.disabled = false;
    }
    
    // 更新识别结果
    if (data.last_result && JSON.stringify(data.last_result) !== JSON.stringify(state.lastResult)) {
        state.lastResult = data.last_result;
        updateResultUI(data.last_result);
    }
    
    // 更新状态消息
    if (data.status_messages && data.status_messages.length > 0) {
        updateStatusMessages(data.status_messages);
    }
}

// 更新服务状态 UI
function updateServiceStatusUI(isRunning) {
    elements.btnStart.disabled = isRunning;
    elements.btnStop.disabled = !isRunning;
    elements.btnScreenshot.disabled = !isRunning;
    
    if (isRunning) {
        elements.serviceStatus.className = 'status-indicator status-running';
        elements.serviceStatus.innerHTML = '<i class="bi bi-circle-fill"></i> 服务正在运行';
    } else {
        elements.serviceStatus.className = 'status-indicator status-stopped';
        elements.serviceStatus.innerHTML = '<i class="bi bi-circle-fill"></i> 服务未运行';
    }
}

// 更新识别结果 UI
function updateResultUI(result) {
    if (result.error) {
        elements.resultContent.innerHTML = `<p class="result-error">错误: ${result.error}</p>`;
        return;
    }
    
    let content = '';
    
    if (result.answer) {
        // 使用 markdown 样式展示答案
        content = `<div class="result-answer">${formatAnswer(result.answer)}</div>`;
    } else {
        content = '<p class="result-placeholder">无法解析答案</p>';
    }
    
    elements.resultContent.innerHTML = content;
}

// 格式化答案
function formatAnswer(answer) {
    // 简单的文本格式化，保留换行和空格
    let formatted = answer
        .replace(/\n/g, '<br>')
        .replace(/\s{2}/g, '&nbsp;&nbsp;');
    
    // 尝试检测和强调选项
    const optionRegex = /([A-D])(\s*[\.、]|\s+)/g;
    formatted = formatted.replace(optionRegex, '<strong>$1</strong>$2');
    
    // 尝试检测和强调关键信息
    const keywordRegex = /(正确答案|答案|解析)[:：]/g;
    formatted = formatted.replace(keywordRegex, '<strong>$1</strong>:');
    
    return formatted;
}

// 更新状态消息
function updateStatusMessages(messages) {
    let html = '';
    
    messages.forEach(msg => {
        html += `<p class="status-message">[${msg.time}] ${msg.message}</p>`;
    });
    
    elements.statusMessages.innerHTML = html;
    elements.statusMessages.scrollTop = elements.statusMessages.scrollHeight;
}

// 添加状态消息（仅UI）
function addStatusMessage(message) {
    const timestamp = new Date().toLocaleTimeString();
    const html = `<p class="status-message">[${timestamp}] ${message}</p>`;
    
    elements.statusMessages.innerHTML += html;
    elements.statusMessages.scrollTop = elements.statusMessages.scrollHeight;
}

// 更新历史记录 UI
function updateHistoryUI(records) {
    if (!records || records.length === 0) {
        elements.historyList.innerHTML = `
            <div class="history-empty">
                <p>暂无历史记录</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    
    // 按时间倒序排列
    records.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    records.forEach(record => {
        const answer = record.recognition_result && record.recognition_result.answer 
            ? record.recognition_result.answer 
            : '无法解析答案';
        
        // 截取答案的前30个字符作为预览
        const answerPreview = answer.length > 30 
            ? answer.substring(0, 30) + '...' 
            : answer;
        
        html += `
            <div class="history-item" data-id="${record.id}" onclick="showHistoryDetail('${record.id}')">
                <div class="history-time">${record.timestamp}</div>
                <div class="history-answer">${answerPreview}</div>
            </div>
        `;
    });
    
    elements.historyList.innerHTML = html;
}

// 显示历史记录详情
function showHistoryDetail(recordId) {
    // 实现查看历史记录详情的功能
    fetch(`/api/history/${recordId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.record) {
                showHistoryModal(data.record);
            }
        })
        .catch(error => console.error('获取历史记录详情失败:', error));
}

// 显示历史记录模态框
function showHistoryModal(record) {
    elements.modalTitle.textContent = `历史记录 - ${record.timestamp}`;
    
    let content = `
        <div class="modal-section">
            <h3>截图</h3>
            <div class="modal-screenshot">
                <img src="/screenshots/${record.image_path}" alt="历史截图">
            </div>
        </div>
        
        <div class="modal-section">
            <h3>识别结果</h3>
            <div class="modal-result">
                ${formatAnswer(record.recognition_result.answer)}
            </div>
        </div>
    `;
    
    elements.modalBody.innerHTML = content;
    elements.modal.style.display = 'flex';
}

// 关闭模态框
function closeModal() {
    elements.modal.style.display = 'none';
}

// 更新当前时间
function updateCurrentTime() {
    const now = new Date();
    elements.currentTime.textContent = now.toLocaleString();
}

// ===== 辅助函数 =====
// 显示加载动画
function showLoading(text = '正在处理...') {
    elements.loadingText.textContent = text;
    elements.loadingOverlay.style.display = 'flex';
}

// 隐藏加载动画
function hideLoading() {
    elements.loadingOverlay.style.display = 'none';
}

// 暴露给全局作用域的函数（用于HTML内联事件）
window.showHistoryDetail = showHistoryDetail;

// 初始化应用
document.addEventListener('DOMContentLoaded', init); 