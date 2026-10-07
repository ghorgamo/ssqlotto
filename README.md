# 🎱 中国福利彩票双色球 & 🏆 体育彩票超级大乐透 1000期大数据可视化系统

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Cloudflare Pages](https://img.shields.io/badge/Cloudflare%20Pages-Functions%20Ready-orange.svg)](#-cloudflare-pages--github-pages-部署指南)
[![Data Scope](https://img.shields.io/badge/Data%20Scope-Up%20to%201000%20Issues-red.svg)](#-项目定位与数据规格)

一个轻量级、开箱即用的**中国福利彩票双色球（SSQ）与体育彩票超级大乐透（DLT）最近 1000 期开奖走势大数据分析与可视化看板系统**。本系统支持一键双彩种切换，涵盖**开奖号码走势大盘**、**每期全量数字遗漏矩阵**、**冷/热/温号出球数多维排行**与**单号码历史遗漏波浪图**，并内置**手动实时更新官方数据**功能（支持 Cloudflare Pages Functions 边缘无跨域代理、在线代理通道、本地数据拖拽导入及命令行一键同步）。

---

## 📌 双彩种看板页面导航

- **`index.html`**：🎱 **中国福利彩票双色球 (SSQ)** 看板（红球 33 选 6，蓝球 16 选 1）
- **`dlt.html`**：🏆 **中国体育彩票超级大乐透 (DLT)** 看板（前区 35 选 5，后区 12 选 2）
- 页面顶部右上角提供 **一键互相切换按钮**，无需手动修改网址即可在双色球与大乐透之间流畅跳转。

---

## 📌 核心功能与可视化模块

### 1. 🔄 实时手动更新官方数据（福彩 + 体彩双接口）
看板右上角内置 **「🔄 实时更新官方数据」** 交互弹窗，提供三种灵活更新渠道：
- **🌐 在线一键更新**：
  - 在 Cloudflare Pages 上运行时，自动调用内置的 `functions/api/ssq.js` 或 `functions/api/dlt.js` 边缘函数作为反向代理，直连中国福利彩票（`cwl.gov.cn`）或体育彩票官方接口（`sporttery.cn`），彻底突破浏览器的 CORS（跨域）及 Mixed Content 限制。
  - 在本地打开时，自动启用备用安全公共代理，支持选择同步 50 期 / 100 期 / 200 期 / 500 期 / 1000 期，实时渲染加载进度条并在前端原地完成遗漏矩阵重算与图表重绘。
- **📁 本地文件拖拽导入**：
  - 支持将爬虫生成的 `JSON` 或 `CSV` 文件直接拖拽入网页，毫秒级解析并无缝刷新整个看板。
- **💻 终端命令行一键更新**：
  - 双色球：`python3 scripts/fetch_ssq_data.py --count 1000`
  - 大乐透：`python3 scripts/fetch_dlt_data.py --count 1000`

### 2. 📊 1000 期综合大盘概览 (Executive Dashboard)
- **最新开奖直报**：展示最新一期官方开奖号码（3D立体质感球体）、开奖日期与星期。
- **形态学指标实时计算**：和值（Sum）、跨度（Span）、AC值（数字复杂度）、奇偶比（Odd/Even）、大小比（Big/Small）、后区形态。
- **极值看板与警示**：出球榜首热号、当前最大遗漏冷号预警。
- **全盘热度全景矩阵**：动态映射所选周期内累计出球数与当前遗漏状态。
- **形态分布图表**：和值正态分布直方图、奇偶比与大小比结构图。

### 3. 🔥 号码统计与冷/热/温出球数排名 (Hot / Warm / Cold Rankings)
- **多周期自由切换**：支持全量 1000 期、500 期、200 期、100 期、50 期、30 期动态重算。
- **出球频次排行榜**：
  - 双色球红球（1~33）/ 蓝球（1~16），大乐透前区（1~35）/ 后区（1~12）按累计出球次数进行**降序严格排名**。
  - 对比理论出球期望值（如大乐透 1000 期前区理论值 $\approx 142.9$ 次，后区理论值 $= 166.7$ 次），高亮显示偏离差值。
- **冷/热/温号科学分类**：
  - **🔥 热号 (Hot)**：出球频次排名前 30%，出球频次显著高于理论均值。
  - **🌤️ 温号 (Warm)**：出球频次处于中间 40%，处于均值平衡区间。
  - **❄️ 冷号 (Cold)**：出球频次处于后 30%，出球频次显著偏低。
- **可视化图表**：
  - 动态水平柱状对比图（带理论期望虚线定位）。
  - 冷/热/温号码结构环形分布图（Donut Chart）。

### 4. 📉 每期数字全量遗漏走势图阵 (Omission Trend Matrix)
- **全景走势矩阵**：
  - 纵轴为开奖期号（支持最新期置顶或正序，可选 30 / 50 / 100 / 200 / 500 / 1000 期）。
  - 横轴为号码分区走势。
- **双重视觉反馈**：
  - **中奖开出**：实心立体球高亮显示，遗漏值归零。
  - **未开出遗漏**：清晰显示该号码距上次开出的**连续遗漏期数**，配合动态热力色阶。
- **底部汇总统计行**：表格底部固定呈现“出现总次数”、“平均遗漏”、“历史最大遗漏”、“当前遗漏期数”。

### 5. 🌊 单号码遗漏波浪折线图 (Omission Waveform)
- 任意点击或切换号码。
- 绘制连续遗漏波浪图：波峰清晰展示历史长遗漏区间，波谷落回 0 刻度代表开出中奖点，辅助识别号码周期律。

### 6. 📋 1000 期开奖历史明细库与组合查询 (History Archive)
- 分页浏览最近 1000 期完整开奖历史记录。
- 支持按期号模糊搜索、按开奖日期定位、或筛选包含特定红球/蓝球/前区/后区的全部历史期次。
- 提供一键导出全量数据为标准 `JSON` 与 `CSV` 格式。

---

## 🗂️ 项目目录结构

```text
ssq-lottery-visualizer/
├── functions/
│   └── api/
│       ├── ssq.js                # Cloudflare Pages 福彩官方接口代理
│       └── dlt.js                # Cloudflare Pages 体彩官方接口代理
├── data/
│   ├── ssq_history_1000.json     # 双色球 1000 期全量数据 (JSON)
│   ├── ssq_history_1000.csv      # 双色球 1000 期表格 (CSV)
│   ├── dlt_history_1000.json     # 大乐透 1000 期全量数据 (JSON)
│   └── dlt_history_1000.csv      # 大乐透 1000 期表格 (CSV)
├── scripts/
│   ├── fetch_ssq_data.py         # 双色球官方数据抓取脚本 (1000期)
│   ├── fetch_dlt_data.py         # 大乐透官方数据抓取脚本 (1000期)
│   ├── analyze_ssq.py            # 双色球多维统计分析工具
│   └── analyze_dlt.py            # 大乐透多维统计分析工具
├── index.html                    # 双色球可视化分析大屏 (带切换至大乐透入口)
├── dlt.html                      # 超级大乐透可视化分析大屏 (带切换至双色球入口)
├── .github/workflows/            # GitHub Actions 自动化工作流
├── requirements.txt              # Python 依赖
├── LICENSE                       # MIT 开源协议
└── README.md                     # 项目技术文档
```

---

## 🚀 极速上手使用指南

### 在本地运行 Python 抓取与分析

```bash
cd ssq-lottery-visualizer

# 双色球：从官方接口拉取最新 1000 期数据并自动更新 index.html
python3 scripts/fetch_ssq_data.py --count 1000

# 大乐透：从官方接口拉取最新 1000 期数据并自动更新 dlt.html
python3 scripts/fetch_dlt_data.py --count 1000

# 终端数据分析报告
python3 scripts/analyze_ssq.py --count 1000
python3 scripts/analyze_dlt.py --count 1000
```

---

## 🌐 Cloudflare Pages 部署说明

1. 登录 [Cloudflare 控制台](https://dash.cloudflare.com/)。
2. 进入 **Workers 和 Pages** $\rightarrow$ **创建应用程序** $\rightarrow$ **Pages** $\rightarrow$ **连接到 Git**。
3. 选择您的 GitHub 仓库 `ghorgamo/ssqlotto`。
4. 构建设置：框架预设选 **None**，构建命令和输出目录**留空**。
5. 点击 **保存并部署**。
   - 部署后访问根路径即可打开双色球看板，访问 `/dlt.html` 或通过右上角按钮切换即可打开超级大乐透看板。
   - 双彩种均已配置 Cloudflare Pages Functions 边缘代理，在线实时更新完全免跨域限制！
