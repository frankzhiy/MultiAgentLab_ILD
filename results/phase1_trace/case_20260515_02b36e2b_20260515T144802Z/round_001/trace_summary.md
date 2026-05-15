# Phase 1 Trace Round 001

- Selected file: data/01.txt
- case_id: case_20260515_02b36e2b
- input_id: input_20260515_54c25801
- parent_input_id: None
- input_order: 1
- case_structuring_result_id: case_structuring_result_20260515_8b268ce9
- attribute_extraction_result_id: attribute_extraction_result_20260515_31f29576
- atomization_result_id: atomization_result_20260515_7b24b6b4
- case_structurer_duration: 1 min 13.7 s
- attribute_extractor_duration: 27.04 s
- evidence_atomizer_duration: 6 min 19.1 s
- round_duration: 7 min 59.9 s

## Structuring Summary

- ready_for_attribute_extraction: True
- clinical_sections: 5
- structured_items: 13

## Case Structurer Results

### Stage Context

| stage_id | stage_order | stage_type | relation_to_previous_stage | previous_stage_id | is_initial_stage | classification_confidence | classification_basis |
| --- | --- | --- | --- | --- | --- | --- | --- |
| stage_20260515_011ef493 | 1 | initial_input | new_case_start |  | True | high | First input in the case providing initial patient history and admission details. |

### Clinical Sections

| section_id | section_order | section_type | title | parent_section_id | classification_confidence | source_span_ids | normalized_text |
| --- | --- | --- | --- | --- | --- | --- | --- |
| section_001 | 1 | demographics |  |  | high | span_section_001 | 患者***,女,77岁 |
| section_002 | 2 | chief_complaint |  |  | high | span_section_002 | 主因“间断咳嗽咳痰伴胸闷气短8年，加重2月”入院 |
| section_003 | 3 | uncertain |  |  | high | span_section_003 | 一般健康状况：良好 |
| section_004 | 4 | past_medical_history |  |  | high | span_section_004 | 疾病史：既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史。40年前左下肢骨折固定术 |
| section_005 | 5 | history_of_present_illness |  |  | high | span_section_005 | 现病史：患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗。1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善。2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适，遂就诊于当地医院，完善2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊，考虑为“肺部感染”，治疗上给予抗感染（具体不详）治疗后，胸闷气短症状改善不明显，为进一步诊治，遂就诊于我院，详阅当地胸部CT，请我科医师会诊后，以“间质性肺炎，肺部感染”收住我科。病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化。 |

### Structured Clinical Items

| item_id | item_order | section_id | item_type | label | temporality | certainty | negation | classification_confidence | source_span_ids | source_text |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| item_001 | 1 | section_001 | demographic | 患者***,女,77岁 | unknown | definite | present | high | span_item_001 | 患者***,女,77岁 |
| item_002 | 2 | section_002 | symptom | 主因“间断咳嗽咳痰伴胸闷气短8年，加重2月”入院 | chronic | definite | present | high | span_item_002 | 主因“间断咳嗽咳痰伴胸闷气短8年，加重2月”入院 |
| item_003 | 3 | section_003 | other | 一般健康状况：良好 | current | definite | present | high | span_item_003 | 一般健康状况：良好 |
| item_004 | 4 | section_004 | comorbidity | 既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史 | chronic | definite | present | high | span_item_004 | 既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史 |
| item_005 | 5 | section_004 | procedure | 40年前左下肢骨折固定术 | past | definite | present | high | span_item_005 | 40年前左下肢骨折固定术 |
| item_006 | 6 | section_005 | symptom | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 | chronic | definite | present | high | span_item_006 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| item_007 | 7 | section_005 | symptom | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 | past | definite | present | high | span_item_007 | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| item_008 | 8 | section_005 | symptom | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 | recent_worsening | definite | present | high | span_item_008 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| item_009 | 9 | section_005 | imaging_finding | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 | recent_worsening | definite | present | high | span_item_009 | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 |
| item_010 | 10 | section_005 | diagnosis_history | 考虑为“肺部感染” | recent_worsening | possible | present | high | span_item_010 | 考虑为“肺部感染” |
| item_011 | 11 | section_005 | treatment | 治疗上给予抗感染（具体不详）治疗后，胸闷气短症状改善不明显 | recent_worsening | definite | present | high | span_item_011 | 治疗上给予抗感染（具体不详）治疗后，胸闷气短症状改善不明显 |
| item_012 | 12 | section_005 | diagnosis_history | 以“间质性肺炎，肺部感染”收住我科 | current | definite | present | high | span_item_012 | 以“间质性肺炎，肺部感染”收住我科 |
| item_013 | 13 | section_005 | sign | 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 | current | definite | present | high | span_item_013 | 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 |

### Structuring Warnings

| severity | code | message | related_object_id |
| --- | --- | --- | --- |
| No structuring warnings produced. |  |  |  |

## Attribute Extraction Summary

- attribute_extraction_result_id: attribute_extraction_result_20260515_31f29576
- clinical_attributes: 18
- ready_for_evidence_atomization: True
- validation_accepted: True

## Attribute Extractor Validation Issues

No validation issues.

## Clinical Attributes

| attribute_id | source_item_id | attribute_role | attribute_scope | span_text | applies_to_text | context_text | normalized_value | normalized_unit | normalized_text | extraction_confidence | source_span_id |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| attribute_20260515_d7313ca4 | item_001 | sex | item | 女 | 患者***,女,77岁 | 患者***,女,77岁 |  |  | female | high | span_attr_001 |
| attribute_20260515_f3dd8378 | item_001 | age | item | 77岁 | 患者***,女,77岁 | 患者***,女,77岁 | 77 | year | 77 years | high | span_attr_002 |
| attribute_20260515_54dea621 | item_002 | symptom_duration | local_phrase | 8年 | 间断咳嗽咳痰伴胸闷气短8年 | 主因“间断咳嗽咳痰伴胸闷气短8年，加重2月”入院 | 8 | year | 8 years | high | span_attr_003 |
| attribute_20260515_608b40c4 | item_002 | worsening_interval | local_phrase | 加重2月 | 加重2月 | 主因“间断咳嗽咳痰伴胸闷气短8年，加重2月”入院 | 2 | month | 2 months | high | span_attr_004 |
| attribute_20260515_a5a79b14 | item_004 | disease_history_duration | local_phrase | 8年 | 既往高血压8年 | 既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史 | 8 | year | 8 years | high | span_attr_005 |
| attribute_20260515_4981b0bc | item_004 | medication_dose | local_phrase | 2片/次 | 沙库巴曲缬沙坦片 2片/次 | 既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史 | 2 | 片/次 | 2 tablets per dose | high | span_attr_006 |
| attribute_20260515_30826545 | item_004 | medication_frequency | local_phrase | 1次/日 | 1次/日 口服 | 既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史 | 1 | 次/日 | once daily | high | span_attr_007 |
| attribute_20260515_5fefd334 | item_004 | medication_route | local_phrase | 口服 | 1次/日 口服 | 既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史 |  |  | oral | high | span_attr_008 |
| attribute_20260515_c402cd3e | item_005 | uncertain_attribute | local_phrase | 40年前 | 40年前左下肢骨折固定术 | 40年前左下肢骨折固定术 | 40 | 年 | 40 years ago | high | span_attr_009 |
| attribute_20260515_c805e07e | item_006 | onset_time | local_phrase | 8年前 | 患者于8年前无明显诱因出现咳嗽咳痰 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 | 8 | 年 | 8 years ago | high | span_attr_010 |
| attribute_20260515_28e99288 | item_007 | onset_time | local_phrase | 1年前 | 1年前新冠病毒感染后再次出现咳嗽咳痰 | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 | 1 | 年 | 1 year ago | high | span_attr_011 |
| attribute_20260515_17d18ce5 | item_007 | uncertain_attribute | local_phrase | 1周余 | 于当地诊所输液1周余（具体不详）后 | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 | 1 | 周 | about 1 week | medium | span_attr_012 |
| attribute_20260515_5dbb4227 | item_008 | onset_time | local_phrase | 2月前 | 2月前无明显诱因再次出现咳嗽咳痰 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 | 2 | 月 | 2 months ago | high | span_attr_013 |
| attribute_20260515_b430becd | item_009 | onset_time | local_phrase | 2024年6月11日 | 2024年6月11日胸部CT示 | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 | 2024-06-11 |  | 2024-06-11 | high | span_attr_014 |
| attribute_20260515_afe967e3 | item_009 | qualitative_result | local_phrase | 双肺间质增粗纹理走形杂乱 | 双肺间质增粗纹理走形杂乱 | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 |  |  | bilateral lung interstitial thickening with irregular texture | high | span_attr_015 |
| attribute_20260515_9b3110bc | item_009 | qualitative_result | local_phrase | 肺野密度增高 | 肺野密度增高 | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 |  |  | increased lung field density | high | span_attr_016 |
| attribute_20260515_79480106 | item_009 | qualitative_result | local_phrase | 右肺中叶、下叶、左肺舌段条片状实性高密度影 | 右肺中叶、下叶、左肺舌段条片状实性高密度影 | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 |  |  | strip-like solid high-density shadows in right middle and lower lobes and left lingular segment | high | span_attr_017 |
| attribute_20260515_23c26ccb | item_009 | qualitative_result | local_phrase | 右肺中叶、下叶病灶边缘模糊 | 右肺中叶、下叶病灶边缘模糊 | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 |  |  | lesion edges in right middle and lower lobes are blurred | high | span_attr_018 |

## Atomization Summary

- atomization_result_id: atomization_result_20260515_7b24b6b4
- evidence_atoms: 36
- item_to_evidence_links: 8
- deferred_items: 0
- atomization_warnings: 27
- evidence_event_frames: 13
- evidence_event_frame_warnings: 4
- validation_accepted: False

## Evidence Atomizer Validation Issues

| severity | code | message | related_item_id | related_attribute_id | related_evidence_id | related_span_id |
| --- | --- | --- | --- | --- | --- | --- |
| warning | structured_item_not_accounted_for | StructuredClinicalItem is not referenced by any evidence atom, item-evidence link, or deferred item. | item_001 |  |  |  |
| warning | structured_item_not_accounted_for | StructuredClinicalItem is not referenced by any evidence atom, item-evidence link, or deferred item. | item_003 |  |  |  |
| warning | structured_item_not_accounted_for | StructuredClinicalItem is not referenced by any evidence atom, item-evidence link, or deferred item. | item_004 |  |  |  |
| warning | structured_item_not_accounted_for | StructuredClinicalItem is not referenced by any evidence atom, item-evidence link, or deferred item. | item_005 |  |  |  |
| warning | structured_item_not_accounted_for | StructuredClinicalItem is not referenced by any evidence atom, item-evidence link, or deferred item. | item_011 |  |  |  |
| error | coverage_unit_not_covered | Required CoverageUnit must be referenced by at least one EvidenceAtom. [coverage_unit_id=item_002__frame_unit_002] | item_002 |  |  |  |
| error | coverage_unit_not_covered | Required CoverageUnit must be referenced by at least one EvidenceAtom. [coverage_unit_id=item_002__frame_unit_003] | item_002 |  |  |  |
| error | coverage_unit_not_covered | Required CoverageUnit must be referenced by at least one EvidenceAtom. [coverage_unit_id=item_002__frame_unit_004] | item_002 |  |  |  |
| warning | absent_atom_has_positive_surface | EvidenceAtom statement contains a positive cue while assertion_status is absent. |  |  | evidence_20260515_6b24c29c |  |
| warning | absent_atom_has_positive_surface | EvidenceAtom statement contains a positive cue while assertion_status is absent. |  |  | evidence_20260515_0f2bdeb1 |  |
| warning | absent_atom_has_positive_surface | EvidenceAtom statement contains a positive cue while assertion_status is absent. |  |  | evidence_20260515_05203802 |  |
| warning | absent_atom_has_positive_surface | EvidenceAtom statement contains a positive cue while assertion_status is absent. |  |  | evidence_20260515_85a30613 |  |
| warning | absent_atom_has_positive_surface | EvidenceAtom statement contains a positive cue while assertion_status is absent. |  |  | evidence_20260515_b2642f6f |  |
| warning | absent_atom_has_positive_surface | EvidenceAtom statement contains a positive cue while assertion_status is absent. |  |  | evidence_20260515_8e96c3f1 |  |
| warning | absent_atom_has_positive_surface | EvidenceAtom statement contains a positive cue while assertion_status is absent. |  |  | evidence_20260515_1f3e1536 |  |
| warning | absent_atom_has_positive_surface | EvidenceAtom statement contains a positive cue while assertion_status is absent. |  |  | evidence_20260515_783a22a6 |  |
| warning | absent_atom_has_positive_surface | EvidenceAtom statement contains a positive cue while assertion_status is absent. |  |  | evidence_20260515_916acb6b |  |

## Evidence Event Frames (debug)

| frame_id | source_item_id | assertion_count | mapped_assertion_count | deferred_assertion_count | number_of_nodes | atomizable_node_count | degenerate_frame_warnings | warning_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| evidence_frame_20260515_f4be5581 | item_001 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
| evidence_frame_20260515_7d03b253 | item_002 | 5 | 5 | 0 | 5 | 4 | 0 | 0 |
| evidence_frame_20260515_58546962 | item_003 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
| evidence_frame_20260515_9e44cf87 | item_004 | 0 | 0 | 0 | 4 | 4 | 0 | 0 |
| evidence_frame_20260515_2f021c6a | item_005 | 0 | 0 | 0 | 1 | 1 | 0 | 0 |
| evidence_frame_20260515_3a66ab73 | item_006 | 16 | 16 | 0 | 16 | 14 | 0 | 0 |
| evidence_frame_20260515_b50d994b | item_007 | 10 | 10 | 0 | 9 | 7 | 0 | 1 |
| evidence_frame_20260515_d244e636 | item_008 | 10 | 10 | 0 | 6 | 3 | 0 | 0 |
| evidence_frame_20260515_3df9baa5 | item_009 | 4 | 4 | 0 | 5 | 4 | 0 | 0 |
| evidence_frame_20260515_135329b2 | item_010 | 1 | 1 | 0 | 1 | 1 | 0 | 0 |
| evidence_frame_20260515_307008e2 | item_011 | 0 | 0 | 0 | 3 | 2 | 0 | 0 |
| evidence_frame_20260515_b67681bd | item_012 | 2 | 2 | 0 | 2 | 2 | 0 | 1 |
| evidence_frame_20260515_f2a55086 | item_013 | 4 | 4 | 0 | 4 | 4 | 0 | 0 |

## Evidence Event Frame Tree Preview

- Tree-first view for reading parent/child frame structure.
- Full report file: evidence_event_frames_tree.md.

### Frame item_001

- frame_id: evidence_frame_20260515_f4be5581
- source_text: 患者***,女,77岁
- frame_node_count: 1
- atomizable_node_count: 0
- mapped_assertion_count: 0
- deferred_assertion_count: 0
- degenerate_frame_warnings: 0

```text
└─ clinical_object [4bfaf7ef] 患者***,女,77岁 {role=local_content}
```

### Frame item_002

- frame_id: evidence_frame_20260515_7d03b253
- source_text: 主因“间断咳嗽咳痰伴胸闷气短8年，加重2月”入院
- frame_node_count: 5
- atomizable_node_count: 4
- mapped_assertion_count: 5
- deferred_assertion_count: 0
- degenerate_frame_warnings: 0
- mapped_assertion_ids: clinical_object_assertion_20260515_3c6fab7e, clinical_object_assertion_20260515_76b345b9, clinical_object_assertion_20260515_aac1f548, clinical_object_assertion_20260515_c9df30e2, clinical_object_assertion_20260515_f7dcb8ce

```text
└─ main_event [2d1b256e] 主因“间断咳嗽咳痰伴胸闷气短8年，加重2月”入院 {assertions=clinical_object_assertion_20260515_c9df30e2; role=local_content; context_for=1}
   ↳ context_for_atoms: 1d1e364c
   ├─ clinical_object [fd952aa5] 间断咳嗽 {rel=occurrence_of; assertions=clinical_object_assertion_20260515_aac1f548; atom=generate_atom_with_inherited_context; atoms=1}
   │  ↳ atom[1d1e364c] 主因“间断咳嗽咳痰伴胸闷气短8年，加重2月”入院
   ├─ clinical_object [579c2adf] 咳痰 {rel=occurrence_of; assertions=clinical_object_assertion_20260515_76b345b9; atom=generate_atom_with_inherited_context}
   ├─ clinical_object [f75676c9] 胸闷 {rel=occurrence_of; assertions=clinical_object_assertion_20260515_3c6fab7e; atom=generate_atom_with_inherited_context}
   └─ clinical_object [30c489a8] 气短 {rel=occurrence_of; assertions=clinical_object_assertion_20260515_f7dcb8ce; atom=generate_atom_with_inherited_context}
```

### Frame item_003

- frame_id: evidence_frame_20260515_58546962
- source_text: 一般健康状况：良好
- frame_node_count: 1
- atomizable_node_count: 0
- mapped_assertion_count: 0
- deferred_assertion_count: 0
- degenerate_frame_warnings: 0

```text
└─ negative_finding [94b8800f] 一般健康状况：良好 {role=local_content}
```

### Frame item_004

- frame_id: evidence_frame_20260515_9e44cf87
- source_text: 既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史
- frame_node_count: 4
- atomizable_node_count: 4
- mapped_assertion_count: 0
- deferred_assertion_count: 0
- degenerate_frame_warnings: 0

```text
├─ clinical_object [ff8341da] 既往高血压8年 {atom=generate_atom}
│  └─ treatment_event [5a49d4d4] 目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服 {rel=treatment_for; atom=generate_atom_with_inherited_context}
├─ clinical_object [c3df4f39] 糖尿病 {atom=generate_atom}
└─ clinical_object [ed0a5c8a] 冠心病病史 {atom=generate_atom}
```

### Frame item_005

- frame_id: evidence_frame_20260515_2f021c6a
- source_text: 40年前左下肢骨折固定术
- frame_node_count: 1
- atomizable_node_count: 1
- mapped_assertion_count: 0
- deferred_assertion_count: 0
- degenerate_frame_warnings: 0

```text
└─ negative_finding [4b9ff6ae] 40年前左下肢骨折固定术 {atom=generate_atom}
```

### Frame item_006

- frame_id: evidence_frame_20260515_3a66ab73
- source_text: 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗
- frame_node_count: 16
- atomizable_node_count: 14
- mapped_assertion_count: 16
- deferred_assertion_count: 0
- degenerate_frame_warnings: 0
- mapped_assertion_ids: clinical_object_assertion_20260515_3c9447e2, clinical_object_assertion_20260515_4faf9002, clinical_object_assertion_20260515_4fe0aba2, clinical_object_assertion_20260515_65f6c221, clinical_object_assertion_20260515_75e495f3, clinical_object_assertion_20260515_7f10431b, clinical_object_assertion_20260515_89b780e1, clinical_object_assertion_20260515_96256ea4, clinical_object_assertion_20260515_9fc3aaba, clinical_object_assertion_20260515_a97f1689, clinical_object_assertion_20260515_ab6270e3, clinical_object_assertion_20260515_ad87e3ec, clinical_object_assertion_20260515_c38733af, clinical_object_assertion_20260515_e015a8a7, clinical_object_assertion_20260515_f35aba02, clinical_object_assertion_20260515_f573965c

```text
└─ temporal_context [53549a06] 8年前 {role=local_content; context_for=14}
   ↳ context_for_atoms: 9188f109, 8e96c3f1, b2642f6f, 6b24c29c, 916acb6b ...
   └─ main_event [45d0931b] 患者于8年前无明显诱因出现咳嗽咳痰 {rel=temporal_context_of; assertions=clinical_object_assertion_20260515_89b780e1,clinical_object_assertion_20260515_c38733af; role=local_content; context_for=14}
      ↳ context_for_atoms: 9188f109, 8e96c3f1, b2642f6f, 6b24c29c, 916acb6b ...
      ├─ object_property [ba132417] 痰液为黏白色，量少，易咳出 {rel=property_of; assertions=clinical_object_assertion_20260515_ad87e3ec; atom=generate_atom_with_inherited_context; atoms=1}
      │  ↳ atom[8d67ca7b] 8年前患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出
      ├─ clinical_object [64932bef] 胸闷 {rel=occurrence_of; assertions=clinical_object_assertion_20260515_3c9447e2; atom=generate_atom_with_inherited_context; atoms=1}
      │  ↳ atom[fb9de71b] 8年前患者于8年前无明显诱因出现咳嗽咳痰，胸闷
      │  └─ symptom_modifier [6deeb97f] 夜间为著 {rel=modifier_of; assertions=clinical_object_assertion_20260515_7f10431b; atom=generate_group_modifier_atom; atoms=1}
      │     ↳ atom[9188f109] 8年前患者于8年前无明显诱因出现咳嗽咳痰胸闷，夜间为著
      ├─ clinical_object [189e2c06] 气短 {rel=occurrence_of; assertions=clinical_object_assertion_20260515_9fc3aaba; atom=generate_atom_with_inherited_context; atoms=1}
      │  ↳ atom[9dbc9fa7] 8年前患者于8年前无明显诱因出现咳嗽咳痰，气短
      ├─ negative_finding [9a575935] 发热 {rel=negative_contrast_of; assertions=clinical_object_assertion_20260515_ab6270e3; atom=generate_atom_with_inherited_context; atoms=1}
      │  ↳ atom[6b24c29c] 8年前患者于8年前无明显诱因出现咳嗽咳痰，发热
      ├─ negative_finding [5e7dbd3c] 寒战 {rel=negative_contrast_of; assertions=clinical_object_assertion_20260515_f35aba02; atom=generate_atom_with_inherited_context; atoms=1}
      │  ↳ atom[0f2bdeb1] 8年前患者于8年前无明显诱因出现咳嗽咳痰，寒战
      ├─ negative_finding [bff36013] 胸痛 {rel=negative_contrast_of; assertions=clinical_object_assertion_20260515_65f6c221; atom=generate_atom_with_inherited_context; atoms=1}
      │  ↳ atom[05203802] 8年前患者于8年前无明显诱因出现咳嗽咳痰，胸痛
      ├─ negative_finding [951eae98] 咯血 {rel=negative_contrast_of; assertions=clinical_object_assertion_20260515_e015a8a7; atom=generate_atom_with_inherited_context; atoms=1}
      │  ↳ atom[85a30613] 8年前患者于8年前无明显诱因出现咳嗽咳痰，咯血
      ├─ negative_finding [051ee7c9] 午后低热 {rel=negative_contrast_of; assertions=clinical_object_assertion_20260515_f573965c; atom=generate_atom_with_inherited_context; atoms=1}
      │  ↳ atom[b2642f6f] 8年前患者于8年前无明显诱因出现咳嗽咳痰，午后低热
      ├─ negative_finding [0577d0e2] 乏力 {rel=negative_contrast_of; assertions=clinical_object_assertion_20260515_4fe0aba2; atom=generate_atom_with_inherited_context; atoms=1}
      │  ↳ atom[8e96c3f1] 8年前患者于8年前无明显诱因出现咳嗽咳痰，乏力
      ├─ negative_finding [9e51d032] 盗汗 {rel=negative_contrast_of; assertions=clinical_object_assertion_20260515_75e495f3; atom=generate_atom_with_inherited_context; atoms=1}
      │  ↳ atom[1f3e1536] 8年前患者于8年前无明显诱因出现咳嗽咳痰，盗汗
      ├─ negative_finding [9b3e3ba6] 恶心 {rel=negative_contrast_of; assertions=clinical_object_assertion_20260515_a97f1689; atom=generate_atom_with_inherited_context; atoms=1}
      │  ↳ atom[783a22a6] 8年前患者于8年前无明显诱因出现咳嗽咳痰，恶心
      ├─ negative_finding [753869d6] 呕吐 {rel=negative_contrast_of; assertions=clinical_object_assertion_20260515_4faf9002; atom=generate_atom_with_inherited_context; atoms=1}
      │  ↳ atom[916acb6b] 8年前患者于8年前无明显诱因出现咳嗽咳痰，呕吐
      └─ management_event [5fee9d7c] 未予重视及诊疗 {rel=management_after; assertions=clinical_object_assertion_20260515_96256ea4; atom=generate_atom_with_inherited_context; atoms=1}
         ↳ atom[1af0944b] 8年前患者于8年前无明显诱因出现咳嗽咳痰，未予重视及诊疗
```

### Frame item_007

- frame_id: evidence_frame_20260515_b50d994b
- source_text: 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善
- frame_node_count: 9
- atomizable_node_count: 7
- mapped_assertion_count: 10
- deferred_assertion_count: 0
- degenerate_frame_warnings: 0
- mapped_assertion_ids: clinical_object_assertion_20260515_01cc76d8, clinical_object_assertion_20260515_234e50c8, clinical_object_assertion_20260515_2a435772, clinical_object_assertion_20260515_5e981f3e, clinical_object_assertion_20260515_9971f2e8, clinical_object_assertion_20260515_b07dc424, clinical_object_assertion_20260515_dbd504b8, clinical_object_assertion_20260515_e0324454, clinical_object_assertion_20260515_f00f9644, clinical_object_assertion_20260515_f7d335e6

```text
├─ temporal_context [51fd87ea] 1年前 {assertions=clinical_object_assertion_20260515_f7d335e6,clinical_object_assertion_20260515_2a435772; role=local_content; context_for=7}
│  ↳ context_for_atoms: dce4839f, 78f5d1a3, 9a877fab, ff88e1b3, ab76d6c7 ...
│  └─ main_event [b43c041c] 再次出现咳嗽咳痰 {rel=temporal_context_of; assertions=clinical_object_assertion_20260515_f7d335e6,clinical_object_assertion_20260515_2a435772; role=local_content; context_for=5}
│     ↳ context_for_atoms: dce4839f, 78f5d1a3, 9a877fab, ff88e1b3, ab76d6c7
│     ├─ clinical_object [b72613d9] 痰液为黏白色 {rel=property_of; assertions=clinical_object_assertion_20260515_f00f9644; atom=generate_atom_with_inherited_context; atoms=1}
│     │  ↳ atom[9a877fab] 1年前再次出现咳嗽咳痰，痰液为黏白色
│     ├─ object_property [aeac6c32] 量少 {rel=property_of; assertions=clinical_object_assertion_20260515_dbd504b8; atom=generate_atom_with_inherited_context; atoms=1}
│     │  ↳ atom[ab76d6c7] 1年前再次出现咳嗽咳痰，量少
│     ├─ object_property [52ab96fc] 易咳出 {rel=property_of; assertions=clinical_object_assertion_20260515_9971f2e8; atom=generate_atom_with_inherited_context; atoms=1}
│     │  ↳ atom[78f5d1a3] 1年前再次出现咳嗽咳痰，易咳出
│     └─ clinical_object [a4a07d79] 胸闷气短 {rel=associated_with; assertions=clinical_object_assertion_20260515_e0324454,clinical_object_assertion_20260515_234e50c8; atom=generate_atom_with_inherited_context; atoms=1}
│        ↳ atom[ff88e1b3] 1年前再次出现咳嗽咳痰，胸闷气短
│        └─ symptom_modifier [adc45390] 活动后明显 {rel=modifier_of; assertions=clinical_object_assertion_20260515_01cc76d8; atom=generate_atom_with_inherited_context; atoms=1}
│           ↳ atom[dce4839f] 1年前再次出现咳嗽咳痰胸闷气短，活动后明显
└─ management_event [fc40269a] 于当地诊所输液1周余（具体不详） {assertions=clinical_object_assertion_20260515_5e981f3e; atom=generate_atom_with_inherited_context; atoms=1}
   ↳ atom[b183a78d] 1年前，于当地诊所输液1周余（具体不详）
   └─ treatment_response [b3d0e230] 咳嗽咳痰、胸闷气短有所改善 {rel=response_after; assertions=clinical_object_assertion_20260515_b07dc424; atom=generate_atom_with_inherited_context; atoms=1}
      ↳ atom[1398545c] 于当地诊所输液1周余（具体不详）1年前，咳嗽咳痰、胸闷气短有所改善
```

### Frame item_008

- frame_id: evidence_frame_20260515_d244e636
- source_text: 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适
- frame_node_count: 6
- atomizable_node_count: 3
- mapped_assertion_count: 10
- deferred_assertion_count: 0
- degenerate_frame_warnings: 0
- mapped_assertion_ids: clinical_object_assertion_20260515_0df4c9d5, clinical_object_assertion_20260515_5ff446b3, clinical_object_assertion_20260515_7195cdc8, clinical_object_assertion_20260515_8b7e5d03, clinical_object_assertion_20260515_926a1fee, clinical_object_assertion_20260515_94a4798d, clinical_object_assertion_20260515_a762ce27, clinical_object_assertion_20260515_aa4acadb, clinical_object_assertion_20260515_c2c05f9a, clinical_object_assertion_20260515_c849b1c0

```text
└─ main_event [42e2a8df] 2月前无明显诱因再次出现咳嗽咳痰 {assertions=clinical_object_assertion_20260515_0df4c9d5,clinical_object_assertion_20260515_a762ce27; atom=generate_atom; atoms=1}
   ↳ atom[3aeaf159] 2月前无明显诱因再次出现咳嗽咳痰
   ├─ clinical_object [b0fb64cb] 胸闷 {rel=associated_with; assertions=clinical_object_assertion_20260515_5ff446b3; atom=generate_atom_with_inherited_context; atoms=1}
   │  ↳ atom[ab012d49] 2月前无明显诱因再次出现咳嗽咳痰，胸闷
   ├─ clinical_object [3bc34217] 气短 {rel=associated_with; assertions=clinical_object_assertion_20260515_926a1fee; atom=generate_atom_with_inherited_context; atoms=1}
   │  ↳ atom[2f0c2c0a] 2月前无明显诱因再次出现咳嗽咳痰，气短
   ├─ negative_finding [d0220f9a] 无发热寒战 {rel=negative_contrast_of; assertions=clinical_object_assertion_20260515_8b7e5d03,clinical_object_assertion_20260515_aa4acadb; role=local_content}
   ├─ negative_finding [91511308] 无胸痛咯血 {rel=negative_contrast_of; assertions=clinical_object_assertion_20260515_94a4798d,clinical_object_assertion_20260515_c849b1c0; role=local_content}
   └─ negative_finding [d629ff43] 无恶心呕吐等不适 {rel=negative_contrast_of; assertions=clinical_object_assertion_20260515_7195cdc8,clinical_object_assertion_20260515_c2c05f9a; role=local_content}
```

### Frame item_009

- frame_id: evidence_frame_20260515_3df9baa5
- source_text: 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊
- frame_node_count: 5
- atomizable_node_count: 4
- mapped_assertion_count: 4
- deferred_assertion_count: 0
- degenerate_frame_warnings: 0
- mapped_assertion_ids: clinical_object_assertion_20260515_9b75d2b1, clinical_object_assertion_20260515_d6e10845, clinical_object_assertion_20260515_d75cbe10, clinical_object_assertion_20260515_e4a9b2e7

```text
└─ temporal_context [a4aba859] 2024年6月11日胸部CT示 {role=local_content; context_for=4}
   ↳ context_for_atoms: a7f034e9, b2e77ce4, 8cd44b6e, c545ac0e
   ├─ clinical_object [23738a0c] 双肺间质增粗纹理走形杂乱 {rel=temporal_context_of; assertions=clinical_object_assertion_20260515_d6e10845; atom=generate_atom_with_inherited_context; atoms=1}
   │  ↳ atom[b2e77ce4] 2024年6月11日胸部CT示，双肺间质增粗纹理走形杂乱
   ├─ clinical_object [bb68df03] 肺野密度增高 {rel=temporal_context_of; assertions=clinical_object_assertion_20260515_9b75d2b1; atom=generate_atom_with_inherited_context; atoms=1}
   │  ↳ atom[c545ac0e] 2024年6月11日胸部CT示，肺野密度增高
   └─ clinical_object [6328f8a4] 右肺中叶、下叶、左肺舌段条片状实性高密度影 {rel=temporal_context_of; assertions=clinical_object_assertion_20260515_d75cbe10; atom=generate_atom_with_inherited_context; atoms=1}
      ↳ atom[8cd44b6e] 2024年6月11日胸部CT示，右肺中叶、下叶、左肺舌段条片状实性高密度影
      └─ object_property [9828faaf] 右肺中叶、下叶病灶边缘模糊 {rel=property_of; assertions=clinical_object_assertion_20260515_e4a9b2e7; atom=generate_atom_with_inherited_context; atoms=1}
         ↳ atom[a7f034e9] 2024年6月11日胸部CT示右肺中叶、下叶、左肺舌段条片状实性高密度影，右肺中叶、下叶病灶边缘模糊
```

### Frame item_010

- frame_id: evidence_frame_20260515_135329b2
- source_text: 考虑为“肺部感染”
- frame_node_count: 1
- atomizable_node_count: 1
- mapped_assertion_count: 1
- deferred_assertion_count: 0
- degenerate_frame_warnings: 0
- mapped_assertion_ids: clinical_object_assertion_20260515_c6f1b430

```text
└─ clinical_object [6fccf711] 肺部感染 {assertions=clinical_object_assertion_20260515_c6f1b430; atom=generate_atom; atoms=1}
   ↳ atom[3df040a7] 肺部感染
```

### Frame item_011

- frame_id: evidence_frame_20260515_307008e2
- source_text: 治疗上给予抗感染（具体不详）治疗后，胸闷气短症状改善不明显
- frame_node_count: 3
- atomizable_node_count: 2
- mapped_assertion_count: 0
- deferred_assertion_count: 0
- degenerate_frame_warnings: 0

```text
└─ treatment_event [9b2d94c6] 治疗上给予抗感染（具体不详）治疗后 {role=local_content}
   └─ clinical_object [fb001218] 胸闷气短症状 {rel=treatment_for; atom=generate_atom_with_inherited_context}
      └─ treatment_response [f0630982] 改善不明显 {rel=response_after; atom=generate_atom_with_inherited_context}
```

### Frame item_012

- frame_id: evidence_frame_20260515_b67681bd
- source_text: 以“间质性肺炎，肺部感染”收住我科
- frame_node_count: 2
- atomizable_node_count: 2
- mapped_assertion_count: 2
- deferred_assertion_count: 0
- degenerate_frame_warnings: 0
- mapped_assertion_ids: clinical_object_assertion_20260515_14d317e8, clinical_object_assertion_20260515_8b8bc0aa

```text
├─ negative_finding [0773087c] 间质性肺炎 {assertions=clinical_object_assertion_20260515_8b8bc0aa; atom=generate_atom; atoms=1}
│  ↳ atom[bcba1d00] 间质性肺炎
└─ negative_finding [2c012155] 肺部感染 {assertions=clinical_object_assertion_20260515_14d317e8; atom=generate_atom; atoms=1}
   ↳ atom[e44e593b] 肺部感染
```

### Frame item_013

- frame_id: evidence_frame_20260515_f2a55086
- source_text: 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化
- frame_node_count: 4
- atomizable_node_count: 4
- mapped_assertion_count: 4
- deferred_assertion_count: 0
- degenerate_frame_warnings: 0
- mapped_assertion_ids: clinical_object_assertion_20260515_08348940, clinical_object_assertion_20260515_2b5feb85, clinical_object_assertion_20260515_72a18be9, clinical_object_assertion_20260515_9fa9fe3b

```text
├─ clinical_object [dc162171] 神志清 {assertions=clinical_object_assertion_20260515_08348940; atom=generate_atom; atoms=1}
│  ↳ atom[f3b6755c] 神志清
├─ clinical_object [d0a27713] 精神可 {assertions=clinical_object_assertion_20260515_72a18be9; atom=generate_atom; atoms=1}
│  ↳ atom[bd848145] 精神可
├─ clinical_object [1d50b1bf] 饮食睡眠、大小便正常 {assertions=clinical_object_assertion_20260515_2b5feb85; atom=generate_atom; atoms=1}
│  ↳ atom[e590bd79] 饮食睡眠、大小便正常
└─ negative_finding [09ca49cc] 体重无明显变化 {assertions=clinical_object_assertion_20260515_9fa9fe3b; atom=generate_atom; atoms=1}
   ↳ atom[6ad12f2c] 体重无明显变化
```


## Evidence Atoms

| evidence_id | evidence_type | clinical_domain | statement | normalized_label | assertion_status | certainty | temporality | source_item_ids | source_attribute_ids | source_span_ids | source_assertion_ids | source_frame_node_ids | context_frame_node_ids | local_content_text | atom_context_text | source_contexts | source_text |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| evidence_20260515_1d1e364c | symptom | respiratory | 主因“间断咳嗽咳痰伴胸闷气短8年，加重2月”入院 | 间断咳嗽 | present | definite | chronic | item_002 | attribute_20260515_54dea621, attribute_20260515_608b40c4 | span_item_002 | clinical_object_assertion_20260515_aac1f548 | evidence_frame_node_20260515_fd952aa5 | evidence_frame_node_20260515_2d1b256e | 间断咳嗽 | 主因“间断咳嗽咳痰伴胸闷气短8年，加重2月”入院 | chief_complaint(section_002) | 主因“间断咳嗽咳痰伴胸闷气短8年，加重2月”入院 |
| evidence_20260515_8d67ca7b | symptom | respiratory | 8年前患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出 | 痰液为黏白色，量少，易咳出 | present | definite | chronic | item_006 | attribute_20260515_c805e07e | span_item_006 | clinical_object_assertion_20260515_ad87e3ec | evidence_frame_node_20260515_ba132417 | evidence_frame_node_20260515_53549a06, evidence_frame_node_20260515_45d0931b | 痰液为黏白色，量少，易咳出 | 8年前患者于8年前无明显诱因出现咳嗽咳痰 | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_fb9de71b | symptom | respiratory | 8年前患者于8年前无明显诱因出现咳嗽咳痰，胸闷 | 胸闷 | present | definite | chronic | item_006 | attribute_20260515_c805e07e | span_item_006 | clinical_object_assertion_20260515_3c9447e2 | evidence_frame_node_20260515_64932bef | evidence_frame_node_20260515_53549a06, evidence_frame_node_20260515_45d0931b | 胸闷 | 8年前患者于8年前无明显诱因出现咳嗽咳痰 | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_9dbc9fa7 | symptom | respiratory | 8年前患者于8年前无明显诱因出现咳嗽咳痰，气短 | 气短 | present | definite | chronic | item_006 | attribute_20260515_c805e07e | span_item_006 | clinical_object_assertion_20260515_9fc3aaba | evidence_frame_node_20260515_189e2c06 | evidence_frame_node_20260515_53549a06, evidence_frame_node_20260515_45d0931b | 气短 | 8年前患者于8年前无明显诱因出现咳嗽咳痰 | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_9188f109 | symptom | respiratory | 8年前患者于8年前无明显诱因出现咳嗽咳痰胸闷，夜间为著 | 夜间为著 | present | definite | chronic | item_006 | attribute_20260515_c805e07e | span_item_006 | clinical_object_assertion_20260515_7f10431b | evidence_frame_node_20260515_6deeb97f | evidence_frame_node_20260515_53549a06, evidence_frame_node_20260515_45d0931b, evidence_frame_node_20260515_64932bef | 夜间为著 | 8年前患者于8年前无明显诱因出现咳嗽咳痰胸闷 | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_6b24c29c | uncertain | respiratory | 8年前患者于8年前无明显诱因出现咳嗽咳痰，发热 | 发热 | absent | definite | chronic | item_006 | attribute_20260515_c805e07e | span_item_006 | clinical_object_assertion_20260515_ab6270e3 | evidence_frame_node_20260515_9a575935 | evidence_frame_node_20260515_53549a06, evidence_frame_node_20260515_45d0931b | 发热 | 8年前患者于8年前无明显诱因出现咳嗽咳痰 | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_0f2bdeb1 | uncertain | respiratory | 8年前患者于8年前无明显诱因出现咳嗽咳痰，寒战 | 寒战 | absent | definite | chronic | item_006 | attribute_20260515_c805e07e | span_item_006 | clinical_object_assertion_20260515_f35aba02 | evidence_frame_node_20260515_5e7dbd3c | evidence_frame_node_20260515_53549a06, evidence_frame_node_20260515_45d0931b | 寒战 | 8年前患者于8年前无明显诱因出现咳嗽咳痰 | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_05203802 | uncertain | respiratory | 8年前患者于8年前无明显诱因出现咳嗽咳痰，胸痛 | 胸痛 | absent | definite | chronic | item_006 | attribute_20260515_c805e07e | span_item_006 | clinical_object_assertion_20260515_65f6c221 | evidence_frame_node_20260515_bff36013 | evidence_frame_node_20260515_53549a06, evidence_frame_node_20260515_45d0931b | 胸痛 | 8年前患者于8年前无明显诱因出现咳嗽咳痰 | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_85a30613 | uncertain | respiratory | 8年前患者于8年前无明显诱因出现咳嗽咳痰，咯血 | 咯血 | absent | definite | chronic | item_006 | attribute_20260515_c805e07e | span_item_006 | clinical_object_assertion_20260515_e015a8a7 | evidence_frame_node_20260515_951eae98 | evidence_frame_node_20260515_53549a06, evidence_frame_node_20260515_45d0931b | 咯血 | 8年前患者于8年前无明显诱因出现咳嗽咳痰 | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_b2642f6f | uncertain | respiratory | 8年前患者于8年前无明显诱因出现咳嗽咳痰，午后低热 | 午后低热 | absent | definite | chronic | item_006 | attribute_20260515_c805e07e | span_item_006 | clinical_object_assertion_20260515_f573965c | evidence_frame_node_20260515_051ee7c9 | evidence_frame_node_20260515_53549a06, evidence_frame_node_20260515_45d0931b | 午后低热 | 8年前患者于8年前无明显诱因出现咳嗽咳痰 | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_8e96c3f1 | uncertain | respiratory | 8年前患者于8年前无明显诱因出现咳嗽咳痰，乏力 | 乏力 | absent | definite | chronic | item_006 | attribute_20260515_c805e07e | span_item_006 | clinical_object_assertion_20260515_4fe0aba2 | evidence_frame_node_20260515_0577d0e2 | evidence_frame_node_20260515_53549a06, evidence_frame_node_20260515_45d0931b | 乏力 | 8年前患者于8年前无明显诱因出现咳嗽咳痰 | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_1f3e1536 | uncertain | respiratory | 8年前患者于8年前无明显诱因出现咳嗽咳痰，盗汗 | 盗汗 | absent | definite | chronic | item_006 | attribute_20260515_c805e07e | span_item_006 | clinical_object_assertion_20260515_75e495f3 | evidence_frame_node_20260515_9e51d032 | evidence_frame_node_20260515_53549a06, evidence_frame_node_20260515_45d0931b | 盗汗 | 8年前患者于8年前无明显诱因出现咳嗽咳痰 | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_783a22a6 | uncertain | respiratory | 8年前患者于8年前无明显诱因出现咳嗽咳痰，恶心 | 恶心 | absent | definite | chronic | item_006 | attribute_20260515_c805e07e | span_item_006 | clinical_object_assertion_20260515_a97f1689 | evidence_frame_node_20260515_9b3e3ba6 | evidence_frame_node_20260515_53549a06, evidence_frame_node_20260515_45d0931b | 恶心 | 8年前患者于8年前无明显诱因出现咳嗽咳痰 | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_916acb6b | uncertain | respiratory | 8年前患者于8年前无明显诱因出现咳嗽咳痰，呕吐 | 呕吐 | absent | definite | chronic | item_006 | attribute_20260515_c805e07e | span_item_006 | clinical_object_assertion_20260515_4faf9002 | evidence_frame_node_20260515_753869d6 | evidence_frame_node_20260515_53549a06, evidence_frame_node_20260515_45d0931b | 呕吐 | 8年前患者于8年前无明显诱因出现咳嗽咳痰 | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_1af0944b | other | respiratory | 8年前患者于8年前无明显诱因出现咳嗽咳痰，未予重视及诊疗 | 未予重视及诊疗 | present | definite | chronic | item_006 | attribute_20260515_c805e07e | span_item_006 | clinical_object_assertion_20260515_96256ea4 | evidence_frame_node_20260515_5fee9d7c | evidence_frame_node_20260515_53549a06, evidence_frame_node_20260515_45d0931b | 未予重视及诊疗 | 8年前患者于8年前无明显诱因出现咳嗽咳痰 | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_9a877fab | symptom | respiratory | 1年前再次出现咳嗽咳痰，痰液为黏白色 | 痰液为黏白色 | present | definite | past | item_007 | attribute_20260515_28e99288 | span_item_007 | clinical_object_assertion_20260515_f00f9644 | evidence_frame_node_20260515_b72613d9 | evidence_frame_node_20260515_51fd87ea, evidence_frame_node_20260515_b43c041c | 痰液为黏白色 | 1年前再次出现咳嗽咳痰 | history_of_present_illness(section_005) | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_ab76d6c7 | uncertain | respiratory | 1年前再次出现咳嗽咳痰，量少 | 量少 | present | definite | past | item_007 | attribute_20260515_28e99288 | span_item_007 | clinical_object_assertion_20260515_dbd504b8 | evidence_frame_node_20260515_aeac6c32 | evidence_frame_node_20260515_51fd87ea, evidence_frame_node_20260515_b43c041c | 量少 | 1年前再次出现咳嗽咳痰 | history_of_present_illness(section_005) | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_78f5d1a3 | uncertain | respiratory | 1年前再次出现咳嗽咳痰，易咳出 | 易咳出 | present | definite | past | item_007 | attribute_20260515_28e99288 | span_item_007 | clinical_object_assertion_20260515_9971f2e8 | evidence_frame_node_20260515_52ab96fc | evidence_frame_node_20260515_51fd87ea, evidence_frame_node_20260515_b43c041c | 易咳出 | 1年前再次出现咳嗽咳痰 | history_of_present_illness(section_005) | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_ff88e1b3 | symptom | respiratory | 1年前再次出现咳嗽咳痰，胸闷气短 | 胸闷气短 | present | definite | past | item_007 | attribute_20260515_28e99288 | span_item_007 | clinical_object_assertion_20260515_e0324454, clinical_object_assertion_20260515_234e50c8 | evidence_frame_node_20260515_a4a07d79 | evidence_frame_node_20260515_51fd87ea, evidence_frame_node_20260515_b43c041c | 胸闷气短 | 1年前再次出现咳嗽咳痰 | history_of_present_illness(section_005) | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_dce4839f | symptom | respiratory | 1年前再次出现咳嗽咳痰胸闷气短，活动后明显 | 活动后明显 | present | definite | past | item_007 | attribute_20260515_28e99288 | span_item_007 | clinical_object_assertion_20260515_01cc76d8 | evidence_frame_node_20260515_adc45390 | evidence_frame_node_20260515_51fd87ea, evidence_frame_node_20260515_b43c041c, evidence_frame_node_20260515_a4a07d79 | 活动后明显 | 1年前再次出现咳嗽咳痰胸闷气短 | history_of_present_illness(section_005) | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_b183a78d | treatment | treatment | 1年前，于当地诊所输液1周余（具体不详） | 于当地诊所输液1周余（具体不详） | present | uncertain | past | item_007 | attribute_20260515_17d18ce5, attribute_20260515_28e99288 | span_item_007 | clinical_object_assertion_20260515_5e981f3e | evidence_frame_node_20260515_fc40269a | evidence_frame_node_20260515_51fd87ea | 于当地诊所输液1周余（具体不详） | 1年前 | history_of_present_illness(section_005) | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_1398545c | treatment_response | treatment | 于当地诊所输液1周余（具体不详）1年前，咳嗽咳痰、胸闷气短有所改善 | 咳嗽咳痰、胸闷气短有所改善 | present | definite | past | item_007 | attribute_20260515_17d18ce5, attribute_20260515_28e99288 | span_item_007 | clinical_object_assertion_20260515_b07dc424 | evidence_frame_node_20260515_b3d0e230 | evidence_frame_node_20260515_fc40269a, evidence_frame_node_20260515_51fd87ea | 咳嗽咳痰、胸闷气短有所改善 | 于当地诊所输液1周余（具体不详）1年前 | history_of_present_illness(section_005) | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_3aeaf159 | symptom | respiratory | 2月前无明显诱因再次出现咳嗽咳痰 | 2月前无明显诱因再次出现咳嗽咳痰 | present | definite | recent_worsening | item_008 | attribute_20260515_5dbb4227 | span_item_008 | clinical_object_assertion_20260515_0df4c9d5, clinical_object_assertion_20260515_a762ce27 | evidence_frame_node_20260515_42e2a8df |  | 2月前无明显诱因再次出现咳嗽咳痰 |  | history_of_present_illness(section_005) | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_ab012d49 | symptom | respiratory | 2月前无明显诱因再次出现咳嗽咳痰，胸闷 | 胸闷 | present | definite | recent_worsening | item_008 | attribute_20260515_5dbb4227 | span_item_008 | clinical_object_assertion_20260515_5ff446b3 | evidence_frame_node_20260515_b0fb64cb | evidence_frame_node_20260515_42e2a8df | 胸闷 | 2月前无明显诱因再次出现咳嗽咳痰 | history_of_present_illness(section_005) | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_2f0c2c0a | symptom | respiratory | 2月前无明显诱因再次出现咳嗽咳痰，气短 | 气短 | present | definite | recent_worsening | item_008 | attribute_20260515_5dbb4227 | span_item_008 | clinical_object_assertion_20260515_926a1fee | evidence_frame_node_20260515_3bc34217 | evidence_frame_node_20260515_42e2a8df | 气短 | 2月前无明显诱因再次出现咳嗽咳痰 | history_of_present_illness(section_005) | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_b2e77ce4 | imaging_finding | radiology | 2024年6月11日胸部CT示，双肺间质增粗纹理走形杂乱 | 双肺间质增粗纹理走形杂乱 | present | definite | recent_worsening | item_009 | attribute_20260515_afe967e3, attribute_20260515_b430becd | span_item_009 | clinical_object_assertion_20260515_d6e10845 | evidence_frame_node_20260515_23738a0c | evidence_frame_node_20260515_a4aba859 | 双肺间质增粗纹理走形杂乱 | 2024年6月11日胸部CT示 | history_of_present_illness(section_005) | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 |
| evidence_20260515_c545ac0e | imaging_finding | radiology | 2024年6月11日胸部CT示，肺野密度增高 | 肺野密度增高 | present | definite | recent_worsening | item_009 | attribute_20260515_9b3110bc, attribute_20260515_b430becd | span_item_009 | clinical_object_assertion_20260515_9b75d2b1 | evidence_frame_node_20260515_bb68df03 | evidence_frame_node_20260515_a4aba859 | 肺野密度增高 | 2024年6月11日胸部CT示 | history_of_present_illness(section_005) | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 |
| evidence_20260515_8cd44b6e | imaging_finding | radiology | 2024年6月11日胸部CT示，右肺中叶、下叶、左肺舌段条片状实性高密度影 | 右肺中叶、下叶、左肺舌段条片状实性高密度影 | present | definite | recent_worsening | item_009 | attribute_20260515_79480106, attribute_20260515_b430becd | span_item_009 | clinical_object_assertion_20260515_d75cbe10 | evidence_frame_node_20260515_6328f8a4 | evidence_frame_node_20260515_a4aba859 | 右肺中叶、下叶、左肺舌段条片状实性高密度影 | 2024年6月11日胸部CT示 | history_of_present_illness(section_005) | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 |
| evidence_20260515_a7f034e9 | uncertain | radiology | 2024年6月11日胸部CT示右肺中叶、下叶、左肺舌段条片状实性高密度影，右肺中叶、下叶病灶边缘模糊 | 右肺中叶、下叶病灶边缘模糊 | present | definite | recent_worsening | item_009 | attribute_20260515_23c26ccb, attribute_20260515_b430becd, attribute_20260515_79480106 | span_item_009 | clinical_object_assertion_20260515_e4a9b2e7 | evidence_frame_node_20260515_9828faaf | evidence_frame_node_20260515_a4aba859, evidence_frame_node_20260515_6328f8a4 | 右肺中叶、下叶病灶边缘模糊 | 2024年6月11日胸部CT示右肺中叶、下叶、左肺舌段条片状实性高密度影 | history_of_present_illness(section_005) | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 |
| evidence_20260515_3df040a7 | diagnosis_history | infectious_disease | 肺部感染 | 肺部感染 | present | possible | recent_worsening | item_010 |  | span_item_010 | clinical_object_assertion_20260515_c6f1b430 | evidence_frame_node_20260515_6fccf711 |  | 肺部感染 |  | history_of_present_illness(section_005) | 考虑为“肺部感染” |
| evidence_20260515_bcba1d00 | diagnosis_history | respiratory | 间质性肺炎 | 间质性肺炎 | absent | definite | current | item_012 |  | span_item_012 | clinical_object_assertion_20260515_8b8bc0aa | evidence_frame_node_20260515_0773087c |  | 间质性肺炎 |  | history_of_present_illness(section_005) | 以“间质性肺炎，肺部感染”收住我科 |
| evidence_20260515_e44e593b | diagnosis_history | infectious_disease | 肺部感染 | 肺部感染 | absent | definite | current | item_012 |  | span_item_012 | clinical_object_assertion_20260515_14d317e8 | evidence_frame_node_20260515_2c012155 |  | 肺部感染 |  | history_of_present_illness(section_005) | 以“间质性肺炎，肺部感染”收住我科 |
| evidence_20260515_f3b6755c | sign | general | 神志清 | 神志清 | present | definite | current | item_013 |  | span_item_013 | clinical_object_assertion_20260515_08348940 | evidence_frame_node_20260515_dc162171 |  | 神志清 |  | history_of_present_illness(section_005) | 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 |
| evidence_20260515_bd848145 | sign | general | 精神可 | 精神可 | present | definite | current | item_013 |  | span_item_013 | clinical_object_assertion_20260515_72a18be9 | evidence_frame_node_20260515_d0a27713 |  | 精神可 |  | history_of_present_illness(section_005) | 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 |
| evidence_20260515_e590bd79 | sign | general | 饮食睡眠、大小便正常 | 饮食睡眠、大小便正常 | present | definite | current | item_013 |  | span_item_013 | clinical_object_assertion_20260515_2b5feb85 | evidence_frame_node_20260515_1d50b1bf |  | 饮食睡眠、大小便正常 |  | history_of_present_illness(section_005) | 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 |
| evidence_20260515_6ad12f2c | uncertain | general | 体重无明显变化 | 体重无明显变化 | absent | definite | current | item_013 |  | span_item_013 | clinical_object_assertion_20260515_9fa9fe3b | evidence_frame_node_20260515_09ca49cc |  | 体重无明显变化 |  | history_of_present_illness(section_005) | 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 |

## Boundary Note

Multi-round support here means the same case_id is reused across rounds with increasing input_order and parent_input_id. Evidence Atomizer remains stateless per round. Cross-round merging, belief revision, and update management belong to later phases.
