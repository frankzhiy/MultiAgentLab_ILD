# Evidence Atomizer Agent 说明

## 1. Agent 定位

`EvidenceAtomizerAgent` 是 Attribute Extractor 之后的证据原子化入口。它接收一个已经验证或校正过的 `CaseStructuringResult` 和对应的 `AttributeExtractionResult`，把 source-level `StructuredClinicalItem` 与抽取式 `ClinicalAttribute` 转换成 `EvidenceAtomizationResult`。

它回答的问题是：

- 哪些结构化临床项目可以被拆成最小证据单元？
- 每个 EvidenceAtom 来自哪些 `StructuredClinicalItem` 和 `ClinicalAttribute`？
- 每个 EvidenceAtom 由哪些 source span 支撑？
- 哪些结构化项目因为歧义、非临床内容或缺少来源而应被 deferred？
- 原子化过程有哪些 warning 或 error？
- 当前结果是否可进入后续 HypothesisState 生成阶段？

它不回答的问题是：

- 最可能的诊断是什么？
- 某条 EvidenceAtom 支持或反驳哪个诊断？
- 是否存在推理冲突？
- 应该推荐什么治疗或检查？
- 是否应该更新病例历史状态？
- 多个 agent 输出如何仲裁？

这些属于后续 Hypothesis、Conflict、Action、Update、SafetyGate 或 Arbitration 相关模块的职责。

## 2. StructuredClinicalItem、ClinicalAttribute 与 EvidenceAtom

`StructuredClinicalItem` 是 Case Structurer 的输出。它保留原始病例文本中的结构化临床材料，粒度可以仍然比较粗，例如一个连续原文片段里同时包含多个症状、检查指标或时间变化。

`ClinicalAttribute` 是 Attribute Extractor 的输出。它不是自由生成的字段，而是从 `StructuredClinicalItem.source_text` 中抽取连续原文片段并标注角色，例如 `77岁 -> age`、`8年 -> symptom_duration`、`阳性 -> qualitative_result`。

`EvidenceAtom` 是更小的、可被后续推理阶段引用的证据单元。它仍然只描述来源中的临床事实，不描述诊断判断，也不包含 support/refute 关系。

简化理解：

```text
StructuredClinicalItem = 结构化病例事实
ClinicalAttribute = 原文属性 span + role label
EvidenceAtom = 最小、可追溯、供后续推理引用的证据材料
```

## 3. 输入输出契约

公开入口只接收：

- `structuring_result: CaseStructuringResult`
- `attribute_result: AttributeExtractionResult`

常用方式：

```python
from src.agents.evidence_atomizer import EvidenceAtomizerAgent

atomizer = EvidenceAtomizerAgent()
bundle = atomizer.run_with_validation(structuring_result, attribute_result)

result = bundle.atomization_result
report = bundle.validation_report
```

`run_with_validation()` 返回 `EvidenceAtomizationValidationResult`，包含：

- `atomization_result`
- `validation_report`
- `accepted`

`run()` 只在 deterministic validator 接受时返回 `EvidenceAtomizationResult`；如果 validator 拒绝，会抛出 `EvidenceAtomizationValidationError`。

## 4. Pipeline 流程

当前 pipeline 顺序如下：

1. `EvidenceAtomizerInputGuard`

   检查 `CaseStructuringResult` 是否适合进入原子化，包括 ready flag、是否存在 structured items、item 是否有 source spans。
   同时检查 `AttributeExtractionResult` 是否属于同一个 case/input/structuring result，并且已 ready for atomization。

2. `AtomizationCandidateBuilder`

   将 `StructuredClinicalItem` 和按 item 分组的 `ClinicalAttribute` 转换成紧凑的 atomization candidates。LLM 不会接收完整 `CaseStructuringResult`。

3. `EvidenceAtomExtractor`

   调用 LLM 一次，让 LLM 输出 draft JSON，包括 evidence atom drafts、item links、deferred items 和 warnings。draft 需要用 `source_attribute_ids` 引用相关属性，不允许输出旧的自由字段。

4. `EvidenceAtomNormalizer`

   确定性地把 draft JSON 转成正式 schema 对象。这里生成 persistent evidence ids、强制 case/input/stage identity、修正 enum、补齐来源、过滤越界字段。

5. `EvidenceAtomizationAssembler`

   组装 `EvidenceAtomizationResult`，并保守设置 `ready_for_hypothesis_state`。

6. `EvidenceAtomizationValidator`

   验证结果是否能追溯到输入的 `CaseStructuringResult` 和 `AttributeExtractionResult`，包括 item refs、attribute refs、span refs、link refs、deferred item refs 和内部 coverage。

## 5. LLM 与确定性代码分工

LLM 负责：

- 提议如何拆分 compound structured item。
- 提议 evidence atom draft 的 statement、类型、domain、粒度和来源引用。
- 标记不能安全原子化的项目。
- 给出原子化质量 warning。

代码负责：

- 输入 guard。
- 构造紧凑 candidates。
- 生成 persistent ids。
- 规范化 enum 和 optional text。
- 强制 identity 字段来自上游 result。
- 丢弃或 defer 越界推理字段。
- 组装正式 schema。
- 运行 deterministic validator。

## 6. Validator 角色

`EvidenceAtomizationValidator` 是 Evidence Atomizer 输出进入后续推理前的确定性闸门。它检查 provenance 和 cross-object grounding，不判断医学结论。

它会检查：

- atomization result identity 是否匹配 upstream structuring result。
- EvidenceAtom.source_item_ids 是否引用现有 item。
- EvidenceAtom.source_attribute_ids 是否引用现有 attribute，且 attribute 属于对应 source item。
- EvidenceAtom.source_span_ids 是否属于对应 source items。
- ItemEvidenceLink 是否引用现有 item 和 atom。
- DeferredStructuredItem 是否引用现有 item。
- 每个 structured item 是否至少被 atom、link 或 deferred item 覆盖。

## 7. Evidence Atomizer 不能做什么

Evidence Atomizer 不得：

- 诊断。
- 判断 IPF、CTD-ILD、HP、感染、急性加重等假设。
- 生成 support/refute 关系。
- 推荐治疗。
- 创建 ActionPlan。
- 创建 HypothesisState。
- 创建 Conflict。
- 创建 UpdateTrace。
- 创建 SafetyGate。
- 创建 Arbitration。
- 写入 StateWriter 或全局状态。

## 8. 当前限制

- 当前版本只处理一个 `CaseStructuringResult`。
- 当前版本不读取历史 `CaseState`。
- 当前版本不做跨输入去重或历史更新。
- 当前版本不持久化状态。
- 当前版本不生成下游 reasoning 对象。

## 9. 推荐使用方式

推荐数据流：

```text
raw_text
  -> CaseStructurerAgent.run_with_validation()
  -> corrected CaseStructuringResult
  -> AttributeExtractorAgent.run_with_validation()
  -> AttributeExtractionResult
  -> EvidenceAtomizerAgent.run_with_validation(
       CaseStructuringResult,
       AttributeExtractionResult,
     )
  -> inspect EvidenceAtomizationValidationReport
```

`EvidenceAtom` 不保存 `value/unit/time_text/body_site` 顶层字段；这些属性由 `ClinicalAttribute` 表示，并通过 `source_attribute_ids` 关联。
