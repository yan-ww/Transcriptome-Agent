from agent.intent_extractor import IntentExtractor
from agent.validator import (ValidationReport, DataValidator)
from agent.planner import Planner
from agent.workflow_selector import WorkflowSelector
import pandas as pd
from pathlib import Path
import os
from agent.executor import Executor

Info = pd.read_csv("data/dataInfo.csv")
validator = DataValidator(min_replicates=3)
validation_report  = validator.check_replicates(Info)
print("Validation Report:", validation_report)
intentex = IntentExtractor()
user_input = "我想做一个差异表达分析，p值小于0.05，log2fc大于1"
# user_input = "我想做一个pca分析"
# user_input = "auhsnfhdm"
intent = intentex.extract(user_input)
print("Intent:", intent)
print(intentex.suggest_corrections(intent))
plan = Planner()
plann = plan.create_plan(intent, validation_report)
print(plann)
print(plan.explain_plan(plann))
workflow_selector = WorkflowSelector(workflow_dir=Path("workflow"))
print("Available Workflows:", workflow_selector.available_workflows)
print(workflow_selector.select_workflow(plann.analysis_type))

# 执行
outdir = Path("output")
executor = Executor(workflow_dir=Path("workflow"))
