from __future__ import annotations

import sys
import unittest
from importlib import util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.schemas.case_structurer.clinical_section import (
    ClinicalSection,
    ClinicalSectionType,
)
from src.schemas.case_structurer.raw_text_input import RawTextInput
from src.schemas.case_structurer.source_span import SourceSpan
from src.schemas.case_structurer.structured_clinical_item import (
    ClinicalItemType,
    StructuredClinicalItem,
)


def _load_source_span_resolver() -> type:
    resolver_path = (
        REPO_ROOT / "src" / "agents" / "case_structurer" / "modules"
        / "source_span_resolver.py"
    )
    spec = util.spec_from_file_location("source_span_resolver_for_test", resolver_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load resolver from {resolver_path}")

    module = util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.SourceSpanResolver


SourceSpanResolver = _load_source_span_resolver()


class TestSourceSpanResolver(unittest.TestCase):
    def test_item_span_prefers_parent_section_when_quote_repeats(self) -> None:
        raw_text = "主诉：伴胸闷气短8年。现病史：8年前出现咳嗽，伴胸闷气短。"
        raw_input = RawTextInput(
            input_id="input_001",
            case_id="case_001",
            raw_text=raw_text,
        )
        sections = [
            ClinicalSection(
                section_id="section_001",
                input_id=raw_input.input_id,
                section_type=ClinicalSectionType.CHIEF_COMPLAINT,
                title="主诉",
                normalized_text="主诉：伴胸闷气短8年。",
                source_spans=[
                    SourceSpan(
                        span_id="span_section_001",
                        input_id=raw_input.input_id,
                        quoted_text="主诉：伴胸闷气短8年。",
                    )
                ],
                section_order=1,
            ),
            ClinicalSection(
                section_id="section_002",
                input_id=raw_input.input_id,
                section_type=ClinicalSectionType.HISTORY_OF_PRESENT_ILLNESS,
                title="现病史",
                normalized_text="现病史：8年前出现咳嗽，伴胸闷气短。",
                source_spans=[
                    SourceSpan(
                        span_id="span_section_002",
                        input_id=raw_input.input_id,
                        quoted_text="现病史：8年前出现咳嗽，伴胸闷气短。",
                    )
                ],
                section_order=2,
            ),
        ]
        item = StructuredClinicalItem(
            item_id="item_001",
            input_id=raw_input.input_id,
            section_id="section_002",
            item_type=ClinicalItemType.SYMPTOM,
            label="胸闷气短",
            source_spans=[
                SourceSpan(
                    span_id="span_item_001",
                    input_id=raw_input.input_id,
                    quoted_text="伴胸闷气短",
                )
            ],
            item_order=1,
        )

        resolved = SourceSpanResolver().resolve(
            raw_input=raw_input,
            sections=sections,
            items=[item],
            timeline_events=[],
            ambiguities=[],
        )

        resolved_span = resolved.items[0].source_spans[0]
        first_occurrence = raw_text.find("伴胸闷气短")
        section_2_start = raw_text.find("现病史")
        expected_occurrence = raw_text.find("伴胸闷气短", section_2_start)

        self.assertNotEqual(resolved_span.char_start, first_occurrence)
        self.assertEqual(resolved_span.char_start, expected_occurrence)
        self.assertEqual(
            resolved_span.char_end,
            expected_occurrence + len("伴胸闷气短"),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
