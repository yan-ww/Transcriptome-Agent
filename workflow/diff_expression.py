# workflow/diff_expression_r.py
"""
使用R/DESeq2的差异表达分析工作流
"""
from pathlib import Path
from typing import Dict, Any
import pandas as pd
from workflow.r_executor import RExecutor

class DiffExpressionWorkflow:
    """基于R的差异表达分析工作流"""
    
    description = "使用DESeq2进行差异表达分析"
    
    def __init__(self):
        self.r_executor = RExecutor()
    
    def run(self, data: pd.DataFrame, sample_info: pd.DataFrame,
            params: Dict, output_dir: Path) -> Dict[str, Any]:
        """
        执行差异表达分析
        """
        print("🔬 执行DESeq2差异表达分析...")
        
        # 保存数据为CSV供R使用
        counts_file = output_dir / "counts_for_r.csv"
        metadata_file = output_dir / "metadata_for_r.csv"
        
        # 确保数据是整数（DESeq2要求）
        data_int = data.round().astype(int)
        data_int.to_csv(counts_file)
        sample_info.to_csv(metadata_file, index=False)
        
        print(f"  📁 数据准备完成:")
        print(f"    表达矩阵: {counts_file}")
        print(f"    样本信息: {metadata_file}")
        
        # 运行DESeq2
        p_value = params.get('p_value', 0.05)
        log2fc = params.get('log2fc', 1.0)
        
        results = self.r_executor.run_deseq2(
            counts_file=counts_file,
            metadata_file=metadata_file,
            output_dir=output_dir,
            p_value=p_value,
            log2fc=log2fc
        )
        
        if 'error' in results:
            return results
        
        # 添加额外信息
        results['type'] = 'differential_expression'
        results['method'] = 'DESeq2'
        results['output_dir'] = str(output_dir)
        
        # 读取显著基因列表
        sig_file = output_dir / "significant_genes.csv"
        if sig_file.exists():
            sig_genes = pd.read_csv(sig_file)
            results['top_up'] = sig_genes.nlargest(10, 'log2FoldChange')[
                ['gene', 'log2FoldChange', 'padj']].to_dict('records')
            results['top_down'] = sig_genes.nsmallest(10, 'log2FoldChange')[
                ['gene', 'log2FoldChange', 'padj']].to_dict('records')
        
        return results