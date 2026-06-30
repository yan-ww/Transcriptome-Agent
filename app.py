# app.py
"""
Streamlit 主应用
"""
import streamlit as st
import pandas as pd
from pathlib import Path
from agent import (
    IntentExtractor, DataValidator, Planner, 
    Executor, ReportGenerator
)
from config import DATA_DIR, OUTPUT_DIR, WORKFLOW_DIR

# 页面配置
st.set_page_config(
    page_title="🧬 转录组分析Agent",
    page_icon="🧬",
    layout="wide"
)

st.title("🧬 迷你转录组分析Agent")

# 初始化Agent组件
@st.cache(allow_output_mutation=True)
def init_agent():
    return {
        'intent_extractor': IntentExtractor(),
        'validator': DataValidator(),
        'planner': Planner(),
        'executor': Executor(WORKFLOW_DIR),
        'report_generator': ReportGenerator(OUTPUT_DIR)
    }

agent_components = init_agent()

if 'risk_confirmed' not in st.session_state:
    st.session_state.risk_confirmed = False
if "start_analysis" not in st.session_state:
    st.session_state.start_analysis = False    
# --- 初始化结束 ---

# 侧边栏 - 数据上传
with st.sidebar:
    st.header("📁 数据上传")
    
    expression_file = st.file_uploader(
        "上传表达矩阵 (CSV)",
        type=['csv'],
        help="行=基因, 列=样本"
    )
    
    sample_file = st.file_uploader(
        "上传样本信息 (CSV)",
        type=['csv'],
        help="包含 sample 和 group 列"
    )
    
    if expression_file and sample_file:
        # 读取数据
        data = pd.read_csv(expression_file, index_col=0)
        sample_info = pd.read_csv(sample_file)
        
        st.success(f"✅ 加载成功!")
        st.write(f"基因数: {data.shape[0]}, 样本数: {data.shape[1]}")
        st.write(f"样本组: {sample_info['group'].unique().tolist()}")

# 主界面
if expression_file and sample_file:
    # 用户输入
    st.header("💬 输入分析需求")
    
    command = st.text_input(
        "请输入您的分析命令",
        placeholder="例如: 帮我分析这个转录组数据，做差异表达分析",
        value=""
    )
    
    if st.button("🚀 开始分析"):
        st.session_state.start_analysis = True

    if st.session_state.start_analysis:
        with st.spinner("正在分析..."):
            # 1. 提取意图
            intent = agent_components['intent_extractor'].extract(command)
            if intent.confidence < 0.5:
                st.warning("⚠️ 您的需求不够明确，请指定分析类型，例如：差异表达分析、聚类分析等")
                st.stop()

            st.info(f"📌 识别分析类型: {intent.analysis_type} (置信度: {intent.confidence:.2f})")
            
            # 2. 验证数据
            validation = agent_components['validator'].check_replicates(sample_info)
            
            # 显示验证结果
            if validation.issues:
                for issue in validation.issues:
                    st.error(f"❌ {issue}")
            if validation.warnings:
                for warning in validation.warnings:
                    st.warning(f"⚠️ {warning}")
            if validation.is_valid:
                st.success(validation.summary)
            
            
            
            # 4. 执行分析
            if validation.is_valid:
                # 如果有风险，确认是否继续
                if validation.risk_groups and not st.session_state.risk_confirmed:
                    st.warning("⚠️ 存在样本数不足的组，继续分析可能导致结果不可靠")
                    # user_choice = st.radio(
                    #     "请选择是否继续：",
                    #     options=["取消分析", "继续分析"],
                    #     index=None
                    # )
                    
                    # # 根据用户选择决定是否继续
                    # if user_choice == "取消分析":
                    #     st.info("已取消分析")
                    #     st.stop()
                    # if user_choice == "继续分析":
                    #     st.session_state.risk_confirmed = True
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("取消分析"):
                            st.info("已取消分析")
                            st.stop()

                    with col2:
                        if st.button("继续分析"):
                            st.session_state.risk_confirmed = True
                    st.stop()
             

            if st.session_state.risk_confirmed or not validation.risk_groups:
                # 3. 生成计划
                plan = agent_components['planner'].create_plan(intent, validation)
                
                with st.expander("📋 查看分析计划", expanded=True):
                    st.text(agent_components['planner'].explain_plan(plan))    
                # 执行
                results = agent_components['executor'].execute(
                    plan, data, sample_info, validation, OUTPUT_DIR
                )
                
                # 5. 生成报告
                report = agent_components['report_generator'].generate_report(results, plan)
                
                # 显示结果
                st.header("📊 分析结果")
                
                # 显示统计信息
                col1, col2, col3 = st.columns(3)
                if results.get('type') == 'differential_expression':
                    col1.metric("上调基因", results.get('up_regulated', 0))
                    col2.metric("下调基因", results.get('down_regulated', 0))
                    col3.metric("显著差异基因", results.get('significant_total', 0))
                
                # 显示报告
                st.markdown(report)
                
                # 下载报告
                report_path = OUTPUT_DIR / 'report.md'
                with open(report_path, 'w',encoding="utf-8") as f:
                    f.write(report)
                
                with open(report_path, 'rb') as f:
                    st.download_button(
                        label="📥 下载分析报告",
                        data=f,
                        file_name="transcriptome_report.md",
                        mime="text/markdown"
                    )
                
                # 显示结果表格
                if 'results_table' in results:
                    st.subheader("📊 差异表达结果表")
                    df = results['results_table']
                    
                    # 添加筛选
                    show_significant = st.checkbox("仅显示显著差异基因")
                    if show_significant:
                        df = df[df['significant']]
                    
                    st.dataframe(df)
                    
                    # 下载CSV
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 下载结果CSV",
                        data=csv,
                        file_name="diff_expression_results.csv",
                        mime="text/csv"
                    )
            else:
                st.error("❌ 数据验证失败，请修复数据后重试")
else:
    st.info("👈 请先在侧边栏上传数据文件")
