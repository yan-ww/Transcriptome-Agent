# agent/intent_extractor.py
"""
意图提取器 - 理解用户自然语言需求
"""
import re
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Intent:
    """用户意图数据类"""
    analysis_type: str  # 'differential_expression', 'clustering', 'heatmap', etc.
    confidence: float   # 置信度 0-1
    params: Dict
    raw_command: str

class IntentExtractor:
    """从自然语言中提取分析意图"""
    
    def __init__(self):
        # 定义关键词映射
        self.intent_patterns = {
            'differential_expression': {
                'keywords': ['差异', 'diff', 'differential', '表达', 'expression', '比较', '对比'],
                'weight': 1.0
            },
            'clustering': {
                'keywords': ['聚类', 'cluster', 'pca', '降维', '分类'],
                'weight': 0.8
            },
            'heatmap': {
                'keywords': ['热图', 'heatmap', '热力图', '聚类图'],
                'weight': 0.7
            },
            'volcano': {
                'keywords': ['火山图', 'volcano', '火山'],
                'weight': 0.6
            },
            'go_enrichment': {
                'keywords': ['go', '富集', 'enrichment', '通路', 'pathway', '功能'],
                'weight': 0.5
            }
        }
        
        # 参数提取模式
        self.param_patterns = {
            'p_value': r'p值\s*(?:小于|大于|≤|≥|=|：|:)\s*([0-9.]+)',
            'log2fc': r'log2fc\s*(?:大于|小于|≥|≤|=|：|:)\s*([0-9.]+)',
            'method': r'方法\s*[：:]\s*([a-zA-Z_]+)'
        }
    
    def extract(self, command: str) -> Intent:
        """
        从命令中提取意图
        """
        command_lower = command.lower()
        
        # 计算每个类型的得分
        scores = {}
        for intent_type, pattern in self.intent_patterns.items():
            score = 0
            for keyword in pattern['keywords']:
                if keyword in command_lower:
                    score += pattern['weight']
            scores[intent_type] = score
        
        # 选择最高得分的类型
        if max(scores.values()) > 0:
            best_type = max(scores, key=scores.get)
            confidence = min(scores[best_type], 1.0)
        else:
            # 默认做差异表达
            best_type = 'differential_expression'
            confidence = 0.3
        
        # 提取参数
        params = {}
        for param_name, pattern in self.param_patterns.items():
            match = re.search(pattern, command_lower)
            if match:
                try:
                    params[param_name] = float(match.group(1))
                except ValueError:
                    params[param_name] = match.group(1)
        
        return Intent(
            analysis_type=best_type,
            confidence=confidence,
            params=params,
            raw_command=command
        )
    
    def suggest_corrections(self, intent: Intent) -> List[str]:
        """
        如果意图不明确，提供建议
        """
        suggestions = []
        if intent.confidence < 0.5:
            suggestions.append("您的需求不够明确，请指定分析类型，例如：差异表达分析、聚类分析等")
        return suggestions