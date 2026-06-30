# config.py
"""
配置文件
"""
import os
from pathlib import Path

# 项目路径
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / 'data'
OUTPUT_DIR = PROJECT_ROOT / 'output'
WORKFLOW_DIR = PROJECT_ROOT / 'workflow'

# Rscript路径（根据实际安装路径修改）
R_CONFIG = {
    'rscript_path': os.environ.get('RSCRIPT_PATH', r"D:\R\R-4.1.1\bin\Rscript.exe")
}

# 确保目录存在
for dir_path in [DATA_DIR, OUTPUT_DIR, WORKFLOW_DIR]:
    dir_path.mkdir(exist_ok=True)

# 分析配置
ANALYSIS_CONFIG = {
    'differential_expression': {
        'default_p_value': 0.05,
        'default_log2fc': 1.0,
        'min_replicates': 3,
        'test_method': 'ttest'
    },
    'clustering': {
        'default_method': 'pca',
        'n_components': 2
    },
    'output': {
        'results_dir': OUTPUT_DIR,
        'report_format': 'markdown',
        'save_plots': True
    }
}