# AI Friends

一个使用 Python 和 PySide6 构建的本地桌面 AI 聊天陪伴机器人。当前为 V0.1：支持可配置的 OpenAI-compatible 模型服务、本地会话持久化、人格设定与少量长期记忆。

## 功能

- PySide6 聊天与模型配置界面。
- 支持 DeepSeek 等 OpenAI-compatible Chat Completions API。
- 从 UI 保存并加载本地 `.env` 模型配置。
- SQLite 保存会话、消息和长期记忆；重启后自动恢复最近会话。
- 基于 `config/personality.json` 的人格提示词。
- 规则提取少量用户长期信息，例如偏好、学习计划和姓名。
- Enter 发送、Shift+Enter 换行；请求期间显示状态并禁用重复发送。

## 环境要求

- Python 3.11 或更新版本
- PySide6

## 安装与运行

```powershell
git clone https://github.com/DataTifox/AI_Friends.git
cd AI_Friends
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

首次启动后，打开“配置”页，填写并保存以下项目：

| 配置项 | DeepSeek 示例 |
| --- | --- |
| `LLM_PROVIDER` | `deepseek` |
| `LLM_API_KEY` | 你的 DeepSeek API Key |
| `LLM_BASE_URL` | `https://api.deepseek.com` |
| `LLM_MODEL` | `deepseek-chat` |

配置会写入项目根目录的 `.env` 文件；该文件已被 Git 忽略，不会上传 API Key。

## UI 开发

使用 Qt Designer 编辑 [ui/forms/main_window.ui](ui/forms/main_window.ui)。编辑完成后运行：

```powershell
.\ui\convert_ui.bat
```

它会把 `.ui` 文件转换为 `ui/generated/main_window.py`。自动生成的 Python 文件不应手动修改。

## 项目结构

```text
app/                 主窗口 Controller
config/              人格配置
core/                对话、人格、记忆等业务逻辑
data/                运行时 SQLite 数据库（不上传）
docs/                需求概设与项目文档
services/llm/        模型 Provider 抽象与 OpenAI-compatible 实现
storage/             SQLite 与 .env 持久化
ui/forms/            Qt Designer 源文件
ui/generated/        由 Designer 自动生成的 Python UI 文件
```

详细设计和 V0.1 验收标准见 [docs/需求概设.md](docs/需求概设.md)。

## 版本计划

- V0.1：文字聊天、人格、SQLite 会话和基础记忆。
- V0.2：后台线程、流式输出和非阻塞网络请求。
- V0.3：TTS。
- V0.4：ASR。
