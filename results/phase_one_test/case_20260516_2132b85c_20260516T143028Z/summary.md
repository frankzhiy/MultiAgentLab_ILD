# Phase One Test Summary

- case_id: `case_20260516_2132b85c`
- input_id: `input_20260516_532b0f65`
- selected_file: `data/01.txt`
- created_at: `2026-05-16T14:30:28.271991+00:00`

## Counts

- clinical_sections: 8
- structured_items: 12
- clinical_attributes: 42
- evidence_atoms: 63
- evidence_event_frames: 12
- deferred_items: 0
- atomization_warnings: 63

## Validation

- attribute_validation_accepted: True
- atomization_validation_accepted: False
- attribute_validation_issue_counts: `{}`
- atomization_validation_issue_counts: `{'clinical_assertion_scope_not_grounded': 2, 'frame_assertion_mapping_missing': 3, 'frame_builder_fallback_mapping_warning': 8, 'frame_builder_fallback_root_added': 2, 'frame_builder_fallback_used': 2, 'frame_grammar_parent_type_not_allowed': 10, 'frame_invalid_assertion_reference': 16, 'frame_no_atomizable_node': 6, 'frame_node_text_not_in_source': 13, 'unknown_source_frame_node_id': 1}`

## Timing

- case_structurer: 56.24 s
- attribute_extractor: 42.17 s
- evidence_atomizer: 10 min 45.4 s
- total: 12 min 23.8 s

## Reader Output

Open `report.html` for the grouped, readable trace view.
