# AI Friends

一个使用 Python 和 PySide6 构建的本地桌面 AI 聊天陪伴机器人。当前仓库版本为 **V0.0.2**：支持可配置的 OpenAI-compatible 模型服务、本地会话持久化、人格设定、少量长期记忆、阶段摘要与基础主动跟进。

版本改动见 [CHANGELOG.md](CHANGELOG.md)。需求概设中的 V0.1/V0.2 为功能阶段规划，与仓库发布版本分别记录。

## 功能

- PySide6 聊天与模型配置界面。
- 支持 DeepSeek 等 OpenAI-compatible Chat Completions API。
- 从 UI 保存并加载本地 `.env` 模型配置。
- SQLite 保存会话、消息和长期记忆；重启后自动恢复最近会话。
- 基于 `config/personality.json` 的人格提示词。
- 规则提取少量用户长期信息，例如偏好、学习计划和姓名。
- Enter 发送、Shift+Enter 换行；请求期间显示状态并禁用重复发送。
- 后台线程执行模型请求；启动只加载最近 50 条消息，向上滚动或点击按钮加载更早记录。
- 增量阶段摘要：保存旧消息的摘要及来源范围，原始消息完整保留。
- 基础主动关心：识别明确的购买/学习经历，数天后在聊天空档自然跟进。
- 消息显示北京时间，并支持按本地日期导出 JSONL。

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

首次启动后，打开“模型设置”页，填写并保存以下项目：

| 配置项 | DeepSeek 示例 |
| --- | --- |
| `LLM_PROVIDER` | `deepseek` |
| `LLM_API_KEY` | 你的 DeepSeek API Key |
| `LLM_BASE_URL` | `https://api.deepseek.com` |
| `LLM_MODEL` | `deepseek-v4-pro` |

配置会写入项目根目录的 `.env` 文件；该文件已被 Git 忽略，不会上传 API Key。

模型名可能变化，请以 [DeepSeek 官方文档](https://api-docs.deepseek.com/zh-cn/) 为准。

## 连续性与主动关心

策略参数可在“交互设置”页查看、修改，点击“保存配置”后立即生效并写入 `config/companion.json`；“恢复默认”只回填表单，点击保存才生效。手工修改 JSON 后仍需重启。数值输入提供单位、范围校验及字段说明，主动关心下拉框显示实际启用状态。模型请求进行中暂时禁止保存或恢复配置。

默认上下文包含人格、最多 5 条长期记忆、最近 3 份阶段摘要和最近 12 条消息，并限制总字符数。修改跟进等待天数只影响新创建的事项，不重排已有事项的到期时间；修改其余限制用于之后的查询、请求和跟进检查。

成功聊天后，程序最多整理一批较早且尚未汇总的消息：积累到 24 条，或较早消息属于北京时间的前一天时生成摘要。摘要使用额外一次模型请求，不保证每天都有摘要；失败不删除原记录、不推进汇总进度，也不丢弃已保存的回复。当前按最近摘要取上下文，尚未实现按话题检索全部历史。

例如发送“我今天买了一支笛子。”会记录购买经历，默认 3 天后可以跟进。应用在前台对话页、输入框为空且空闲至少 120 秒时，每 30 秒检查一次。北京时间 22:00–09:00 不主动发言；全局每 24 小时最多一次，同一话题至少间隔 7 天，来源超过 30 天的事项不再提起。购买不等于已经开始学习，提问会以原话为依据。

说“别再问笛子了”可停止这个话题；说“关闭主动关心”或“以后不要主动问我了”可关闭全部跟进；说“开启主动关心”可重新开启全局功能。关闭、冷却和提问记录持久化保存。只对升级后新输入且符合规则的明确陈述创建事项，当前不是通用语义理解，也不提供退出后的系统通知。

旧数据库首次升级前自动备份为 `data/companion.pre-continuity.db`，原有会话、消息和记忆保留。

按北京时间日期导出聊天记录：

```powershell
python tools/export_messages.py 2026-10-12
```

输出为 `exports/2026-10-12_messages.jsonl`，每行一条消息，包含角色、内容、会话编号及 UTC/北京时间。导出和本地数据库均不提交到 Git。

离线测试（使用临时数据库及模拟模型，不消耗 API 额度）：

```powershell
$env:QT_QPA_PLATFORM = "offscreen"
python -m unittest discover -s tests -v
```

详细说明与验收步骤见 [连续性与主动跟进](docs/连续性与主动跟进.md)。

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
- 本次优化：历史分页、后台请求、阶段摘要与基础主动跟进。
- 下一步：流式输出，以及记忆/跟进事项的可视化管理。
- V0.3：TTS。
- V0.4：ASR。
