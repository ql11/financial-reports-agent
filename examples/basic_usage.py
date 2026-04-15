#!/usr/bin/env python
"""财报分析系统使用示例"""

import os
import sys
import yaml
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def load_config():
    """加载配置文件"""
    config_path = project_root / "configs" / "main_config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def list_agents():
    """列出所有可用的Agent"""
    config = load_config()
    print("📋 可用Agent列表:")
    print("-" * 50)
    
    for agent_name, agent_config in config.get('agents', {}).items():
        if agent_config.get('enabled', True):
            print(f"🔹 {agent_name}")
            print(f"   描述: {agent_config.get('description', '无描述')}")
            print(f"   技能: {', '.join(agent_config.get('skills', []))}")
            print()

def list_skills():
    """列出所有可用的技能"""
    skills_dir = project_root / "skills"
    print("📋 可用技能列表:")
    print("-" * 50)
    
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir():
            skill_config_path = skill_dir / "skill.yaml"
            if skill_config_path.exists():
                with open(skill_config_path, 'r', encoding='utf-8') as f:
                    skill_config = yaml.safe_load(f)
                    print(f"🔹 {skill_dir.name}")
                    print(f"   描述: {skill_config.get('description', '无描述')}")
                    print(f"   版本: {skill_config.get('version', '1.0.0')}")
                    print()

def list_workflows():
    """列出所有可用的工作流"""
    workflows_dir = project_root / "workflows"
    print("📋 可用工作流列表:")
    print("-" * 50)
    
    for workflow_file in workflows_dir.glob("*.yaml"):
        with open(workflow_file, 'r', encoding='utf-8') as f:
            workflow_config = yaml.safe_load(f)
            workflow_name = workflow_config.get('workflow', {}).get('name', workflow_file.stem)
            print(f"🔹 {workflow_name}")
            print(f"   文件: {workflow_file.name}")
            steps = workflow_config.get('workflow', {}).get('steps', [])
            print(f"   步骤数: {len(steps)}")
            print()

def run_simple_analysis():
    """运行简单的分析示例"""
    print("🚀 运行简单分析示例")
    print("-" * 50)
    
    # 检查输入目录
    inputs_dir = project_root / "inputs"
    if not inputs_dir.exists():
        print("❌ inputs目录不存在，正在创建...")
        inputs_dir.mkdir(parents=True, exist_ok=True)
    
    # 检查是否有PDF文件
    pdf_files = list(inputs_dir.glob("*.pdf"))
    if not pdf_files:
        print("ℹ️  inputs目录中没有PDF文件")
        print("   请将PDF财报文件放入 inputs/ 目录")
        print("   示例文件: 英洛华_2025_年报.pdf")
        return
    
    print(f"✅ 找到 {len(pdf_files)} 个PDF文件:")
    for pdf_file in pdf_files:
        print(f"   - {pdf_file.name}")
    
    # 模拟分析流程
    print("\n📊 模拟分析流程:")
    print("1. 📄 读取PDF文件...")
    print("2. 🔍 提取财务数据...")
    print("3. 📈 分析财务指标...")
    print("4. ⚠️  评估风险...")
    print("5. 📋 生成报告...")
    print("6. ✅ 分析完成!")
    
    # 创建输出目录
    outputs_dir = project_root / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建示例报告
    report_path = outputs_dir / "example_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 财报分析报告示例\n\n")
        f.write("## 公司信息\n")
        f.write("- 公司名称: 示例公司\n")
        f.write("- 报告年份: 2025\n")
        f.write("- 分析时间: 2026-04-15\n\n")
        f.write("## 关键指标\n")
        f.write("| 指标 | 数值 | 行业平均 | 状态 |\n")
        f.write("|------|------|----------|------|\n")
        f.write("| 毛利率 | 35.2% | 30.5% | ✅ 良好 |\n")
        f.write("| 净利率 | 12.8% | 10.2% | ✅ 良好 |\n")
        f.write("| ROE | 15.3% | 12.1% | ✅ 良好 |\n")
        f.write("| 资产负债率 | 45.2% | 55.8% | ✅ 良好 |\n\n")
        f.write("## 风险提示\n")
        f.write("1. 应收账款周转率较低\n")
        f.write("2. 存货周转率下降\n")
        f.write("3. 现金流波动较大\n\n")
        f.write("## 综合评分: 7.5/10\n")
    
    print(f"\n📄 示例报告已生成: {report_path}")

def main():
    """主函数"""
    print("=" * 60)
    print("📊 财报分析系统 - Agent架构")
    print("=" * 60)
    
    while True:
        print("\n请选择操作:")
        print("1. 📋 查看可用Agent")
        print("2. 🛠️  查看可用技能")
        print("3. 🔄 查看可用工作流")
        print("4. 🚀 运行简单分析示例")
        print("5. 📖 查看文档")
        print("6. 🚪 退出")
        
        choice = input("\n请输入选项 (1-6): ").strip()
        
        if choice == "1":
            list_agents()
        elif choice == "2":
            list_skills()
        elif choice == "3":
            list_workflows()
        elif choice == "4":
            run_simple_analysis()
        elif choice == "5":
            print("\n📚 文档:")
            print("1. README.md - 项目概述和使用指南")
            print("2. docs/ARCHITECTURE.md - 架构设计文档")
            print("3. 查看 configs/ 目录下的配置文件")
            print("4. 查看 agents/ 目录下的Agent配置")
            print("5. 查看 skills/ 目录下的技能配置")
        elif choice == "6":
            print("\n👋 再见!")
            break
        else:
            print("❌ 无效选项，请重新输入")

if __name__ == "__main__":
    main()