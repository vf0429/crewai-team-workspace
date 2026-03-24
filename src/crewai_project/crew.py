import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

# 强制读取 .env 文件里的 Key，覆盖系统旧的环境变量
load_dotenv(override=True)

def load_agent_from_md(filepath: str) -> dict:
    """读取 Markdown 内的 Agent 配置，支持旧版 Headers 格式和新版 YAML Frontmatter 格式"""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"找不到 Agent 配置文件: {filepath}")
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 尝试解析 YAML Frontmatter (agency-agents 格式)
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            body = parts[2].strip()
            
            role = ""
            goal = ""
            for line in frontmatter.split('\n'):
                line = line.strip()
                if line.startswith('name:'):
                    role = line.split('name:', 1)[1].strip().strip('"\'')
                elif line.startswith('description:'):
                    goal = line.split('description:', 1)[1].strip().strip('"\'')
            
            if role and goal:
                return {
                    'role': role,
                    'goal': goal,
                    'backstory': body
                }
    
    # 2. 回退到旧版的 Header 解析逻辑
    sections = {}
    current_section = None
    
    for line in content.split('\n'):
        if line.startswith('# Role'):
            current_section = 'role'
            sections[current_section] = []
        elif line.startswith('# Goal'):
            current_section = 'goal'
            sections[current_section] = []
        elif line.startswith('# Backstory'):
            current_section = 'backstory'
            sections[current_section] = []
        elif current_section and line.strip():
            sections[current_section].append(line.strip())
            
    return {
        'role': ' '.join(sections.get('role', [])),
        'goal': ' '.join(sections.get('goal', [])),
        'backstory': '\n'.join(sections.get('backstory', []))
    }

base_dir = os.path.dirname(__file__)
agents_dir = os.path.join(base_dir, 'config/agents')

# ----------------------------------------------------
# 1. 预定义三大模型 (LLM_MAP)
# ----------------------------------------------------
LLM_MAP = {
    "codex": LLM(
        model="openai/gpt-5.4",
        api_key=os.getenv("CODEX_API_KEY", ""),
        base_url="http://localhost:8081/v1"
    ),
    "kimi": LLM(
        model="anthropic/kimi-k2.5-thinking-turbo",
        api_key=os.getenv("KIMI_API_KEY", ""),
        base_url="https://api.kimi.com/coding/"
    ),
    "minimax": LLM(
        model="openai/MiniMax-M2.7",
        api_key=os.getenv("MINIMAX_API_KEY", ""),
        base_url="https://api.minimaxi.chat/v1"
    )
}

# ==============================================================================
# ⬇️ OPENCLAW FILL-IN-THE-BLANKS AREA ⬇️
# OpenClaw 只需要根据需求，修改这个 TEAM_TASKS 列表。其他所有代码都不需要动！
# 可用的 model 只有三个: "codex", "kimi", "minimax"
# 可用的 agent_file 存在于 src/crewai_project/config/agents/ 目录下
# ==============================================================================

TEAM_TASKS = [
    {
        "agent_file": "product_manager.md",
        "model": "codex",
        "task_description": "用一句话描述一个'计算器'网页应用的核心功能，并列出需要的3个API接口名称。",
        "expected_output": "一句话功能描述 + 3个API接口名称列表。",
    },
    {
        "agent_file": "backend_engineer.md",
        "model": "kimi",
        "task_description": "写一个 Python 函数 add(a, b)，返回两个数的和，并写一个简单测试用例。",
        "expected_output": "一个 add 函数和一个 assert 测试语句。",
    },
    {
        "agent_file": "frontend_engineer.md",
        "model": "minimax",
        "task_description": "写一段 10 行以内的 HTML 代码，显示标题'Hello CrewAI'和一个按钮。",
        "expected_output": "一段简短的 HTML 代码。",
    }
]

# ==============================================================================
# ⬆️ OPENCLAW FILL-IN-THE-BLANKS AREA ⬆️
# ==============================================================================


# ----------------------------------------------------
# 2. 动态构建 Agents 和 Tasks，并相互赋能
# ----------------------------------------------------
created_agents = []
created_tasks = []

# 第 2.1 步：提前读取所有人的简历，组装出“团队通讯录”
# 这样所有人都会在背景故事里知道自己是在跟谁合作、对方负责什么。
team_configs = []
team_roster_context = "\n\n=================================\n"
team_roster_context += "【团队协作通讯录】\n"
team_roster_context += "本次研发任务由以下特工共同协作完成。请了解他们的职责，并在需要时向他们求助或交接工作：\n"

for i, item in enumerate(TEAM_TASKS):
    agent_path = os.path.join(agents_dir, item["agent_file"])
    agent_config = load_agent_from_md(agent_path)
    team_configs.append(agent_config)
    
    # 将此人加入通讯录
    team_roster_context += f"{i+1}. 角色名：[{agent_config['role']}] - 负责范围：{agent_config['goal']}\n"

team_roster_context += "=================================\n"


# 第 2.2 步：正式构建团队
for config, item in zip(team_configs, TEAM_TASKS):
    llm_instance = LLM_MAP.get(item["model"])
    if not llm_instance:
        raise ValueError(f"未知的模型: {item['model']}。只能使用: {list(LLM_MAP.keys())}")
        
    # 动态将团队通讯录注入到该特工的私人背景故事中
    enhanced_backstory = config['backstory'] + team_roster_context

    agent = Agent(
        role=config['role'],
        goal=config['goal'],
        backstory=enhanced_backstory,
        llm=llm_instance,
        verbose=True,
        allow_delegation=True  # 允许他们互相打探情报或委派子任务
    )
    created_agents.append(agent)
    
    task = Task(
        description=item["task_description"],
        expected_output=item["expected_output"],
        agent=agent
    )
    created_tasks.append(task)

# ----------------------------------------------------
# 3. 组装 Crew 并执行
# ----------------------------------------------------
my_crew = Crew(
    agents=created_agents,
    tasks=created_tasks,
    process=Process.sequential,
    verbose=True
)
