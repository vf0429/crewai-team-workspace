---
description: 启动多智能体协作团队开始联合编程（OpenClaw 专属 SOP）
---

# Team Code 技能工作流

当用户呼叫此技能（例如输入 `/team_code [附带需求]`）时，**作为 OpenClaw，你的主要职责是做“项目统筹经理”**。你不需要自己写业务代码，只需要规划外包团队、跟用户确认，并配置执行脚本。你只需要“做填空题”。

请严格遵循以下互动步骤，**必须一步步执行，不能跳过用户的确认环节**：

### Step 1: 扫描资源与拆解任务（不写代码，只口头汇报）
1. 扫描 `src/crewai_project/config/agents/` 及其子目录，特别是海量特工库 `agency_agents_library/`。按需查看里面数百个现成的 `.md` 特工简历（例如 `engineering/`, `design/` 等不同领域的特工）。
2. 根据用户给的需求，决定这个项目需要哪几个 Agent 参与，选出最精干的组合。
3. 帮用户制定出具体的子任务（每个选中 Agent 的 `description` 和 `expected_output`）。
4. **【交互】**：将你的“任务拆解计划”和“选择的 Agent 列表”发给用户看，并询问用户：“**请问对这个任务流水线拆解满意吗？如果满意，请为这几位员工分配他们各自应使用的 Model（可选：codex / kimi / minimax）。**”
   *(⚠️ 必须在这里停顿，等待用户的批准和模型分配。)*

### Step 2: 填写配置文件（填空题）
1. 当用户批准了任务拆解并指定了 Model 之后。
2. 打开 `/Users/vfzzz/Desktop/crewai_project/src/crewai_project/crew.py` 文件。
3. 找到代码中间被标记为 `OPENCLAW FILL-IN-THE-BLANKS AREA` 的区域。
4. 你只需要修改 `TEAM_TASKS` 列表！**绝对不要动其他任何 Python 逻辑代码。**
   格式如下：
   ```python
   TEAM_TASKS = [
       {
           "agent_file": "agency_agents_library/engineering/engineering-frontend-developer.md",  # 相对于 config/agents/ 的相对路径
           "model": "codex",                     # 根据用户指定，只能在 "codex", "kimi", "minimax" 中选
           "task_description": "...",            # 你拆解的针对此 agent 的任务要求
           "expected_output": "...",             # 你拆解的输出规范
       },
       # 增删 dict 即可控制多少个 agent 参与。顺序就是他们干活的先后顺序。
   ]
   ```

### Step 3: 一键发包执行
1. 修改完 `TEAM_TASKS` 后，使用 Bash 运行脚本流水线：
   ```bash
   bash /Users/vfzzz/Desktop/crewai_project/run.sh
   ```
   *(注：该脚本会自动开启 codex proxy 并在后台执行 main.py。)*

### Step 4: 收集汇报
脚本运行完毕后，分析终端输出，将 CrewAI 团队生成的最终文件或结果用人类友好的方式展示给用户，宣告任务完成。
