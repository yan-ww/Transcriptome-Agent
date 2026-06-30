# Transcriptome-Agent
# 🧬 超迷你转录组分析Agent

一个基于Python的智能转录组数据分析Agent，支持自然语言交互、数据质量验证和差异表达分析。

## 📋 项目概述

这是一个轻量级的转录组数据分析工具，它将复杂的生物信息学分析流程封装为智能Agent。用户只需用自然语言描述分析需求，Agent会自动解析意图、验证数据质量并执行相应的分析流程。

### 核心特性

- 🗣️ **自然语言交互**: 支持中文命令输入，自动识别分析意图
- 🔍 **数据质量检查**: 自动验证样本重复数，识别统计学风险
- 📊 **差异表达分析**: 支持使用Python统计方法或R/DESeq2进行分析
- 📈 **可视化报告**: 自动生成火山图、热图等可视化结果
- 🎯 **可扩展架构**: 模块化设计，易于添加新的分析流程

## 🏗️ 项目架构
Projects/
├── app.py # Streamlit Web界面  
├── config.py # 配置文件  
├── run.py # 命令行运行脚本  
├── test_quick.py # 快速测试脚本  
│
├── agent/ # Agent核心模块  
│ ├── intent_extractor.py # 意图识别器  
│ ├── validator.py # 数据验证器
│ ├── planner.py # 分析规划器
│ ├── workflow_selector.py # 工作流选择器
│ ├── executor.py # 执行引擎
│ └── report_generator.py # 报告生成器
│
├── workflow/ # 分析工作流
│ ├── diff_expression.py # Python差异表达分析
│ ├── diff_expression_r.py # R/DESeq2差异表达分析
│ ├── clustering.py # 聚类分析
│ ├── r_executor.py # R脚本执行器
│ └── scripts/
│ └── deseq2_analysis.R # DESeq2 R脚本
│
├── data/ # 数据目录
├── output/ # 输出目录
└── scripts/
└── generate_test_data.py # 测试数据生成


## 🚀 快速开始

### 环境要求

- Python 3.8+
- R 4.0+ (可选，用于DESeq2分析)
- 依赖包: pandas, numpy, scipy, scikit-learn, streamlit

### 安装步骤

```bash
# 1. 克隆项目
git clone <repository-url>
cd Projects

# 2. 安装Python依赖
pip install pandas numpy scipy scikit-learn streamlit

# 3. 安装R依赖 (可选)
# 在R中执行:
# install.packages(c("DESeq2", "tidyverse", "optparse", "ggplot2"))
```
运行方式
方式1: Web界面 (推荐)
```bash
streamlit run app.py
```
📊 数据格式要求
表达矩阵 (expression_data.csv)
```csv
,Gene_001,Gene_002,Gene_003
Control_1,120.5,95.2,80.1
Control_2,115.3,98.7,75.3
Control_3,118.7,92.4,82.6
Treatment_1,302.1,245.6,40.2
Treatment_2,298.5,238.9,38.7
Treatment_3,310.2,250.1,42.3
```

样本信息 (sample_info.csv)
```csv
sample,group
Control_1,Control
Control_2,Control
Control_3,Control
Treatment_1,Treatment
Treatment_2,Treatment
Treatment_3,Treatment
```

## 🎯 使用示例
Web界面使用
1. 上传表达矩阵和样本信息文件
2. 输入分析命令，例如：
    "帮我分析这个转录组数据，做差异表达分析"
    "分析差异表达，P值: 0.01, log2FC: 1.5"
3. 点击"开始分析"
4. 查看结果并下载报告

## 📝 输出结果
分析完成后，会在output/目录生成：

diff_expression_results.csv: 完整差异表达结果

significant_genes.csv: 显著差异基因列表

volcano.png: 火山图

report.md: 分析报告