# Phase One Test Summary

- case_id: `case_20260518_5ef53e4e`
- input_id: `input_20260518_b6a26d41`
- selected_file: `data/05.txt`
- created_at: `2026-05-18T10:14:58.735393+00:00`

## Counts

- clinical_sections: 9
- structured_items: 16
- clinical_object_assertions: 113
- evidence_trees: 16
- item_to_tree_links: 16
- deferred_items: 0
- tree_structuring_warnings: 52
- evidence_tree_warnings: 50

## Validation

- tree_structuring_validation_accepted: False
- tree_structuring_validation_issue_counts: `{'clinical_assertion_dropped': 2, 'tree_assertion_mapping_missing': 6, 'tree_build_fallback_uncertain': 2, 'tree_grammar_parent_type_not_allowed': 25, 'tree_grammar_root_not_allowed': 2, 'tree_node_dropped': 15}`

## Timing

- case_structurer: 1 min 48.2 s
- evidence_tree_structurer: 15 min 11.3 s
- evidence_tree_structurer.ItemContextBuilder: 0 ms
- evidence_tree_structurer.ClinicalAssertionResolver: 5 min 1.5 s
- evidence_tree_structurer.EvidenceTreeBuilder: 10 min 9.8 s
- evidence_tree_structurer.EvidenceTreeStructuringValidator: 0 ms
- total: 16 min 59.5 s

## Reader Output

Open `report.html` for the grouped, readable trace view.
