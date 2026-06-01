# Changelog

## v0.1.0 (2026-06-01)

### Added
- Cookie 获取（Playwright 浏览器登录）
- 视频列表采集（页面滚动绕过 API 分页）
- 视频下载（aiohttp 异步并发，支持 302 重定向）
- 日期筛选（按 `--start-date` / `--end-date` 过滤）
- 跳过已下载（自动检测已存在文件）
- 两种下载模式：文件夹模式（视频 + 封面 + 元数据）、仅视频模式（平铺 .mp4）
- 元数据导出（JSON 格式）
- README 中英文说明、合规声明、Cookie 安全说明
