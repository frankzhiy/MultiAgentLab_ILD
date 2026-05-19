from __future__ import annotations

import json
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
    issue_count_breakdown,
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


def collapsible_section(
    title: str,
    body: str,
    *,
    meta: str = "",
    open_by_default: bool = False,
    class_name: str = "",
) -> str:
    open_attr = " open" if open_by_default else ""
    class_attr = f"report-section {class_name}".strip()
    return (
        f"<details class='{h(class_attr)}'{open_attr}>"
        f"<summary><span class='section-title'>{h(title)}</span>"
        f"<span class='section-meta-summary'>{meta}</span></summary>"
        f"<div class='section-body'>{body}</div>"
        "</details>"
    )


def render_raw_input_html(raw_text: str, selected_payload: dict[str, Any]) -> str:
    metadata_rows = "".join(
        f"<tr><td>{h(key)}</td><td>{h(value)}</td></tr>"
        for key, value in selected_payload.items()
        if key != "absolute_path"
    )
    body = (
        "<div class='output-grid two'>"
        "<div><h3>Selected File</h3>"
        f"<div class='table-wrap compact-table'><table><tbody>{metadata_rows}</tbody></table></div>"
        "</div>"
        "<div><h3>Original Text</h3>"
        f"<pre class='text-block'>{h(raw_text)}</pre>"
        "</div></div>"
    )
    return collapsible_section(
        "Raw Input",
        body,
        meta=f"{h(selected_payload.get('file_name'))} · {h(selected_payload.get('character_count'))} chars",
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
    body = (
        "<p class='muted'>Case Structurer 给当前输入分配的 workflow 位置。它不是临床事实抽取，但会影响后续 evidence 的 stage provenance。</p>"
        f"<div class='table-wrap'><table><tbody>{rows}</tbody></table></div>"
    )
    return collapsible_section("Stage Context", body)


def render_clinical_sections_html(corrected_result: Any) -> str:
    sections = obj_list(corrected_result, "clinical_sections")
    if not sections:
        return collapsible_section("Clinical Sections", "<p class='muted'>No clinical sections produced.</p>")

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
            "<details class='nested-section'>"
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
    body = (
        "<p class='muted'>Case Structurer 最开始切分出的 section 内容。这里应该能直接检查 section 边界是否过粗、过碎、或分类错位。</p>"
        + "".join(blocks)
    )
    return collapsible_section("Clinical Sections", body, meta=f"{len(sections)} sections")


def render_structured_items_html(
    *,
    corrected_result: Any,
) -> str:
    rows = []
    for item in obj_list(corrected_result, "structured_items"):
        item_id = enum_text(obj_field(item, "item_id"))
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
            "</tr>"
        )
    body = (
        "<p class='muted'>Section 内进一步抽出的 source-level 临床陈述。Evidence Graph Structurer 后续基于这些 item 继续拆 assertions。</p>"
        "<div class='table-wrap'><table><thead><tr>"
        "<th>item</th><th>section</th><th>order</th><th>type</th><th>time</th><th>certainty</th><th>negation</th>"
        "<th>source text</th><th>spans</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
    )
    return collapsible_section(
        "Structured Items",
        body,
        meta=f"{len(obj_list(corrected_result, 'structured_items'))} items",
    )


def render_structuring_warnings_html(corrected_result: Any) -> str:
    warnings = obj_list(corrected_result, "structuring_warnings")
    if not warnings:
        return collapsible_section("Structuring Warnings", "<p class='muted'>No structuring warnings.</p>")
    rows = "".join(
        "<tr>"
        f"<td>{badge(obj_field(warning, 'severity'), enum_text(obj_field(warning, 'severity')))}</td>"
        f"<td><code>{h(obj_field(warning, 'code'))}</code></td>"
        f"<td>{h(obj_field(warning, 'related_object_id'))}</td>"
        f"<td>{h(obj_field(warning, 'message'))}</td>"
        "</tr>"
        for warning in warnings
    )
    body = (
        "<div class='table-wrap'><table><thead><tr>"
        "<th>severity</th><th>code</th><th>object</th><th>message</th>"
        "</tr></thead><tbody>"
        + rows
        + "</tbody></table></div>"
    )
    return collapsible_section("Structuring Warnings", body, meta=f"{len(warnings)} warnings", open_by_default=True)


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

    body = (
        render_stage("Section Source Span Validation And Correction", obj_field(case_bundle, "section_span_result"))
        + render_stage("Item Source Span Validation And Correction", obj_field(case_bundle, "item_span_result"))
    )
    return collapsible_section("Source Span Validation And Correction", body)


def render_assertions_html(
    *,
    corrected_result: Any,
    structuring_result: Any,
) -> str:
    assertions_by_item = index_by(
        obj_list(structuring_result, "clinical_object_assertions"),
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
            "<details class='nested-section'>"
            f"<summary><code>{h(short_id(item_id))}</code> · {h(compact(source_text_for_item(item), 110))}"
            f"<span class='count'>{len(assertions)} assertions</span></summary>"
            + body
            + "</details>"
        )

    body = (
        "<p class='muted'>Evidence Graph Structurer 首先从每个 item 中拆出的临床对象及肯否定状态。这些 assertions 会继续被组装成 frames、nodes 和 relations。</p>"
        + "".join(blocks)
    )
    return collapsible_section(
        "Clinical Object Assertions",
        body,
        meta=f"{len(obj_list(structuring_result, 'clinical_object_assertions'))} assertions",
    )


def render_assertion_issues_html(structuring_result: Any) -> str:
    warnings = obj_list(structuring_result, "assertion_issues")

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

    body = (
        "<p class='muted'>Clinical Object Assertion validator 报告的 warning（无修补动作；validator 直接丢弃无效条目并附 warning）。</p>"
        "<div class='metrics slim'>"
        f"<div class='metric'><span>warnings</span><strong>{len(warnings)}</strong></div>"
        "</div>"
        + warning_table()
    )
    return collapsible_section(
        "Clinical Assertion Validation Warnings",
        body,
        meta=f"{len(warnings)} warnings",
        open_by_default=bool(warnings),
    )


def _collect_graph_items(structuring_result: Any) -> tuple[list[Any], list[Any], list[Any], list[Any]]:
    graphlets = obj_list(structuring_result, "graphlets")
    frames: list[Any] = []
    nodes: list[Any] = []
    relations: list[Any] = []
    for graphlet in graphlets:
        frames.extend(obj_list(graphlet, "frames"))
        nodes.extend(obj_list(graphlet, "nodes"))
        relations.extend(obj_list(graphlet, "relations"))
    return graphlets, frames, nodes, relations


def _single_index(items: list[Any], key: str) -> dict[str, Any]:
    indexed: dict[str, Any] = {}
    for item in items:
        value = enum_text(obj_field(item, key))
        if value:
            indexed[value] = item
    return indexed


def _count_by(items: list[Any], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        value = enum_text(obj_field(item, key)) or "unknown"
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def _render_pills(counts: dict[str, int]) -> str:
    if not counts:
        return "<span class='muted'>none</span>"
    return "".join(
        f"<span class='pill'><code>{h(label)}</code> {h(count)}</span>"
        for label, count in counts.items()
    )


def _ref_label(ref: Any, ref_type: Any, lookup: dict[str, Any]) -> str:
    ref_text = enum_text(ref)
    item = lookup.get(ref_text)
    if item is None:
        return f"<code>{h(short_id(ref_text))}</code>"
    label_field = "frame_label" if enum_text(ref_type) == "frame" else "text"
    type_field = "frame_type" if enum_text(ref_type) == "frame" else "node_type"
    return (
        f"<code>{h(short_id(ref_text))}</code> "
        f"{badge(obj_field(item, type_field))}"
        f"<span class='ref-text'>{h(compact(obj_field(item, label_field), 80))}</span>"
    )


def _build_graph_elements(
    frames: list[Any],
    nodes: list[Any],
    relations: list[Any],
) -> list[dict[str, Any]]:
    """Build Cytoscape.js elements with frames as compound parent nodes."""
    elements: list[dict[str, Any]] = []
    frame_ids: set[str] = set()

    # node_id -> chosen parent frame_id (first frame that lists it as a member)
    node_parent: dict[str, str] = {}
    for frame in frames:
        frame_id = enum_text(obj_field(frame, "frame_id"))
        if not frame_id:
            continue
        for member_id in obj_list(frame, "member_node_ids"):
            mid = enum_text(member_id)
            if mid and mid not in node_parent:
                node_parent[mid] = frame_id

    # Frame compound parents
    for frame in frames:
        frame_id = enum_text(obj_field(frame, "frame_id"))
        if not frame_id:
            continue
        frame_ids.add(frame_id)
        elements.append({
            "group": "nodes",
            "data": {
                "id": frame_id,
                "label": enum_text(obj_field(frame, "frame_label")) or short_id(frame_id),
                "kind": "frame",
                "frame_type": enum_text(obj_field(frame, "frame_type")),
                "short": short_id(frame_id),
                "title": (
                    f"frame · {enum_text(obj_field(frame, 'frame_type'))}\n"
                    f"{enum_text(obj_field(frame, 'frame_label'))}\n"
                    f"{frame_id}"
                ),
            },
            "classes": "frame",
        })

    # Regular nodes
    for node in nodes:
        node_id = enum_text(obj_field(node, "node_id"))
        if not node_id:
            continue
        status = enum_text(obj_field(node, "assertion_status")) or "present"
        data: dict[str, Any] = {
            "id": node_id,
            "label": enum_text(obj_field(node, "text")) or short_id(node_id),
            "kind": "node",
            "node_type": enum_text(obj_field(node, "node_type")),
            "status": status,
            "short": short_id(node_id),
            "title": (
                f"node · {enum_text(obj_field(node, 'node_type'))} · {status}\n"
                f"{enum_text(obj_field(node, 'text'))}\n"
                f"{node_id}"
            ),
        }
        parent = node_parent.get(node_id)
        if parent and parent in frame_ids:
            data["parent"] = parent
        elements.append({
            "group": "nodes",
            "data": data,
            "classes": f"node status-{status}",
        })

    # Edges
    seen_edge_ids: set[str] = set()
    for relation in relations:
        source = enum_text(obj_field(relation, "source_ref"))
        target = enum_text(obj_field(relation, "target_ref"))
        if not source or not target:
            continue
        relation_id = enum_text(obj_field(relation, "relation_id")) or f"{source}->{target}"
        if relation_id in seen_edge_ids:
            relation_id = f"{relation_id}-{len(seen_edge_ids)}"
        seen_edge_ids.add(relation_id)
        relation_type = enum_text(obj_field(relation, "relation_type"))
        basis = enum_text(obj_field(relation, "evidence_basis"))
        elements.append({
            "group": "edges",
            "data": {
                "id": relation_id,
                "source": source,
                "target": target,
                "label": relation_type,
                "basis": basis,
                "title": (
                    f"{relation_type}\n"
                    f"basis: {basis}\n"
                    f"confidence: {enum_text(obj_field(relation, 'confidence'))}\n"
                    f"{enum_text(obj_field(relation, 'notes')) or ''}"
                ).strip(),
            },
            "classes": f"rel basis-{basis or 'unknown'}",
        })

    return elements


def render_graph_html(
    *,
    frames: list[Any],
    nodes: list[Any],
    relations: list[Any],
    container_id: str,
) -> str:
    if not frames and not nodes:
        return "<p class='muted'>No graph elements.</p>"

    elements = _build_graph_elements(frames, nodes, relations)
    payload = json.dumps(elements, ensure_ascii=False)
    # Escape only the HTML-significant chars for an attribute value.
    payload_attr = (
        payload.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
    legend = (
        "<div class='graph-legend'>"
        "<span><i class='legend-frame'></i>frame (compound)</span>"
        "<span><i class='legend-node present'></i>present</span>"
        "<span><i class='legend-node absent'></i>absent</span>"
        "<span><i class='legend-node uncertain'></i>uncertain / possible</span>"
        "<span><i class='legend-edge'></i>relation</span>"
        "</div>"
    )
    toolbar = (
        "<div class='graph-toolbar'>"
        f"<button type='button' data-cy-action='fit' data-cy-target='{h(container_id)}'>Fit</button>"
        f"<button type='button' data-cy-action='relayout' data-cy-target='{h(container_id)}'>Re-layout</button>"
        "<span class='muted'>滚轮缩放 · 拖拽节点 · 鼠标悬停查看详情</span>"
        "</div>"
    )
    return (
        "<div class='graph-view'>"
        + toolbar
        + f"<div class='cy-graph' id='{h(container_id)}' "
        f"data-cy-elements=\"{payload_attr}\"></div>"
        + legend
        + "</div>"
    )


def render_evidence_graph_overview_html(structuring_result: Any) -> str:
    graphlets, frames, nodes, relations = _collect_graph_items(structuring_result)
    reports = obj_list(structuring_result, "validation_reports")
    ready = obj_field(structuring_result, "ready_for_hypothesis_state")
    status_counts = _count_by(graphlets, "status")
    frame_counts = _count_by(frames, "frame_type")
    node_counts = _count_by(nodes, "node_type")
    relation_counts = _count_by(relations, "relation_type")
    basis_counts = _count_by(relations, "evidence_basis")

    body = (
        "<p class='muted'>最新输出的核心已经不是单纯 assertion 列表，而是每个 structured item 对应一个局部 graphlet：frames 作为语义场景容器，nodes 作为 source-grounded 临床对象，relations 表示结构关系。</p>"
        "<div class='metrics'>"
        f"<div class='metric'><span>graphlets</span><strong>{len(graphlets)}</strong></div>"
        f"<div class='metric'><span>frames</span><strong>{len(frames)}</strong></div>"
        f"<div class='metric'><span>nodes</span><strong>{len(nodes)}</strong></div>"
        f"<div class='metric'><span>relations</span><strong>{len(relations)}</strong></div>"
        f"<div class='metric'><span>validation reports</span><strong>{len(reports)}</strong></div>"
        f"<div class='metric'><span>hypothesis ready</span><strong>{h(ready)}</strong></div>"
        "</div>"
        "<div class='overview-grid'>"
        f"<div><h3>Graphlet Status</h3>{_render_pills(status_counts)}</div>"
        f"<div><h3>Frame Types</h3>{_render_pills(frame_counts)}</div>"
        f"<div><h3>Node Types</h3>{_render_pills(node_counts)}</div>"
        f"<div><h3>Relation Types</h3>{_render_pills(relation_counts)}</div>"
        f"<div><h3>Relation Basis</h3>{_render_pills(basis_counts)}</div>"
        "</div>"
    )
    return collapsible_section(
        "Evidence Graph Overview",
        body,
        meta=f"{len(graphlets)} graphlets · {len(relations)} relations",
        open_by_default=True,
    )


def render_evidence_graphlets_html(
    *,
    corrected_result: Any,
    structuring_result: Any,
) -> str:
    graphlets = obj_list(structuring_result, "graphlets")
    if not graphlets:
        return collapsible_section("Evidence Graphlets", "<p class='muted'>No graphlets produced.</p>")

    items = _single_index(obj_list(corrected_result, "structured_items"), "item_id")
    reports = _single_index(obj_list(structuring_result, "validation_reports"), "graphlet_id")
    all_lookup: dict[str, Any] = {}
    for graphlet in graphlets:
        all_lookup.update(_single_index(obj_list(graphlet, "frames"), "frame_id"))
        all_lookup.update(_single_index(obj_list(graphlet, "nodes"), "node_id"))

    blocks = []
    for graphlet in graphlets:
        source_item_id = enum_text(obj_field(graphlet, "source_item_id"))
        item = items.get(source_item_id)
        frames = obj_list(graphlet, "frames")
        nodes = obj_list(graphlet, "nodes")
        relations = obj_list(graphlet, "relations")
        report = reports.get(enum_text(obj_field(graphlet, "graphlet_id")))
        issues = obj_list(report, "issues")

        frame_rows = "".join(
            "<tr>"
            f"<td><code>{h(short_id(obj_field(frame, 'frame_id')))}</code></td>"
            f"<td>{badge(obj_field(frame, 'frame_type'))}</td>"
            f"<td>{h(obj_field(frame, 'frame_label'))}</td>"
            f"<td>{h(len(obj_list(frame, 'member_assertion_ids')))}</td>"
            f"<td>{h(len(obj_list(frame, 'member_node_ids')))}</td>"
            f"<td>{badge(obj_field(frame, 'confidence'))}</td>"
            "</tr>"
            for frame in frames
        )
        node_rows = "".join(
            "<tr>"
            f"<td><code>{h(short_id(obj_field(node, 'node_id')))}</code></td>"
            f"<td>{badge(obj_field(node, 'node_type'))}</td>"
            f"<td>{h(obj_field(node, 'text'))}</td>"
            f"<td>{badge(obj_field(node, 'assertion_status'), enum_text(obj_field(node, 'assertion_status')))}</td>"
            f"<td>{h(', '.join(short_id(assertion_id) for assertion_id in obj_list(node, 'assertion_ids')))}</td>"
            f"<td>{badge(obj_field(node, 'confidence'))}</td>"
            "</tr>"
            for node in nodes
        )
        relation_rows = "".join(
            "<tr>"
            f"<td><code>{h(short_id(obj_field(relation, 'relation_id')))}</code></td>"
            f"<td>{_ref_label(obj_field(relation, 'source_ref'), obj_field(relation, 'source_ref_type'), all_lookup)}</td>"
            f"<td>{badge(obj_field(relation, 'relation_type'))}</td>"
            f"<td>{_ref_label(obj_field(relation, 'target_ref'), obj_field(relation, 'target_ref_type'), all_lookup)}</td>"
            f"<td>{badge(obj_field(relation, 'evidence_basis'))}</td>"
            f"<td>{badge(obj_field(relation, 'confidence'))}</td>"
            f"<td>{h(compact(obj_field(relation, 'notes'), 120))}</td>"
            "</tr>"
            for relation in relations
        )
        issue_rows = "".join(
            "<tr>"
            f"<td>{badge(obj_field(issue, 'severity'), enum_text(obj_field(issue, 'severity')))}</td>"
            f"<td><code>{h(obj_field(issue, 'code'))}</code></td>"
            f"<td>{h(obj_field(issue, 'related_item_id'))}</td>"
            f"<td>{h(obj_field(issue, 'message'))}</td>"
            "</tr>"
            for issue in issues
        )
        validation_summary = (
            "<div class='validation-strip'>"
            f"{badge(obj_field(report, 'status'), enum_text(obj_field(report, 'status')))}"
            f"<span>downstream_ready: <strong>{h(obj_field(report, 'downstream_readiness'))}</strong></span>"
            f"<span>issues: <strong>{len(issues)}</strong></span>"
            f"<span>assertion_coverage: <code>{h(obj_field(report, 'assertion_coverage'))}</code></span>"
            f"<span>relation_checks: <code>{h(obj_field(report, 'relation_checks'))}</code></span>"
            "</div>"
            if report
            else "<p class='muted'>No validation report for this graphlet.</p>"
        )
        issue_table = (
            "<p class='muted'>No graph validation issues.</p>"
            if not issue_rows
            else (
                "<div class='table-wrap'><table><thead><tr>"
                "<th>severity</th><th>code</th><th>item</th><th>message</th>"
                "</tr></thead><tbody>"
                + issue_rows
                + "</tbody></table></div>"
            )
        )
        graph_view = render_graph_html(
            frames=frames,
            nodes=nodes,
            relations=relations,
            container_id=f"cy-{enum_text(obj_field(graphlet, 'graphlet_id')) or short_id(source_item_id)}",
        )
        open_attr = " open" if enum_text(obj_field(graphlet, "status")) == "needs_review" else ""

        blocks.append(
            f"<details class='graphlet'{open_attr}>"
            f"<summary><code>{h(short_id(obj_field(graphlet, 'graphlet_id')))}</code> "
            f"{badge(obj_field(graphlet, 'status'), enum_text(obj_field(graphlet, 'status')))}"
            f"<span class='count'>{len(frames)} frames · {len(nodes)} nodes · {len(relations)} relations</span>"
            f"<span class='summary-source'>{h(compact(source_text_for_item(item), 130))}</span></summary>"
            "<div class='graphlet-body'>"
            "<div class='source'>"
            f"<span class='label'>item</span><code>{h(source_item_id)}</code><br>"
            f"{h(source_text_for_item(item))}"
            "</div>"
            f"{validation_summary}"
            "<h3>Graph View</h3>"
            + graph_view
            + "<h3>Frames</h3><div class='table-wrap'><table><thead><tr>"
            "<th>frame</th><th>type</th><th>label</th><th>assertions</th><th>nodes</th><th>confidence</th>"
            "</tr></thead><tbody>"
            + frame_rows
            + "</tbody></table></div>"
            "<h3>Nodes</h3><div class='table-wrap'><table><thead><tr>"
            "<th>node</th><th>type</th><th>text</th><th>status</th><th>assertions</th><th>confidence</th>"
            "</tr></thead><tbody>"
            + node_rows
            + "</tbody></table></div>"
            "<h3>Relations</h3>"
            + (
                "<p class='muted'>No relations.</p>"
                if not relations
                else (
                    "<div class='table-wrap'><table><thead><tr>"
                    "<th>relation</th><th>source</th><th>type</th><th>target</th><th>basis</th><th>confidence</th><th>notes</th>"
                    "</tr></thead><tbody>"
                    + relation_rows
                    + "</tbody></table></div>"
                )
            )
            + "<h3>Validation Issues</h3>"
            + issue_table
            + "</div></details>"
        )

    body = (
        "<p class='muted'>这里按 structured item 展示最新 graph 模型。调试时优先看 needs_review graphlet：通常是 relation 方向、endpoint 类型、或 frame/node coverage 的问题。</p>"
        + "".join(blocks)
    )
    status_counts = _count_by(graphlets, "status")
    return collapsible_section(
        "Evidence Graphlets",
        body,
        meta=_render_pills(status_counts),
        open_by_default=True,
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
            "把 item 里的临床对象拆出来，标注 present/absent/possible，并保留 temporal、trigger、modifier 等来源上下文。",
            "ClinicalObjectAssertion[]",
        ),
        (
            "5",
            "Evidence Graph 组装",
            "为每个 item 生成 graphlet：frames 组织临床场景，nodes 承载 source-grounded 对象，relations 表达结构关系。",
            "EvidenceGraphlet[]",
        ),
        (
            "6",
            "Graph 校验与报告",
            "检查 coverage、relation vocabulary、endpoint compatibility，并把 JSON 产物重新组织成可读 HTML。",
            "validation_reports + report.html",
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
    return collapsible_section(
        "End-to-end Flow",
        f"<div class='flow-strip'>{cards}</div>",
        meta="6 stages",
    )


def render_stage_diagnostics_html(
    *,
    summary: dict[str, Any],
    case_bundle: Any,
    corrected_result: Any,
    structuring_result: Any,
) -> str:
    raw_input = obj_field(corrected_result, "input", {})
    raw_char_count = len(enum_text(obj_field(raw_input, "raw_text")))
    section_span_result = obj_field(case_bundle, "section_span_result")
    item_span_result = obj_field(case_bundle, "item_span_result")
    section_final_report = obj_field(section_span_result, "final_validation_report")
    item_final_report = obj_field(item_span_result, "final_validation_report")
    section_correction_report = obj_field(section_span_result, "correction_report")
    item_correction_report = obj_field(item_span_result, "correction_report")
    assertion_issues = obj_list(structuring_result, "assertion_issues")
    graphlets, frames, nodes, relations = _collect_graph_items(structuring_result)
    validation_reports = obj_list(structuring_result, "validation_reports")
    graph_validation_issues = sum(len(obj_list(report, "issues")) for report in validation_reports)

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
            "status": "ready" if summary["ready_for_evidence_graph_structuring"] else "blocked",
            "plain": "作用：从原文里切出 section 和 item。目的：把长文本变成后续模块能逐条处理的病例事实。",
            "input": "raw_text",
            "output": f"{summary['clinical_sections']} sections, {summary['structured_items']} structured items",
            "schemas": "RawTextInput, StageContext, ClinicalSection, StructuredClinicalItem, SourceSpan, CaseStructuringResult",
            "mechanisms": "RawInputBuilder -> StageContextExtractor -> ClinicalSectionExtractor -> SectionNormalizer -> SectionSourceSpanValidationCorrection -> StructuredClinicalItemExtractor -> ItemNormalizer -> ItemSourceSpanValidationCorrection -> CaseStructuringAssembler",
            "risk": "item 边界太粗会让后面 assertion 变复杂；item 边界太碎会丢上下文。",
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
            "status": "warning" if assertion_issues else "done",
            "plain": "作用：把 item 内的临床对象、肯否定状态和上下文提示（temporal/trigger/modifiers）拆出来。目的：给 graph composer 提供 source-grounded 的最小事实单元。",
            "input": "ItemContext[] = item + section + spans",
            "output": (
                f"{len(obj_list(structuring_result, 'clinical_object_assertions'))} assertions; "
                f"warnings={len(assertion_issues)} {render_counts(issue_count_breakdown(assertion_issues))}"
            ),
            "schemas": "ItemContext, ClinicalObjectAssertion, ClinicalAssertionResolutionResult",
            "mechanisms": "ClinicalAssertionResolver (LLM) + ClinicalAssertionValidator (source-grounding only, drops invalid drafts with warnings).",
            "risk": "如果 object_text 拆错或不在原文，下游会拿到错误的原子节点。",
        },
        {
            "name": "Evidence Graph Composer",
            "status": "ready" if obj_field(structuring_result, "ready_for_hypothesis_state") else "blocked",
            "plain": "作用：把 assertions 组装成局部 evidence graph。目的：用 frames/nodes/relations 取代旧的树式 parent 字段，让结构关系显式可校验。",
            "input": "ClinicalObjectAssertion[] grouped by source_item_id",
            "output": f"{len(graphlets)} graphlets, {len(frames)} frames, {len(nodes)} nodes, {len(relations)} relations",
            "schemas": "EvidenceFrame, EvidenceNode, EvidenceRelation, EvidenceGraphlet, EvidenceStructuringResult",
            "mechanisms": "EvidenceFrameAssembler -> EvidenceRelationExtractor -> EvidenceGraphComposer -> EvidenceGraphValidator -> EvidenceResultAssembler",
            "risk": "重点查 needs_review graphlet、空 frame、未覆盖 assertion，以及 relation endpoint 类型不兼容。",
        },
        {
            "name": "Evidence Graph Validation",
            "status": "warning" if graph_validation_issues else "done",
            "plain": "作用：给每个 graphlet 生成 validation report。目的：判断它是否能继续交给 hypothesis state 层。",
            "input": "EvidenceGraphlet[]",
            "output": f"{len(validation_reports)} reports; graph issues={graph_validation_issues}; ready_for_hypothesis_state={h(obj_field(structuring_result, 'ready_for_hypothesis_state'))}",
            "schemas": "EvidenceGraphValidationReport, EvidenceStructuringIssue",
            "mechanisms": "coverage checks + relation vocabulary checks + endpoint compatibility checks.",
            "risk": "如果总 ready 为 true 但仍有 needs_review，说明 validator 没有把 review 级问题阻断，需要看 downstream_readiness 与 issue severity。",
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
    body = (
        "<p class='muted'>这个部分只放阶段健康度和调试重点；完整阶段输出在后面的 Raw Input、Clinical Sections、Structured Items、Assertions 各区块里。</p>"
        f"<div class='stage-diagnostics'>{rows}</div>"
    )
    return collapsible_section("Stage Diagnostics", body, open_by_default=True)


def render_item_lineage_html(
    *,
    corrected_result: Any,
    structuring_result: Any,
) -> str:
    assertions_by_item = index_by(
        obj_list(structuring_result, "clinical_object_assertions"),
        "source_item_id",
    )
    rows = []
    for item in obj_list(corrected_result, "structured_items"):
        item_id = enum_text(obj_field(item, "item_id"))
        assertions = assertions_by_item.get(item_id, [])
        rows.append(
            "<tr>"
            f"<td><code>{h(item_id)}</code><br>{badge(obj_field(item, 'item_type'))}</td>"
            f"<td>{h(compact(source_text_for_item(item), 180))}</td>"
            f"<td>{len(assertions)}<br>{h(', '.join(compact(obj_field(assertion, 'object_text'), 20) for assertion in assertions[:5]))}</td>"
            "</tr>"
        )
    body = (
        "<p class='muted'>每一行回答：这个 item 后面有没有对象断言。断点通常就藏在某个数字突然变成 0 的地方。</p>"
        "<div class='table-wrap'><table><thead><tr>"
        "<th>item</th><th>source text</th><th>assertions</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
    )
    return collapsible_section("Item Lineage Matrix", body)


def render_html_report(
    *,
    summary: dict[str, Any],
    raw_text: str,
    selected_payload: dict[str, Any],
    case_bundle: Any,
    corrected_result: Any,
    structuring_result: Any,
) -> str:
    assertion_issues = obj_list(structuring_result, "assertion_issues") if structuring_result else []
    metrics = [
        ("sections", summary["clinical_sections"]),
        ("items", summary["structured_items"]),
        ("assertions", summary.get("clinical_object_assertions", 0)),
        ("frames", summary.get("evidence_frames", 0)),
        ("nodes", summary.get("evidence_nodes", 0)),
        ("relations", summary.get("evidence_relations", 0)),
        ("graphlets", summary.get("evidence_graphlets", 0)),
        ("needs review", (summary.get("evidence_graphlets_by_status") or {}).get("needs_review", 0)),
    ]
    metric_cards = "".join(
        f"<div class='metric'><span>{h(label)}</span><strong>{h(value)}</strong></div>"
        for label, value in metrics
    )
    top_level_duration_rows = "".join(
        f"<tr><td>{h(key)}</td><td>{h(summary['durations_human'].get(key))}</td></tr>"
        for key in ("case_structurer", "evidence_graph_structurer", "total")
        if key in summary["durations_human"]
    )

    run_summary = collapsible_section(
        "Run Summary",
        (
            "<div class='table-wrap'><table><tbody>"
            f"<tr><td>case_id</td><td><code>{h(summary['case_id'])}</code></td></tr>"
            f"<tr><td>input_id</td><td><code>{h(summary['input_id'])}</code></td></tr>"
            "<tr><td>recommended debug targets</td><td><code>evidence_graphlets.json</code>, <code>evidence_graph_validation_reports.json</code>, <code>clinical_object_assertions.json</code></td></tr>"
            f"<tr><td>ready_for_hypothesis_state</td><td>{badge(summary.get('ready_for_hypothesis_state'), 'ready' if summary.get('ready_for_hypothesis_state') else 'blocked')}</td></tr>"
            "</tbody></table></div>"
            "<h3>Top-level Timing</h3>"
            f"<div class='table-wrap'><table><tbody>{top_level_duration_rows}</tbody></table></div>"
        ),
        meta=f"{h(summary['durations_human'].get('total'))}",
        open_by_default=True,
    )
    case_agent_body = (
        render_raw_input_html(raw_text=raw_text, selected_payload=selected_payload)
        + render_stage_context_html(corrected_result)
        + render_clinical_sections_html(corrected_result)
        + render_structured_items_html(corrected_result=corrected_result)
        + render_structuring_warnings_html(corrected_result)
        + render_span_validation_html(case_bundle)
    )
    case_agent = collapsible_section(
        "Case Structurer Agent",
        case_agent_body,
        meta=(
            f"{summary['clinical_sections']} sections · "
            f"{summary['structured_items']} items · "
            f"ready={h(summary['ready_for_evidence_graph_structuring'])}"
        ),
        open_by_default=True,
        class_name="agent-section",
    )
    evidence_agent_body = (
        render_evidence_graph_overview_html(structuring_result)
        + render_evidence_graphlets_html(corrected_result=corrected_result, structuring_result=structuring_result)
        + render_item_lineage_html(corrected_result=corrected_result, structuring_result=structuring_result)
        + render_assertion_issues_html(structuring_result)
        + render_assertions_html(corrected_result=corrected_result, structuring_result=structuring_result)
    )
    evidence_agent = collapsible_section(
        "Evidence Graph Structurer Agent",
        evidence_agent_body,
        meta=(
            f"{summary.get('evidence_graphlets', 0)} graphlets · "
            f"{summary.get('evidence_nodes', 0)} nodes · "
            f"{summary.get('evidence_relations', 0)} relations"
        ),
        open_by_default=True,
        class_name="agent-section",
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
  max-width: 1280px;
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
details.report-section {{
  padding: 0;
  overflow: hidden;
}}
details.report-section > summary {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  background: #fbfcff;
}}
.section-title {{
  font-size: 16px;
}}
.section-meta-summary {{
  color: var(--muted);
  font-weight: 500;
  text-align: right;
}}
.section-body {{
  border-top: 1px solid var(--line);
  padding: 16px;
}}
details.agent-section {{
  border-color: #b8c7dd;
}}
details.agent-section > summary {{
  background: #eef4ff;
}}
details.agent-section > summary .section-title {{
  font-size: 19px;
}}
details.nested-section {{
  background: #fbfcff;
}}
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
.badge.needs_review {{ color: var(--yellow); border-color: #f6d58f; background: #fff8e8; }}
.badge.rejected, .badge.absent {{ color: var(--red); border-color: #f4aaa4; background: #fff1f0; }}
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
.warnings {{
  border: 1px solid #f6d58f;
  background: #fff8e8;
  border-radius: 8px;
  padding: 8px 12px;
  margin: 12px 0;
}}
.overview-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
  margin-top: 12px;
}}
.overview-grid > div {{
  background: #fbfcff;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 12px;
}}
.overview-grid h3 {{
  margin-top: 0;
}}
.graphlet {{
  padding: 0;
  overflow: hidden;
}}
.graphlet > summary {{
  padding: 14px 16px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}}
.graphlet-body {{
  border-top: 1px solid var(--line);
  padding: 16px;
}}
.summary-source {{
  color: var(--muted);
  flex-basis: 100%;
  font-weight: 400;
}}
.validation-strip {{
  display: flex;
  gap: 8px 14px;
  flex-wrap: wrap;
  align-items: center;
  margin: 12px 0;
  padding: 10px 12px;
  background: #fbfcff;
  border: 1px solid var(--line);
  border-radius: 8px;
}}
.validation-strip code {{
  white-space: normal;
}}
.ref-text {{
  display: block;
  color: #344054;
  margin-top: 3px;
}}
.graph-view {{
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fcfdff;
  margin: 8px 0 16px;
  overflow: hidden;
}}
.graph-toolbar {{
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-bottom: 1px solid var(--line);
  background: #f7f9fd;
  font-size: 12px;
}}
.graph-toolbar button {{
  border: 1px solid var(--line);
  background: #fff;
  color: var(--ink);
  border-radius: 6px;
  padding: 3px 10px;
  cursor: pointer;
  font: inherit;
}}
.graph-toolbar button:hover {{
  background: var(--soft-blue);
  border-color: #8fb3e8;
}}
.cy-graph {{
  width: 100%;
  height: 520px;
  background: #fcfdff;
}}
.cy-graph.is-empty {{
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--muted);
  font-style: italic;
}}
.graph-legend {{
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  padding: 8px 12px 10px;
  color: var(--muted);
  font-size: 12px;
  border-top: 1px solid var(--line);
  background: #f7f9fd;
}}
.graph-legend span {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
}}
.graph-legend i {{
  display: inline-block;
  width: 18px;
  height: 10px;
  border-radius: 4px;
}}
.legend-frame {{ background: #eef4ff; border: 1px dashed #8fb3e8; }}
.legend-node.present {{ background: #eefaf3; border: 1px solid #8dc9a7; }}
.legend-node.absent {{ background: #fff1f0; border: 1px solid #f0a49e; }}
.legend-node.uncertain {{ background: #fff8e8; border: 1px solid #e8c46e; }}
.legend-edge {{ background: #667085; height: 2px !important; border-radius: 0; }}
</style>
</head>
<body>
<header>
  <h1>Phase One Test Diagnostic Report</h1>
  <div>{badge(summary["case_id"])} {badge(summary["selected_file"])} {badge(summary["created_at"])}</div>
</header>
<main>
  <div class="metrics">{metric_cards}</div>
  {render_pipeline_flow_html()}
  {run_summary}
  {render_stage_diagnostics_html(summary=summary, case_bundle=case_bundle, corrected_result=corrected_result, structuring_result=structuring_result)}
  {case_agent}
  {evidence_agent}
</main>
<script src="https://unpkg.com/cytoscape@3.28.1/dist/cytoscape.min.js"></script>
<script>
(function () {{
  if (typeof cytoscape === "undefined") {{
    document.querySelectorAll(".cy-graph").forEach(function (el) {{
      el.classList.add("is-empty");
      el.textContent = "Cytoscape.js 加载失败（可能离线），无法渲染图。表格视图见下方。";
    }});
    return;
  }}

  var instances = {{}};

  var graphStyle = [
    {{
      selector: "node",
      style: {{
        "background-color": "#eefaf3",
        "border-color": "#8dc9a7",
        "border-width": 1.4,
        "shape": "round-rectangle",
        "label": "data(label)",
        "color": "#17202a",
        "font-size": 11,
        "text-wrap": "wrap",
        "text-max-width": 140,
        "text-valign": "center",
        "text-halign": "center",
        "padding": 8,
        "width": "label",
        "height": "label",
        "min-zoomed-font-size": 6,
      }},
    }},
    {{
      selector: "node.status-absent",
      style: {{ "background-color": "#fff1f0", "border-color": "#f0a49e" }},
    }},
    {{
      selector: "node.status-uncertain, node.status-possible",
      style: {{ "background-color": "#fff8e8", "border-color": "#e8c46e" }},
    }},
    {{
      selector: "node.frame",
      style: {{
        "background-color": "#eef4ff",
        "background-opacity": 0.55,
        "border-color": "#8fb3e8",
        "border-style": "dashed",
        "border-width": 1.6,
        "shape": "round-rectangle",
        "label": "data(label)",
        "color": "#1463ff",
        "font-weight": 700,
        "font-size": 11,
        "text-valign": "top",
        "text-halign": "center",
        "text-margin-y": -4,
        "padding": 18,
        "min-zoomed-font-size": 6,
      }},
    }},
    {{
      selector: "edge",
      style: {{
        "curve-style": "bezier",
        "width": 1.4,
        "line-color": "#667085",
        "target-arrow-color": "#667085",
        "target-arrow-shape": "triangle",
        "arrow-scale": 1.0,
        "label": "data(label)",
        "font-size": 9,
        "color": "#344054",
        "text-background-color": "#fcfdff",
        "text-background-opacity": 1,
        "text-background-padding": 2,
        "text-background-shape": "round-rectangle",
        "text-rotation": "autorotate",
        "min-zoomed-font-size": 6,
      }},
    }},
    {{
      selector: "edge.basis-inferred",
      style: {{ "line-style": "dashed", "line-color": "#8a5b00", "target-arrow-color": "#8a5b00" }},
    }},
    {{
      selector: ":selected",
      style: {{
        "border-color": "#1463ff",
        "border-width": 2.2,
        "line-color": "#1463ff",
        "target-arrow-color": "#1463ff",
      }},
    }},
  ];

  function makeLayout() {{
    return {{
      name: "cose",
      animate: false,
      padding: 24,
      nodeRepulsion: function () {{ return 14000; }},
      idealEdgeLength: function () {{ return 110; }},
      edgeElasticity: function () {{ return 80; }},
      gravity: 0.2,
      numIter: 1200,
      nestingFactor: 1.4,
      fit: true,
    }};
  }}

  function initContainer(el) {{
    var raw = el.getAttribute("data-cy-elements");
    if (!raw) {{ return; }}
    var elements;
    try {{
      elements = JSON.parse(raw);
    }} catch (err) {{
      el.classList.add("is-empty");
      el.textContent = "图数据解析失败：" + err.message;
      return;
    }}
    if (!elements || !elements.length) {{
      el.classList.add("is-empty");
      el.textContent = "本 graphlet 没有 frame / node。";
      return;
    }}
    el.removeAttribute("data-cy-elements");
    var cy = cytoscape({{
      container: el,
      elements: elements,
      style: graphStyle,
      layout: makeLayout(),
      wheelSensitivity: 0.25,
      minZoom: 0.2,
      maxZoom: 2.5,
    }});
    // Tooltips via native title attribute (cytoscape renders to canvas, so use qtip-free approach)
    cy.on("mouseover", "node, edge", function (evt) {{
      var t = evt.target.data("title");
      if (t) {{ el.title = t; }}
    }});
    cy.on("mouseout", "node, edge", function () {{ el.title = ""; }});
    instances[el.id] = cy;
  }}

  function lazyInit() {{
    var observer = new IntersectionObserver(function (entries) {{
      entries.forEach(function (entry) {{
        if (entry.isIntersecting) {{
          initContainer(entry.target);
          observer.unobserve(entry.target);
        }}
      }});
    }}, {{ rootMargin: "200px" }});

    document.querySelectorAll(".cy-graph").forEach(function (el) {{
      // If inside a closed <details>, still observe; we also init on toggle.
      observer.observe(el);
      var details = el.closest("details");
      if (details) {{
        details.addEventListener("toggle", function () {{
          if (details.open && !instances[el.id]) {{
            initContainer(el);
          }} else if (details.open && instances[el.id]) {{
            instances[el.id].resize();
            instances[el.id].fit(undefined, 24);
          }}
        }});
      }}
    }});
  }}

  if ("IntersectionObserver" in window) {{
    lazyInit();
  }} else {{
    document.querySelectorAll(".cy-graph").forEach(initContainer);
  }}

  document.addEventListener("click", function (event) {{
    var btn = event.target.closest("[data-cy-action]");
    if (!btn) {{ return; }}
    var targetId = btn.getAttribute("data-cy-target");
    var cy = instances[targetId];
    if (!cy) {{
      var el = document.getElementById(targetId);
      if (el) {{ initContainer(el); cy = instances[targetId]; }}
    }}
    if (!cy) {{ return; }}
    var action = btn.getAttribute("data-cy-action");
    if (action === "fit") {{
      cy.fit(undefined, 24);
    }} else if (action === "relayout") {{
      cy.layout(makeLayout()).run();
    }}
  }});
}})();
</script>
</body>
</html>
"""
