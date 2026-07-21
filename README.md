# 交付人力投入看板

业务二组人力投入看板，基于 TAPD 任务数据，实时展示团队成员任务饱和度。

## 功能特性

- 📊 热力图展示：直观显示每个成员每天的任务工时饱和度
- 🎯 状态筛选：快速查看超时未关闭、待处理、已关闭的任务
- 📅 时间范围：上周 + 本周 + 下四周（共6周）
- 👥 成员管理：业务二组15人，按固定顺序展示

## 访问地址

[GitHub Pages 地址]

## 技术栈

- 前端：HTML + CSS + JavaScript
- 数据源：TAPD API
- 自动更新：GitHub Actions（每小时）

## 本地开发

```bash
# 更新数据
python3 scripts/fetch_tapd_tasks.py

# 启动本地服务器
python3 -m http.server 8888

# 访问
open http://localhost:8888/task-dashboard.html
```

## 自动更新

GitHub Actions 每小时自动运行，更新 TAPD 数据并部署到 GitHub Pages。

## 作者

OpenClaw Assistant
