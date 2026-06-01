# douyin-kit

> 基于浏览器滚动采集公开页面内容、代码干净——一个纯粹用于技术研究的抖音下载工具。

<p align="center">
  <a href="https://github.com/mumushuo/douyin-kit"><img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=flat-square"/></a>
  <a href="https://github.com/mumushuo/douyin-kit/releases"><img src="https://img.shields.io/github/v/release/mumushuo/douyin-kit?style=flat-square&label=version"/></a>
  <a href="https://github.com/mumushuo/douyin-kit/issues"><img src="https://img.shields.io/github/issues/mumushuo/douyin-kit?style=flat-square"/></a>
</p>

<p align="center">
  <a href="https://github.com/mumushuo/douyin-kit/stargazers"><img src="https://img.shields.io/github/stars/mumushuo/douyin-kit?style=social"/></a>
  <a href="https://github.com/mumushuo/douyin-kit/network/members"><img src="https://img.shields.io/github/forks/mumushuo/douyin-kit?style=social"/></a>
</p>

---

## ⚠️ 免责声明与合规边界

**本工具仅供个人学习与技术研究使用。**

- 仅下载**无需登录即可查看的公开页面内容**，不绕过任何权限控制
- 下载的视频**保留原始水印**（无水印去除功能）
- **不得**用于商业用途、侵犯版权或二次分发
- **不得**用于抓取非公开内容或规避平台访问限制
- 使用者须自行遵守抖音用户协议及相关法律法规，尊重创作者权益

---

## 🔒 Cookie 安全说明

- Cookie 凭证**仅保存在本地** `config/cookies.json`，不会上传至任何服务器
- `config/cookies.json` 已加入 `.gitignore`，**请勿手动提交至仓库**
- 如怀疑凭证泄漏，请立即在抖音 App/网页端退出登录以刷新凭证
- 建议使用测试账号获取 Cookie，与日常使用的个人账号分离

---

## 功能特性

- **浏览器登录取 Cookie** — 通过 Playwright 一次性登录获取凭证，无需手动配置
- **基于浏览器滚动采集** — 滚动创作者主页采集公开页面内容
- **日期筛选** — 按时间范围精准下载指定视频
- **跳过已下载** — 自动检测并跳过已存在文件，避免重复下载
- **两种下载模式**
  - **文件夹模式**（默认）：视频 + 封面 + 元数据，按文件夹存放
  - **仅视频模式**：只下载 `.mp4` 文件，平铺输出，干净简洁
- **元数据导出** — 保存视频信息为 JSON，支持离线分析
- **无需 API 密钥** — 使用你自己的浏览器登录态

---

## 快速开始

### 安装

```bash
git clone https://github.com/mumushuo/douyin-kit.git
cd douyin-kit
pip install -r requirements.txt
playwright install chromium
```

### 模式一：完整文件夹下载

每个视频存入独立文件夹，包含 `.mp4` 视频、`_cover.jpg` 封面、`_data.json` 元数据。

```bash
python main.py all "https://www.douyin.com/user/YOUR_SEC_UID" \
  --start-date 2026-05-01 \
  --end-date 2026-05-31 \
  --output ./downloads/
```

### 模式二：仅下载视频文件

只下载 `.mp4` 文件，平铺在输出目录，无子文件夹、无封面、无元数据。

```bash
python main.py all "https://www.douyin.com/user/YOUR_SEC_UID" \
  --start-date 2026-05-01 \
  --end-date 2026-05-31 \
  --output ./videos/ \
  --mode video-only
```

---

## 分步操作

### 1. 获取 Cookie（首次执行）

```bash
python main.py fetch-cookies
```

浏览器窗口自动打开，登录抖音后关闭窗口，Cookie 自动保存至 `config/cookies.json`。

### 2. 采集视频列表

```bash
# 采集全部视频
python main.py scrape "https://www.douyin.com/user/YOUR_SEC_UID"

# 按日期筛选
python main.py scrape "https://www.douyin.com/user/YOUR_SEC_UID" \
  --start-date 2026-05-01 \
  --end-date 2026-05-31
```

输出：`videos.json`，包含完整视频元数据。

### 3. 下载视频

```bash
# 文件夹模式（默认）
python main.py download --metadata videos.json --output ./downloads/

# 仅视频模式
python main.py download --metadata videos.json --output ./videos/ --mode video-only
```

---

## 输出结构

### 文件夹模式（默认）

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

### 仅视频模式

```
videos/
├── 2026-05-14_AI工具推荐_1234567890.mp4
└── 2026-05-21_深度学习入门_0987654321.mp4
```

---

## 常见问题

**Q: 如何获取创作者的 sec_uid / 主页链接？**

打开抖音网页版 → 进入创作者主页 → 复制浏览器地址栏中 `https://www.douyin.com/user/` 后面的完整内容。

**Q: Cookie 过期了怎么办？**

重新运行 `python main.py fetch-cookies`，按提示登录即可更新。

**Q: 抓取的视频数量比主页显示的少？**

可能原因：浏览器滚动被反爬拦截、网络不稳定导致 API 响应丢失。建议关闭无头模式（`--headless` 不加）观察滚动过程。

**Q: 某些视频下载失败（HTTP 403/404）？**

视频签名 URL 有有效期。抓取后尽快下载；如果批量下载时间较长，考虑分批执行。

**Q: 支持 Windows / Linux 吗？**

理论上支持，但目前主要验证环境为 macOS（Apple Silicon）。Windows 用户需确保 Playwright 正确安装了 Chromium。

---

## 如何获取创作者链接

1. 打开抖音，进入创作者主页
2. 复制浏览器地址栏中的 URL
3. 格式类似：`https://www.douyin.com/user/MS4wLjABAA...`

---

## 目录结构

```
douyin-kit/
├── main.py                  # 命令行入口
├── douyin_kit/
│   ├── __init__.py
│   ├── cookie_fetcher.py    # 浏览器登录取 Cookie
│   ├── scraper.py           # 页面滚动采集元数据
│   └── downloader.py        # aiohttp 下载视频
├── config/
│   └── cookies.json         # fetch-cookies 后生成
├── videos.json              # scrape 后生成
├── downloads/               # 下载的视频
├── requirements.txt
├── LICENSE
└── README.md
```

---

## 环境要求

- Python 3.10+
- Playwright (Chromium)
- aiohttp

> 已验证平台：macOS（Apple Silicon）。Windows / Linux 用户请确保 Playwright 正确安装 Chromium。

---

## Topics

`douyin` `douyin-downloader` `video-downloader` `python` `playwright` `metadata-export` `cli`

---

## License

MIT © [mumushuo](https://github.com/mumushuo)
