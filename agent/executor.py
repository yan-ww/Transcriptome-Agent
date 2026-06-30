# agent/executor.py
"""
执行器 - 调用分析流程
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional, Any
from pathlib import Path
import importlib
from agent.workflow_selector import WorkflowSelector
from agent.planner import AnalysisPlan
from agent.validator import ValidationReport

class Executor:
    """执行分析流程"""
    
    def __init__(self, workflow_dir: Path):
        self.workflow_selector = WorkflowSelector(workflow_dir)
        self.current_workflow = None
        
    def execute(self, plan: AnalysisPlan, data: pd.DataFrame, 
                sample_info: pd.DataFrame, validation_report: ValidationReport,
                output_dir: Path) -> Dict[str, Any]:
        """
        执行分析计划
        """
        print(f"\n🚀 开始执行: {plan.analysis_type}")
        print("-" * 50)
        
        # 选择工作流
        workflow_info = self.workflow_selector.select_workflow(plan.analysis_type)
        if not workflow_info:
            raise ValueError(f"未找到 '{plan.analysis_type}' 工作流")
        
        # 动态加载工作流
        try:
            module = importlib.import_module(workflow_info['module'])
            workflow_class = getattr(module, workflow_info['class'])
            workflow = workflow_class()
        except Exception as e:
            raise ValueError(f"❌ 加载工作流失败: {e}")
            
        
        # 执行工作流
        try:
            results = workflow.run(
                data=data,
                sample_info=sample_info,
                params=plan.parameters,
                output_dir=output_dir
            )
            print(f"✅ 工作流执行完成")
            return results
        except Exception as e:
            raise ValueError(f"❌ 工作流执行失败: {e}")

    
    