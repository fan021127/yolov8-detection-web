// ========== 登录/注册页面逻辑 ==========

const loginPanel = document.getElementById('loginPanel');
const registerPanel = document.getElementById('registerPanel');
const messageBox = document.getElementById('messageBox');

// 切换登录/注册
document.getElementById('toRegister').addEventListener('click', () => {
    loginPanel.classList.add('hidden');
    registerPanel.classList.remove('hidden');
    hideMessage();
});

document.getElementById('toLogin').addEventListener('click', () => {
    registerPanel.classList.add('hidden');
    loginPanel.classList.remove('hidden');
    hideMessage();
});

// 显示消息
function showMessage(text, type = 'error') {
    messageBox.textContent = text;
    messageBox.className = `message-box ${type}`;
    messageBox.classList.remove('hidden');
    setTimeout(hideMessage, 4000);
}

function hideMessage() {
    messageBox.classList.add('hidden');
}

// 登录
document.getElementById('loginBtn').addEventListener('click', async () => {
    const username = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value;

    if (!username || !password) {
        showMessage('请输入用户名和密码');
        return;
    }

    try {
        const res = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });
        const data = await res.json();

        if (data.success) {
            showMessage('登录成功，正在跳转...', 'success');
            setTimeout(() => { window.location.href = '/detect'; }, 800);
        } else {
            showMessage(data.message || '登录失败');
        }
    } catch (e) {
        showMessage('网络错误，请稍后重试');
    }
});

// 注册
document.getElementById('registerBtn').addEventListener('click', async () => {
    const username = document.getElementById('regUsername').value.trim();
    const password = document.getElementById('regPassword').value;
    const confirm = document.getElementById('regConfirm').value;

    if (!username || !password || !confirm) {
        showMessage('请填写完整信息');
        return;
    }
    if (username.length < 3) {
        showMessage('用户名至少3个字符');
        return;
    }
    if (password.length < 6) {
        showMessage('密码至少6个字符');
        return;
    }
    if (password !== confirm) {
        showMessage('两次密码不一致');
        return;
    }

    try {
        const res = await fetch('/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password, confirm_password: confirm }),
        });
        const data = await res.json();

        if (data.success) {
            showMessage('注册成功，请登录', 'success');
            setTimeout(() => {
                registerPanel.classList.add('hidden');
                loginPanel.classList.remove('hidden');
                document.getElementById('loginUsername').value = username;
            }, 1200);
        } else {
            showMessage(data.message || '注册失败');
        }
    } catch (e) {
        showMessage('网络错误，请稍后重试');
    }
});

// 回车提交
document.getElementById('loginPassword').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') document.getElementById('loginBtn').click();
});
document.getElementById('regConfirm').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') document.getElementById('registerBtn').click();
});
