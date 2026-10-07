# 🎱 双色球最近1000期大数据可视化分析系统 (SSQ 1000-Issue Visualizer)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Cloudflare Pages](https://img.shields.io/badge/Cloudflare%20Pages-Functions%20Ready-orange.svg)](#-cloudflare-pages--github-pages-部署指南)
[![Data Scope](https://img.shields.io/badge/Data%20Scope-Up%20to%201000%20Issues-red.svg)](#-项目定位与数据规格)

一个轻量级、开箱即用的**中国福利彩票双色球（SSQ）最近 1000 期开奖走势大数据分析与可视化看板系统**。本系统涵盖**开奖号码走势大盘**、**每期全量数字遗漏矩阵**、**冷/热/温号出球数多维排行**与**单号码历史遗漏波浪图**，并内置**手动实时更新官方数据**功能（支持 Cloudflare Pages Functions 边缘无跨域代理、在线代理通道、本地数据拖拽导入及命令行一键同步）。

---

## 📌 核心功能与可视化模块

### 1. 🔄 实时手动更新官方数据（新增重点功能）
看板右上角内置 **「🔄 实时更新官方数据」** 交互弹窗，提供三种灵活更新渠道：
- **🌐 在线一键更新**：
  - 在 Cloudflare Pages 上运行时，自动调用内置的 `functions/api/ssq.js` 边缘函数作为反向代理，直连中国福利彩票官方数据接口（`cwl.gov.cn`），彻底突破浏览器的 CORS（跨域）及 Mixed Content 限制。
  - 在本地打开时，自动启用备用安全公共代理，支持选择同步 50 期 / 100 期 / 200 期 / 500 期 / 1000 期，实时渲染加载进度条并在前端原地完成遗漏矩阵重算与图表重绘。
- **📁 本地文件拖拽导入**：
  - 支持将爬虫生成的 `JSON` 或 `CSV` 文件直接拖拽入网页，毫秒级解析并无缝刷新整个看板。
- **💻 终端命令行一键更新**：
  - 复制命令 `python scripts/fetch_ssq_data.py --count 1000`，在本地终端直连福彩官网下载官方最新数据。

### 2. 📊 1000 期综合大盘概览 (Executive Dashboard)
- **最新开奖直报**：展示最新一期官方开奖号码（3D立体质感红球与蓝球）、开奖日期与星期。
- **形态学指标实时计算**：和值（Sum）、跨度（Span）、AC值（数字复杂度）、奇偶比（Odd/Even）、大小比（Big/Small）。
- **极值看板与警示**：红球/蓝球出球榜首热号、当前最大遗漏冷号预警。
- **33红球与16蓝球热度全景矩阵**：动态映射所选周期内累计出球数与当前遗漏状态。
- **形态分布图表**：和值正态分布直方图、奇偶比与大小比结构图。

### 3. 🔥 号码统计与冷/热/温出球数排名 (Hot / Warm / Cold Rankings)
- **多周期自由切换**：支持全量 1000 期、500 期、200 期、100 期、50 期、30 期动态重算。
- **出球频次排行榜**：
  - 红球（1~33 号）与蓝球（1~16 号）按累计出球次数进行**降序严格排名**（支持升序、号码顺序、当前遗漏排序）。
  - 对比理论出球期望值（1000 期红球理论值 $\approx 181.8$ 次，蓝球理论值 $= 62.5$ 次；500 期红球 $\approx 90.9$ 次，蓝球 $= 31.3$ 次），高亮显示偏离差值。
- **冷/热/温号科学分类**：
  - **🔥 热号 (Hot)**：出球频次排名前 30%（红球前 10 名，蓝球前 5 名），出球频次显著高于理论均值。
  - **🌤️ 温号 (Warm)**：出球频次处于中间 40%（红球第 11~23 名，蓝球第 6~11 名），处于均值平衡区间。
  - **❄️ 冷号 (Cold)**：出球频次处于后 30%（红球后 10 名，蓝球后 5 名），出球频次显著偏低。
- **可视化图表**：
  - 动态水平柱状对比图（带理论期望虚线定位）。
  - 冷/热/温号码结构环形分布图（Donut Chart）。

### 4. 📉 每期数字全量遗漏走势图阵 (Omission Trend Matrix)
- **全景走势矩阵**：
  - 纵轴为开奖期号（支持最新期置顶或正序，可选 30 / 50 / 100 / 200 / 500 / 1000 期）。
  - 横轴为红球（01~33）或蓝球（01~16）。
- **双重视觉反馈**：
  - **中奖开出**：实心红/蓝立体球高亮显示，遗漏值归零。
  - **未开出遗漏**：清晰显示该号码距上次开出的**连续遗漏期数**，配合动态热力色阶。
- **底部汇总统计行**：表格底部固定呈现“出现总次数”、“平均遗漏”、“历史最大遗漏”、“当前遗漏期数”。

### 5. 🌊 单号码遗漏波浪折线图 (Omission Waveform)
- 任意点击或切换 33 个红球与 16 个蓝球中的任一号码。
- 绘制连续遗漏波浪图：波峰清晰展示历史长遗漏区间，波谷落回 0 刻度代表开出中奖点，辅助识别号码周期律。

### 6. 📋 1000 期开奖历史明细库与组合查询 (History Archive)
- 分页浏览最近 1000 期完整开奖历史记录。
- 支持按期号模糊搜索、按开奖日期定位、或筛选包含特定红球/蓝球的全部历史期次。
- 提供一键导出全量数据为标准 `JSON` 与 `CSV` 格式。

---

## 🗂️ 项目目录结构

```text
ssq-lottery-visualizer/
├── .github/
│   └── workflows/
│       ├── deploy.yml            # GitHub Pages 自动部署工作流
│       └── update_data.yml        # 定时抓取最新开奖并自动推送的 Action (1000期)
├── functions/
│   └── api/
│       └── ssq.js                # Cloudflare Pages Functions 边缘反向代理 (解决CORS跨域)
├── data/
│   ├── ssq_history_1000.json     # 1000 期结构化开奖与遗漏明细数据 (JSON)
│   ├── ssq_history_1000.csv      # 1000 期历史明细数据表格 (CSV，Excel 兼容)
│   ├── ssq_history_500.json      # 500 期兼容数据集
│   └── ssq_history_500.csv       # 500 期兼容 CSV
├── scripts/
│   ├── fetch_ssq_data.py         # 福彩官方开奖接口直连爬虫 (默认 1000 期)
│   └── analyze_ssq.py            # 终端多维数据统计与冷热排行榜分析工具
├── index.html                    # 核心可视化 Web 看板 (支持实时在线更新与文件导入)
├── requirements.txt              # Python 辅助脚本依赖库
├── .gitignore                    # Git 忽略配置
├── LICENSE                       # MIT 开源协议
└── README.md                     # 项目技术文档与使用手册
```

---

## 🚀 极速上手使用指南

### 方式一：在本地运行 Python 官方抓取与分析

```bash
# 1. 进入项目文件夹
cd ssq-lottery-visualizer

# 2. 从中国福利彩票官方接口拉取最新 1000 期真实数据并自动刷新前端
python scripts/fetch_ssq_data.py --count 1000

# 3. 运行终端数据分析报告 (可指定期数，如 1000 或 500)
python scripts/analyze_ssq.py --count 1000
```

---

## 🌐 Cloudflare Pages / GitHub Pages 部署指南

### 推荐部署方案：Cloudflare Pages（自带官方接口代理）

1. 登录 [Cloudflare 控制台](https://dash.cloudflare.com/)。
2. 进入 **Workers 和 Pages** $\rightarrow$ **创建应用程序** $\rightarrow$ **Pages** $\rightarrow$ **连接到 Git**。
3. 选择您的 GitHub 仓库 `ghorgamo/ssqlotto`。
4. 构建设置：
   - 框架预设：**None**
   - 构建命令：**留空**
   - 构建输出目录：**留空**
5. 点击 **保存并部署**。
   - Cloudflare Pages 将自动识别 `functions/api/ssq.js` 并激活 `/api/ssq` 接口。
   - 部署后在网页上点击「🔄 实时更新官方数据」，前端将通过 Cloudflare 边缘服务器直连中国福彩官方 API，实现零跨域限制的毫秒级在线实时刷新！

---

## 📄 开源许可证

本项目基于 [MIT License](LICENSE) 开源，允许任何个人或团队自由学习、二开、集成与分享。
