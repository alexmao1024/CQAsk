# CQAsk-Pro

这是一个基于 [OpenOrion/CQAsk](https://github.com/OpenOrion/CQAsk.git) 进行二次开发的增强版项目。本项目在保留其核心的“自然语言到CAD模型”功能的基础上，进行了一系列的功能增强和架构优化，旨在提供更强大、更稳定、更具交互性的CAD建模体验。

## 主要功能与优化

相较于原始的 `CQAsk` 项目，本项目引入了以下核心改进：

1.  **全功能多轮对话系统**
    *   用户可以与AI进行连续的多轮对话，在之前生成模型的基础上进行迭代修改（例如“先创建一个方块”，然后“在方块顶上打个孔”）。
    *   所有对话历史都会被自动保存，方便随时回顾。

2.  **智能错误修正与重试机制**
    *   当AI生成的CAD代码执行失败时，系统会自动捕获错误信息。
    *   在下一次尝试中，系统会将错误信息反馈给大模型，引导其进行自我修正，从而大大提高了复杂模型生成的成功率。

3.  **可交互的对话历史浏览器**
    *   前端界面提供了一个完整的对话历史列表。
    *   用户不仅可以查看历史对话，还可以点击任意一条历史消息，即时重新加载和渲染当时生成的3D模型，实现了真正的“版本回溯”。

4.  **优化的后端架构**
    *   对后端代码进行了重构，将对话管理、代码生成、API服务等模块进行了解耦，使得代码结构更清晰，易于维护和二次开发。

5.  **增强的前端用户体验**
    *   重新设计了前端界面，使其能够支持和展示新增的对话历史功能，提供了更流畅、更直观的用户体验。

## 技术栈

*   **后端**: Python, Flask, CadQuery, OpenAI API
*   **前端**: Next.js, React, TypeScript, Tailwind CSS, antd, axios

## 启动项目

请确保您的环境中已安装 Python (3.8+) 和 Node.js (18+)。

### 1. 后端启动

首先，进入 `backend` 目录并设置环境。

```bash
# 进入后端目录
cd backend

# (建议) 创建并激活虚拟环境
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
# 复制 .env_template 文件为 .env
cp .env_template .env
```

接下来，编辑新建的 `.env` 文件，填入您的 `SiliconFlow` API Key。

```
SILICONFLOW_API_KEY="sk-..."
```

最后，启动后端服务。服务将默认运行在 `http://127.0.0.1:5001`。

```bash
python api.py
```

### 2. 前端启动

打开一个新的终端，进入 `ui` 目录并设置环境。

```bash
# 进入前端目录
cd ui

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端开发服务器将默认运行在 `http://localhost:3000`。

### 3. 访问应用

打开您的浏览器，访问 [http://localhost:3000](http://localhost:3000)，即可开始使用。

## 项目结构

```
.
├── backend/                # 后端服务
│   ├── api.py              # Flask API 入口
│   ├── codex.py            # 与大模型交互，生成和执行CadQuery代码
│   ├── conversation.py     # 多轮对话管理核心逻辑
│   ├── conversations/      # 存放对话历史的JSON文件
│   ├── generated/          # 存放成功生成的CadQuery代码文件
│   ├── utils/              # 工具函数 (模型三角剖分、下载等)
│   └── requirements.txt    # Python 依赖
│
└── ui/                     # 前端应用
    ├── app/                # Next.js 13 app router
    │   ├── api/            # 前端API请求封装
    │   ├── components/     # React 组件 (3D查看器, 对话历史等)
    │   └── page.tsx        # 主页面
    ├── package.json        # Node.js 依赖
    └── ...
``` 