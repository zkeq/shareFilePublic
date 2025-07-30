# ShareFile Public

![image-20250730201541564](https://img.onmicrosoft.cn/zkeq/20250730201541666.png)

![image-20250730201551642](https://img.onmicrosoft.cn/zkeq/20250730201551748.png)

Wiki：https://deepwiki.com/zkeq/shareFilePublic

一个基于多吉云的现代化文件分享平台，支持视频处理和在线预览功能。 （已支持视频转码+一起看功能）

## 项目概述

ShareFile Public 是一个功能强大的文件分享平台，采用前后端分离架构，提供文件上传、分享、视频处理等功能。项目使用 Vue 3 + FastAPI 技术栈开发，具有高性能、可扩展性强的特点。

### 主要功能

- 📁 文件上传与分享
- 🎥 视频文件处理
- 📊 文件访问统计
- 📝 视频公告系统
- 👀 在线预览支持
- 🔒 安全的文件存储

## 技术栈

### 前端 (Frontend)

- Vue 3 - 渐进式 JavaScript 框架
- Vite - 新一代前端构建工具
- Ant Design Vue 4.x - UI 组件库
- TailwindCSS - 原子化 CSS 框架
- DPlayer & APlayer - 媒体播放器
- Vue Router - 路由管理
- Axios - HTTP 客户端

### 后端 (Backend)

- FastAPI - 现代、快速的 Web 框架
- Python 3.x
- 异步任务处理系统
- RESTful API 设计

## 快速开始

### 前端部署

```bash
cd frontend
npm install
npm run dev    # 开发环境
npm run build  # 生产环境构建
```

### 后端部署

```bash
cd backend
pip install -r requirements.txt
python main.py
```

## API 文档

主要 API 端点：

- `GET /public/info` - 获取存储统计信息
- `POST /share/submit` - 提交分享列表
- `GET /share/{hash_value}` - 获取分享内容
- `POST /upload/token` - 获取上传凭证
- `POST /tasks/submit` - 提交视频处理任务
- `GET /video/{vcode}` - 获取视频信息
- `POST /notice` - 创建视频公告

详细 API 文档请访问运行中的后端服务的 `/docs` 或 `/redoc` 端点。

## 项目结构

```
├── frontend/               # 前端项目目录
│   ├── src/               # 源代码
│   ├── public/            # 静态资源
│   └── package.json       # 项目依赖
│
└── backend/               # 后端项目目录
    ├── main.py           # 主程序入口
    ├── tasks.py          # 任务处理
    ├── share.py          # 分享功能
    ├── video.py          # 视频处理
    ├── notice.py         # 公告系统
    └── requirements.txt   # Python 依赖
```

## 环境要求

- Node.js 16.x 或更高版本
- Python 3.8 或更高版本
- 现代浏览器支持

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。在提交 PR 之前，请确保：

1. 代码符合项目的编码规范
2. 所有测试通过
3. 更新相关文档

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。
