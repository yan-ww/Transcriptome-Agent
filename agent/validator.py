# agent/validator.py
"""
数据验证器 - 检查数据质量和实验设计
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class ValidationReport:
    """验证报告"""
    is_valid: bool
    issues: List[str]
    warnings: List[str]
    group_counts: Dict[str, int]
    risk_groups: Dict[str, int]
    summary: str

class DataValidator:
    """数据质量验证器"""
    
    def __init__(self, min_replicates: int = 3):
        self.min_replicates = min_replicates
        
    def validate_expression_data(self, data: pd.DataFrame) -> List[str]:
        """
        验证表达矩阵质量
        """
        issues = []
        
        # 检查是否有缺失值
        if data.isnull().any().any():
            n_nulls = data.isnull().sum().sum()
            issues.append(f"数据包含 {n_nulls} 个缺失值")
        
        # 检查是否有零值或负值
        if (data <= 0).any().any():
            n_zero = (data <= 0).sum().sum()
            issues.append(f"数据包含 {n_zero} 个零值或负值")
        
        # 检查数据是否已标准化
        if data.max().max() > 1000 or data.min().min() < 0:
            issues.append("数据范围较大，建议进行标准化或取对数")
        
        return issues
    
    def validate_sample_info(self, sample_info: pd.DataFrame) -> List[str]:
        """
        验证样本信息
        """
        issues = []
        
        # 检查必要列
        required_cols = ['sample', 'group']
        for col in required_cols:
            if col not in sample_info.columns:
                issues.append(f"样本信息缺少必要列: {col}")
        
        # 检查是否有重复样本
        if 'sample' in sample_info.columns:
            duplicates = sample_info['sample'].duplicated().sum()
            if duplicates > 0:
                issues.append(f"存在 {duplicates} 个重复样本名")
        
        return issues
    
    def check_replicates(self, sample_info: pd.DataFrame) -> ValidationReport:
        """
        检查实验重复数
        """
        issues = []
        warnings = []
        
        # 计算每组样本数
        group_counts = sample_info['group'].value_counts().to_dict()
        
        # 检查各组样本数
        risk_groups = {}
        for group, count in group_counts.items():
            if count < self.min_replicates:
                risk_groups[group] = count
                warnings.append(f"组 '{group}' 只有 {count} 个样本 (建议 ≥ {self.min_replicates})")
        
        # 检查是否有足够的组
        if len(group_counts) < 2:
            issues.append(f"需要至少2个组进行差异表达分析，当前只有 {len(group_counts)} 组")
        
        # 生成摘要
        if risk_groups:
            summary = f"⚠️ 存在 {len(risk_groups)} 个组样本数不足 (建议 {self.min_replicates} 个重复)"
        else:
            summary = f"✅ 所有组都有 ≥ {self.min_replicates} 个样本"
        
        is_valid = len(issues) == 0
        
        return ValidationReport(
            is_valid=is_valid,
            issues=issues,
            warnings=warnings,
            group_counts=group_counts,
            risk_groups=risk_groups,
            summary=summary
        )
    
    def validate_match(self, data: pd.DataFrame, sample_info: pd.DataFrame) -> List[str]:
        """
        验证表达矩阵和样本信息是否匹配
        """
        issues = []
        
        data_samples = set(data.columns)
        info_samples = set(sample_info['sample'].values)
        
        # 检查样本是否完全匹配
        if not data_samples == info_samples:
            missing_in_data = info_samples - data_samples
            missing_in_info = data_samples - info_samples
            
            if missing_in_data:
                issues.append(f"样本信息中的样本在表达矩阵中缺失: {missing_in_data}")
            if missing_in_info:
                issues.append(f"表达矩阵中的样本在样本信息中缺失: {missing_in_info}")
        
        return issues