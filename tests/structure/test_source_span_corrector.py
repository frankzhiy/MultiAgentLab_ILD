from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult
from src.schemas.case_structurer.clinical_section import (
    ClinicalSection,
    ClinicalSectionType,
)
from src.schemas.case_structurer.common import (
    CertaintyLevel,
    NegationStatus,
    TemporalRelation,
)
from src.schemas.case_structurer.raw_text_input import RawTextInput
from src.schemas.case_structurer.source_span import SourceSpan
from src.schemas.case_structurer.stage_context import (
    StageContext,
    StageRelation,
    StageType,
)
from src.schemas.case_structurer.structured_clinical_item import (
    ClinicalItemType,
    StructuredClinicalItem,
)
from src.validators.case_structurer import validate_and_correct_source_spans


RAW_TEXT = (
    "现病史：患者完善2024年6月11日胸部CT提示考虑为“肺部感染”。"
    "血常规）:新型冠状病毒IgG/IgM抗体:2019-nCoV IgG 10.926S/CO,"
    "术前八项:HBeAb 1.790index,HBcAb 2.010index。"
)


class TestSourceSpanCorrector(unittest.TestCase):
    def test_repairs_source_span_input_id_mismatch(self) -> None:
        result = _result_with_item(
            label="考虑为“肺部感染”",
            source_quote="考虑为“肺部感染”",
        )
        item = result.structured_items[0]
        bad_span = item.source_spans[0].model_copy(update={"input_id": "wrong"})
        bad_item = item.model_copy(update={"source_spans": [bad_span]})
        bad_result = result.model_copy(update={"structured_items": [bad_item]})

        bundle = validate_and_correct_source_spans(bad_result)

        self.assertTrue(bundle.final_validation_report.is_valid)
        self.assertEqual(
            bundle.corrected_result.structured_items[0].source_spans[0].input_id,
            result.input.input_id,
        )
        self.assertIn(
            "source_span_input_id_mismatch",
            {action.code for action in bundle.correction_report.actions},
        )

    def test_resolves_missing_offsets_for_existing_quote(self) -> None:
        result = _result_with_item(
            label="考虑为“肺部感染”",
            source_quote="考虑为“肺部感染”",
            char_start=None,
            char_end=None,
        )

        bundle = validate_and_correct_source_spans(result)
        span = bundle.corrected_result.structured_items[0].source_spans[0]

        self.assertTrue(bundle.final_validation_report.is_valid)
        self.assertEqual(span.char_start, RAW_TEXT.find("考虑为“肺部感染”"))
        self.assertEqual(span.char_end, span.char_start + len("考虑为“肺部感染”"))

    def test_repairs_invalid_offsets_for_existing_quote(self) -> None:
        result = _result_with_item(
            label="考虑为“肺部感染”",
            source_quote="考虑为“肺部感染”",
            char_start=0,
            char_end=3,
        )

        bundle = validate_and_correct_source_spans(result)
        span = bundle.corrected_result.structured_items[0].source_spans[0]

        self.assertTrue(bundle.final_validation_report.is_valid)
        self.assertEqual(RAW_TEXT[span.char_start : span.char_end], span.quoted_text)

    def test_replaces_rewritten_quote_when_unique_support_is_locatable(self) -> None:
        result = _result_with_item(
            label="新型冠状病毒IgG 10.926S/CO",
            value="10.926",
            unit="S/CO",
            item_type=ClinicalItemType.LAB_RESULT,
            source_quote="新型冠状病毒IgG 10.926S/CO",
        )

        bundle = validate_and_correct_source_spans(result)
        span = bundle.corrected_result.structured_items[0].source_spans[0]

        self.assertTrue(bundle.final_validation_report.is_valid)
        self.assertIn("新型冠状病毒IgG/IgM抗体", span.quoted_text)
        self.assertIn("2019-nCoV IgG 10.926S/CO", span.quoted_text)

    def test_creates_missing_source_span_when_unique_support_is_locatable(self) -> None:
        result = _result_with_item(
            label="考虑为“肺部感染”",
            source_quote="考虑为“肺部感染”",
        )
        item = result.structured_items[0]
        bad_item = item.model_copy(update={"source_spans": []})
        bad_result = result.model_copy(update={"structured_items": [bad_item]})

        bundle = validate_and_correct_source_spans(bad_result)

        self.assertTrue(bundle.final_validation_report.is_valid)
        self.assertEqual(
            bundle.corrected_result.structured_items[0].source_spans[0].quoted_text,
            "考虑为“肺部感染”",
        )
        self.assertIn(
            "missing_source_span",
            {action.code for action in bundle.correction_report.actions},
        )

    def test_relocates_item_span_inside_parent_section_when_quote_repeats(self) -> None:
        raw_text = "主诉：咳嗽。现病史：咳嗽。"
        result = _result_with_item(
            raw_text=raw_text,
            section_quote="现病史：咳嗽。",
            label="咳嗽",
            source_quote="咳嗽",
            char_start=raw_text.find("咳嗽"),
            char_end=raw_text.find("咳嗽") + len("咳嗽"),
        )

        bundle = validate_and_correct_source_spans(result)
        span = bundle.corrected_result.structured_items[0].source_spans[0]

        self.assertTrue(bundle.final_validation_report.is_valid)
        self.assertEqual(span.char_start, raw_text.rfind("咳嗽"))

    def test_adds_minimal_span_for_unsupported_time_text(self) -> None:
        result = _result_with_item(
            label="考虑为“肺部感染”",
            source_quote="考虑为“肺部感染”",
            time_text="2024年6月11日",
            item_type=ClinicalItemType.DIAGNOSIS_HISTORY,
            temporality=TemporalRelation.RECENT_WORSENING,
        )

        bundle = validate_and_correct_source_spans(result)
        quotes = [
            span.quoted_text
            for span in bundle.corrected_result.structured_items[0].source_spans
        ]

        self.assertTrue(bundle.final_validation_report.is_valid)
        self.assertIn("2024年6月11日", quotes)

    def test_adds_minimal_span_for_unsupported_label_prefix(self) -> None:
        result = _result_with_item(
            label="术前八项:HBcAb 2.010index",
            value="2.010",
            unit="index",
            item_type=ClinicalItemType.LAB_RESULT,
            source_quote="HBcAb 2.010index",
        )

        bundle = validate_and_correct_source_spans(result)
        quotes = [
            span.quoted_text
            for span in bundle.corrected_result.structured_items[0].source_spans
        ]

        self.assertTrue(bundle.final_validation_report.is_valid)
        self.assertIn("术前八项", quotes)

    def test_unlocatable_or_ambiguous_repair_is_reported_not_forced(self) -> None:
        raw_text = "现病史：咳嗽。复述：咳嗽。"
        result = _result_with_item(
            raw_text=raw_text,
            section_quote=raw_text,
            label="咳嗽",
            source_quote="咳嗽咳痰",
        )

        bundle = validate_and_correct_source_spans(result)

        self.assertFalse(bundle.final_validation_report.is_valid)
        self.assertTrue(bundle.residual_issues)
        self.assertIn(
            "skipped",
            {action.status for action in bundle.correction_report.actions},
        )

    def test_unrepairable_missing_source_span_is_reported_not_crashing(self) -> None:
        raw_text = "现病史：咳嗽。复述：咳嗽。"
        result = _result_with_item(
            raw_text=raw_text,
            section_quote=raw_text,
            label="咳嗽",
            source_quote="咳嗽",
        )
        item = result.structured_items[0]
        bad_item = item.model_copy(update={"source_spans": []})
        bad_result = result.model_copy(update={"structured_items": [bad_item]})

        bundle = validate_and_correct_source_spans(bad_result)

        self.assertFalse(bundle.final_validation_report.is_valid)
        self.assertIn(
            "missing_source_span",
            {issue.code for issue in bundle.residual_issues},
        )

    def test_correction_does_not_change_medical_fields(self) -> None:
        result = _result_with_item(
            label="考虑为“肺部感染”",
            source_quote="考虑为“肺部感染”",
            time_text="2024年6月11日",
            item_type=ClinicalItemType.DIAGNOSIS_HISTORY,
            temporality=TemporalRelation.RECENT_WORSENING,
            certainty=CertaintyLevel.POSSIBLE,
            negation=NegationStatus.PRESENT,
        )

        bundle = validate_and_correct_source_spans(result)
        before = result.structured_items[0]
        after = bundle.corrected_result.structured_items[0]

        self.assertEqual(after.item_type, before.item_type)
        self.assertEqual(after.temporality, before.temporality)
        self.assertEqual(after.certainty, before.certainty)
        self.assertEqual(after.negation, before.negation)
        self.assertEqual(after.section_id, before.section_id)


def _result_with_item(
    *,
    raw_text: str = RAW_TEXT,
    section_quote: str | None = None,
    label: str,
    source_quote: str,
    value: str | None = None,
    unit: str | None = None,
    time_text: str | None = None,
    item_type: ClinicalItemType = ClinicalItemType.OTHER,
    temporality: TemporalRelation = TemporalRelation.CURRENT,
    certainty: CertaintyLevel = CertaintyLevel.DEFINITE,
    negation: NegationStatus = NegationStatus.PRESENT,
    char_start: int | None = None,
    char_end: int | None = None,
) -> CaseStructuringResult:
    raw_input = RawTextInput(
        input_id="input_001",
        case_id="case_001",
        raw_text=raw_text,
    )
    stage_context = StageContext(
        stage_id="stage_001",
        case_id=raw_input.case_id,
        input_id=raw_input.input_id,
        stage_order=1,
        stage_type=StageType.INITIAL_INPUT,
        relation_to_previous_stage=StageRelation.NEW_CASE_START,
        is_initial_stage=True,
    )
    section_text = section_quote or raw_text
    section = ClinicalSection(
        section_id="section_001",
        input_id=raw_input.input_id,
        section_type=ClinicalSectionType.OTHER,
        title=None,
        normalized_text=section_text,
        source_spans=[
            SourceSpan(
                span_id="span_section_001",
                input_id=raw_input.input_id,
                quoted_text=section_text,
                char_start=raw_text.find(section_text),
                char_end=raw_text.find(section_text) + len(section_text),
            )
        ],
        section_order=1,
    )
    if char_start is None and char_end is None:
        source_span = SourceSpan(
            span_id="span_item_001",
            input_id=raw_input.input_id,
            quoted_text=source_quote,
        )
    else:
        source_span = SourceSpan(
            span_id="span_item_001",
            input_id=raw_input.input_id,
            quoted_text=source_quote,
            char_start=char_start,
            char_end=char_end,
        )
    item = StructuredClinicalItem(
        item_id="item_001",
        input_id=raw_input.input_id,
        section_id=section.section_id,
        item_type=item_type,
        label=label,
        value=value,
        unit=unit,
        body_site=None,
        temporality=temporality,
        time_text=time_text,
        certainty=certainty,
        negation=negation,
        source_spans=[source_span],
        item_order=1,
    )

    return CaseStructuringResult(
        input=raw_input,
        stage_context=stage_context,
        clinical_sections=[section],
        structured_items=[item],
        timeline_events=[],
        ambiguities=[],
        structuring_warnings=[],
        ready_for_evidence_atomization=True,
    )


if __name__ == "__main__":
    unittest.main(verbosity=2)
