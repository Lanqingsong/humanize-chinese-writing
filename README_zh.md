# humanize-writing

> 让 AI 在第一次动笔时，就按"作品"的方式写。

[English](README.md)

---

`humanize-writing` 是一套面向 Codex、Claude Code、WorkBuddy、TRAE 等本地 AI 工具的写作 Skill。它会在正文形成之前调整模型的写作路径，减少回答者惯性、提纲拼接感、机械句式和过度修辞，同时保留事实、语域、限制条件与作者意图。

很多"AI 味"并不来自错别字或语法错误。文本可能完整、礼貌、清楚，却仍然像一条被拉长的聊天回复。真正需要处理的地方，通常发生在落笔之前：模型需要先判断文体、读者、使用场景和材料主线，再开始写正文。

本项目的目标，是把这套判断过程沉淀成可复用的 Skill，让 AI 生成交付文稿时，少一点回答感，多一点作品结构。

## 适用场景

适合用于生成或改写以下文本：

- CSDN 技术博客、公众号文章、项目介绍
- README、接口文档、开发文档、使用说明
- 课程讲稿、教程、学习材料
- 客户方案、项目汇报、产品说明
- 评论、分析、长文、叙事文本
- **学术论文**：期刊/会议投稿的写作与润色，涵盖语域切换、术语一致、逻辑结构和冗余控制
- Codex、Claude Code、WorkBuddy、TRAE 等工具中的交付型写作任务

使用示例：

```text
使用 humanize-writing 写一篇 CSDN 博客，直接给出可发布成稿。
```

```text
使用 humanize-writing 重写 README，让文档脱离聊天上下文独立成立。
```

```text
使用 humanize-writing 按学术论文规范审查并改写本文的方法节。
```

## 它解决什么问题

很多 AI 文稿看起来没有明显错误，读起来却像一份过度周到的答复。常见表现包括：

- 开头先确认要求，结尾继续表示愿意协助
- 反复使用 `不是 X，而是 Y`、`不等于`、`关键在于` 一类纠正式句型
- 预设读者犯了错，再逐条澄清
- 严格沿提示词顺序扩写，段落之间缺少作品自身的推进关系
- 每节都以定义、三点列举和原则句收尾，节奏整齐得像同一副模具
- 抽象评价很多，具体条件、动作、细节和结果偏少
- 文章能回答问题，却难以脱离聊天窗口独立成立

这些现象可以合称为 **回答者惯性**。回答者惯性描述的是文本中可观察的姿态，不用于判断作者身份，也不等同于任何 AI 检测结论。

## 为什么模型容易写成"回答"

四种力量把模型推向回答姿态：

1. **预训练学到大量文本模式** — 自回归语言模型从大规模语料中学到词语、句法、文体和篇章之间的统计关系，也会吸收网页、论坛、说明文、新闻、书籍、问答等文本里反复出现的表达模式。预训练赋予模型广泛的续写能力，但不会天然判断当前任务需要一篇独立文章，还是一条针对提问的回复。

2. **指令微调强化"提示—回答"关系** — InstructGPT 的公开方法包含标注者编写理想回答和对多个输出排序两个关键环节。模型因此更擅长接受任务、回应要求和交付完整答案。这让 AI 成为更好的助手，也容易让模型在正式写作中继续沿用答题路径。

3. **人类偏好强化"有帮助"的表达** — 基于人类反馈的强化学习倾向于生成更受评价者认可的输出。完整、清楚、礼貌、覆盖要求，通常会得到更好的评价。这些特征在聊天中有用，进入交付文稿后会形成明显的回答姿态。

4. **对话姿态外溢到成品写作** — 写教程、评论、项目介绍或叙事文本时，模型仍然接收一条"用户消息"。如果任务没有先建立作者站位和作品结构，模型很容易继续使用熟悉路径：先回应提示，再解释每一项要求，最后做总结。文章表面完整，内部仍然依赖聊天上下文。

```mermaid
flowchart LR
    A["大规模文本预训练<br/>学习语言与文体模式"] --> B["指令微调<br/>学习提示与回答的对应关系"]
    B --> C["偏好训练<br/>强化清楚、完整、礼貌的答复"]
    C --> D["独立写作任务<br/>仍可能沿用答题路径"]
    D --> E["回答者惯性<br/>确认、纠正、补充、总结、邀约"]
    E --> F["Skill 在落笔前介入<br/>建立作者站位与作品结构"]
```

## Skill 如何介入首次输出

### 1. 确定文本任务

生成前先判断：文体是什么、读者是谁、文本会在哪里使用、读者读完需要知道什么/相信什么/做什么、正文需要保留哪些事实、术语、数据、限制和责任边界。

### 2. 建立作者站位

用户提示、纠正和评价先被转换为内容边界、重点、语气与节奏要求。正文不保留聊天中的确认、致歉、纠正和邀约，也不把用户提示逐条改写成段落。一篇合格的成品应当能够脱离聊天记录独立成立。

### 3. 选择组织原则

模型根据对象选择主线，而不是照抄提示词顺序：说明文沿现象、原因、条件和后果推进；教程沿目标、操作、观察、判断和常见问题推进；分析文本沿问题、材料、推理和结论推进；叙事由人物视角、时间变化或冲突推动；项目介绍从对象、读者、能力边界和使用路径展开。

### 4. 写出并检查首稿

首稿从具体对象、动作、矛盾、场景或结论起笔。抽象评价尽量落到条件、细节和结果上；过渡内容轻写，关键变化和核心推理放慢。信息完成后自然结束。交付前进行五层检查：

1. `站位层`：正文能否脱离聊天上下文独立成立
2. `结构层`：段落是否由主题推动
3. `信息层`：有没有空泛背景、同义复述、价值膨胀和模糊归因
4. `句式层`：纠正式模板、元话语和虚化动词是否过密
5. `节奏层`：句长、段长、句首、连接词和标点是否整齐得失去变化

检查用于发现风险，不是词语清零。定义、引用、必要辨析和文体本身需要的表达应当保留。

## 安装

本仓库采用 `SKILL.md` 与 YAML frontmatter 组成的开放 Agent Skills 结构。支持 Agent Skills 的工具可以直接读取；只支持 Rules、Memory 或 Custom Instructions 的工具可以导入 `SKILL.md` 正文。

### Codex

```bash
# Windows PowerShell
git clone https://github.com/Lanqingsong/humanize-writing.git "$env:USERPROFILE\.codex\skills\humanize-writing"

# macOS / Linux
git clone https://github.com/Lanqingsong/humanize-writing.git ~/.codex/skills/humanize-writing
```

### Claude Code

```bash
# Windows PowerShell
git clone https://github.com/Lanqingsong/humanize-writing.git "$env:USERPROFILE\.claude\skills\humanize-writing"

# macOS / Linux
git clone https://github.com/Lanqingsong/humanize-writing.git ~/.claude/skills/humanize-writing
```

参考：[Claude Code Skills 文档](https://code.claude.com/docs/en/skills)

### WorkBuddy

```bash
# Windows PowerShell
git clone https://github.com/Lanqingsong/humanize-writing.git "$env:USERPROFILE\.workbuddy\skills\humanize-writing"

# macOS / Linux
git clone https://github.com/Lanqingsong/humanize-writing.git ~/.workbuddy/skills/humanize-writing
```

### TRAE

TRAE 支持自定义 Rules 和 Agent。不同版本入口可能变化：有 Skills 导入功能时可导入整个仓库；只有 Rules 功能时可将 `SKILL.md` 正文作为用户级或项目级规则。参考：[TRAE IDE](https://www.trae.ai/ide/)

### 其他工具

其他支持 [Agent Skills](https://agentskills.io/) 的工具也可以使用本仓库。`agents/openai.yaml` 只提供 Codex/OpenAI 界面元数据，不影响其他工具读取 `SKILL.md`。

## 使用方式

可以直接点名 Skill：

```text
使用 humanize-writing 写一篇面向初学者的教程，直接给出成稿。
```

```text
使用 humanize-writing 写项目介绍。先建立文章主线，不要沿我的提示逐条回答。
```

```text
使用 humanize-writing 重写 README，让它能脱离聊天上下文独立成立。
```

```text
使用 humanize-writing 按学术论文规范审查并改写本文的方法节。
```

各工具的显式调用语法可能是 `$humanize-writing` 或 `/humanize-writing`。没有显式调用机制时，也可将 `SKILL.md` 作为用户规则或项目规则载入。

## 可选审计脚本

仓库附带机械审计脚本，用于长文或文件交付前寻找高风险模式：

```bash
python scripts/audit_chinese_ai_style.py path/to/file.md
python scripts/audit_chinese_ai_style.py path/to/file.md --strict
python scripts/audit_chinese_ai_style.py path/to/docs --json
```

脚本会提示以下风险：模板对立、回答者姿态、空泛开场、宣传腔、机械连接、连续短句、重复句首、段落等长、AI 工具残留标记。审计脚本只提供回看线索，不判断作者身份，也不输出所谓 AI 概率。

## 方法边界

本项目遵守以下边界：

- 不承诺绕过 AIGC 检测器
- 不用检测分数衡量写作质量
- 不根据文风判断作者身份、学术诚信或事实真伪
- 不通过错别字、病句、虚构经历和混乱标点制造"人味"
- 不为追求流畅而删除证据、条件、限定词与责任边界
- 不擅自改写需要逐字保留的来源文本
- 不把必要的定义、引用、术语辨析和正式表达全部视为问题

目标是减少可观察的模板化风险，让 AI 文本更适合交付，而不是制造不可靠的伪装效果。

## 项目结构

```text
humanize-writing/
├── SKILL.md
├── README.md
├── README_zh.md
├── LICENSE
├── agents/
│   └── openai.yaml
├── references/
│   ├── patterns.md
│   └── academic-paper-guide.md
└── scripts/
    └── audit_chinese_ai_style.py
```

## 研究依据

- Brown et al., [Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165), 2020.
- Ouyang et al., [Training language models to follow instructions with human feedback](https://arxiv.org/abs/2203.02155), 2022.
- OpenAI, [Aligning language models to follow instructions](https://openai.com/index/instruction-following/), 2022.

上述资料支持对预训练、指令微调和人类反馈训练的机制说明。"回答者惯性"及其与纠正式文风的关系，是本项目用于指导生成与编辑的工作模型。

## 参与项目

欢迎提交 Issue 或 PR，尤其是以下内容：

- AI 味常见模式（包括学术论文场景）
- CSDN、README、技术方案、课程讲稿、学术论文等文体样例
- Codex、Claude Code、WorkBuddy、TRAE 的适配经验
- 审计脚本可识别的新模式
- 当前规则误伤正常表达的案例
- 更适合交付写作的组织方式

项目会围绕一个目标持续迭代：让 AI 生成的交付文稿少一点回答感，多一点真正面向读者的组织能力。

## 作者

LanQS — [874953727@qq.com](mailto:874953727@qq.com)

## 许可证

[MIT License](LICENSE)
