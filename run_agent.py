#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
财报分析系统 - Agent架构启动脚本
"""

import os
import sys
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/agent_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AgentSystem:
    """Agent系统管理器"""
    
    def __init__(self, config_path: str = "configs/main_config.yaml"):
        """初始化Agent系统
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = self.load_config()
        self.agents = {}
        self.skills = {}
        
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件
        
        Returns:
            配置字典
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"配置文件加载成功: {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"配置文件加载失败: {e}")
            raise
    
    def initialize_directories(self):
        """初始化目录结构"""
        directories = self.config.get('directories', {})
        for dir_name, dir_path in directories.items():
            path = Path(dir_path)
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                logger.info(f"创建目录: {path}")
    
    def load_agents(self):
        """加载所有Agent配置"""
        agents_config = self.config.get('agents', {})
        for agent_name, agent_config in agents_config.items():
            if agent_config.get('enabled', True):
                try:
                    agent_path = agent_config.get('config_file')
                    if agent_path and Path(agent_path).exists():
                        with open(agent_path, 'r', encoding='utf-8') as f:
                            agent_info = yaml.safe_load(f)
                        self.agents[agent_name] = agent_info
                        logger.info(f"Agent加载成功: {agent_name}")
                    else:
                        logger.warning(f"Agent配置文件不存在: {agent_path}")
                except Exception as e:
                    logger.error(f"Agent加载失败 {agent_name}: {e}")
    
    def load_skills(self):
        """加载所有技能配置"""
        skills_config = self.config.get('skills', {})
        for skill_name, skill_config in skills_config.items():
            if skill_config.get('enabled', True):
                try:
                    skill_path = skill_config.get('config_file')
                    if skill_path and Path(skill_path).exists():
                        with open(skill_path, 'r', encoding='utf-8') as f:
                            skill_info = yaml.safe_load(f)
                        self.skills[skill_name] = skill_info
                        logger.info(f"技能加载成功: {skill_name}")
                    else:
                        logger.warning(f"技能配置文件不存在: {skill_path}")
                except Exception as e:
                    logger.error(f"技能加载失败 {skill_name}: {e}")
    
    def list_agents(self):
        """列出所有可用的Agent"""
        print("\n" + "="*60)
        print("可用的Agent:")
        print("="*60)
        for agent_name, agent_info in self.agents.items():
            print(f"\n🔹 {agent_name}")
            print(f"   描述: {agent_info.get('description', '无描述')}")
            print(f"   版本: {agent_info.get('version', '未知')}")
            print(f"   技能: {', '.join(agent_info.get('skills', []))}")
    
    def list_skills(self):
        """列出所有可用的技能"""
        print("\n" + "="*60)
        print("可用的技能:")
        print("="*60)
        for skill_name, skill_info in self.skills.items():
            print(f"\n🔧 {skill_name}")
            print(f"   描述: {skill_info.get('description', '无描述')}")
            print(f"   版本: {skill_info.get('version', '未知')}")
            capabilities = skill_info.get('capabilities', [])
            if capabilities:
                print(f"   能力: {', '.join(capabilities[:3])}...")
    
    def list_workflows(self):
        """列出所有可用的工作流"""
        workflows = self.config.get('workflows', {})
        print("\n" + "="*60)
        print("可用的工作流:")
        print("="*60)
        for workflow_name, workflow_config in workflows.items():
            print(f"\n📋 {workflow_name}")
            print(f"   名称: {workflow_config.get('name', '未知')}")
            print(f"   描述: {workflow_config.get('description', '无描述')}")
            steps = workflow_config.get('steps', [])
            if steps:
                print(f"   步骤数: {len(steps)}")
    
    def run_workflow(self, workflow_name: str, inputs: Dict[str, Any]):
        """运行工作流
        
        Args:
            workflow_name: 工作流名称
            inputs: 输入参数
        """
        workflows = self.config.get('workflows', {})
        if workflow_name not in workflows:
            logger.error(f"工作流不存在: {workflow_name}")
            return
        
        workflow = workflows[workflow_name]
        logger.info(f"开始执行工作流: {workflow.get('name', workflow_name)}")
        
        # 这里应该实现工作流执行逻辑
        # 由于这是示例，我们只打印工作流信息
        print(f"\n🚀 执行工作流: {workflow.get('name', workflow_name)}")
        print(f"输入参数: {inputs}")
        
        # 模拟工作流执行
        steps = workflow.get('steps', [])
        for step in steps:
            step_name = step.get('name', '未知步骤')
            agent_name = step.get('agent', '未知Agent')
            print(f"  → 步骤: {step_name} (Agent: {agent_name})")
        
        print(f"\n✅ 工作流执行完成")
        logger.info(f"工作流执行完成: {workflow_name}")
    
    def start(self):
        """启动Agent系统"""
        logger.info("启动财报分析Agent系统")
        print("="*60)
        print("💰 财报分析Agent系统")
        print("="*60)
        
        # 初始化
        self.initialize_directories()
        self.load_agents()
        self.load_skills()
        
        # 显示系统信息
        print(f"\n系统名称: {self.config.get('system_name', '未知')}")
        print(f"系统版本: {self.config.get('version', '未知')}")
        print(f"Agent数量: {len(self.agents)}")
        print(f"技能数量: {len(self.skills)}")
        print(f"工作流数量: {len(self.config.get('workflows', {}))}")
        
        return self


def main():
    """主函数"""
    try:
        # 创建Agent系统
        system = AgentSystem()
        system.start()
        
        # 显示可用资源
        system.list_agents()
        system.list_skills()
        system.list_workflows()
        
        # 示例：运行工作流
        print("\n" + "="*60)
        print("示例：运行完整财报分析工作流")
        print("="*60)
        
        # 这里可以添加实际的工作流执行代码
        # 例如：system.run_workflow('full_analysis', {'pdf_file': 'source/英洛华_2025_年报.pdf'})
        
        print("\n🎯 Agent系统已就绪，等待指令...")
        
    except Exception as e:
        logger.error(f"系统启动失败: {e}")
        print(f"❌ 系统启动失败: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
