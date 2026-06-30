# agent/report_generator.py
"""
报告生成器 - 生成分析报告
"""
from typing import Dict, Any
from pathlib import Path
import pandas as pd
from datetime import datetime

class ReportGenerator:
    """生成分析报告"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        
    def generate_report(self, results: Dict[str, Any], plan) -> str:
        """
        生成分析报告
        """
        report_type = results.get('type', 'unknown')
        
        if report_type == 'differential_expression':
            return self._generate_diff_report(results, plan)
        elif report_type == 'clustering':
            return self._generate_clustering_report(results, plan)
        else:
            return self._generate_general_report(results, plan)
    
    def _generate_diff_report(self, results: Dict, plan) -> str:
        """生成差异表达报告"""
        lines = [
            "# 转录组差异表达分析报告",
            "",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 分析概述",
            f"- 分析类型: 差异表达分析",
            f"- 比较组: {results.get('group1', 'N/A')} vs {results.get('group2', 'N/A')}",
            f"- 总基因数: {results.get('total_genes', 0)}",
            f"- 显著差异基因: {results.get('significant_total', 0)}",
            "",
            "## 差异表达统计",
            f"- 🔺 上调基因: **{results.get('up_regulated', 0)}** 个",
            f"- 🔻 下调基因: **{results.get('down_regulated', 0)}** 个",
            "",
        ]
        
        # 添加前10个差异基因
        if 'results_table' in results:
            df = results['results_table']
            df_sig = df[df['significant']].sort_values('log2FoldChange', ascending=False)
            
            if len(df_sig) > 10:
                lines.append("## Top 10 差异基因")
                lines.append("")
                lines.append("| 基因 | log2FC | p值 | 表达趋势 |")
                lines.append("|------|--------|-----|----------|")
                
                top_genes = df_sig.head(10)
                for _, row in top_genes.iterrows():
                    trend = "上调" if row['log2FoldChange'] > 0 else "下调"
                    lines.append(f"| {row['gene']} | {row['log2FoldChange']:.3f} | {row['pvalue']:.3e} | {trend} |")
        
        # 添加建议
        lines.extend([
            "",
            "## 建议",
            "- 建议对显著差异基因进行GO和KEGG富集分析",
            "- 可使用qPCR验证关键差异基因的表达变化",
            "- 考虑使用更严格的FDR校正控制假阳性率"
        ])
        
        return '\n'.join(lines)
    
    def _generate_clustering_report(self, results: Dict, plan) -> str:
        """生成聚类报告"""
        lines = [
            "# 转录组聚类分析报告",
            "",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 分析概述",
            f"- 分析类型: 聚类分析",
            f"- 聚类方法: {results.get('method', 'PCA + K-means')}",
            "",
            "## 聚类结果",
            f"- 聚类数量: {results.get('n_clusters', 'N/A')}",
            f"- 解释方差比例: {results.get('explained_variance', 'N/A')}",
            "",
            "## 聚类分布",
            results.get('cluster_distribution', '')
        ]
        
        return '\n'.join(lines)
    
    def _generate_general_report(self, results: Dict, plan) -> str:
        """生成通用报告"""
        lines = [
            "# 转录组分析报告",
            "",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 分析结果",
            f"- 分析类型: {results.get('type', '未知')}",
            "- 详细结果请查看输出文件",
            "",
            "## 输出文件",
        ]
        
        # 列出输出文件
        for file in self.output_dir.glob('*'):
            if file.is_file():
                lines.append(f"- {file.name}")
        
        return '\n'.join(lines)
    
    def save_report(self, report: str, filename: str = 'report.md'):
        """
        保存报告到文件
        """
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        return output_path