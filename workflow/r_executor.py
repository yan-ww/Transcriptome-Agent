# workflow/r_executor.py
"""
R脚本执行器
"""
import subprocess
import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional
import shutil
from config import R_CONFIG

class RExecutor:
    """R脚本执行器"""
    
    def __init__(self):
        """
        初始化R执行器
        
        Parameters:
        -----------
        rscript_path: Rscript可执行文件路径
        """
        self.rscript_path = R_CONFIG['rscript_path']
        self._check_r_available()
    
    def _check_r_available(self):
        """检查R是否可用"""
        if not shutil.which(self.rscript_path):
            raise RuntimeError(f"Rscript not found at {self.rscript_path}. Please install R.")
    
    def run_deseq2(self, counts_file: Path, metadata_file: Path, 
                   output_dir: Path, p_value: float = 0.05, 
                   log2fc: float = 1.0) -> Dict[str, Any]:
        """
        运行DESeq2分析
        
        Returns:
        --------
        包含分析结果的字典
        """
        # 准备R脚本路径
        script_dir = Path(__file__).parent
        r_script = script_dir / "deseq2_analysis.R"
        
        if not r_script.exists():
            raise FileNotFoundError(f"R脚本不存在: {r_script}")
        
        # 构建命令
        cmd = [
            self.rscript_path,
            str(r_script),
            "--counts", str(counts_file),
            "--metadata", str(metadata_file),
            "--output", str(output_dir),
            "--pvalue", str(p_value),
            "--log2fc", str(log2fc)
        ]
        
        print(f"🚀 执行R脚本: {' '.join(cmd)}")
        
        # 执行命令
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # 打印R输出
            print(result.stdout)
            if result.stderr:
                print("R警告/错误:", result.stderr)
            
            # 读取统计结果
            stats_file = output_dir / "statistics.json"
            if stats_file.exists():
                with open(stats_file, 'r') as f:
                    stats = json.load(f)
                
                # 读取结果表格
                results_file = output_dir / "significant_genes.csv"
                if results_file.exists():
                    results_df = pd.read_csv(results_file)
                    stats['results_table'] = results_df
                
                return stats
            else:
                return {'error': '统计文件未生成'}
                
        except subprocess.CalledProcessError as e:
            print(f"❌ R脚本执行失败: {e}")
            print(f"错误输出: {e.stderr}")
            return {'error': str(e), 'stderr': e.stderr}