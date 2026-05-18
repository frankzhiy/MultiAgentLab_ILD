# Case Structurer Agent 说明

## 1. Agent 定位

`CaseStructurerAgent` 是病例结构化阶段的入口 agent。它的核心职责是把一段原始自由文本病历输入转换成一个结构化的 `CaseStructuringResult`。

它回答的问题是：

- 这段输入属于哪个病例、哪一次输入？
- 这段输入在病例流程中大概是什么阶段？
- 文本里有哪些粗粒度临床段落？
- 每个段落里有哪些细粒度临床事实或陈述？
- 文本里有哪些时间线事件？
- 哪些内容存在歧义，不能被强行结构化成确定事实？
- 每个结构化对象能否追溯到原始文本中的 source span？

它不回答的问题是：

- 最可能的诊断是什么？
- 某条信息支持或反驳哪个诊断假设？
- 应该生成怎样的 EvidenceTree？
- 病例中有哪些推理冲突？
- 下一步治疗或检查建议是什么？
- 多个 agent 输出之间如何仲裁？

这些属于后续 Evidence Tree Structurer、Hypothesis、Conflict、Action 或 Arbitration 相关模块的职责。

## 2. 低耦合边界

当前 `CaseStructurerAgent` 是一个低耦合的 extraction agent。它可以被外部编排器反复调用，但不能理解成会自动读取全局 blackboard 的 agent。

公开入口只接收：

- `raw_text`: 原始自由文本。
- `case_id`: 病例 ID；可以为空，空时由系统生成新病例 ID。
- `input_order`: 同一病例内第几次输入。
- `parent_input_id`: 可选，用来表示当前输入补充或关联哪一次之前的输入。

它不会接收 `CaseState`，也不会主动读取 prior case state。因此：

- 多轮输入时，调用方必须负责复用同一个 `case_id`。
- 调用方必须负责递增 `input_order`。
- 如果当前输入是补充材料，调用方应该传入 `parent_input_id`。
- 写入共享状态时，应该通过 `StateWriter` 做确定性校验和写入。

换句话说，它是“文本到结构化结果”的独立抽取器，不是“上下文感知 blackboard 推理器”。

## 3. 主要源码位置

- Public facade: `src/agents/case_structurer/agent.py`
- Internal pipeline: `src/agents/case_structurer/pipeline.py`
- Internal modules: `src/agents/case_structurer/modules/`
- Prompt files: `src/agents/case_structurer/prompts/`
- Prompt utilities: `src/agents/case_structurer/prompting/`
- Output schemas: `src/schemas/case_structurer/`
- Source-span validators: `src/validators/case_structurer/`
- Agent config: `configs/agents.yaml`
- State write entry: `src/state/state_writer/state_writer.py`

## 4. 输入输出契约

### 输入

最常用调用方式：

```python
from src.agents.case_structurer import CaseStructurerAgent

agent = CaseStructurerAgent()

result = agent.run(
    raw_text="患者女，77岁，咳嗽咳痰8年，加重2月。",
    case_id=None,
    input_order=1,
    parent_input_id=None,
)
```

如果调用方需要查看 source-span 校验和校正过程：

```python
bundle = agent.run_with_validation(
    raw_text="患者女，77岁，咳嗽咳痰8年，加重2月。",
    case_id=None,
    input_order=1,
    parent_input_id=None,
)

corrected_result = bundle.corrected_result
section_span_result = bundle.section_span_result
item_span_result = bundle.item_span_result
```

### 输出

`run()` 返回 `CaseStructuringResult`。这是 Case Structurer 的正式输出包，包含：

- `input`: 系统包装后的 `RawTextInput`。
- `stage_context`: 当前输入在病例流程中的阶段上下文。
- `clinical_sections`: 从原文抽取出的粗粒度临床段落。
- `structured_items`: 从临床段落中抽取出的 source-level 临床陈述。
- `structuring_warnings`: 结构化过程中的警告。
- `ready_for_evidence_tree_structuring`: 是否适合进入 Evidence Tree Structurer。

`run_with_validation()` 返回 `CaseStructuringSourceSpanResult`，其中包含最终 `corrected_result`，以及分开的 `section_span_result` 和 `item_span_result`。

## 5. 端到端数据流

从一段原始病例文本进入 `CaseStructurerAgent`，到最终写入病例状态，推荐的数据流如下：

```text
raw_text
  -> CaseStructurerAgent.run_with_validation()
  -> section source-span validation/correction
  -> item source-span validation/correction
  -> corrected CaseStructuringResult
  -> StateWriter.write_case_structuring_result()
  -> CaseState
```

如果调用方使用 `agent.run()`，上面的 validation/correction 仍然会执行，只是调用方只拿到最终的 `corrected CaseStructuringResult`，看不到中间报告。

### 5.1 输入进入 agent

调用方把 `raw_text` 交给 `CaseStructurerAgent`，同时可选传入 `case_id/input_order/parent_input_id`。

agent 内部首先把这些信息包装成 `RawTextInput`：

- 如果 `case_id=None`，系统生成新的病例 ID。
- 如果传入已有 `case_id`，这一轮输入会被归入该病例。
- `input_order` 只表示同一病例内第几次输入。
- `parent_input_id` 只表示当前输入和之前某个输入的关联，不会让 agent 自动读取之前输入内容。

### 5.2 初始结构化

随后 pipeline 会生成一个初始的 `CaseStructuringResult`。这个阶段主要完成结构化抽取：

- 识别 `StageContext`。
- 抽取 `ClinicalSection`。
- 抽取 `StructuredClinicalItem`。
- 解析每个对象的 `source_spans`。
- 组装成完整的 `CaseStructuringResult`。

这个初始结果已经通过 schema 组装，但其中的 source span 仍可能存在偏移、无法匹配原文、quoted text 不一致等问题，所以不能直接当作最终可信结果写入状态。

### 5.3 Source-span 验证

Section 规范化后会进入 `validate_and_correct_section_spans()`；Item 规范化后会进入 `validate_and_correct_item_spans()`。两者分别验证：

- 每个 source span 是否引用同一个 `RawTextInput`。
- `char_start/char_end` 是否在原文范围内。
- span 指向的原文片段是否和 `quoted_text` 一致。
- section/item 是否都有可追溯 provenance。

每个阶段都会形成自己的 `initial_validation_report`。

### 5.4 确定性校正

如果发现可自动修复的问题，corrector 会做确定性校正。这里的“校正”只处理 provenance，不改变医学语义。

典型校正包括：

- 根据 `quoted_text` 在原文中重新定位字符范围。
- 修正轻微错位的 `char_start/char_end`。
- 补齐可以确定匹配的 source span。
- 保留无法安全修复的问题到最终报告。

每个阶段的校正过程都会形成自己的 `correction_report`。

### 5.5 最终验证与返回

校正后的 section/items 会分别再次验证，形成各自的 `final_validation_report`。

如果调用的是 `run_with_validation()`，返回的是完整 bundle：

- `corrected_result`
- `section_span_result`
- `item_span_result`

如果调用的是 `run()`，返回的是 `corrected_result`。

### 5.6 StateWriter 写入

agent 自己不持久化状态。调用方需要把结果交给 `StateWriter.write_case_structuring_result()`。

`StateWriter` 会再次做写入前检查：

- `result.input.case_id` 必须等于 `state.case_id`。
- 同一个 `input_id` 不能重复写入。
- source spans 会再次经过验证和确定性校正。
- 如果最终仍有严重 source-span 错误，写入会被拒绝。

写入成功时，`StateWriter` 会更新 `CaseState`：

- 如果 raw input 不存在，追加到 `state.raw_inputs`。
- 追加 corrected `CaseStructuringResult` 到 `state.case_structuring_results`。
- 追加分阶段 source-span 结果到 `state.case_structuring_source_span_results`。
- 追加一次 `WriteEvent` 到 `state.write_events`。

因此，推荐心智模型是：`CaseStructurerAgent` 负责结构化和返回可校正结果，`StateWriter` 负责决定这个结果能不能进入共享状态。

## 6. Pipeline 流程

当前 pipeline 位于 `src/agents/case_structurer/pipeline.py`，顺序如下：

1. `RawInputBuilder`

   把 `raw_text/case_id/input_order/parent_input_id` 包装成 `RawTextInput`。如果没有传 `case_id`，这里会生成新病例 ID。

2. `StageContextExtractor`

   使用 LLM 判断当前输入在病例轨迹中的粗粒度阶段，例如初始输入、补充输入、新检查结果、随访输入、MDT 讨论、治疗更新等。

3. `ClinicalSectionExtractor`

   使用 LLM 抽取粗粒度临床段落，例如主诉、现病史、既往史、实验室检查、影像、病理、治疗史、随访等。

4. `SectionNormalizer`

   对 clinical sections 做确定性规范化，包括 ID、顺序、字段一致性和 source span 相关整理。

5. `StructuredClinicalItemExtractor`

   使用 LLM 从已识别段落中抽取 source-level 临床陈述，例如一段连续原文中的症状、体征、实验室结果、影像发现、病理发现、用药、暴露史、治疗反应等。这里不抽取 `value/unit/time_text/body_site`，也不拆成 evidence tree nodes。

6. `ItemNormalizer`

   对 structured items 做确定性规范化，并校验它们引用的 section 是否存在。

7. `ItemSourceSpanValidationCorrection`

   在 item 输出后验证和修补 item source spans，确保每个 item 可以追溯到所属 section 内的原文片段。

8. `CaseStructuringAssembler`

   把前面所有对象组装成最终 `CaseStructuringResult`。

9. `run()` 返回校正后的结果

   `run_with_validation()` 返回 corrected result 以及 section/item 两套 source-span 报告。

## 7. Schema 语义边界

### RawTextInput

`RawTextInput` 只记录系统在摄入时确定的信息：原文、病例 ID、输入 ID、接收时间、输入顺序和父输入 ID。它不判断这段文本是检查报告、随访记录还是补充说明。

### StageContext

`StageContext` 描述输入在病例流程中的位置。它是 workflow-level 分类，不做临床事实抽取，也不做诊断判断。

### ClinicalSection

`ClinicalSection` 是粗粒度临床段落，例如现病史、影像、实验室检查、治疗史。它只负责分段和段落分类，不表示 evidence tree node。

### StructuredClinicalItem

`StructuredClinicalItem` 是 source-level clinical statement extracted from a `ClinicalSection`。它的 `label` 应贴近原文，可以保留连续陈述中的并列症状、发现或测量。最小 evidence 拆分和属性角色标注属于下游 Attribute Extractor / Evidence Tree Structurer，不属于 Case Structurer。

它不保存 `value/unit/time_text/body_site` 顶层字段，也不表示诊断证据的支持或反驳方向。

## 8. Source Span 与校验

Case Structurer 非常依赖 source span，因为后续模块需要知道每个结构化对象来自原文哪里。

source-span 相关流程包括：

- LLM 抽取阶段可以给出初步 source span。
- `validate_and_correct_section_spans()` 会在 section 输出后验证和修补 section spans。
- `validate_and_correct_item_spans()` 会在 item 输出后验证和修补 item spans。
- 如果存在可自动修复的问题，corrector 会做确定性校正。
- 如果校正后仍有严重错误，`StateWriter` 会拒绝写入共享状态。

这意味着调用方应该优先使用 `run_with_validation()` 或至少信任 `run()` 返回的 corrected result，而不要绕过 source-span 校验直接使用内部初始结果。

## 9. 与 CaseState / Blackboard 的关系

当前项目还没有单独的 `Blackboard` 类，`CaseState` 目前承担病例级共享状态快照的角色。

推荐写入方式：

```python
from src.agents.case_structurer import CaseStructurerAgent
from src.state.case_state import CaseState
from src.state.state_writer import StateWriter

agent = CaseStructurerAgent()
writer = StateWriter()

result = agent.run(
    raw_text="患者女，77岁，咳嗽咳痰8年，加重2月。",
    case_id="case_xxx",
    input_order=1,
)

state = CaseState(case_id=result.input.case_id)
write_result = writer.write_case_structuring_result(
    state=state,
    result=result,
    agent_name="case_structurer",
)
```

`StateWriter` 会检查：

- `result.input.case_id` 是否等于 `state.case_id`。
- 同一个 `input_id` 是否已经写入过。
- source spans 是否可被校验和校正到可接受状态。

如果通过检查，它会把 corrected result、raw input、validation correction result 和 write event 写入 `CaseState`。

## 10. 多轮输入调用方式

多轮输入时，建议由外部编排器维护顺序：

```python
agent = CaseStructurerAgent()
writer = StateWriter()

state = None
previous_input_id = None

for order, raw_text in enumerate(raw_inputs, start=1):
    result = agent.run(
        raw_text=raw_text,
        case_id=state.case_id if state is not None else None,
        input_order=order,
        parent_input_id=previous_input_id,
    )

    if state is None:
        state = CaseState(case_id=result.input.case_id)

    write_result = writer.write_case_structuring_result(state, result)

    if write_result.accepted:
        previous_input_id = write_result.corrected_result.input.input_id
```

注意：当前 agent 不会把上一轮 `CaseState` 内容放进 prompt。因此第二轮输入虽然可以带同一个 `case_id` 和 `parent_input_id`，但 LLM 抽取时仍然只看当前 `raw_text`。

## 11. 配置与运行依赖

配置文件：`configs/agents.yaml`

当前 `case_structurer` 配置包含：

- provider: `chatanywhere`
- model: `gpt-4.1-mini`
- temperature: `0.0`
- max_tokens: `32000`
- response_format: `json_object`
- prompts:
  - `stage_context`
  - `clinical_section`
  - `structured_item`

运行时依赖环境变量：

- `CHATANYWHERE_API_KEY`
- `CHATANYWHERE_BASE_URL`，可选，默认是 `https://api.chatanywhere.tech/v1`

如果没有设置 `CHATANYWHERE_API_KEY`，初始化默认 `ChatAnywhereClient` 时会报错。测试或离线场景可以通过构造函数注入自定义 `llm_client`。

## 12. 错误处理

pipeline 使用统一 `_run_step()` 包装每个步骤：

- 如果 LLM 返回无法解析的 JSON，会包装为 `CaseStructuringParseError`。
- 如果 Pydantic schema 校验失败，也会包装为 parse/validation 相关错误。
- 其他步骤异常会包装为 `CaseStructuringStepError`。
- 已经是 `CaseStructuringPipelineError` 的异常会继续向外抛出。

调用方应该在 agent 边界捕获这些异常，并记录当前输入、case_id、input_order 和失败 step。

## 13. 使用建议

- 新病例第一轮可以传 `case_id=None`，让系统生成。
- 同一病例后续输入必须复用第一轮产生的 `case_id`。
- 多轮输入时由编排器递增 `input_order`。
- 补充输入建议传 `parent_input_id`，但不要期待 agent 自动读取 parent input 内容。
- 写入共享状态时使用 `StateWriter`，不要直接修改 `CaseState.case_structuring_results`。
- downstream agent 不应该直接依赖 raw LLM 输出，应依赖 `CaseStructuringResult` schema。
- 如果后续要做 context-aware structuring，需要显式扩展 agent 接口，让它接收 prior `CaseState` 或经过压缩的病例上下文。

## 14. 当前限制

- 不读取 prior `CaseState`。
- 不自动合并多轮输入之间的重复事实。
- 不自动修正前一轮结构化结果。
- 不生成 EvidenceTree。
- 不做诊断、治疗建议、冲突判断或仲裁。
- LLM 抽取质量依赖 prompt、模型和 source text 质量。
- source span 可以做确定性校正，但无法修复所有语义级抽取错误。

## 15. 推荐心智模型

可以把 `CaseStructurerAgent` 理解成病例流水线里的第一层“结构化摄入器”：

```text
Raw clinical text
  -> CaseStructurerAgent
  -> CaseStructuringResult
  -> StateWriter
  -> CaseState
  -> downstream agents
```

它的输出应该是干净、可追溯、schema-valid 的结构化病例材料。它负责把原文变成后续 agent 可以消费的结构化对象，但不负责后续医学推理。
