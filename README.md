# Douyin Kit / 抖音工具箱

> Download public videos from Douyin (Chinese TikTok) creators — for personal backup and research use only.
>
> 下载抖音公开视频 — 仅限个人备份与技术研究用途。

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## ⚠️ Disclaimer / 免责声明

**This tool is for personal learning and research purposes only.**
**本工具仅供个人学习与技术研究使用。**

- Only downloads **publicly available** videos that are visible without login / 仅下载无需登录即可查看的公开视频
- Videos are downloaded **with original watermarks intact** (no watermark removal) / 下载的视频**保留原始水印**（无水印去除功能）
- Do **NOT** use this tool for commercial purposes, copyright infringement, or content redistribution / 请勿用于商业用途、侵犯版权或二次分发
- Users are solely responsible for complying with Douyin's Terms of Service / 使用者须自行遵守抖音用户协议
- Respect creators' rights — use responsibly / 尊重创作者权益，合理使用

This project is not affiliated with, endorsed by, or associated with Douyin or ByteDance.
本项目与抖音、字节跳动无关，亦非其授权产品。

---

## Features / 功能

- **Browser-based cookie acquisition** / 浏览器登录取Cookie — 通过 Playwright 一次性登录获取凭证
- **Bypasses API pagination limits** / 绕过API分页限制 — 滚动创作者主页采集全部视频
- **Date filtering** / 日期筛选 — 按时间范围下载指定视频
- **Incremental download** / 增量下载 — 自动跳过已下载视频
- **Two download modes** / 两种下载模式：
  - **Folder mode** (default): video + cover + metadata in sub-directories
  - **文件夹模式**（默认）：视频 + 封面 + 元数据，按文件夹存放
  - **Video-only mode**: only `.mp4` files, flat output — clean and simple
  - **仅视频模式**：只下载 `.mp4` 文件，平铺输出 — 干净简洁
- **Metadata export** / 元数据导出 — 保存视频信息为 JSON 离线分析
- **No API keys required** / 无需API密钥 — 使用你自己的浏览器登录态

---

## 💡 What Makes This Different / 差异化定位

> **唯一一个不做水印去除、用浏览器真实滚动绕过 API 分页限制、且代码干净到可以直接读懂的技术研究型抖音下载工具。**
>
> *The only Douyin video downloader that skips watermark removal, bypasses API pagination via real browser scrolling, and keeps the codebase clean enough to read in one sitting.*

| | 同类项目 / Others | douyin-kit |
|---|---|---|
| **水印 / Watermark** | 去除水印（灰色地带） | **保留原始水印**（合规） |
| **采集方式 / Scraping** | API 直接调用，受分页限制 | **Playwright 浏览器滚动**，绕过 API 分页上限 |
| **安装门槛 / Setup** | 模拟器、adb、复杂依赖 | **pip install + playwright install，两行搞定** |
| **下载模式 / Download** | 一刀切：每视频一个文件夹 | **双模式**：文件夹 / 仅视频平铺输出 |
| **工程规范 / Code Quality** | 无注释、无文档 | **全 docstring + 双语文档 + 清晰的 CLI 子命令** |

This project is not trying to be another "free watermark remover" — it exists to be the clean, principled alternative that actually **survives**.
本项目不做又一个「免费去水印工具」—— 它的定位是干净、讲原则、能**长期存活**的替代方案。

---

## Installation / 安装

```bash
# Clone / 克隆
git clone https://github.com/mumushuo/douyin-kit.git
cd douyin-kit

# Install dependencies / 安装依赖
pip install -r requirements.txt

# Install Playwright browser / 安装 Playwright 浏览器
playwright install chromium
```

---

## Quick Start / 快速开始

### Mode 1: Full folder download / 模式一：完整文件夹下载

Each video is saved in its own folder with `.mp4` video, `_cover.jpg` thumbnail, and `_data.json` metadata.
每个视频存入独立文件夹，包含 `.mp4` 视频、`_cover.jpg` 封面、`_data.json` 元数据。

```bash
python main.py all "https://www.douyin.com/user/YOUR_SEC_UID" \
  --start-date 2026-05-01 \
  --end-date 2026-05-31 \
  --output ./downloads/
```

### Mode 2: Video-only download / 模式二：仅下载视频文件

Only `.mp4` files are downloaded, flat in the output directory. No subfolders, no covers, no metadata.
仅下载 `.mp4` 文件，平铺在输出目录，无子文件夹、无封面、无元数据。

```bash
python main.py all "https://www.douyin.com/user/YOUR_SEC_UID" \
  --start-date 2026-05-01 \
  --end-date 2026-05-31 \
  --output ./videos/ \
  --mode video-only
```

---

## Step-by-Step / 分步操作

### 1. Get cookies / 获取 Cookie（首次执行）

```bash
python main.py fetch-cookies
```

A browser window opens. Log in to Douyin, then close the browser. Cookies are saved to `config/cookies.json`.
浏览器窗口自动打开，登录抖音后关闭窗口，Cookie 自动保存至 `config/cookies.json`。

### 2. Scrape video list / 采集视频列表

```bash
# Get all videos / 采集全部视频
python main.py scrape "https://www.douyin.com/user/YOUR_SEC_UID"

# Filter by date / 按日期筛选
python main.py scrape "https://www.douyin.com/user/YOUR_SEC_UID" \
  --start-date 2026-05-01 \
  --end-date 2026-05-31
```

Output: `videos.json` with full video metadata.
输出：`videos.json`，包含完整视频元数据。

### 3. Download videos / 下载视频

```bash
# Folder mode (default): video + cover + metadata
# 文件夹模式（默认）：视频 + 封面 + 元数据
python main.py download --metadata videos.json --output ./downloads/

# Video-only mode: just the .mp4 files
# 仅视频模式：只下载 .mp4 文件
python main.py download --metadata videos.json --output ./videos/ --mode video-only
```

---

## Output Structure / 输出结构

### Folder mode (default) / 文件夹模式（默认）

```
downloads/
├── 2026-05-14_AI工具推荐_1234567890/
│   ├── 2026-05-14_AI工具推荐_1234567890.mp4
│   ├── 2026-05-14_AI工具推荐_1234567890_cover.jpg
│   └── 2026-05-14_AI工具推荐_1234567890_data.json
└── 2026-05-21_深度学习入门_0987654321/
    ├── 2026-05-21_深度学习入门_0987654321.mp4
    ├── 2026-05-21_深度学习入门_0987654321_cover.jpg
    └── 2026-05-21_深度学习入门_0987654321_data.json
```

### Video-only mode / 仅视频模式

```
videos/
├── 2026-05-14_AI工具推荐_1234567890.mp4
└── 2026-05-21_深度学习入门_0987654321.mp4
```

---

## How to Get the Creator URL / 如何获取创作者链接

1. Open Douyin and visit the creator's profile page / 打开抖音，进入创作者主页
2. Copy the URL from your browser's address bar / 复制浏览器地址栏中的 URL
3. It looks like: `https://www.douyin.com/user/MS4wLjABAA...`

---

## Directory Structure / 目录结构

```
douyin-kit/
├── main.py                  # CLI entry point / 命令行入口
├── douyin_kit/
│   ├── __init__.py
│   ├── cookie_fetcher.py    # Browser login & cookie extraction / 浏览器登录取Cookie
│   ├── scraper.py           # Page scrolling & metadata collection / 页面滚动采集元数据
│   └── downloader.py        # Video download with aiohttp / aiohttp 下载视频
├── config/
│   └── cookies.json         # Generated after fetch-cookies / fetch-cookies 后生成
├── videos.json              # Generated after scrape / scrape 后生成
├── downloads/               # Downloaded videos / 下载的视频
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Requirements / 环境要求

- Python 3.10+
- Playwright (Chromium)
- aiohttp

---

## License / 许可证

MIT © [mumushuo](https://github.com/mumushuo)
