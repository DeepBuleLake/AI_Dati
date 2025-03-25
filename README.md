# 智能答题助手 (DatiAI)

一个基于Coze API的智能答题助手，可以通过截图识别题目并给出答案。

## 功能特点

- **全局热键截图**：使用Ctrl+Alt+A进行全屏截图
- **智能识别**：利用Coze API进行OCR识别和答案生成
- **美观界面**：基于Windows Fluent Design的暗色主题
- **历史记录**：保存所有识别结果和截图，方便查看
- **反截图检测**：基本的反检测机制

## 系统要求

- Windows 10或更高版本
- Python 3.8或更高版本
- 网络连接（用于调用Coze API）

## 安装步骤

1. 安装Python依赖：

```bash
pip install -r requirements.txt
```

2. 配置应用：

编辑`config.py`文件，设置您的Coze API认证信息：

```python
AUTH_TOKEN = "Bearer 您的TOKEN"
BOT_ID = "您的BOT_ID"
WORKFLOW_ID = "您的WORKFLOW_ID"
```

## 使用方法

1. 启动应用：

```bash
python app.py
```

2. 在浏览器中访问：`http://127.0.0.1:5000`

3. 点击"启动服务"按钮开始监听热键

4. 按下`Ctrl+Alt+A`进行截图，或使用界面上的"截图"按钮

5. 等待识别结果

## 目录结构

```
DatiAI/
├── app.py                 # 主程序入口
├── config.py              # 配置文件
├── requirements.txt       # 依赖包列表
├── README.md              # 说明文档
├── static/                # 静态资源
│   ├── css/               # 样式文件
│   ├── js/                # JavaScript文件
│   └── images/            # 图片资源
├── templates/             # HTML模板
├── modules/               # 功能模块
│   ├── screenshot.py      # 截图模块
│   ├── recognition.py     # 识别模块
│   ├── history.py         # 历史记录模块
│   └── anti_detect.py     # 反截图检测模块
└── data/                  # 数据存储
    ├── history.json       # 历史记录
    └── screenshots/       # 截图存储
```

## 常见问题

1. **热键不工作**：确保应用以管理员权限运行
2. **识别失败**：检查API认证信息是否正确
3. **界面不显示**：确保Flask服务正常运行且端口未被占用

## 注意事项

- 本应用仅用于学习参考，请遵守相关法律法规
- 避免频繁调用API，以免超出限制 