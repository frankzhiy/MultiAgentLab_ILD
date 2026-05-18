# Evidence Tree Structurer Agent 说明

## 1. Agent 定位

`EvidenceTreeStructurerAgent` 位于 Case Structurer 之后。当前版本负责：

- 从 `StructuredClinicalItem` 中解析对象级临床断言。
- 基于断言、上下文/属性文本和结构性事件生成 `EvidenceTree` 树形证据结构。
- 让每个 `EvidenceTreeNode` 自带来源分类和 provenance，供下游直接读取。

它不使用 coverage 阶段，不做 dedup，也不做下游诊断推理。

## 2. 输入输出契约

公开入口接收：

```python
from src.agents.evidence_tree_structurer import EvidenceTreeStructurerAgent

tree_structurer = EvidenceTreeStructurerAgent()
bundle = tree_structurer.run_with_validation(structuring_result)

trees = bundle.tree_structuring_result.evidence_trees
assertions = bundle.clinical_assertion_resolution.clinical_object_assertions
report = bundle.validation_report
```

`tree_structuring_result` 是正式输出：

- `evidence_trees`: 正式的树状结构化证据输出。
- `item_to_tree_links`: 代码按 tree 的 source_item_id 自动生成。
- `tree_structuring_warnings`: assertion 和 tree 构建/校验过程中的 warning/error。
- `ready_for_hypothesis_state`: 有 trees 且没有 error warning 时为 true。

## 3. Pipeline 流程

当前 pipeline 顺序如下：

1. `EvidenceTreeStructurerInputGuard`

   检查 `CaseStructuringResult` 的 ready flag，确认存在 structured items 且每个 item 有 source spans。

2. `TreeStructuringCandidateBuilder`

   将每个 `StructuredClinicalItem`、所属 section 和 source spans 合成一个紧凑的 `TreeStructuringCandidate`。

3. `ClinicalAssertionResolver`

   对需要细拆的 item 调用 LLM，生成 `ClinicalObjectAssertion`。随后通过 `ClinicalAssertionValidator` 确认 object/cue/scope 都能回到 candidate source text。

4. `EvidenceTreeBuilder`

   基于 candidate、assertions、局部上下文/属性文本构建 `EvidenceTree`。每棵 tree 包含一组 `EvidenceTreeNode`，节点之间通过 `parent_node_id` 和 `relation_to_parent` 表示树形结构。

5. `EvidenceTreeValidator`

   校验 tree node 是否来自原文、parent/context/assertion/span 引用是否有效，以及 `node_origin` 是否和 provenance 一致。无法安全修复的 tree 会 fallback 或产生 warning。

6. `EvidenceTreeStructuringResult`

   组装 trees、item-to-tree links 和 warnings。没有 coverage completeness 校验，没有 dedup。

## 4. Schema 分工

```text
CaseStructuringResult
  -> StructuredClinicalItem[]
  -> ClinicalSection[]

EvidenceTreeStructurer internal
  -> TreeStructuringCandidate[]
  -> ClinicalObjectAssertion[]
  -> EvidenceTree[]
     -> EvidenceTreeNode[]
  -> ItemEvidenceTreeLink[]
```

`EvidenceTreeNode` 的来源分三类：

- `assertion_backed`: 节点由 `ClinicalObjectAssertion` 支撑，必须带 `source_assertion_ids`。
- `context_backed`: 节点来自 item 原文中的时间、属性、修饰语等上下文，必须带 source span 或 attribute provenance。
- `structural_group`: 节点用于组织事件、管理行为、检查行为等语义结构，通常不直接绑定 assertion。

## 5. 当前不保留的复杂层

以下旧层不参与当前流程：

- coverage 阶段
- coverage completeness validator
- 额外的叶节点证据对象
- 复杂 normalizer

删除/不使用原因：这些层会把 evidence tree 又转成一套额外的覆盖约束，增加调试难度。当前科研任务更需要直接检查 item、assertion、tree node 和 provenance 之间的关系。

## 6. Evidence Tree Structurer 不能做什么

Evidence Tree Structurer 不得：

- 诊断。
- 判断 IPF、CTD-ILD、HP、感染、急性加重等假设。
- 生成 support/refute 关系。
- 推荐治疗。
- 创建 ActionPlan、HypothesisState、Conflict、UpdateTrace、SafetyGate 或 Arbitration。
- 写入 StateWriter 或全局状态。
