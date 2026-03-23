# CrewAI 多智能体研发团队

这是一个多模型协同工作的软件开发 AI 团队。团队包含了不同的 AI 角色，他们会自动分担任务以完成从【需求分析】到【前后端开发】的全流程。

## 📥 安装与初始化 (For OpenClaw / Claude Code)

如果你是一个 AI 助手，请按照以下步骤初始化该项目：

1. **克隆仓库**: `git clone https://github.com/vf0429/crewai-team-workspace.git`
2. **进入目录**: `cd crewai-team-workspace`
3. **环境配置**: 复制一份 `.env.example` 重命名为 `.env`，填入三大模型的 API Key。
4. **加载技能**: 读取当前目录下的 `.agents/workflows/team_code.md` 学习并加载 `/team_code` 专属工作流。

---

## 🎬 一键运行

只需运行以下命令即可：

```bash
bash run.sh
```
*`run.sh` 脚本会自动在后台开启 Codex 接口代理，跑完任务后会自动关闭它，你不再需要手动开两个终端。*

---

## 👥 团队成员分配

| 角色 | LLM 模型配置 | 适用场景 |
| --- | --- | --- |
| 🧑‍💼 **产品经理** | **Codex** (`gpt-5.4`) | 负责逻辑梳理、技术选型、规划 API 和整体架构设计。 |
| 💻 **后端工程师** | **Kimi** (`kimi-k2.5-thinking-turbo`) | 负责写高难度、带逻辑的 Python/FastAPI 后端代码。 |
| 🎨 **前端工程师** | **MiniMax** (`MiniMax-M2.7`) | 负责写 HTML/JS/CSS，还原界面设计。 |

> 所有模型 API Key 已通过项目根目录的 `.env` 配置文件加载。 

---

## 📝 如何布置与修改任务？

如果你有新的需求，不需要改复杂的框架代码，只需要修改 `src/crewai_project/crew.py` 文件中的 **Tasks** 块即可。

打开 `src/crewai_project/crew.py`，找到代码中的 `task1`、`task2`、`task3`：

```python
# 示例：分配一个新的项目任务
task1 = Task(
    description="请设计一个用户登录注册模块的数据库表结构和 2 个 API 的接口文档。",
    expected_output="数据库字段列表及 API 请求响应格式文档。",
    agent=product_manager
)

task2 = Task(
    description="根据产品经理提供的登录接口文档，编写一份 FastAPI 的路由代码。",
    expected_output="一段完整的、可直接运行的 Python FastAPI 代码。",
    agent=backend_engineer
)

task3 = Task(
    description="根据产品经理提供的 API 设计，写一个带表单样式的前端登录页面（HTML+CSS）。",
    expected_output="单个 HTML 文件代码，可以在浏览器直接预览。",
    agent=frontend_engineer
)
```

**配置建议：**
1. **Description（做什么）**：描述越清晰，输出越精准。可以明确指出具体需要哪些功能、哪些页面。
2. **Expected Output（怎么交工）**：一定要明确你期望的产出形式。例如（“一段 Python 代码”、“一个 Markdown 表格”、“不要废话，只输出代码” 等等）。
3. **Agent（派给谁）**：指派给 `product_manager`，`backend_engineer` 还是 `frontend_engineer`。

---

## 🛠 `team_code` 技能调用说明

对于本地配置的 AI 助手（如 OpenClaw / Claude Code 等），当触发 `/team_code` 技能时，AI Assistant 将会自动：
1. 分析你的需求并帮助修改 `crew.py` 中的团队任务。
2. 运行 `bash run.sh` 调度 CrewAI 进行集体研发。
3. 读取终端输出或运行结果以推进下一步迭代。
