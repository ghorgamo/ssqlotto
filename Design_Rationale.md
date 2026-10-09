# UI/UX 设计重构规范：基于 Apple 视觉语言与冷温热层级体系

本项目看板（`index.html` 及 `dlt.html`）全面引入 **Apple 极简设计哲学（Apple Design Language）**，在保持数据准确性与高性能渲染的同时，系统性重构了视觉效果、色彩对比、排版层级、微交互质感以及冷温热三态号码的视觉识别系统。

---

## 1. 字体系统与排版层级 (Typography & Hierarchy)
- **字体族选择**：采用 Apple 原生字体系统 `-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", Arial, sans-serif`，代码与指标数字采用等宽等距字体 `"SF Mono", Menlo, Consolas, monospace`。
- **等宽数字对齐（Tabular Nums）**：所有开奖期号、统计频次、百分比、遗漏期数均启用 `font-variant-numeric: tabular-nums`，消除数字动态跳变时的晃动感，确保表格垂直列对齐工整。
- **字阶与字距系统**：
  - 顶部导航增加 Apple 经典 **Eyebrow 标语**（`LOTTERY BIG DATA INTELLIGENCE · PRO EDITION`），字距舒展（`letter-spacing: 0.08em`）。
  - 核心指标数值：`34px / 700`，字距收紧 `letter-spacing: -0.03em`，呈现 Apple 标志性的紧凑力量感。
  - 卡片大标题：`16px–18px / 700`，字距 `letter-spacing: -0.02em`。
  - 辅助元信息：`12px–13px / 500–600`，字距微调 `letter-spacing: 0.02em`，大写字母略微舒展以提升可读性。

---

## 2. 色彩系统与对比度优化 (Color Contrast & Apple System Colors)
- **深色模式（Apple Pro Dark Aesthetic）**：
  - 纯黑基底：采用 `#000000` 纯黑底色，适配 OLED/Mini-LED 屏幕，呈现极致深邃对比。
  - 毛玻璃层级：卡片容器采用 `rgba(28, 28, 30, 0.78)` 配合 `backdrop-filter: blur(24px) saturate(180%)`，使不同模块之间产生悬浮空间感。
  - 微光发丝边框：`1px solid rgba(255, 255, 255, 0.12)`，取代原本粗重的边框线。
- **浅色模式（Apple iOS Light Aesthetic）**：
  - 银灰底色：`#F5F5F7` 经典暖灰，文字采用 `#1D1D1F` 高对比近黑色，彻底消除刺眼白底。
  - 细腻环境阴影：多层级软投影 `box-shadow: 0 8px 30px rgba(0, 0, 0, 0.06)`。

---

## 3. 冷、温、热号码视觉识别系统 (Hot / Warm / Cold Distinction)
针对彩票大数据分析的核心痛点——“如何在海量号码中瞬间锁定冷热状态”，建立了独立且高对比度的三态感官体系：

| 状态分类 | 视觉定义 | 色系与渐变 | 容器材质与光效 |
| :--- | :--- | :--- | :--- |
| **🔥 热号 (Hot)** | 极高频出号态 | Apple Crimson 烈焰渐变<br>`linear-gradient(135deg, #FF453A, #FF2D55)` | 顶部暖光辐射背景，烈焰红微光投影 `box-shadow: 0 4px 16px rgba(255, 69, 58, 0.28)` |
| **🌤️ 温号 (Warm)** | 均值平衡态 | Apple Solar 琥珀金渐变<br>`linear-gradient(135deg, #FF9F0A, #FFD60A)` | 平和日光金边框，稳态琥珀柔光 `box-shadow: 0 4px 16px rgba(255, 159, 10, 0.22)` |
| **❄️ 冷号 (Cold)** | 长遗漏蓄势态 | Apple Glacier 极冰蓝渐变<br>`linear-gradient(135deg, #0A84FF, #64D2FF)` | 霜冷冰晶色调，极冷青蓝光效 `box-shadow: 0 4px 16px rgba(10, 132, 255, 0.22)`，遗漏值高亮醒目标注 |

- **全域温度光谱标尺（Thermal Spectrum Gauge）**：看板顶部设有动态温度色阶标尺，实时统计展示冷、温、热号码的数量分布（30% 极冷蓄势 · 40% 稳态平衡 · 30% 烈焰活跃），支持点击图例快速筛选。
- **全览网格卡片（Ball Stat Cards）**：卡片宽度拓宽至 `84px–88px`，提供充裕呼吸空间；卡片配备 3px 动态热力指示条（Heat Meter Bar），顶部带有对应温态的微光环境反射；长遗漏号码（≥15期）展示极冷雪花标识。
- **全量遗漏矩阵走势图（Omission Matrix）**：
  - 中奖号（Hit）：渲染为立体高光 3D 物理质感球体（含左上方反射高光与环境漫反射投影）。
  - 遗漏值（Omission）：分级热力色彩——普通遗漏（1–9 期）弱对比呈现；中度预警（10–17 期）琥珀微光；极端极冷预警（18+ 期）珊瑚烈焰加粗胶囊高亮，使长久未开出的冷号一眼可见。

---

## 4. 用户交互与微动效 (Interaction & Micro-animations)
- **双层交互分段控制器（Segmented Controls）**：双色球/大乐透切换与冷温热分类筛选均采用 Apple 胶囊分段组件，选中状态触发专属色系微光阴影（热号染红、温号染金、冷号染蓝）。
- **全览分布网格即时筛选**：支持在概览大盘中直接切换“全部 / 🔥热号 / 🌤️温号 / ❄️冷号”，实时重排网格视图。
- **卡片触觉悬浮**：鼠标悬停在卡片或球体上触发平滑浮起（`translateY(-3px) scale(1.02)`）与扩散柔光阴影。
- **操作按钮**：全胶囊圆角（Pill shape, 980px），主要同步操作采用 Apple Blue 亮眼主色，次要操作采用磨砂半透材质。
