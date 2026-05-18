from __future__ import annotations

from typing import Any

from phase_one_common import (
    badge,
    compact,
    enum_text,
    h,
    index_by,
    obj_field,
    obj_list,
    short_id,
    source_text_for_item,
    warning_counts,
)

def source_text_for_spans(spans: list[Any]) -> str:
    return "\n".join(
        enum_text(obj_field(span, "quoted_text"))
        for span in spans
        if enum_text(obj_field(span, "quoted_text")).strip()
    )


def span_debug_text(spans: list[Any]) -> str:
    if not spans:
        return ""
    return "; ".join(
        (
            f"{short_id(obj_field(span, 'span_id'))} "
            f"[{enum_text(obj_field(span, 'char_start'))},"
            f"{enum_text(obj_field(span, 'char_end'))}]"
        )
        for span in spans
    )


def render_raw_input_html(raw_text: str, selected_payload: dict[str, Any]) -> str:
    metadata_rows = "".join(
        f"<tr><td>{h(key)}</td><td>{h(value)}</td></tr>"
        for key, value in selected_payload.items()
        if key != "absolute_path"
    )
    return (
        "<section><h2>Raw Input</h2>"
        "<div class='output-grid two'>"
        "<div><h3>Selected File</h3>"
        f"<div class='table-wrap compact-table'><table><tbody>{metadata_rows}</tbody></table></div>"
        "</div>"
        "<div><h3>Original Text</h3>"
        f"<pre class='text-block'>{h(raw_text)}</pre>"
        "</div></div></section>"
    )


def render_stage_context_html(corrected_result: Any) -> str:
    stage = obj_field(corrected_result, "stage_context", {})
    fields = [
        "stage_id",
        "case_id",
        "input_id",
        "stage_order",
        "stage_type",
        "relation_to_previous_stage",
        "previous_stage_id",
        "is_initial_stage",
        "classification_confidence",
        "classification_basis",
    ]
    rows = "".join(
        f"<tr><td>{h(field)}</td><td>{h(obj_field(stage, field))}</td></tr>"
        for field in fields
    )
    return (
        "<section><h2>Stage Context</h2>"
        "<p class='muted'>Case Structurer 给当前输入分配的 workflow 位置。它不是临床事实抽取，但会影响后续 evidence 的 stage provenance。</p>"
        f"<div class='table-wrap'><table><tbody>{rows}</tbody></table></div></section>"
    )


def render_clinical_sections_html(corrected_result: Any) -> str:
    sections = obj_list(corrected_result, "clinical_sections")
    if not sections:
        return "<section><h2>Clinical Sections</h2><p class='muted'>No clinical sections produced.</p></section>"

    items_by_section = index_by(
        obj_list(corrected_result, "structured_items"),
        "section_id",
    )
    blocks = []
    for section in sorted(
        sections,
        key=lambda item: int(obj_field(item, "section_order", 0) or 0),
    ):
        section_id = enum_text(obj_field(section, "section_id"))
        spans = obj_list(section, "source_spans")
        text = source_text_for_spans(spans) or enum_text(
            obj_field(section, "normalized_text")
        )
        child_items = items_by_section.get(section_id, [])
        blocks.append(
            "<details open>"
            f"<summary><code>{h(short_id(section_id))}</code> "
            f"{badge(obj_field(section, 'section_type'))}"
            f"{h(obj_field(section, 'title') or '')}"
            f"<span class='count'>{len(child_items)} items</span></summary>"
            "<div class='section-meta'>"
            f"<span>order: {h(obj_field(section, 'section_order'))}</span>"
            f"<span>confidence: {h(obj_field(section, 'classification_confidence'))}</span>"
            f"<span>spans: {h(span_debug_text(spans))}</span>"
            "</div>"
            f"<pre class='text-block section-text'>{h(text)}</pre>"
            "</details>"
        )
    return (
        "<section><h2>Clinical Sections</h2>"
        "<p class='muted'>Case Structurer 最开始切分出的 section 内容。这里应该能直接检查 section 边界是否过粗、过碎、或分类错位。</p>"
        + "".join(blocks)
        + "</section>"
    )


def render_structured_items_html(
    *,
    corrected_result: Any,
    tree_result: Any,
) -> str:
    trees_by_item = index_by(obj_list(tree_result, "evidence_trees"), "source_item_id")
    rows = []
    for item in obj_list(corrected_result, "structured_items"):
        item_id = enum_text(obj_field(item, "item_id"))
        trees = trees_by_item.get(item_id, [])
        node_count = sum(len(tree_nodes(tree)) for tree in trees)
        rows.append(
            "<tr>"
            f"<td><code>{h(item_id)}</code></td>"
            f"<td><code>{h(short_id(obj_field(item, 'section_id')))}</code></td>"
            f"<td>{h(obj_field(item, 'item_order'))}</td>"
            f"<td>{badge(obj_field(item, 'item_type'))}</td>"
            f"<td>{badge(obj_field(item, 'temporality'))}</td>"
            f"<td>{badge(obj_field(item, 'certainty'))}</td>"
            f"<td>{badge(obj_field(item, 'negation'))}</td>"
            f"<td>{h(source_text_for_item(item))}</td>"
            f"<td>{h(span_debug_text(obj_list(item, 'source_spans')))}</td>"
            f"<td>{len(trees)} trees<br>{node_count} nodes</td>"
            "</tr>"
        )
    return (
        "<section><h2>Structured Items</h2>"
        "<p class='muted'>Section 内进一步抽出的 source-level 临床陈述。Evidence Tree Structurer 后续基于这些 item 继续拆 assertions 并构建 evidence tree。</p>"
        "<div class='table-wrap'><table><thead><tr>"
        "<th>item</th><th>section</th><th>order</th><th>type</th><th>time</th><th>certainty</th><th>negation</th>"
        "<th>source text</th><th>spans</th><th>tree</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div></section>"
    )


def render_structuring_warnings_html(corrected_result: Any) -> str:
    warnings = obj_list(corrected_result, "structuring_warnings")
    if not warnings:
        return "<section><h2>Structuring Warnings</h2><p class='muted'>No structuring warnings.</p></section>"
    rows = "".join(
        "<tr>"
        f"<td>{badge(obj_field(warning, 'severity'), enum_text(obj_field(warning, 'severity')))}</td>"
        f"<td><code>{h(obj_field(warning, 'code'))}</code></td>"
        f"<td>{h(obj_field(warning, 'related_object_id'))}</td>"
        f"<td>{h(obj_field(warning, 'message'))}</td>"
        "</tr>"
        for warning in warnings
    )
    return (
        "<section><h2>Structuring Warnings</h2>"
        "<div class='table-wrap'><table><thead><tr>"
        "<th>severity</th><th>code</th><th>object</th><th>message</th>"
        "</tr></thead><tbody>"
        + rows
        + "</tbody></table></div></section>"
    )


def render_span_validation_html(case_bundle: Any) -> str:
    def issue_table(title: str, issues: list[Any]) -> str:
        if not issues:
            return f"<h3>{h(title)}</h3><p class='muted'>No issues.</p>"
        rows = "".join(
            "<tr>"
            f"<td>{badge(obj_field(issue, 'severity'), enum_text(obj_field(issue, 'severity')))}</td>"
            f"<td><code>{h(obj_field(issue, 'code'))}</code></td>"
            f"<td>{h(obj_field(issue, 'object_type'))}</td>"
            f"<td><code>{h(short_id(obj_field(issue, 'object_id')))}</code></td>"
            f"<td><code>{h(short_id(obj_field(issue, 'span_id')))}</code></td>"
            f"<td>{h(compact(obj_field(issue, 'quoted_text'), 100))}</td>"
            f"<td>{h(obj_field(issue, 'message'))}</td>"
            "</tr>"
            for issue in issues
        )
        return (
            f"<h3>{h(title)}</h3>"
            "<div class='table-wrap'><table><thead><tr>"
            "<th>severity</th><th>code</th><th>object type</th><th>object</th><th>span</th><th>quoted text</th><th>message</th>"
            "</tr></thead><tbody>"
            + rows
            + "</tbody></table></div>"
        )

    def action_table(correction_report: Any) -> str:
        actions = obj_list(correction_report, "actions")
        if not actions:
            return "<p class='muted'>No correction actions.</p>"
        rows = "".join(
            "<tr>"
            f"<td>{badge(obj_field(action, 'status'))}</td>"
            f"<td><code>{h(obj_field(action, 'code'))}</code></td>"
            f"<td>{h(obj_field(action, 'object_type'))}</td>"
            f"<td><code>{h(short_id(obj_field(action, 'object_id')))}</code></td>"
            f"<td><code>{h(short_id(obj_field(action, 'span_id')))}</code></td>"
            f"<td>{h(compact(obj_field(action, 'before_quoted_text'), 90))}</td>"
            f"<td>{h(compact(obj_field(action, 'after_quoted_text'), 90))}</td>"
            f"<td>{h(obj_field(action, 'message'))}</td>"
            "</tr>"
            for action in actions
        )
        return (
            "<div class='table-wrap'><table><thead><tr>"
            "<th>status</th><th>code</th><th>object type</th><th>object</th><th>span</th><th>before</th><th>after</th><th>message</th>"
            "</tr></thead><tbody>"
            + rows
            + "</tbody></table></div>"
        )

    def render_stage(title: str, stage_result: Any) -> str:
        initial_report = obj_field(stage_result, "initial_validation_report")
        final_report = obj_field(stage_result, "final_validation_report")
        correction_report = obj_field(stage_result, "correction_report")
        return (
            f"<h3>{h(title)}</h3>"
            "<div class='metrics slim'>"
            f"<div class='metric'><span>initial valid</span><strong>{h(obj_field(initial_report, 'is_valid'))}</strong></div>"
            f"<div class='metric'><span>initial issues</span><strong>{len(obj_list(initial_report, 'issues'))}</strong></div>"
            f"<div class='metric'><span>applied</span><strong>{h(obj_field(correction_report, 'applied_count'))}</strong></div>"
            f"<div class='metric'><span>skipped</span><strong>{h(obj_field(correction_report, 'skipped_count'))}</strong></div>"
            f"<div class='metric'><span>final valid</span><strong>{h(obj_field(final_report, 'is_valid'))}</strong></div>"
            f"<div class='metric'><span>final issues</span><strong>{len(obj_list(final_report, 'issues'))}</strong></div>"
            "</div>"
            "<h4>Correction Actions</h4>"
            + action_table(correction_report)
            + issue_table("Initial Validation Issues", obj_list(initial_report, "issues"))
            + issue_table("Final Validation Issues", obj_list(final_report, "issues"))
        )

    return (
        "<section><h2>Source Span Validation And Correction</h2>"
        + render_stage("Section Source Span Validation And Correction", obj_field(case_bundle, "section_span_result"))
        + render_stage("Item Source Span Validation And Correction", obj_field(case_bundle, "item_span_result"))
        + "</section>"
    )


def render_assertions_html(
    *,
    corrected_result: Any,
    assertion_resolution: Any,
) -> str:
    assertions_by_item = index_by(
        obj_list(assertion_resolution, "clinical_object_assertions"),
        "source_item_id",
    )
    blocks = []
    for item in obj_list(corrected_result, "structured_items"):
        item_id = enum_text(obj_field(item, "item_id"))
        assertions = assertions_by_item.get(item_id, [])
        if not assertions:
            body = "<p class='muted'>No assertions for this item.</p>"
        else:
            rows = "".join(
                "<tr>"
                f"<td><code>{h(short_id(obj_field(assertion, 'object_id')))}</code></td>"
                f"<td>{h(obj_field(assertion, 'object_text'))}</td>"
                f"<td>{badge(obj_field(assertion, 'object_type'))}</td>"
                f"<td>{badge(obj_field(assertion, 'assertion_status'))}</td>"
                f"<td>{h(obj_field(assertion, 'assertion_cue_text'))}</td>"
                f"<td>{h(obj_field(assertion, 'assertion_scope_text'))}</td>"
                f"<td>{h(obj_field(assertion, 'temporal_anchor_text'))}</td>"
                f"<td>{h(obj_field(assertion, 'trigger_text'))}</td>"
                f"<td>{h(', '.join(obj_list(assertion, 'modifier_texts')))}</td>"
                f"<td>{badge(obj_field(assertion, 'confidence'))}</td>"
                "</tr>"
                for assertion in assertions
            )
            body = (
                "<div class='table-wrap'><table><thead><tr>"
                "<th>assertion</th><th>object text</th><th>type</th><th>status</th>"
                "<th>cue</th><th>scope</th>"
                "<th>temporal</th><th>trigger</th><th>modifiers</th><th>confidence</th>"
                "</tr></thead><tbody>"
                + rows
                + "</tbody></table></div>"
            )
        blocks.append(
            "<details>"
            f"<summary><code>{h(short_id(item_id))}</code> · {h(compact(source_text_for_item(item), 110))}"
            f"<span class='count'>{len(assertions)} assertions</span></summary>"
            + body
            + "</details>"
        )

    return (
        "<section><h2>Clinical Object Assertions</h2>"
        "<p class='muted'>Evidence Tree Structurer 首先从每个 item 中拆出的临床对象及肯否定状态。这是 evidence tree 的输入。</p>"
        + "".join(blocks)
        + "</section>"
    )


def render_assertion_warnings_html(assertion_resolution: Any) -> str:
    warnings = obj_list(assertion_resolution, "assertion_warnings")

    def warning_table() -> str:
        if not warnings:
            return "<p class='muted'>No clinical assertion validation warnings.</p>"
        rows = "".join(
            "<tr>"
            f"<td>{badge(obj_field(warning, 'severity'), enum_text(obj_field(warning, 'severity')))}</td>"
            f"<td><code>{h(obj_field(warning, 'code'))}</code></td>"
            f"<td><code>{h(short_id(obj_field(warning, 'related_item_id')))}</code></td>"
            f"<td>{h(obj_field(warning, 'message'))}</td>"
            "</tr>"
            for warning in warnings
        )
        return (
            "<div class='table-wrap'><table><thead><tr>"
            "<th>severity</th><th>code</th><th>item</th><th>message</th>"
            "</tr></thead><tbody>"
            + rows
            + "</tbody></table></div>"
        )

    return (
        "<section><h2>Clinical Assertion Validation Warnings</h2>"
        "<p class='muted'>Clinical Object Assertion validator 报告的 warning（无修补动作；validator 直接丢弃无效条目并附 warning）。</p>"
        "<div class='metrics slim'>"
        f"<div class='metric'><span>warnings</span><strong>{len(warnings)}</strong></div>"
        "</div>"
        + warning_table()
        + "</section>"
    )


def render_tree_structuring_metadata_html(
    tree_structuring_result: Any,
    tree_structuring_validation_report: Any,
) -> str:
    tree_links = obj_list(tree_structuring_result, "item_to_tree_links")
    deferred_items = obj_list(tree_structuring_result, "deferred_items")
    tree_structuring_warnings = obj_list(tree_structuring_result, "tree_structuring_warnings")
    validation_issues = obj_list(tree_structuring_validation_report, "issues")

    def issue_row(issue: Any) -> str:
        related_ids = [
            short_id(obj_field(issue, "related_item_id")),
            short_id(obj_field(issue, "related_tree_node_id")),
            short_id(obj_field(issue, "related_span_id")),
        ]
        related = " / ".join(item for item in related_ids if item)
        return (
            "<tr>"
            f"<td>{badge(obj_field(issue, 'severity'), enum_text(obj_field(issue, 'severity')))}</td>"
            f"<td><code>{h(obj_field(issue, 'code'))}</code></td>"
            f"<td>{h(related)}</td>"
            f"<td>{h(obj_field(issue, 'message'))}</td>"
            "</tr>"
        )

    def issue_table(issues: list[Any], empty_text: str) -> str:
        if not issues:
            return f"<p class='muted'>{h(empty_text)}</p>"
        return (
            "<div class='table-wrap'><table><thead><tr>"
            "<th>severity</th><th>code</th><th>related id</th><th>message</th>"
            "</tr></thead><tbody>"
            + "".join(issue_row(issue) for issue in issues)
            + "</tbody></table></div>"
        )

    if tree_links:
        tree_link_rows = "".join(
            "<tr>"
            f"<td><code>{h(short_id(obj_field(link, 'item_id')))}</code></td>"
            f"<td>{badge(obj_field(link, 'transformation_type'))}</td>"
            f"<td>{h(', '.join(short_id(tree_id) for tree_id in obj_list(link, 'tree_ids')))}</td>"
            f"<td>{h(obj_field(link, 'explanation'))}</td>"
            "</tr>"
            for link in tree_links
        )
        tree_link_html = (
            "<div class='table-wrap'><table><thead><tr>"
            "<th>item</th><th>transformation</th><th>tree ids</th><th>explanation</th>"
            "</tr></thead><tbody>"
            + tree_link_rows
            + "</tbody></table></div>"
        )
    else:
        tree_link_html = "<p class='muted'>No item-to-tree links.</p>"

    if deferred_items:
        deferred_rows = "".join(
            "<tr>"
            f"<td><code>{h(short_id(obj_field(item, 'item_id')))}</code></td>"
            f"<td>{badge(obj_field(item, 'reason'))}</td>"
            f"<td>{h(obj_field(item, 'explanation'))}</td>"
            "</tr>"
            for item in deferred_items
        )
        deferred_html = (
            "<div class='table-wrap'><table><thead><tr>"
            "<th>item</th><th>reason</th><th>explanation</th>"
            "</tr></thead><tbody>"
            + deferred_rows
            + "</tbody></table></div>"
        )
    else:
        deferred_html = "<p class='muted'>No deferred items.</p>"

    return (
        "<section><h2>Evidence Tree Structuring Metadata</h2>"
        "<p class='muted'>这里放 Evidence Tree Structurer 的链接和质量信息：item 如何变成 tree，哪些 item 被延后，以及最终 validator issue。</p>"
        "<div class='output-grid'>"
        "<div><h3>Item To Tree Links</h3>"
        + tree_link_html
        + "</div><div><h3>Deferred Items</h3>"
        + deferred_html
        + "</div></div>"
        "<div class='output-grid'>"
        "<div><h3>Tree Warnings</h3>"
        + issue_table(tree_structuring_warnings, "No tree warnings.")
        + "</div><div><h3>Tree Structuring Validation Issues</h3>"
        + issue_table(validation_issues, "No tree-structuring validation issues.")
        + "</div></div>"
        + "</section>"
    )


def node_parent_text(node: Any, node_by_id: dict[str, Any]) -> str:
    parent_id = enum_text(obj_field(node, "parent_node_id"))
    if not parent_id:
        return ""
    parent = node_by_id.get(parent_id)
    if parent is None:
        return short_id(parent_id)
    return compact(obj_field(parent, "node_text"), 80)


def tree_node_id(node: Any) -> str:
    return enum_text(obj_field(node, "tree_node_id"))


def tree_nodes(tree: Any) -> list[Any]:
    return obj_list(tree, "tree_nodes")


def tree_warnings(tree: Any) -> list[Any]:
    return obj_list(tree, "tree_warnings")


def render_node_tree_html(
    *,
    node: Any,
    children_by_parent: dict[str, list[Any]],
) -> str:
    node_id = tree_node_id(node)
    relation = obj_field(node, "relation_to_parent")
    relation_html = f" <span class='muted'>rel={h(relation)}</span>" if relation else ""

    child_html = ""
    children = children_by_parent.get(node_id, [])
    if children:
        child_html = (
            "<ul>"
            + "".join(
                render_node_tree_html(
                    node=child,
                    children_by_parent=children_by_parent,
                )
                for child in children
            )
            + "</ul>"
        )

    return (
        "<li>"
        "<div class='node-line'>"
        f"{badge(obj_field(node, 'node_type'))}"
        f"<span class='node-text'>{h(obj_field(node, 'node_text'))}</span>"
        f"{relation_html}"
        f" <span class='muted'>origin={h(obj_field(node, 'node_origin'))}</span>"
        "</div>"
        + child_html
        + "</li>"
    )


def render_tree_structure_html(
    *,
    nodes: list[Any],
) -> str:
    if not nodes:
        return "<p class='muted'>No tree nodes.</p>"

    node_ids = {tree_node_id(node) for node in nodes}
    children_by_parent: dict[str, list[Any]] = {}
    roots: list[Any] = []
    for node in nodes:
        parent_id = enum_text(obj_field(node, "parent_node_id"))
        if parent_id and parent_id in node_ids:
            children_by_parent.setdefault(parent_id, []).append(node)
        else:
            roots.append(node)

    return (
        "<div class='tree'><ul>"
        + "".join(
            render_node_tree_html(
                node=root,
                children_by_parent=children_by_parent,
            )
            for root in roots
        )
        + "</ul></div>"
    )


def render_trees_html(
    *,
    tree_result: Any,
) -> str:
    trees = obj_list(tree_result, "evidence_trees")
    top_level_warnings = obj_list(tree_result, "warnings")

    def tree_warning_html(warnings: list[Any], *, force_summary: bool = False) -> str:
        if not warnings:
            return ""
        counts = render_counts(warning_counts(warnings))
        if force_summary or len(warnings) > 8:
            return (
                "<div class='warnings'>"
                f"<p><strong>{len(warnings)} warnings/issues</strong> {counts}</p>"
                "<details><summary>Show warning details</summary>"
                + "".join(
                    f"<p>{badge(obj_field(w, 'severity'), enum_text(obj_field(w, 'severity')))} "
                    f"<code>{h(obj_field(w, 'code'))}</code> {h(obj_field(w, 'message'))}</p>"
                    for w in warnings
                )
                + "</details></div>"
            )
        return (
            "<div class='warnings'>"
            + "".join(
                f"<p>{badge(obj_field(w, 'severity'), enum_text(obj_field(w, 'severity')))} "
                f"<code>{h(obj_field(w, 'code'))}</code> {h(obj_field(w, 'message'))}</p>"
                for w in warnings
            )
            + "</div>"
        )

    if not trees:
        return (
            "<section><h2>Evidence Trees</h2>"
            + tree_warning_html(top_level_warnings)
            + "<p class='muted'>No evidence tree payload was produced.</p></section>"
        )

    all_nodes = [node for tree in trees for node in tree_nodes(tree)]
    summary_cards = "".join(
        f"<div class='metric'><span>{h(label)}</span><strong>{h(value)}</strong></div>"
        for label, value in (
            ("trees", len(trees)),
            ("tree nodes", len(all_nodes)),
            ("top-level warnings", len(top_level_warnings)),
        )
    )

    blocks = []
    for index, tree in enumerate(trees):
        nodes = tree_nodes(tree)
        node_by_id = {tree_node_id(node): node for node in nodes}
        warnings = tree_warnings(tree)

        rows = []
        for node in nodes:
            assertion_count = len(obj_list(node, "source_assertion_ids"))
            rows.append(
                "<tr>"
                f"<td>{badge(obj_field(node, 'node_type'))}</td>"
                f"<td>{h(obj_field(node, 'node_text'))}</td>"
                f"<td>{h(node_parent_text(node, node_by_id))}</td>"
                f"<td>{h(obj_field(node, 'relation_to_parent'))}</td>"
                f"<td>{badge(obj_field(node, 'node_origin'))}</td>"
                f"<td>{badge(obj_field(node, 'context_role'))}</td>"
                f"<td>{assertion_count}</td>"
                "</tr>"
            )

        warning_html = tree_warning_html(warnings)
        open_attr = " open" if index < 3 else ""

        blocks.append(
            f"<details class='tree-detail'{open_attr}>"
            f"<summary><code>{h(obj_field(tree, 'source_item_id'))}</code> · {h(compact(obj_field(tree, 'source_text'), 120))} "
            f"<span class='count'>{len(nodes)} nodes</span></summary>"
            f"<p class='source'>{h(obj_field(tree, 'source_text'))}</p>"
            + warning_html
            + "<h3>Tree structure</h3>"
            + render_tree_structure_html(
                nodes=nodes,
            )
            + "<h3>Tree nodes</h3><div class='table-wrap'><table><thead><tr>"
            "<th>type</th><th>node text</th><th>parent</th><th>relation</th><th>origin</th><th>role</th><th>assertions</th>"
            "</tr></thead><tbody>"
            + "".join(rows)
            + "</tbody></table></div></details>"
        )
    return (
        "<section><h2>Evidence Trees Primary View</h2>"
        "<p class='muted'>这是当前 Evidence Tree Structurer 的最终输出：tree 表达层级结构，节点直接携带 assertion/context/structural provenance。前 3 棵树默认展开，方便直接检查结构是否真的成树。</p>"
        f"<div class='metrics slim'>{summary_cards}</div>"
        + tree_warning_html(top_level_warnings, force_summary=True)
        + "".join(blocks)
        + "</section>"
    )


def render_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "<span class='muted'>none</span>"
    return "".join(
        f"<span class='pill'><code>{h(code)}</code> {count}</span>"
        for code, count in counts.items()
    )


def validation_issue_count(report: Any) -> int:
    return len(obj_list(report, "issues"))


def render_pipeline_flow_html() -> str:
    stages = [
        (
            "1",
            "选择输入",
            "把文件读成原始文本，并记录文件路径、字符数、case 参数。",
            "Raw text",
        ),
        (
            "2",
            "病例结构化",
            "先分 section，再从 section 中抽 StructuredClinicalItem；这一步只做来源级结构化，不做推理。",
            "CaseStructuringResult",
        ),
        (
            "3",
            "Span 校验校正",
            "检查每个 section/item 的 quoted_text 是否真的能在 raw_text 里定位，能修就自动修。",
            "corrected_result",
        ),
        (
            "4",
            "对象断言解析",
            "把 item 里的临床对象拆出来，标注 present/absent/possible，并记录 assertion 修补动作。",
            "ClinicalObjectAssertion[]",
        ),
        (
            "5",
            "树形证据构建",
            "把对象断言、上下文、修饰语和结构节点组织成 EvidenceTree，保留 parent、relation、node_origin 和 provenance。",
            "EvidenceTree[]",
        ),
        (
            "6",
            "报告输出",
            "写出 JSON 与 HTML。报告展示 assertions、trees 和节点 provenance 的对应关系。",
            "report.html",
        ),
    ]
    cards = "".join(
        "<article class='flow-step'>"
        f"<strong>{number}</strong>"
        f"<h3>{h(title)}</h3>"
        f"<p>{h(description)}</p>"
        f"<span>{h(output)}</span>"
        "</article>"
        for number, title, description, output in stages
    )
    return f"<section><h2>End-to-end Flow</h2><div class='flow-strip'>{cards}</div></section>"


def render_stage_diagnostics_html(
    *,
    summary: dict[str, Any],
    case_bundle: Any,
    corrected_result: Any,
    tree_structuring_result: Any,
    tree_structuring_validation_report: Any,
    assertion_resolution: Any,
    tree_result: Any,
) -> str:
    raw_input = obj_field(corrected_result, "input", {})
    raw_char_count = len(enum_text(obj_field(raw_input, "raw_text")))
    section_span_result = obj_field(case_bundle, "section_span_result")
    item_span_result = obj_field(case_bundle, "item_span_result")
    section_final_report = obj_field(section_span_result, "final_validation_report")
    item_final_report = obj_field(item_span_result, "final_validation_report")
    section_correction_report = obj_field(section_span_result, "correction_report")
    item_correction_report = obj_field(item_span_result, "correction_report")
    assertion_warnings = obj_list(assertion_resolution, "assertion_warnings")
    tree_warning_items = obj_list(tree_result, "warnings")
    for tree in obj_list(tree_result, "evidence_trees"):
        tree_warning_items.extend(tree_warnings(tree))

    stages = [
        {
            "name": "Input Loader",
            "status": "done",
            "plain": "作用：把你选择的病例文件变成一个字符串。目的：后面所有对象都必须能追溯到这段原文。",
            "input": f"{h(summary['selected_file'])} ({raw_char_count} chars)",
            "output": f"raw_text + selected_file payload; input_order={h(obj_field(raw_input, 'input_order'))}",
            "schemas": "selected_file.json 是测试脚本自定义 payload；RawTextInput 在 Case Structurer 里生成。",
            "mechanisms": "文件扫描、UTF-8 读取、记录路径/字节数/字符数。",
            "risk": "如果原文切分或编码不稳定，后面 source_span 全都会偏。",
        },
        {
            "name": "Case Structurer",
            "status": "ready" if summary["ready_for_evidence_tree_structuring"] else "blocked",
            "plain": "作用：从原文里切出 section 和 item。目的：把长文本变成后续模块能逐条处理的病例事实。",
            "input": "raw_text",
            "output": f"{summary['clinical_sections']} sections, {summary['structured_items']} structured items",
            "schemas": "RawTextInput, StageContext, ClinicalSection, StructuredClinicalItem, SourceSpan, CaseStructuringResult",
            "mechanisms": "RawInputBuilder -> StageContextExtractor -> ClinicalSectionExtractor -> SectionNormalizer -> SectionSourceSpanValidationCorrection -> StructuredClinicalItemExtractor -> ItemNormalizer -> ItemSourceSpanValidationCorrection -> CaseStructuringAssembler",
            "risk": "item 边界太粗会让后面 assertion/tree 变复杂；item 边界太碎会丢上下文。",
        },
        {
            "name": "Source Span Correction",
            "status": (
                "valid"
                if obj_field(section_final_report, "is_valid")
                and obj_field(item_final_report, "is_valid")
                else "error"
            ),
            "plain": "作用：确认每个抽出的对象真的来自原文。目的：防止 LLM 编造或 span 坐标错位。",
            "input": "normalized sections, then normalized items",
            "output": (
                f"section final issues={validation_issue_count(section_final_report)}, "
                f"section corrections={len(obj_list(section_correction_report, 'actions'))}, "
                f"item final issues={validation_issue_count(item_final_report)}, "
                f"item corrections={len(obj_list(item_correction_report, 'actions'))}"
            ),
            "schemas": "SourceSpanValidationReport, SourceSpanCorrectionReport, SectionSourceSpanValidationCorrectionResult, ItemSourceSpanValidationCorrectionResult",
            "mechanisms": "SectionSourceSpanValidator/Corrector + ItemSourceSpanValidator/Corrector",
            "risk": "如果 correction 很多，说明上游抽取的 span grounding 不稳。",
        },
        {
            "name": "Clinical Assertion Resolver",
            "status": "warning" if assertion_warnings else "done",
            "plain": "作用：把 item 内的临床对象、肯否定状态和结构提示（parent/relation/temporal/trigger/modifiers）拆出来。目的：为树形证据提供带结构线索的最小对象节点。",
            "input": "ItemContext[] = item + section + spans",
            "output": (
                f"{len(obj_list(assertion_resolution, 'clinical_object_assertions'))} assertions; "
                f"warnings={len(assertion_warnings)} {render_counts(warning_counts(assertion_warnings))}"
            ),
            "schemas": "ItemContext, ClinicalObjectAssertion, ClinicalAssertionResolutionResult",
            "mechanisms": "ClinicalAssertionResolver (LLM) + ClinicalAssertionValidator (source-grounding only, drops invalid drafts with warnings).",
            "risk": "如果 object_text 拆错或不在原文，下游 tree builder 会拿到错误的原子节点。注意 assertion 不再带 parent/relation 提示，树的拓扑由 LLM 在建树阶段决定。",
        },
        {
            "name": "Evidence Tree Builder",
            "status": "warning" if tree_warning_items else "done",
            "plain": "作用：LLM 读 source_text + assertions，自己决定树的父子、兼顾 grammar 和 source grounding。目的：输出完整的结构化证据。",
            "input": "ItemContext[] + ClinicalObjectAssertion[]",
            "output": (
                f"{summary['evidence_trees']} trees; "
                f"tree warnings={summary['evidence_tree_warnings']} "
                f"{render_counts(warning_counts(tree_warning_items))}"
            ),
            "schemas": "EvidenceTree, EvidenceTreeNode, EvidenceTreeBuildResult, TreeStructuringWarning",
            "mechanisms": "EvidenceTreeBuilder + EvidenceTreeValidator；validator 检查 node_text grounding、parent/context/assertion/span 引用和 node_origin。",
            "risk": "tree warning 多时，问题通常在 assertion 映射、父子关系、节点文本不在原文、或强行套模板。",
        },
    ]

    rows = "".join(
        "<article class='stage-card'>"
        "<div class='stage-card-head'>"
        f"<h3>{h(stage['name'])}</h3>"
        f"{badge(stage['status'], enum_text(stage['status']))}"
        "</div>"
        f"<p class='plain'>{stage['plain']}</p>"
        "<dl class='stage-facts'>"
        f"<dt>Input</dt><dd>{stage['input']}</dd>"
        f"<dt>Output</dt><dd>{stage['output']}</dd>"
        f"<dt>Schema</dt><dd>{stage['schemas']}</dd>"
        f"<dt>Mechanism</dt><dd>{stage['mechanisms']}</dd>"
        f"<dt>Debug focus</dt><dd class='risk-text'>{stage['risk']}</dd>"
        "</dl>"
        "</article>"
        for stage in stages
    )
    return (
        "<section><h2>Stage Diagnostics</h2>"
        "<p class='muted'>这个部分只放阶段健康度和调试重点；完整阶段输出在后面的 Raw Input、Clinical Sections、Structured Items、Assertions、Evidence Trees 各区块里。</p>"
        f"<div class='stage-diagnostics'>{rows}</div></section>"
    )


def render_item_lineage_html(
    *,
    corrected_result: Any,
    assertion_resolution: Any,
    tree_result: Any,
) -> str:
    assertions_by_item = index_by(
        obj_list(assertion_resolution, "clinical_object_assertions"),
        "source_item_id",
    )
    trees_by_item = {
        enum_text(obj_field(tree, "source_item_id")): tree
        for tree in obj_list(tree_result, "evidence_trees")
    }
    rows = []
    for item in obj_list(corrected_result, "structured_items"):
        item_id = enum_text(obj_field(item, "item_id"))
        assertions = assertions_by_item.get(item_id, [])
        tree = trees_by_item.get(item_id)
        nodes = tree_nodes(tree) if tree is not None else []
        warnings = tree_warnings(tree) if tree is not None else []
        rows.append(
            "<tr>"
            f"<td><code>{h(item_id)}</code><br>{badge(obj_field(item, 'item_type'))}</td>"
            f"<td>{h(compact(source_text_for_item(item), 180))}</td>"
            f"<td>{len(assertions)}<br>{h(', '.join(compact(obj_field(assertion, 'object_text'), 20) for assertion in assertions[:5]))}</td>"
            f"<td>{len(nodes)} nodes<br>{len(warnings)} warnings</td>"
            "</tr>"
        )
    return (
        "<section><h2>Item Lineage Matrix</h2>"
        "<p class='muted'>每一行回答：这个 item 后面有没有对象断言、有没有 tree、有没有 warning。断点通常就藏在某个数字突然变成 0 或 warning 激增的地方。</p>"
        "<div class='table-wrap'><table><thead><tr>"
        "<th>item</th><th>source text</th><th>assertions</th><th>tree</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div></section>"
    )


def render_html_report(
    *,
    summary: dict[str, Any],
    raw_text: str,
    selected_payload: dict[str, Any],
    case_bundle: Any,
    corrected_result: Any,
    tree_structuring_result: Any,
    tree_structuring_validation_report: Any,
    assertion_resolution: Any,
    tree_result: Any,
) -> str:
    metrics = [
        ("sections", summary["clinical_sections"]),
        ("items", summary["structured_items"]),
        ("assertions", len(obj_list(assertion_resolution, "clinical_object_assertions"))),
        ("clinical object assertions", summary.get("clinical_object_assertions", 0)),
        ("trees", summary["evidence_trees"]),
        ("tree warnings", summary["evidence_tree_warnings"]),
        ("warnings", summary["tree_structuring_warnings"]),
    ]
    metric_cards = "".join(
        f"<div class='metric'><span>{h(label)}</span><strong>{h(value)}</strong></div>"
        for label, value in metrics
    )
    top_level_duration_rows = "".join(
        f"<tr><td>{h(key)}</td><td>{h(summary['durations_human'].get(key))}</td></tr>"
        for key in ("case_structurer", "evidence_tree_structurer", "total")
        if key in summary["durations_human"]
    )
    tree_structurer_duration_rows = "".join(
        f"<tr><td>{h(key.removeprefix('evidence_tree_structurer.'))}</td><td>{h(value)}</td></tr>"
        for key, value in summary["durations_human"].items()
        if key.startswith("evidence_tree_structurer.")
    )
    tree_structurer_timing_html = (
        "<p class='muted'>No Evidence Tree Structurer internal timings were captured.</p>"
        if not tree_structurer_duration_rows
        else "<h3>Evidence Tree Structurer Internal Timing</h3>"
        "<div class='table-wrap'><table><tbody>"
        + tree_structurer_duration_rows
        + "</tbody></table></div>"
    )
    tree_note = (
        "Current Evidence Tree Structurer produces EvidenceTrees as the final "
        "hierarchical evidence output. Tree nodes carry assertion/context/"
        "structural provenance directly."
    )

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Phase One Test Report · {h(summary["case_id"])}</title>
<style>
:root {{
  --bg: #f7f8fb;
  --panel: #ffffff;
  --ink: #17202a;
  --muted: #697386;
  --line: #d9dee8;
  --accent: #1463ff;
  --green: #147a45;
  --yellow: #8a5b00;
  --red: #b42318;
  --soft-blue: #eaf2ff;
  --soft-green: #e8f7f1;
  --soft-yellow: #fff7e6;
  --soft-red: #fff1ef;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font: 14px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}
header {{
  background: #101828;
  color: white;
  padding: 28px max(24px, calc((100vw - 1180px) / 2));
}}
main {{
  max-width: 1180px;
  margin: 0 auto;
  padding: 24px;
}}
h1 {{ margin: 0 0 6px; font-size: 28px; }}
h2 {{ margin: 28px 0 12px; font-size: 20px; }}
h3 {{ margin: 18px 0 10px; font-size: 15px; }}
code {{ background: #eef2f7; border-radius: 4px; padding: 1px 5px; }}
section, details {{
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  margin: 14px 0;
  padding: 16px;
}}
details summary {{
  cursor: pointer;
  font-weight: 650;
  list-style-position: outside;
}}
details[open] summary {{ margin-bottom: 12px; }}
table {{
  width: 100%;
  border-collapse: collapse;
  min-width: 860px;
}}
th, td {{
  border-bottom: 1px solid var(--line);
  padding: 8px 9px;
  text-align: left;
  vertical-align: top;
}}
th {{ color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0; }}
.table-wrap {{ overflow-x: auto; }}
.muted {{ color: var(--muted); }}
.plain {{ color: #344054; font-size: 14px; }}
.source {{
  border-left: 4px solid var(--accent);
  padding-left: 12px;
  color: #344054;
}}
.metrics {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 10px;
  margin: 18px 0;
}}
.metrics.slim {{
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
}}
.metric {{
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 12px;
}}
.metric span {{
  color: var(--muted);
  display: block;
  font-size: 12px;
  text-transform: uppercase;
}}
.metric strong {{ font-size: 26px; display: block; }}
.metrics.slim .metric strong {{ font-size: 20px; }}
.output-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 12px;
}}
.output-grid.two {{
  grid-template-columns: minmax(260px, 0.8fr) minmax(360px, 1.2fr);
}}
.text-block {{
  white-space: pre-wrap;
  word-break: break-word;
  background: #fbfcff;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 12px;
  margin: 0;
  max-height: 420px;
  overflow: auto;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}}
.section-text {{
  max-height: 260px;
}}
.section-meta {{
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  color: var(--muted);
  margin-bottom: 8px;
  font-size: 12px;
}}
.compact-table table {{
  min-width: 0;
}}
.flow-strip {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 10px;
}}
.flow-step {{
  background: #fbfcff;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 12px;
  min-height: 180px;
}}
.flow-step strong {{
  display: inline-grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--accent);
  color: white;
}}
.flow-step h3 {{ margin: 10px 0 6px; }}
.flow-step span {{
  display: inline-block;
  margin-top: 6px;
  color: var(--accent);
  font-weight: 650;
}}
.stage-diagnostics {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 12px;
}}
.stage-card {{
  background: #fbfcff;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 14px;
  margin: 0;
}}
.stage-card-head {{
  display: flex;
  justify-content: space-between;
  gap: 8px;
  align-items: flex-start;
}}
.stage-card h3 {{
  margin: 0 0 8px;
  font-size: 16px;
}}
.stage-facts {{
  display: grid;
  grid-template-columns: 90px 1fr;
  gap: 6px 10px;
  margin: 10px 0 0;
}}
.stage-facts dt {{
  color: var(--muted);
  font-size: 12px;
  text-transform: uppercase;
}}
.stage-facts dd {{
  margin: 0;
}}
.risk-text {{
  background: var(--soft-yellow);
  border: 1px solid #f3d28a;
  border-radius: 6px;
  padding: 6px 8px;
}}
.pill {{
  display: inline-block;
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 2px 8px;
  margin: 2px 4px 2px 0;
  background: #fff;
  white-space: nowrap;
}}
.callout {{
  border: 1px solid #b8d2ff;
  background: var(--soft-blue);
  border-radius: 8px;
  padding: 12px;
  margin-top: 12px;
}}
.badge {{
  display: inline-block;
  border: 1px solid #cdd5df;
  border-radius: 999px;
  padding: 1px 8px;
  margin: 0 4px 4px 0;
  color: #344054;
  background: #f8fafc;
  font-size: 12px;
  white-space: nowrap;
}}
.badge.warning {{ color: var(--yellow); border-color: #f6d58f; background: #fff8e8; }}
.badge.error {{ color: var(--red); border-color: #f4aaa4; background: #fff1f0; }}
.badge.present {{ color: var(--green); border-color: #acd9bf; background: #eefaf3; }}
.badge.done, .badge.ready, .badge.valid, .badge.accepted {{ color: var(--green); border-color: #acd9bf; background: #eefaf3; }}
.badge.blocked {{ color: var(--red); border-color: #f4aaa4; background: #fff1f0; }}
.count {{
  color: var(--muted);
  font-weight: 500;
  margin-left: 8px;
}}
.label {{
  color: var(--muted);
  display: inline-block;
  min-width: 54px;
  font-size: 12px;
  text-transform: uppercase;
}}
.tree {{
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fbfcff;
  padding: 10px 12px;
  overflow-x: auto;
}}
.tree ul {{
  list-style: none;
  margin: 0 0 0 22px;
  padding: 0;
  border-left: 1px solid #cfd7e3;
}}
.tree > ul {{
  margin-left: 0;
  border-left: 0;
}}
.tree li {{
  margin: 6px 0 6px 0;
  padding-left: 12px;
  position: relative;
}}
.tree li::before {{
  content: "";
  position: absolute;
  top: 15px;
  left: 0;
  width: 10px;
  border-top: 1px solid #cfd7e3;
}}
.tree > ul > li::before {{ display: none; }}
.node-line {{
  display: flex;
  align-items: baseline;
  gap: 6px;
  flex-wrap: wrap;
}}
.node-text {{
  font-weight: 650;
}}
.warnings {{
  border: 1px solid #f6d58f;
  background: #fff8e8;
  border-radius: 8px;
  padding: 8px 12px;
  margin: 12px 0;
}}
</style>
</head>
<body>
<header>
  <h1>Phase One Test Diagnostic Report</h1>
  <div>{badge(summary["case_id"])} {badge(summary["selected_file"])} {badge(summary["created_at"])}</div>
</header>
<main>
  <div class="metrics">{metric_cards}</div>
  <section>
    <h2>How To Read This Report</h2>
    <div class="callout">
      <p><strong>这份报告的目的不是展示漂亮结果，而是帮你定位项目问题。</strong></p>
      <p>{h(tree_note)}</p>
      <p>阅读顺序建议：先看 End-to-end Flow 和 Stage Diagnostics；再从 Raw Input、Stage Context、Clinical Sections、Structured Items 逐层往下查；assertion 和 tree 的 warning 分别放在对应区域里。</p>
    </div>
  </section>
  {render_pipeline_flow_html()}
  <section>
    <h2>Run Summary</h2>
    <div class="table-wrap"><table><tbody>
      <tr><td>case_id</td><td><code>{h(summary["case_id"])}</code></td></tr>
      <tr><td>input_id</td><td><code>{h(summary["input_id"])}</code></td></tr>
      <tr><td>evidence tree structurer validation</td><td>{badge(summary["tree_structuring_validation_accepted"])}</td></tr>
      <tr><td>recommended debug target</td><td><code>clinical_object_assertions.json</code> + <code>evidence_trees.json</code></td></tr>
    </tbody></table></div>
    <h3>Top-level Timing</h3>
    <div class="table-wrap"><table><tbody>{top_level_duration_rows}</tbody></table></div>
    {tree_structurer_timing_html}
  </section>
  {render_stage_diagnostics_html(summary=summary, case_bundle=case_bundle, corrected_result=corrected_result, tree_structuring_result=tree_structuring_result, tree_structuring_validation_report=tree_structuring_validation_report, assertion_resolution=assertion_resolution, tree_result=tree_result)}
  {render_raw_input_html(raw_text=raw_text, selected_payload=selected_payload)}
  {render_stage_context_html(corrected_result)}
  {render_clinical_sections_html(corrected_result)}
  {render_structuring_warnings_html(corrected_result)}
  {render_structured_items_html(corrected_result=corrected_result, tree_result=tree_result)}
  {render_span_validation_html(case_bundle)}
  {render_item_lineage_html(corrected_result=corrected_result, assertion_resolution=assertion_resolution, tree_result=tree_result)}
  {render_assertion_warnings_html(assertion_resolution)}
  {render_assertions_html(corrected_result=corrected_result, assertion_resolution=assertion_resolution)}
  {render_trees_html(tree_result=tree_result)}
  {render_tree_structuring_metadata_html(tree_structuring_result, tree_structuring_validation_report)}
</main>
</body>
</html>
"""
