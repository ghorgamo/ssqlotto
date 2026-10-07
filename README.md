# 🎱 双色球最近500期大数据可视化分析系统 (SSQ 500-Issue Visualizer)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live%20Demo-orange.svg)](#-在线体验--github-pages-部署)
[![Data Scope](https://img.shields.io/badge/Data%20Scope-Latest%20500%20Issues-red.svg)](#-项目定位与数据规格)

一个轻量级、零外部网络依赖、开箱即用的**中国福利彩票双色球（SSQ）最近 500 期开奖走势大数据分析与可视化看板系统**。本系统涵盖**开奖号码走势大盘**、**每期全量数字遗漏矩阵**、**冷/热/温号出球数多维排行**与**单号码历史遗漏波浪图**，支持 GitHub Pages 一键静态托管及 GitHub Actions 自动化开奖抓取同步。

---

## 📌 核心功能与可视化模块

### 1. 📊 综合大盘概览 (Executive Dashboard)
- **最新开奖直报**：展示最新一期开奖号码（3D立体质感红球与蓝球）、开奖日期与星期。
- **形态学指标实时计算**：和值（Sum）、跨度（Span）、AC值（数字复杂度）、奇偶比（Odd/Even）、大小比（Big/Small）。
- **极值看板与警示**：红球/蓝球出球榜首热号、当前最大遗漏冷号预警。
- **33红球与16蓝球热度全景矩阵**：色阶直观映射 500 期累计出球数与当前遗漏状态。
- **形态分布图表**：和值正态分布直方图、奇偶比与大小比结构图。

### 2. 🔥 号码统计与冷/热/温出球数排名 (Hot / Warm / Cold Rankings)
- **出球频次排行榜**：
  - 红球（1~33 号）与蓝球（1~16 号）按 500 期累计出球次数进行**降序严格排名**（支持升序、号码顺序、当前遗漏排序）。
  - 对比理论出球期望值（红球理论值 $\approx 90.9$ 次，蓝球理论值 $= 31.3$ 次），高亮显示正负偏离差值（Theory Diff）。
- **冷/热/温号科学分类**：
  - **🔥 热号 (Hot)**：出球频次排名前 30%（红球前 10 名，蓝球前 5 名），出球频次显著高于理论均值；或近期遗漏 $\le 4$ 期。
  - **🌤️ 温号 (Warm)**：出球频次处于中间 40%（红球第 11~23 名，蓝球第 6~11 名），处于均值平衡区间。
  - **❄️ 冷号 (Cold)**：出球频次处于后 30%（红球后 10 名，蓝球后 5 名），出球频次显著偏低；或当前遗漏 $\ge 10$ 期。
- **可视化图表**：
  - 动态水平柱状对比图（带理论期望虚线定位）。
  - 冷/热/温号码结构环形分布图（Donut Chart）。

### 3. 📉 每期数字全量遗漏走势图阵 (Omission Trend Matrix)
- **全景走势矩阵**：
  - 纵轴为开奖期号（支持最新期置顶或正序，可选 30 / 50 / 100 / 200 / 500 期）。
  - 横轴为红球（01~33）或蓝球（01~16）。
- **双重视觉反馈**：
  - **中奖开出**：实心红/蓝立体球高亮显示，遗漏值归零。
  - **未开出遗漏**：清晰显示该号码距上次开出的**连续遗漏期数**，配合动态热力色阶（深度背景色预警高遗漏冷号）。
- **底部汇总统计行**：表格底部固定呈现“出现总次数”、“平均遗漏”、“历史最大遗漏”、“当前遗漏期数”。

### 4. 🌊 单号码 500 期遗漏波浪折线图 (Omission Waveform)
- 任意点击或切换 33 个红球与 16 个蓝球中的任一号码。
- 绘制 500 期连续遗漏波浪图：波峰清晰展示历史极度冷态区间，波谷落回 0 刻度代表开出中奖点，辅助识别号码周期律。

### 5. 📋 500 期开奖历史明细库与组合查询 (History Archive)
- 分页浏览最近 500 期完整开奖历史记录。
- 支持按期号模糊搜索、按开奖日期定位、或筛选包含特定红球/蓝球的全部历史期次。
- 提供一键导出全量数据为标准 `JSON` 与 `CSV` 格式。

---

## 🗂️ 项目目录结构

```text
ssq-lottery-visualizer/
├── .github/
│   └── workflows/
│       ├── deploy.yml            # GitHub Pages 自动部署工作流
│       └── update_data.yml        # 定时爬取最新开奖并自动推送的 Action
├── data/
│   ├── ssq_history_500.json      # 500 期结构化开奖与遗漏明细数据 (JSON)
│   └── ssq_history_500.csv       # 500 期历史明细数据表格 (CSV，Excel 兼容)
├── scripts/
│   ├── fetch_ssq_data.py         # 福彩官方开奖接口爬虫与增量同步工具
│   ├── analyze_ssq.py            # 控制台统计分析引擎 (输出排名与极值报告)
│   └── generate_dataset.py       # 基准数据集与模拟验证生成脚本
├── index.html                    # 核心可视化 Web 看板 (纯原生 HTML5/CSS3/Canvas，零外链)
├── requirements.txt              # Python 辅助脚本依赖库
├── .gitignore                    # Git 忽略配置
├── LICENSE                       # MIT 开源协议
└── README.md                     # 项目技术文档与使用手册
```

---

## 🚀 极速上手使用指南

### 方式一：直接在浏览器中打开 (零环境配置)
本项目的前端 `index.html` 采用纯原生 Vanilla JavaScript、CSS3 与 HTML5 Canvas 构建，**未引用任何外部第三方 CDN**，完全离线运行：
1. 下载或克隆本仓库到本地。
2. 双击 `index.html` 即可在 Chrome、Edge、Safari、Firefox 等现代浏览器中流畅运行全套交互图表。

### 方式二：在本地运行 Python 分析工具
如果您需要通过命令行进行数据分析或导出报表：

```bash
# 1. 克隆代码仓库
git clone https://github.com/<your-username>/ssq-lottery-visualizer.git
cd ssq-lottery-visualizer

# 2. 安装 Python 依赖 (可选，仅用于爬虫与分析脚本)
pip install -r requirements.txt

# 3. 运行终端数据分析报告
python scripts/analyze_ssq.py
```

终端将即时打印 500 期红球与蓝球的出球次数排名、出现频率、当前遗漏值、冷热归类及极值分析：

```text
====================================================================
  🔴 红球出球数排名与冷/热/温分类 (1-33号)
====================================================================
排名  号码    出球次数      出现频率      当前遗漏      最大遗漏      状态分类    
--------------------------------------------------------------------
1   16    118       23.6%     0         19        🔥 热号    
2   18    111       22.2%     4         21        🔥 热号    
3   02    108       21.6%     1         26        🔥 热号    
...
```

---

## 🌐 在 GitHub 建仓与 GitHub Pages 部署步骤

按照以下步骤即可将本项目推送到 GitHub 并开启公网免费在线访问：

### 第一步：在 GitHub 创建空仓库
1. 登录 [GitHub](https://github.com/)，点击右上角 **New repository**。
2. 填写仓库名称，例如 `ssq-lottery-visualizer`。
3. 选择 **Public**，不要勾选 "Initialize this repository with a README"（本地已有完整工程文件）。
4. 点击 **Create repository**。

### 第二步：推送本地代码到 GitHub
在项目根目录下打开终端，执行以下 Git 命令：

```bash
# 初始化 Git 仓库
git init

# 添加所有工程文件
git add .

# 提交初始版本
git commit -m "feat: initial commit with 500-issue SSQ visualizer, omission matrix and rankings"

# 重命名主分支为 main
git branch -M main

# 关联远程仓库 (将 <your-username> 替换为您的 GitHub 用户名)
git remote add origin https://github.com/<your-username>/ssq-lottery-visualizer.git

# 推送到 GitHub
git push -u origin main
```

### 第三步：启用 GitHub Pages 在线展示
1. 打开刚刚推送的 GitHub 仓库页面，点击顶部的 **Settings** 选项卡。
2. 在左侧菜单中找到 **Pages**（位于 Code and automation 分类下）。
3. 在 **Build and deployment** 下的 **Source** 下拉框中，选择 **GitHub Actions**（本仓库内置了 `.github/workflows/deploy.yml` 自动化工作流）。
4. 部署完成后，您将获得公开访问链接：`https://<your-username>.github.io/ssq-lottery-visualizer/`。

---

## 🧮 算法原理与指标定义

### 1. 每期数字遗漏期数 (Omission Value)
- **定义**：某个特定号码自上次开出中奖后，至当前期次之间连续未开出的期数。
- **递推算法**：
  设第 $t$ 期开奖红球集合为 $R_t \subset \{1, 2, \dots, 33\}$，对于号码 $k \in \{1, 2, \dots, 33\}$：
  $$\text{Omission}(t, k) = \begin{cases} 0, & \text{若 } k \in R_t \text{ (本期中奖开出)} \\ \text{Omission}(t-1, k) + 1, & \text{若 } k \notin R_t \text{ (本期未开出)} \end{cases}$$
- **统计特征**：
  - 当前遗漏（Current Omission）：最新一期结束后的实时遗漏值。
  - 最大遗漏（Max Omission）：500 期历史长河中该号码出现过的最大连续未开出期数峰值。
  - 平均遗漏（Average Omission）：样本总期数 / 出现总次数。

### 2. 出球数与冷热温标准 (Hot / Warm / Cold Criteria)
在 500 次独立摇奖过程中，每个红球每期开出的理论独立概率为 $P_{red} = \frac{6}{33} \approx 18.18\%$，蓝球概率为 $P_{blue} = \frac{1}{16} = 6.25\%$。
- **500 期理论期望值**：
  - 红球：$E_{red} = 500 \times \frac{6}{33} \approx 90.91$ 次。
  - 蓝球：$E_{blue} = 500 \times \frac{1}{16} = 31.25$ 次。
- **冷热等级评定标准**：
  - 依据 500 期累计出球数排名分位区间：
    - **前 30% 档位** $\rightarrow$ **🔥 热号**（红球出球数排名前 10 位，蓝球前 5 位）。
    - **中间 40% 档位** $\rightarrow$ **🌤️ 温号**（红球出球数排名 11~23 位，蓝球 6~11 位）。
    - **后 30% 档位** $\rightarrow$ **❄️ 冷号**（红球出球数排名 24~33 位，蓝球 12~16 位）。
  - 同时系统在每期走势中结合当前遗漏值提供了**短期冷热预警**（红球遗漏 $\le 4$ 为近期热态，遗漏 $\ge 10$ 为冰冷预警）。

### 3. AC值 (数字复杂度 Arithmetic Complexity)
- 计算双色球 6 个红球两两差值的正整数集合的大小减去 $(6 - 1)$：
  $$AC = \text{Count}(\{|r_j - r_i| \mid 1 \le i < j \le 6\}) - (6 - 1)$$
- 经典双色球 AC 值范围通常在 6~9 之间，是衡量选号分散度与复杂度的重要依据。

---

## ⚙️ 自动化数据更新机制 (GitHub Actions)

项目仓库内包含 `.github/workflows/update_data.yml`，设置了定周期定时任务（Cron）：
- **触发时机**：北京时间每周二、周四、周日晚上 22:30（双色球当期官方摇奖完毕后）。
- **执行过程**：
  1. 运行 `scripts/fetch_ssq_data.py` 增量抓取最新开奖并重新计算全盘 33 红球与 16 蓝球的遗漏链。
  2. 自动更新 `data/ssq_history_500.json`、`data/ssq_history_500.csv` 及静态看板。
  3. 自动将最新数据变更 Git Commit 并推送回仓库，触发 GitHub Pages 自动刷新上线。

---

## 📄 开源许可证

本项目基于 [MIT License](LICENSE) 开源，允许任何个人或团队自由学习、二开、集成与分享。

*免责声明：本软件仅用于彩票历史大数据数理统计与可视化技术学习，彩票开奖结果由物理随机摇奖产生，历史统计规律不可作为绝对的预测保证，请广大彩友理性购彩。*
