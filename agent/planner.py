# agent/planner.py
"""
规划器 - 生成分析计划
"""
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from agent.intent_extractor import Intent
from agent.validator import ValidationReport

@dataclass
class AnalysisPlan:
    """分析计划"""
    analysis_type: str
    steps: List[str]
    required_R_libraries: List[str]
    expected_outputs: List[str]
    parameters: Dict
    priority: int  # 1-5, 1最高
    
class Planner:
    """生成分析计划"""
    
    def __init__(self):
        self.workflow_registry = self._init_workflows()
        
    def _init_workflows(self) -> Dict:
        """初始化可用的工作流"""
        return {
            'differential_expression': {
                'steps': [
                    'DESeq2分析',
                    '筛选显著差异基因',
                    '生成火山图'
                ],
                'required_R_libraries': ['DESeq2', 'ggplot2'],
                'outputs': ['diff_genes.csv', 'volcano.png', 'report.md'],
                'priority': 1
            },
            'clustering': {
                'steps': [
                    '数据标准化',
                    'PCA降维',
                    '可视化聚类结果',
                ],
                'required_R_libraries': ['pca','ggplot2'],
                'outputs': ['pca_plot.png', 'cluster_results.csv', 'report.md'],
                'priority': 2
            },
            'heatmap': {
                'steps': [
                    '数据标准化',
                    '计算样本相关性',
                    '层次聚类',
                    '绘制热图',
                    '注释样本分组'
                ],
                'required_R_libraries': ['pheatmap', 'ggplot2'],
                'outputs': ['heatmap.png', 'correlation_matrix.csv'],
                'priority': 3
            }
        }
    
    def create_plan(self, intent: Intent, validation_report: ValidationReport) -> AnalysisPlan:
        """
        根据意图和验证结果创建分析计划
        """
        analysis_type = intent.analysis_type
        
        # 如果验证失败，调整计划
        if not validation_report.is_valid:
            # 添加数据修复步骤
            fix_steps = ['数据修复和清洗']
        else:
            fix_steps = []
        
        # 获取工作流定义
        workflow = self.workflow_registry.get(analysis_type, self.workflow_registry['differential_expression'])
        
        # 检查风险并调整
        if validation_report.risk_groups:
            # 在计划中加入警告
            risk_steps = [f"⚠️ 警告: 样本数不足 (groups: {list(validation_report.risk_groups.keys())})"]
        else:
            risk_steps = []
        
        # 合并所有步骤
        all_steps = fix_steps + risk_steps + workflow['steps']
        
        # 合并参数
        params = intent.params.copy()
        params['min_replicates'] = 3
        
        return AnalysisPlan(
            analysis_type=analysis_type,
            steps=all_steps,
            required_R_libraries=workflow['required_R_libraries'],
            expected_outputs=workflow['outputs'],
            parameters=params,
            priority=workflow['priority']
        )
    
    def explain_plan(self, plan: AnalysisPlan) -> str:
        """
        生成分析计划的易读描述
        """
        lines = [
            f"📋 分析计划: {plan.analysis_type}",
            f"  🎯 优先级: {plan.priority}",
            f"  📦 所需库: {', '.join(plan.required_R_libraries)}",
            "\n  📝 执行步骤:"
        ]
        
        for i, step in enumerate(plan.steps, 1):
            lines.append(f"    {i}. {step}")
        
        lines.append(f"\n  📤 输出文件: {', '.join(plan.expected_outputs)}")
        
        if plan.parameters:
            lines.append("\n  ⚙️ 参数:")
            for key, value in plan.parameters.items():
                lines.append(f"    {key}: {value}")
        
        return '\n'.join(lines)