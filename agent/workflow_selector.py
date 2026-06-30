# agent/workflow_selector.py
"""
工作流选择器 - 选择合适的分析流程
"""
from typing import Dict, List, Optional
from pathlib import Path
import importlib.util
import sys

class WorkflowSelector:
    """选择和执行分析工作流"""
    
    def __init__(self, workflow_dir: Path):
        self.workflow_dir = workflow_dir
        self.available_workflows = self._discover_workflows()
        
    def _discover_workflows(self) -> Dict[str, Dict]:
        """
        发现可用的工作流
        """
        workflows = {}
        
        # 内置工作流
        builtin = {
            'differential_expression': {
                'module': 'workflow.diff_expression',
                'class': 'DiffExpressionWorkflow',
                'description': '差异表达分析工作流'
            },
            'clustering': {
                'module': 'workflow.clustering',
                'class': 'ClusteringWorkflow',
                'description': '聚类分析工作流'
            },
            'heatmap': {
                'module': 'workflow.heatmap',
                'class': 'HeatmapWorkflow',
                'description': '热图绘制工作流'
            }
        }
        
        # # 检查用户自定义工作流
        # for workflow_file in self.workflow_dir.glob('*.py'):
        #     if workflow_file.stem.startswith('_'):
        #         continue
            
        #     module_name = f"workflow.{workflow_file.stem}"
        #     spec = importlib.util.spec_from_file_location(module_name, workflow_file)
        #     if spec and spec.loader:
        #         module = importlib.util.module_from_spec(spec)
        #         sys.modules[module_name] = module
        #         try:
        #             spec.loader.exec_module(module)
        #             # 查找工作流类
        #             for attr_name in dir(module):
        #                 if attr_name.endswith('Workflow'):
        #                     workflow_class = getattr(module, attr_name)
        #                     workflows[workflow_file.stem] = {
        #                         'module': module_name,
        #                         'class': attr_name,
        #                         'description': getattr(workflow_class, 'description', f'{attr_name}工作流')
        #                     }
        #         except Exception as e:
        #             print(f"⚠️ 加载工作流 {workflow_file} 失败: {e}")
        
        # 添加内置工作流
        for key, value in builtin.items():
            if key not in workflows:
                workflows[key] = value
        
        return workflows
    
    def select_workflow(self, analysis_type: str) -> Optional[Dict]:
        """
        选择合适的工作流
        """
        # 精确匹配
        if analysis_type in self.available_workflows:
            return self.available_workflows[analysis_type]
        
        # 模糊匹配
        for workflow_name, workflow_info in self.available_workflows.items():
            if workflow_name.lower() in analysis_type.lower():
                return workflow_info
        
        # 默认返回差异表达
        return self.available_workflows.get('differential_expression')
    
    def list_workflows(self) -> Dict[str, str]:
        """
        列出所有可用工作流
        """
        return {name: info['description'] for name, info in self.available_workflows.items()}