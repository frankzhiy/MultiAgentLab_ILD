# Phase 1 Trace Round 001

- Selected file: data/01.txt
- case_id: case_20260515_1ef422a9
- input_id: input_20260515_220232a8
- parent_input_id: None
- input_order: 1
- case_structuring_result_id: case_structuring_result_20260515_b3e778a9
- attribute_extraction_result_id: attribute_extraction_result_20260515_f4f9e290
- atomization_result_id: atomization_result_20260515_b67bf980
- case_structurer_duration: 1 min 22.7 s
- attribute_extractor_duration: 43.02 s
- evidence_atomizer_duration: 9 min 30.9 s
- round_duration: 11 min 36.6 s

## Structuring Summary

- ready_for_attribute_extraction: True
- clinical_sections: 5
- structured_items: 13

## Case Structurer Results

### Stage Context

| stage_id | stage_order | stage_type | relation_to_previous_stage | previous_stage_id | is_initial_stage | classification_confidence | classification_basis |
| --- | --- | --- | --- | --- | --- | --- | --- |
| stage_20260515_4db1a934 | 1 | initial_input | new_case_start |  | True | high | First input in the case providing initial patient history and admission details. |

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
| item_003 | 3 | section_003 | uncertain | 一般健康状况：良好 | current | definite | present | medium | span_item_003 | 一般健康状况：良好 |
| item_004 | 4 | section_004 | comorbidity | 既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史 | chronic | definite | present | high | span_item_004 | 既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史 |
| item_005 | 5 | section_004 | procedure | 40年前左下肢骨折固定术 | past | definite | present | high | span_item_005 | 40年前左下肢骨折固定术 |
| item_006 | 6 | section_005 | symptom | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 | chronic | definite | present | high | span_item_006 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| item_007 | 7 | section_005 | symptom | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 | past | definite | present | high | span_item_007 | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| item_008 | 8 | section_005 | symptom | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适，遂就诊于当地医院 | recent_worsening | definite | present | high | span_item_008 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适，遂就诊于当地医院 |
| item_009 | 9 | section_005 | imaging_finding | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 | recent_worsening | definite | present | high | span_item_009 | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 |
| item_010 | 10 | section_005 | diagnosis_history | 考虑为“肺部感染” | recent_worsening | possible | present | medium | span_item_010 | 考虑为“肺部感染” |
| item_011 | 11 | section_005 | treatment | 治疗上给予抗感染（具体不详）治疗后，胸闷气短症状改善不明显 | recent_worsening | definite | present | high | span_item_011 | 治疗上给予抗感染（具体不详）治疗后，胸闷气短症状改善不明显 |
| item_012 | 12 | section_005 | diagnosis_history | 请我科医师会诊后，以“间质性肺炎，肺部感染”收住我科 | current | definite | present | high | span_item_012 | 请我科医师会诊后，以“间质性肺炎，肺部感染”收住我科 |
| item_013 | 13 | section_005 | sign | 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 | current | definite | present | high | span_item_013 | 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 |

### Structuring Warnings

| severity | code | message | related_object_id |
| --- | --- | --- | --- |
| No structuring warnings produced. |  |  |  |

## Attribute Extraction Summary

- attribute_extraction_result_id: attribute_extraction_result_20260515_f4f9e290
- clinical_attributes: 27
- ready_for_evidence_atomization: True
- validation_accepted: True

## Attribute Extractor Validation Issues

No validation issues.

## Clinical Attributes

| attribute_id | source_item_id | attribute_role | attribute_scope | span_text | applies_to_text | context_text | normalized_value | normalized_unit | normalized_text | extraction_confidence | source_span_id |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| attribute_20260515_839ac65a | item_001 | sex | item | 女 | 患者***,女,77岁 | 患者***,女,77岁 |  |  | female | high | span_attr_001 |
| attribute_20260515_72d3e886 | item_001 | age | item | 77岁 | 患者***,女,77岁 | 患者***,女,77岁 | 77 | year | 77岁 | high | span_attr_002 |
| attribute_20260515_774509fb | item_002 | symptom_duration | local_phrase | 8年 | 间断咳嗽咳痰伴胸闷气短8年 | 主因“间断咳嗽咳痰伴胸闷气短8年，加重2月”入院 | 8 | year | 8年 | high | span_attr_003 |
| attribute_20260515_a64125bd | item_002 | worsening_interval | local_phrase | 加重2月 | 加重2月 | 主因“间断咳嗽咳痰伴胸闷气短8年，加重2月”入院 | 2 | month | 2月 | high | span_attr_004 |
| attribute_20260515_18d4a4c6 | item_004 | disease_history_duration | local_phrase | 8年 | 既往高血压8年 | 既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史 | 8 | year | 8年 | high | span_attr_005 |
| attribute_20260515_2092c707 | item_004 | medication_dose | local_phrase | 2片/次 | 沙库巴曲缬沙坦片 2片/次 | 既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史 | 2 | 片/次 | 2片/次 | high | span_attr_006 |
| attribute_20260515_47372265 | item_004 | medication_frequency | local_phrase | 1次/日 | 1次/日 口服 | 既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史 | 1 | 次/日 | 1次/日 | high | span_attr_007 |
| attribute_20260515_67ba6756 | item_004 | medication_route | local_phrase | 口服 | 1次/日 口服 | 既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史 |  |  | 口服 | high | span_attr_008 |
| attribute_20260515_09941ea8 | item_005 | onset_time | local_phrase | 40年前 | 40年前左下肢骨折固定术 | 40年前左下肢骨折固定术 | 40 | 年 | 40年前 | high | span_attr_009 |
| attribute_20260515_44d93664 | item_006 | onset_time | local_phrase | 8年前 | 患者于8年前无明显诱因出现咳嗽咳痰 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 | 8 | 年 | 8年前 | high | span_attr_010 |
| attribute_20260515_da58c084 | item_006 | qualitative_result | local_phrase | 黏白色 | 痰液为黏白色 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |  |  | 黏白色 | high | span_attr_011 |
| attribute_20260515_24fd0d0d | item_006 | qualitative_result | local_phrase | 量少 | 量少 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |  |  | 量少 | high | span_attr_012 |
| attribute_20260515_1d45bad2 | item_006 | other_attribute | local_phrase | 夜间为著 | 夜间为著 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |  |  | 夜间为著 | medium | span_attr_013 |
| attribute_20260515_c0fafd5e | item_007 | onset_time | local_phrase | 1年前 | 1年前新冠病毒感染后再次出现咳嗽咳痰 | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 | 1 | 年 | 1年前 | high | span_attr_014 |
| attribute_20260515_e8f436b0 | item_007 | qualitative_result | local_phrase | 黏白色 | 痰液为黏白色 | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |  |  | 黏白色 | high | span_attr_015 |
| attribute_20260515_e3247cfe | item_007 | qualitative_result | local_phrase | 量少 | 量少 | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |  |  | 量少 | high | span_attr_016 |
| attribute_20260515_bb986cf0 | item_007 | other_attribute | local_phrase | 活动后明显 | 活动后明显 | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |  |  | 活动后明显 | medium | span_attr_017 |
| attribute_20260515_028ee26d | item_007 | other_attribute | local_phrase | 1周余 | 输液1周余 | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 | 7 | 天 | 1周余 | medium | span_attr_018 |
| attribute_20260515_ceb30487 | item_008 | onset_time | local_phrase | 2月前 | 2月前无明显诱因再次出现咳嗽咳痰 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适，遂就诊于当地医院 | 2 | 月 | 2月前 | high | span_attr_019 |
| attribute_20260515_b8458eba | item_008 | qualitative_result | local_phrase | 无发热寒战 | 无发热寒战 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适，遂就诊于当地医院 |  |  | 无发热寒战 | high | span_attr_020 |
| attribute_20260515_2243123c | item_008 | qualitative_result | local_phrase | 无胸痛咯血 | 无胸痛咯血 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适，遂就诊于当地医院 |  |  | 无胸痛咯血 | high | span_attr_021 |
| attribute_20260515_76a73321 | item_008 | qualitative_result | local_phrase | 无恶心呕吐等不适 | 无恶心呕吐等不适 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适，遂就诊于当地医院 |  |  | 无恶心呕吐等不适 | high | span_attr_022 |
| attribute_20260515_3f47b10f | item_009 | onset_time | local_phrase | 2024年6月11日 | 2024年6月11日胸部CT示 | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 | 2024-06-11 |  | 2024年6月11日 | high | span_attr_023 |
| attribute_20260515_e8c82932 | item_009 | qualitative_result | local_phrase | 双肺间质增粗纹理走形杂乱 | 双肺间质增粗纹理走形杂乱 | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 |  |  | 双肺间质增粗纹理走形杂乱 | high | span_attr_024 |
| attribute_20260515_48c7f591 | item_009 | qualitative_result | local_phrase | 肺野密度增高 | 肺野密度增高 | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 |  |  | 肺野密度增高 | high | span_attr_025 |
| attribute_20260515_dd5cd253 | item_009 | qualitative_result | coordinated_objects | 右肺中叶、下叶、左肺舌段条片状实性高密度影 | 右肺中叶、下叶、左肺舌段条片状实性高密度影 | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 |  |  | 右肺中叶、下叶、左肺舌段条片状实性高密度影 | high | span_attr_026 |
| attribute_20260515_d9049680 | item_009 | qualitative_result | local_phrase | 右肺中叶、下叶病灶边缘模糊 | 右肺中叶、下叶病灶边缘模糊 | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 |  |  | 右肺中叶、下叶病灶边缘模糊 | high | span_attr_027 |

## Atomization Summary

- atomization_result_id: atomization_result_20260515_b67bf980
- evidence_atoms: 57
- item_to_evidence_links: 13
- deferred_items: 2
- atomization_warnings: 71
- evidence_event_frames: 13
- evidence_event_frame_warnings: 8
- validation_accepted: True

## Evidence Atomizer Validation Issues

| severity | code | message | related_item_id | related_attribute_id | related_evidence_id | related_span_id |
| --- | --- | --- | --- | --- | --- | --- |
| warning | frame_context_not_reflected_in_statement | EvidenceAtom statement may not reflect inherited frame context from its CoverageUnit. [coverage_unit_id=item_007__frame_unit_001] | item_007 |  | evidence_20260515_1bfc4258 |  |
| warning | frame_context_not_reflected_in_statement | EvidenceAtom statement may not reflect inherited frame context from its CoverageUnit. [coverage_unit_id=item_007__frame_unit_002] | item_007 |  | evidence_20260515_7f938872 |  |
| warning | frame_context_not_reflected_in_statement | EvidenceAtom statement may not reflect inherited frame context from its CoverageUnit. [coverage_unit_id=item_007__frame_unit_010] | item_007 |  | evidence_20260515_8ecf3c12 |  |
| warning | frame_context_not_reflected_in_statement | EvidenceAtom statement may not reflect inherited frame context from its CoverageUnit. [coverage_unit_id=item_007__frame_unit_011] | item_007 |  | evidence_20260515_3e014714 |  |
| warning | frame_context_not_reflected_in_statement | EvidenceAtom statement may not reflect inherited frame context from its CoverageUnit. [coverage_unit_id=item_007__frame_unit_012] | item_007 |  | evidence_20260515_259a57f7 |  |
| warning | frame_context_not_reflected_in_statement | EvidenceAtom statement may not reflect inherited frame context from its CoverageUnit. [coverage_unit_id=item_007__frame_unit_013] | item_007 |  | evidence_20260515_31539872 |  |
| warning | present_atom_has_negation_surface | EvidenceAtom statement begins with a negation expression while assertion_status is present. |  |  | evidence_20260515_7aab6972 |  |

## Evidence Event Frames (debug)

| frame_id | source_item_id | assertion_count | mapped_assertion_count | deferred_assertion_count | number_of_nodes | atomizable_node_count | degenerate_frame_warnings | warning_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| evidence_frame_20260515_ad997479 | item_001 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
| evidence_frame_20260515_68c48aac | item_002 | 4 | 4 | 0 | 2 | 0 | 0 | 2 |
| evidence_frame_20260515_870d3a00 | item_003 | 0 | 0 | 0 | 1 | 1 | 0 | 1 |
| evidence_frame_20260515_d7945666 | item_004 | 0 | 0 | 0 | 4 | 4 | 0 | 0 |
| evidence_frame_20260515_a7f045d2 | item_005 | 0 | 0 | 0 | 1 | 1 | 0 | 1 |
| evidence_frame_20260515_c3d19655 | item_006 | 18 | 18 | 0 | 18 | 18 | 0 | 3 |
| evidence_frame_20260515_3fb80d5a | item_007 | 13 | 13 | 0 | 16 | 13 | 0 | 0 |
| evidence_frame_20260515_68e7800e | item_008 | 11 | 11 | 0 | 7 | 7 | 0 | 0 |
| evidence_frame_20260515_b99d5051 | item_009 | 4 | 4 | 0 | 5 | 4 | 0 | 0 |
| evidence_frame_20260515_5050bd14 | item_010 | 1 | 1 | 0 | 1 | 1 | 0 | 0 |
| evidence_frame_20260515_34d48404 | item_011 | 0 | 0 | 0 | 3 | 2 | 0 | 0 |
| evidence_frame_20260515_70caa2fa | item_012 | 2 | 2 | 0 | 2 | 2 | 0 | 0 |
| evidence_frame_20260515_35624c0f | item_013 | 4 | 4 | 0 | 4 | 4 | 0 | 0 |

## Evidence Event Frame Tree Preview

- Tree-first view for reading parent/child frame structure.
- Full report file: evidence_event_frames_tree.md.

### Frame item_001

- frame_id: evidence_frame_20260515_ad997479
- source_text: 患者***,女,77岁
- frame_node_count: 1
- atomizable_node_count: 0
- mapped_assertion_count: 0
- deferred_assertion_count: 0
- degenerate_frame_warnings: 0

```text
└─ uncertain_or_other [2753648d] 患者***,女,77岁 {role=uncertain}
```

### Frame item_002

- frame_id: evidence_frame_20260515_68c48aac
- source_text: 主因“间断咳嗽咳痰伴胸闷气短8年，加重2月”入院
- frame_node_count: 2
- atomizable_node_count: 0
- mapped_assertion_count: 4
- deferred_assertion_count: 0
- degenerate_frame_warnings: 0
- mapped_assertion_ids: clinical_object_assertion_20260515_14aaba1e, clinical_object_assertion_20260515_25f0d60b, clinical_object_assertion_20260515_52890efe, clinical_object_assertion_20260515_766a4be5

```text
└─ symptom_modifier [2820de42] 间断咳嗽咳痰伴胸闷气短8年 {assertions=clinical_object_assertion_20260515_14aaba1e,clinical_object_assertion_20260515_52890efe,clinical_object_assertion_20260515_766a4be5,clinical_object_assertion_20260515_25f0d60b; role=local_content}
   └─ symptom_modifier [db669ef9] 加重2月 {rel=modifier_of; role=modifier_context}
```

### Frame item_003

- frame_id: evidence_frame_20260515_870d3a00
- source_text: 一般健康状况：良好
- frame_node_count: 1
- atomizable_node_count: 1
- mapped_assertion_count: 0
- deferred_assertion_count: 0
- degenerate_frame_warnings: 0

```text
└─ uncertain_or_other [5e707e0e] 一般健康状况：良好 {atom=generate_atom; atoms=1}
   ↳ atom[c3916f74] 一般健康状况：良好
```

### Frame item_004

- frame_id: evidence_frame_20260515_d7945666
- source_text: 既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史
- frame_node_count: 4
- atomizable_node_count: 4
- mapped_assertion_count: 0
- deferred_assertion_count: 0
- degenerate_frame_warnings: 0

```text
├─ clinical_object [59d4759e] 既往高血压8年 {atom=generate_atom; atoms=1}
│  ↳ atom[b771a992] 既往高血压8年
├─ treatment_event [b3f68ded] 口服沙库巴曲缬沙坦片 2片/次 1次/日 口服 {atom=generate_atom_with_inherited_context; atoms=1}
│  ↳ atom[eac82c80] 既往高血压8年，口服沙库巴曲缬沙坦片 2片/次 1次/日 口服
├─ clinical_object [73b1f314] 糖尿病 {atom=generate_atom; atoms=1}
│  ↳ atom[0ea46465] 糖尿病
└─ clinical_object [724c300c] 冠心病病史 {atom=generate_atom; atoms=1}
   ↳ atom[36ca7ee9] 冠心病病史
```

### Frame item_005

- frame_id: evidence_frame_20260515_a7f045d2
- source_text: 40年前左下肢骨折固定术
- frame_node_count: 1
- atomizable_node_count: 1
- mapped_assertion_count: 0
- deferred_assertion_count: 0
- degenerate_frame_warnings: 0

```text
└─ uncertain_or_other [b0d6c7a1] 40年前左下肢骨折固定术 {atom=generate_atom; atoms=1}
   ↳ atom[488a43b7] 40年前左下肢骨折固定术
```

### Frame item_006

- frame_id: evidence_frame_20260515_c3d19655
- source_text: 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗
- frame_node_count: 18
- atomizable_node_count: 18
- mapped_assertion_count: 18
- deferred_assertion_count: 0
- degenerate_frame_warnings: 0
- mapped_assertion_ids: clinical_object_assertion_20260515_0263e156, clinical_object_assertion_20260515_0d7031e5, clinical_object_assertion_20260515_12f36bad, clinical_object_assertion_20260515_29f9e734, clinical_object_assertion_20260515_55d1cbcb, clinical_object_assertion_20260515_5957d2c1, clinical_object_assertion_20260515_7bdb34cc, clinical_object_assertion_20260515_82505ef4, clinical_object_assertion_20260515_9b3e53e7, clinical_object_assertion_20260515_b76eda22, clinical_object_assertion_20260515_bbbbbf42, clinical_object_assertion_20260515_c2215fa4, clinical_object_assertion_20260515_c963fd4c, clinical_object_assertion_20260515_cae7de18, clinical_object_assertion_20260515_d10e831e, clinical_object_assertion_20260515_d7883f47, clinical_object_assertion_20260515_e5cb1377, clinical_object_assertion_20260515_ffa812f2

```text
├─ clinical_object [3a24ddc6] 咳嗽 {assertions=clinical_object_assertion_20260515_9b3e53e7; atom=generate_atom_with_inherited_context; atoms=1}
│  ↳ atom[70d2970f] 咳嗽
├─ clinical_object [390c50b0] 咳痰 {assertions=clinical_object_assertion_20260515_12f36bad; atom=generate_atom_with_inherited_context; atoms=1}
│  ↳ atom[75b5c817] 咳痰
├─ clinical_object [b50bb754] 痰液为黏白色 {assertions=clinical_object_assertion_20260515_0263e156; atom=generate_atom_with_inherited_context; atoms=1}
│  ↳ atom[c7406dd4] 痰液为黏白色
├─ clinical_object [b615c02a] 量少 {assertions=clinical_object_assertion_20260515_c2215fa4; atom=generate_atom_with_inherited_context; atoms=1}
│  ↳ atom[d0b00144] 量少
├─ clinical_object [0fca6b45] 易咳出 {assertions=clinical_object_assertion_20260515_bbbbbf42; atom=generate_atom_with_inherited_context; atoms=1}
│  ↳ atom[c3803813] 易咳出
├─ clinical_object [364ddc44] 胸闷 {assertions=clinical_object_assertion_20260515_cae7de18; atom=generate_atom_with_inherited_context; atoms=1}
│  ↳ atom[bc76e2f5] 胸闷
├─ clinical_object [4b005a8e] 气短 {assertions=clinical_object_assertion_20260515_0d7031e5; atom=generate_atom_with_inherited_context; atoms=1}
│  ↳ atom[3860f608] 气短
├─ clinical_object [c5f81996] 夜间为著 {assertions=clinical_object_assertion_20260515_d10e831e; atom=generate_atom_with_inherited_context; atoms=1}
│  ↳ atom[a1a33732] 夜间为著
├─ negative_finding [6e287698] 发热 {assertions=clinical_object_assertion_20260515_5957d2c1; atom=generate_atom_with_inherited_context; atoms=1}
│  ↳ atom[6101b648] 无发热
├─ negative_finding [fd6fbafe] 寒战 {assertions=clinical_object_assertion_20260515_d7883f47; atom=generate_atom_with_inherited_context; atoms=1}
│  ↳ atom[20fa4256] 无寒战
├─ negative_finding [2e94c05c] 胸痛 {assertions=clinical_object_assertion_20260515_55d1cbcb; atom=generate_atom_with_inherited_context; atoms=1}
│  ↳ atom[ddab4f41] 无胸痛
├─ negative_finding [a1d45411] 咯血 {assertions=clinical_object_assertion_20260515_82505ef4; atom=generate_atom_with_inherited_context; atoms=1}
│  ↳ atom[13758846] 无咯血
├─ negative_finding [69f4d555] 午后低热 {assertions=clinical_object_assertion_20260515_b76eda22; atom=generate_atom_with_inherited_context; atoms=1}
│  ↳ atom[79a654ef] 无午后低热
├─ negative_finding [34c6976c] 乏力 {assertions=clinical_object_assertion_20260515_c963fd4c; atom=generate_atom_with_inherited_context; atoms=1}
│  ↳ atom[8e3ce9df] 无乏力
├─ negative_finding [7c4783bb] 盗汗 {assertions=clinical_object_assertion_20260515_7bdb34cc; atom=generate_atom_with_inherited_context; atoms=1}
│  ↳ atom[8aecb875] 无盗汗
├─ negative_finding [2a6abbe0] 恶心 {assertions=clinical_object_assertion_20260515_29f9e734; atom=generate_atom_with_inherited_context; atoms=1}
│  ↳ atom[60962db0] 无恶心
├─ negative_finding [c54729f3] 呕吐 {assertions=clinical_object_assertion_20260515_e5cb1377; atom=generate_atom_with_inherited_context; atoms=1}
│  ↳ atom[98a74656] 无呕吐
└─ management_event [7d4bfd56] 未予重视及诊疗 {assertions=clinical_object_assertion_20260515_ffa812f2; atom=generate_atom_with_inherited_context; atoms=1}
   ↳ atom[7aab6972] 未予重视及诊疗
```

### Frame item_007

- frame_id: evidence_frame_20260515_3fb80d5a
- source_text: 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善
- frame_node_count: 16
- atomizable_node_count: 13
- mapped_assertion_count: 13
- deferred_assertion_count: 0
- degenerate_frame_warnings: 0
- mapped_assertion_ids: clinical_object_assertion_20260515_02d22bf6, clinical_object_assertion_20260515_1971c8f9, clinical_object_assertion_20260515_1cd4b196, clinical_object_assertion_20260515_414b3672, clinical_object_assertion_20260515_55d36ac8, clinical_object_assertion_20260515_56da972e, clinical_object_assertion_20260515_6765f58e, clinical_object_assertion_20260515_6d7072e3, clinical_object_assertion_20260515_b583d1c9, clinical_object_assertion_20260515_c232d48f, clinical_object_assertion_20260515_c9fa265f, clinical_object_assertion_20260515_d8ece1c3, clinical_object_assertion_20260515_dad45d08

```text
├─ temporal_context [a03f7c02] 1年前 {role=local_content; context_for=8}
│  ↳ context_for_atoms: a6e1a2ee, 60f8aa66, 3d87ba84, b98ba9e3, dcdc5890 ...
│  └─ main_event [3b5e2d22] 1年前新冠病毒感染后再次出现咳嗽咳痰 {rel=temporal_context_of; assertions=clinical_object_assertion_20260515_6d7072e3,clinical_object_assertion_20260515_414b3672; role=local_content; context_for=8}
│     ↳ context_for_atoms: a6e1a2ee, 60f8aa66, 3d87ba84, b98ba9e3, dcdc5890 ...
│     ├─ clinical_object [0fc86762] 咳嗽 {rel=occurrence_of; assertions=clinical_object_assertion_20260515_6d7072e3; atom=generate_atom_with_inherited_context; atoms=1}
│     │  ↳ atom[1bfc4258] 咳嗽
│     ├─ clinical_object [e2f5bfad] 咳痰 {rel=occurrence_of; assertions=clinical_object_assertion_20260515_414b3672; atom=generate_atom_with_inherited_context; atoms=1}
│     │  ↳ atom[7f938872] 咳痰
│     │  ├─ object_property [38b95679] 痰液为黏白色 {rel=property_of; assertions=clinical_object_assertion_20260515_1971c8f9; atom=generate_atom_with_inherited_context; atoms=1}
│     │  │  ↳ atom[60f8aa66] 1年前1年前新冠病毒感染后再次出现咳嗽咳痰咳痰，痰液为黏白色
│     │  ├─ object_property [d4a224eb] 量少 {rel=property_of; assertions=clinical_object_assertion_20260515_56da972e; atom=generate_atom_with_inherited_context; atoms=1}
│     │  │  ↳ atom[3d87ba84] 1年前1年前新冠病毒感染后再次出现咳嗽咳痰咳痰，量少
│     │  └─ object_property [cc62e55e] 易咳出 {rel=property_of; assertions=clinical_object_assertion_20260515_c9fa265f; atom=generate_atom_with_inherited_context; atoms=1}
│     │     ↳ atom[a6e1a2ee] 1年前1年前新冠病毒感染后再次出现咳嗽咳痰咳痰，易咳出
│     ├─ clinical_object [5454b206] 胸闷 {rel=occurrence_of; assertions=clinical_object_assertion_20260515_b583d1c9; atom=generate_atom_with_inherited_context; atoms=1}
│     │  ↳ atom[c85b4fea] 1年前1年前新冠病毒感染后再次出现咳嗽咳痰，胸闷
│     │  └─ symptom_modifier [5ecc03dc] 活动后明显 {rel=modifier_of; assertions=clinical_object_assertion_20260515_02d22bf6; atom=generate_group_modifier_atom; atoms=1}
│     │     ↳ atom[b98ba9e3] 1年前1年前新冠病毒感染后再次出现咳嗽咳痰胸闷，活动后明显
│     └─ clinical_object [c0811201] 气短 {rel=occurrence_of; assertions=clinical_object_assertion_20260515_d8ece1c3; atom=generate_atom_with_inherited_context; atoms=1}
│        ↳ atom[dcdc5890] 1年前1年前新冠病毒感染后再次出现咳嗽咳痰，气短
└─ treatment_event [0ed8cda0] 于当地诊所输液1周余（具体不详） {assertions=clinical_object_assertion_20260515_c232d48f; atom=generate_atom; atoms=1}
   ↳ atom[791589ff] 于当地诊所输液1周余（具体不详）
   └─ main_event [d52b1c0d] 感咳嗽咳痰、胸闷气短有所改善 {rel=response_after; assertions=clinical_object_assertion_20260515_55d36ac8,clinical_object_assertion_20260515_dad45d08,clinical_object_assertion_20260515_6765f58e,clinical_object_assertion_20260515_1cd4b196; role=local_content; context_for=4}
      ↳ context_for_atoms: 8ecf3c12, 3e014714, 31539872, 259a57f7
      ├─ clinical_object [2d22ded4] 咳嗽 {rel=occurrence_of; assertions=clinical_object_assertion_20260515_55d36ac8; atom=generate_atom_with_inherited_context; atoms=1}
      │  ↳ atom[8ecf3c12] 咳嗽
      ├─ clinical_object [c33097c8] 咳痰 {rel=occurrence_of; assertions=clinical_object_assertion_20260515_dad45d08; atom=generate_atom_with_inherited_context; atoms=1}
      │  ↳ atom[3e014714] 咳痰
      ├─ clinical_object [f62b9705] 胸闷 {rel=occurrence_of; assertions=clinical_object_assertion_20260515_6765f58e; atom=generate_atom_with_inherited_context; atoms=1}
      │  ↳ atom[259a57f7] 胸闷
      └─ clinical_object [a9460a58] 气短 {rel=occurrence_of; assertions=clinical_object_assertion_20260515_1cd4b196; atom=generate_atom_with_inherited_context; atoms=1}
         ↳ atom[31539872] 气短
```

### Frame item_008

- frame_id: evidence_frame_20260515_68e7800e
- source_text: 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适，遂就诊于当地医院
- frame_node_count: 7
- atomizable_node_count: 7
- mapped_assertion_count: 11
- deferred_assertion_count: 0
- degenerate_frame_warnings: 0
- mapped_assertion_ids: clinical_object_assertion_20260515_0fd4935d, clinical_object_assertion_20260515_1544fdb3, clinical_object_assertion_20260515_174bdc63, clinical_object_assertion_20260515_2a84ed69, clinical_object_assertion_20260515_5aefb72e, clinical_object_assertion_20260515_69f21dc7, clinical_object_assertion_20260515_826a5935, clinical_object_assertion_20260515_aab360b4, clinical_object_assertion_20260515_c6e775a8, clinical_object_assertion_20260515_c8dfbc2b, clinical_object_assertion_20260515_e4db62b0

```text
├─ main_event [3a21767e] 2月前无明显诱因再次出现咳嗽咳痰 {assertions=clinical_object_assertion_20260515_e4db62b0,clinical_object_assertion_20260515_826a5935; atom=generate_atom; atoms=1}
│  ↳ atom[08b0c345] 2月前无明显诱因再次出现咳嗽咳痰
│  ├─ clinical_object [ba1ca8d8] 胸闷 {rel=associated_with; assertions=clinical_object_assertion_20260515_c8dfbc2b; atom=generate_atom_with_inherited_context; atoms=1}
│  │  ↳ atom[01c655b1] 2月前无明显诱因再次出现咳嗽咳痰，胸闷
│  └─ clinical_object [7632404f] 气短 {rel=associated_with; assertions=clinical_object_assertion_20260515_c6e775a8; atom=generate_atom_with_inherited_context; atoms=1}
│     ↳ atom[93c57a12] 2月前无明显诱因再次出现咳嗽咳痰，气短
├─ negative_finding [4096451c] 无发热寒战 {assertions=clinical_object_assertion_20260515_69f21dc7,clinical_object_assertion_20260515_2a84ed69; atom=generate_atom; atoms=1}
│  ↳ atom[375c8a13] 无发热寒战
├─ negative_finding [85de0e9a] 无胸痛咯血 {assertions=clinical_object_assertion_20260515_aab360b4,clinical_object_assertion_20260515_174bdc63; atom=generate_atom; atoms=1}
│  ↳ atom[0edc2df3] 无胸痛咯血
├─ negative_finding [011e3059] 无恶心呕吐等不适 {assertions=clinical_object_assertion_20260515_1544fdb3,clinical_object_assertion_20260515_0fd4935d; atom=generate_atom; atoms=1}
│  ↳ atom[5572b41b] 无恶心呕吐等不适
└─ management_event [9c420e83] 遂就诊于当地医院 {assertions=clinical_object_assertion_20260515_5aefb72e; atom=generate_atom; atoms=1}
   ↳ atom[77fff507] 遂就诊于当地医院
```

### Frame item_009

- frame_id: evidence_frame_20260515_b99d5051
- source_text: 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊
- frame_node_count: 5
- atomizable_node_count: 4
- mapped_assertion_count: 4
- deferred_assertion_count: 0
- degenerate_frame_warnings: 0
- mapped_assertion_ids: clinical_object_assertion_20260515_5fe45635, clinical_object_assertion_20260515_7adf509b, clinical_object_assertion_20260515_d5aec0f8, clinical_object_assertion_20260515_e71af2f0

```text
└─ temporal_context [3bd2b85b] 2024年6月11日胸部CT示 {role=local_content; context_for=4}
   ↳ context_for_atoms: 7099cb2f, dcb4c62f, 8870f368, dd8cea53
   ├─ clinical_object [2494c197] 双肺间质增粗纹理走形杂乱 {rel=temporal_context_of; assertions=clinical_object_assertion_20260515_d5aec0f8; atom=generate_atom_with_inherited_context; atoms=1}
   │  ↳ atom[dcb4c62f] 2024年6月11日胸部CT示，双肺间质增粗纹理走形杂乱
   ├─ clinical_object [db888672] 肺野密度增高 {rel=temporal_context_of; assertions=clinical_object_assertion_20260515_5fe45635; atom=generate_atom_with_inherited_context; atoms=1}
   │  ↳ atom[dd8cea53] 2024年6月11日胸部CT示，肺野密度增高
   └─ clinical_object [8083cb81] 右肺中叶、下叶、左肺舌段条片状实性高密度影 {rel=temporal_context_of; assertions=clinical_object_assertion_20260515_7adf509b; atom=generate_atom_with_inherited_context; atoms=1}
      ↳ atom[8870f368] 2024年6月11日胸部CT示，右肺中叶、下叶、左肺舌段条片状实性高密度影
      └─ object_property [a24a3e26] 右肺中叶、下叶病灶边缘模糊 {rel=property_of; assertions=clinical_object_assertion_20260515_e71af2f0; atom=generate_atom_with_inherited_context; atoms=1}
         ↳ atom[7099cb2f] 2024年6月11日胸部CT示右肺中叶、下叶、左肺舌段条片状实性高密度影，右肺中叶、下叶病灶边缘模糊
```

### Frame item_010

- frame_id: evidence_frame_20260515_5050bd14
- source_text: 考虑为“肺部感染”
- frame_node_count: 1
- atomizable_node_count: 1
- mapped_assertion_count: 1
- deferred_assertion_count: 0
- degenerate_frame_warnings: 0
- mapped_assertion_ids: clinical_object_assertion_20260515_84bdeb49

```text
└─ clinical_object [446ea985] 肺部感染 {assertions=clinical_object_assertion_20260515_84bdeb49; atom=generate_atom; atoms=1}
   ↳ atom[633500f2] 肺部感染
```

### Frame item_011

- frame_id: evidence_frame_20260515_34d48404
- source_text: 治疗上给予抗感染（具体不详）治疗后，胸闷气短症状改善不明显
- frame_node_count: 3
- atomizable_node_count: 2
- mapped_assertion_count: 0
- deferred_assertion_count: 0
- degenerate_frame_warnings: 0

```text
└─ treatment_event [cf2a558a] 治疗上给予抗感染（具体不详）治疗后 {atom=generate_atom; atoms=1}
   ↳ atom[78c370bf] 治疗上给予抗感染（具体不详）治疗后
   └─ treatment_response [e332588c] 改善不明显 {rel=response_after; atom=generate_atom_with_inherited_context; atoms=1}
      ↳ atom[7d67d714] 治疗上给予抗感染（具体不详）治疗后，改善不明显
      └─ clinical_object [deefcf85] 胸闷气短症状 {rel=property_of; role=local_content}
```

### Frame item_012

- frame_id: evidence_frame_20260515_70caa2fa
- source_text: 请我科医师会诊后，以“间质性肺炎，肺部感染”收住我科
- frame_node_count: 2
- atomizable_node_count: 2
- mapped_assertion_count: 2
- deferred_assertion_count: 0
- degenerate_frame_warnings: 0
- mapped_assertion_ids: clinical_object_assertion_20260515_5ce11770, clinical_object_assertion_20260515_5f77ab57

```text
├─ clinical_object [195aaf43] 间质性肺炎 {assertions=clinical_object_assertion_20260515_5f77ab57; atom=generate_atom; atoms=1}
│  ↳ atom[0c016146] 间质性肺炎
└─ clinical_object [c78265ab] 肺部感染 {assertions=clinical_object_assertion_20260515_5ce11770; atom=generate_atom; atoms=1}
   ↳ atom[0b002773] 肺部感染
```

### Frame item_013

- frame_id: evidence_frame_20260515_35624c0f
- source_text: 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化
- frame_node_count: 4
- atomizable_node_count: 4
- mapped_assertion_count: 4
- deferred_assertion_count: 0
- degenerate_frame_warnings: 0
- mapped_assertion_ids: clinical_object_assertion_20260515_0af2898e, clinical_object_assertion_20260515_4119e21e, clinical_object_assertion_20260515_9746b5c6, clinical_object_assertion_20260515_d63a471e

```text
├─ clinical_object [001bfae2] 神志清 {assertions=clinical_object_assertion_20260515_0af2898e; atom=generate_atom; atoms=1}
│  ↳ atom[1ff456c2] 神志清
├─ clinical_object [dea497ea] 精神可 {assertions=clinical_object_assertion_20260515_4119e21e; atom=generate_atom; atoms=1}
│  ↳ atom[76241aa2] 精神可
├─ clinical_object [ca1fd9c1] 饮食睡眠、大小便正常 {assertions=clinical_object_assertion_20260515_d63a471e; atom=generate_atom; atoms=1}
│  ↳ atom[71b0974d] 饮食睡眠、大小便正常
└─ negative_finding [8b14e8c4] 体重无明显变化 {assertions=clinical_object_assertion_20260515_9746b5c6; atom=generate_atom; atoms=1}
   ↳ atom[f7abc52e] 无明显变化体重无明显变化
```


## Evidence Atoms

| evidence_id | evidence_type | clinical_domain | statement | normalized_label | assertion_status | certainty | temporality | source_item_ids | source_attribute_ids | source_span_ids | source_assertion_ids | source_frame_node_ids | context_frame_node_ids | local_content_text | atom_context_text | source_contexts | source_text |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| evidence_20260515_c3916f74 | uncertain | general | 一般健康状况：良好 | 一般健康状况：良好 | present | definite | current | item_003 |  | span_item_003 |  | evidence_frame_node_20260515_5e707e0e |  | 一般健康状况：良好 |  | uncertain(section_003) | 一般健康状况：良好 |
| evidence_20260515_b771a992 | comorbidity | general | 既往高血压8年 | 既往高血压8年 | present | definite | chronic | item_004 | attribute_20260515_18d4a4c6 | span_item_004 |  | evidence_frame_node_20260515_59d4759e |  | 既往高血压8年 |  | past_medical_history(section_004) | 既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史 |
| evidence_20260515_eac82c80 | treatment | treatment | 既往高血压8年，口服沙库巴曲缬沙坦片 2片/次 1次/日 口服 | 口服沙库巴曲缬沙坦片 2片/次 1次/日 口服 | present | definite | chronic | item_004 | attribute_20260515_2092c707, attribute_20260515_47372265, attribute_20260515_67ba6756, attribute_20260515_18d4a4c6 | span_item_004 |  | evidence_frame_node_20260515_b3f68ded | evidence_frame_node_20260515_59d4759e | 口服沙库巴曲缬沙坦片 2片/次 1次/日 口服 | 既往高血压8年 | past_medical_history(section_004) | 既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史 |
| evidence_20260515_0ea46465 | comorbidity | general | 糖尿病 | 糖尿病 | present | definite | unknown | item_004 |  | span_item_004 |  | evidence_frame_node_20260515_73b1f314 |  | 糖尿病 |  | past_medical_history(section_004) | 既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史 |
| evidence_20260515_36ca7ee9 | comorbidity | cardiovascular | 冠心病病史 | 冠心病病史 | present | definite | unknown | item_004 |  | span_item_004 |  | evidence_frame_node_20260515_724c300c |  | 冠心病病史 |  | past_medical_history(section_004) | 既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史 |
| evidence_20260515_488a43b7 | procedure | general | 40年前左下肢骨折固定术 | 40年前左下肢骨折固定术 | present | definite | past | item_005 | attribute_20260515_09941ea8 | span_item_005 |  | evidence_frame_node_20260515_b0d6c7a1 |  | 40年前左下肢骨折固定术 |  | past_medical_history(section_004) | 40年前左下肢骨折固定术 |
| evidence_20260515_70d2970f | symptom | respiratory | 咳嗽 | 咳嗽 | present | definite | chronic | item_006 | attribute_20260515_44d93664, attribute_20260515_da58c084, attribute_20260515_24fd0d0d, attribute_20260515_1d45bad2 | span_item_006 | clinical_object_assertion_20260515_9b3e53e7 | evidence_frame_node_20260515_3a24ddc6 |  | 咳嗽 |  | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_75b5c817 | symptom | respiratory | 咳痰 | 咳痰 | present | definite | chronic | item_006 | attribute_20260515_44d93664, attribute_20260515_da58c084, attribute_20260515_24fd0d0d, attribute_20260515_1d45bad2 | span_item_006 | clinical_object_assertion_20260515_12f36bad | evidence_frame_node_20260515_390c50b0 |  | 咳痰 |  | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_c7406dd4 | symptom | respiratory | 痰液为黏白色 | 痰液为黏白色 | present | definite | chronic | item_006 | attribute_20260515_44d93664, attribute_20260515_da58c084, attribute_20260515_24fd0d0d, attribute_20260515_1d45bad2 | span_item_006 | clinical_object_assertion_20260515_0263e156 | evidence_frame_node_20260515_b50bb754 |  | 痰液为黏白色 |  | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_d0b00144 | symptom | respiratory | 量少 | 量少 | present | definite | chronic | item_006 | attribute_20260515_44d93664, attribute_20260515_da58c084, attribute_20260515_24fd0d0d, attribute_20260515_1d45bad2 | span_item_006 | clinical_object_assertion_20260515_c2215fa4 | evidence_frame_node_20260515_b615c02a |  | 量少 |  | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_c3803813 | symptom | respiratory | 易咳出 | 易咳出 | present | definite | chronic | item_006 | attribute_20260515_44d93664, attribute_20260515_da58c084, attribute_20260515_24fd0d0d, attribute_20260515_1d45bad2 | span_item_006 | clinical_object_assertion_20260515_bbbbbf42 | evidence_frame_node_20260515_0fca6b45 |  | 易咳出 |  | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_bc76e2f5 | symptom | respiratory | 胸闷 | 胸闷 | present | definite | chronic | item_006 | attribute_20260515_44d93664, attribute_20260515_da58c084, attribute_20260515_24fd0d0d, attribute_20260515_1d45bad2 | span_item_006 | clinical_object_assertion_20260515_cae7de18 | evidence_frame_node_20260515_364ddc44 |  | 胸闷 |  | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_3860f608 | symptom | respiratory | 气短 | 气短 | present | definite | chronic | item_006 | attribute_20260515_44d93664, attribute_20260515_da58c084, attribute_20260515_24fd0d0d, attribute_20260515_1d45bad2 | span_item_006 | clinical_object_assertion_20260515_0d7031e5 | evidence_frame_node_20260515_4b005a8e |  | 气短 |  | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_a1a33732 | symptom | respiratory | 夜间为著 | 夜间为著 | present | definite | chronic | item_006 | attribute_20260515_44d93664, attribute_20260515_da58c084, attribute_20260515_24fd0d0d, attribute_20260515_1d45bad2 | span_item_006 | clinical_object_assertion_20260515_d10e831e | evidence_frame_node_20260515_c5f81996 |  | 夜间为著 |  | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_6101b648 | uncertain | respiratory | 无发热 | 无发热 | absent | definite | chronic | item_006 | attribute_20260515_44d93664, attribute_20260515_da58c084, attribute_20260515_24fd0d0d, attribute_20260515_1d45bad2 | span_item_006 | clinical_object_assertion_20260515_5957d2c1 | evidence_frame_node_20260515_6e287698 |  | 无发热 |  | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_20fa4256 | uncertain | respiratory | 无寒战 | 无寒战 | absent | definite | chronic | item_006 | attribute_20260515_44d93664, attribute_20260515_da58c084, attribute_20260515_24fd0d0d, attribute_20260515_1d45bad2 | span_item_006 | clinical_object_assertion_20260515_d7883f47 | evidence_frame_node_20260515_fd6fbafe |  | 无寒战 |  | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_ddab4f41 | uncertain | respiratory | 无胸痛 | 无胸痛 | absent | definite | chronic | item_006 | attribute_20260515_44d93664, attribute_20260515_da58c084, attribute_20260515_24fd0d0d, attribute_20260515_1d45bad2 | span_item_006 | clinical_object_assertion_20260515_55d1cbcb | evidence_frame_node_20260515_2e94c05c |  | 无胸痛 |  | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_13758846 | uncertain | respiratory | 无咯血 | 无咯血 | absent | definite | chronic | item_006 | attribute_20260515_44d93664, attribute_20260515_da58c084, attribute_20260515_24fd0d0d, attribute_20260515_1d45bad2 | span_item_006 | clinical_object_assertion_20260515_82505ef4 | evidence_frame_node_20260515_a1d45411 |  | 无咯血 |  | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_79a654ef | uncertain | respiratory | 无午后低热 | 无午后低热 | absent | definite | chronic | item_006 | attribute_20260515_44d93664, attribute_20260515_da58c084, attribute_20260515_24fd0d0d, attribute_20260515_1d45bad2 | span_item_006 | clinical_object_assertion_20260515_b76eda22 | evidence_frame_node_20260515_69f4d555 |  | 无午后低热 |  | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_8e3ce9df | uncertain | general | 无乏力 | 无乏力 | absent | definite | chronic | item_006 | attribute_20260515_44d93664, attribute_20260515_da58c084, attribute_20260515_24fd0d0d, attribute_20260515_1d45bad2 | span_item_006 | clinical_object_assertion_20260515_c963fd4c | evidence_frame_node_20260515_34c6976c |  | 无乏力 |  | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_8aecb875 | uncertain | general | 无盗汗 | 无盗汗 | absent | definite | chronic | item_006 | attribute_20260515_44d93664, attribute_20260515_da58c084, attribute_20260515_24fd0d0d, attribute_20260515_1d45bad2 | span_item_006 | clinical_object_assertion_20260515_7bdb34cc | evidence_frame_node_20260515_7c4783bb |  | 无盗汗 |  | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_60962db0 | uncertain | general | 无恶心 | 无恶心 | absent | definite | chronic | item_006 | attribute_20260515_44d93664, attribute_20260515_da58c084, attribute_20260515_24fd0d0d, attribute_20260515_1d45bad2 | span_item_006 | clinical_object_assertion_20260515_29f9e734 | evidence_frame_node_20260515_2a6abbe0 |  | 无恶心 |  | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_98a74656 | uncertain | general | 无呕吐 | 无呕吐 | absent | definite | chronic | item_006 | attribute_20260515_44d93664, attribute_20260515_da58c084, attribute_20260515_24fd0d0d, attribute_20260515_1d45bad2 | span_item_006 | clinical_object_assertion_20260515_e5cb1377 | evidence_frame_node_20260515_c54729f3 |  | 无呕吐 |  | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_7aab6972 | treatment | treatment | 未予重视及诊疗 | 未予重视及诊疗 | present | definite | chronic | item_006 | attribute_20260515_44d93664, attribute_20260515_da58c084, attribute_20260515_24fd0d0d, attribute_20260515_1d45bad2 | span_item_006 | clinical_object_assertion_20260515_ffa812f2 | evidence_frame_node_20260515_7d4bfd56 |  | 未予重视及诊疗 |  | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_1bfc4258 | symptom | respiratory | 咳嗽 | 咳嗽 | present | definite | past | item_007 | attribute_20260515_c0fafd5e | span_item_007 | clinical_object_assertion_20260515_6d7072e3 | evidence_frame_node_20260515_0fc86762 | evidence_frame_node_20260515_a03f7c02, evidence_frame_node_20260515_3b5e2d22 | 咳嗽 | 1年前1年前新冠病毒感染后再次出现咳嗽咳痰 | history_of_present_illness(section_005) | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_7f938872 | symptom | respiratory | 咳痰 | 咳痰 | present | definite | past | item_007 | attribute_20260515_c0fafd5e | span_item_007 | clinical_object_assertion_20260515_414b3672 | evidence_frame_node_20260515_e2f5bfad | evidence_frame_node_20260515_a03f7c02, evidence_frame_node_20260515_3b5e2d22 | 咳痰 | 1年前1年前新冠病毒感染后再次出现咳嗽咳痰 | history_of_present_illness(section_005) | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_60f8aa66 | symptom | respiratory | 1年前1年前新冠病毒感染后再次出现咳嗽咳痰咳痰，痰液为黏白色 | 痰液为黏白色 | present | definite | past | item_007 | attribute_20260515_e8f436b0, attribute_20260515_c0fafd5e | span_item_007 | clinical_object_assertion_20260515_1971c8f9 | evidence_frame_node_20260515_38b95679 | evidence_frame_node_20260515_a03f7c02, evidence_frame_node_20260515_3b5e2d22, evidence_frame_node_20260515_e2f5bfad | 痰液为黏白色 | 1年前1年前新冠病毒感染后再次出现咳嗽咳痰咳痰 | history_of_present_illness(section_005) | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_3d87ba84 | symptom | respiratory | 1年前1年前新冠病毒感染后再次出现咳嗽咳痰咳痰，量少 | 量少 | present | definite | past | item_007 | attribute_20260515_e3247cfe, attribute_20260515_c0fafd5e | span_item_007 | clinical_object_assertion_20260515_56da972e | evidence_frame_node_20260515_d4a224eb | evidence_frame_node_20260515_a03f7c02, evidence_frame_node_20260515_3b5e2d22, evidence_frame_node_20260515_e2f5bfad | 量少 | 1年前1年前新冠病毒感染后再次出现咳嗽咳痰咳痰 | history_of_present_illness(section_005) | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_a6e1a2ee | symptom | respiratory | 1年前1年前新冠病毒感染后再次出现咳嗽咳痰咳痰，易咳出 | 易咳出 | present | definite | past | item_007 | attribute_20260515_c0fafd5e | span_item_007 | clinical_object_assertion_20260515_c9fa265f | evidence_frame_node_20260515_cc62e55e | evidence_frame_node_20260515_a03f7c02, evidence_frame_node_20260515_3b5e2d22, evidence_frame_node_20260515_e2f5bfad | 易咳出 | 1年前1年前新冠病毒感染后再次出现咳嗽咳痰咳痰 | history_of_present_illness(section_005) | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_c85b4fea | symptom | respiratory | 1年前1年前新冠病毒感染后再次出现咳嗽咳痰，胸闷 | 胸闷 | present | definite | past | item_007 | attribute_20260515_c0fafd5e | span_item_007 | clinical_object_assertion_20260515_b583d1c9 | evidence_frame_node_20260515_5454b206 | evidence_frame_node_20260515_a03f7c02, evidence_frame_node_20260515_3b5e2d22 | 胸闷 | 1年前1年前新冠病毒感染后再次出现咳嗽咳痰 | history_of_present_illness(section_005) | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_dcdc5890 | symptom | respiratory | 1年前1年前新冠病毒感染后再次出现咳嗽咳痰，气短 | 气短 | present | definite | past | item_007 | attribute_20260515_c0fafd5e | span_item_007 | clinical_object_assertion_20260515_d8ece1c3 | evidence_frame_node_20260515_c0811201 | evidence_frame_node_20260515_a03f7c02, evidence_frame_node_20260515_3b5e2d22 | 气短 | 1年前1年前新冠病毒感染后再次出现咳嗽咳痰 | history_of_present_illness(section_005) | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_b98ba9e3 | symptom | respiratory | 1年前1年前新冠病毒感染后再次出现咳嗽咳痰胸闷，活动后明显 | 活动后明显 | present | definite | past | item_007 | attribute_20260515_bb986cf0, attribute_20260515_c0fafd5e | span_item_007 | clinical_object_assertion_20260515_02d22bf6 | evidence_frame_node_20260515_5ecc03dc | evidence_frame_node_20260515_a03f7c02, evidence_frame_node_20260515_3b5e2d22, evidence_frame_node_20260515_5454b206 | 活动后明显 | 1年前1年前新冠病毒感染后再次出现咳嗽咳痰胸闷 | history_of_present_illness(section_005) | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_791589ff | treatment | treatment | 于当地诊所输液1周余（具体不详） | 于当地诊所输液1周余（具体不详） | present | definite | past | item_007 | attribute_20260515_028ee26d | span_item_007 | clinical_object_assertion_20260515_c232d48f | evidence_frame_node_20260515_0ed8cda0 |  | 于当地诊所输液1周余（具体不详） |  | history_of_present_illness(section_005) | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_8ecf3c12 | symptom | respiratory | 咳嗽 | 咳嗽 | present | definite | past | item_007 | attribute_20260515_028ee26d | span_item_007 | clinical_object_assertion_20260515_55d36ac8 | evidence_frame_node_20260515_2d22ded4 | evidence_frame_node_20260515_0ed8cda0, evidence_frame_node_20260515_d52b1c0d | 咳嗽 | 于当地诊所输液1周余（具体不详）感咳嗽咳痰、胸闷气短有所改善 | history_of_present_illness(section_005) | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_3e014714 | symptom | respiratory | 咳痰 | 咳痰 | present | definite | past | item_007 | attribute_20260515_028ee26d | span_item_007 | clinical_object_assertion_20260515_dad45d08 | evidence_frame_node_20260515_c33097c8 | evidence_frame_node_20260515_0ed8cda0, evidence_frame_node_20260515_d52b1c0d | 咳痰 | 于当地诊所输液1周余（具体不详）感咳嗽咳痰、胸闷气短有所改善 | history_of_present_illness(section_005) | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_259a57f7 | symptom | respiratory | 胸闷 | 胸闷 | present | definite | past | item_007 | attribute_20260515_028ee26d | span_item_007 | clinical_object_assertion_20260515_6765f58e | evidence_frame_node_20260515_f62b9705 | evidence_frame_node_20260515_0ed8cda0, evidence_frame_node_20260515_d52b1c0d | 胸闷 | 于当地诊所输液1周余（具体不详）感咳嗽咳痰、胸闷气短有所改善 | history_of_present_illness(section_005) | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_31539872 | symptom | respiratory | 气短 | 气短 | present | definite | past | item_007 | attribute_20260515_028ee26d | span_item_007 | clinical_object_assertion_20260515_1cd4b196 | evidence_frame_node_20260515_a9460a58 | evidence_frame_node_20260515_0ed8cda0, evidence_frame_node_20260515_d52b1c0d | 气短 | 于当地诊所输液1周余（具体不详）感咳嗽咳痰、胸闷气短有所改善 | history_of_present_illness(section_005) | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_08b0c345 | symptom | respiratory | 2月前无明显诱因再次出现咳嗽咳痰 | 2月前无明显诱因再次出现咳嗽咳痰 | present | definite | recent_worsening | item_008 | attribute_20260515_ceb30487 | span_item_008 | clinical_object_assertion_20260515_e4db62b0, clinical_object_assertion_20260515_826a5935 | evidence_frame_node_20260515_3a21767e |  | 2月前无明显诱因再次出现咳嗽咳痰 |  | history_of_present_illness(section_005) | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适，遂就诊于当地医院 |
| evidence_20260515_01c655b1 | symptom | respiratory | 2月前无明显诱因再次出现咳嗽咳痰，胸闷 | 胸闷 | present | definite | recent_worsening | item_008 | attribute_20260515_ceb30487 | span_item_008 | clinical_object_assertion_20260515_c8dfbc2b | evidence_frame_node_20260515_ba1ca8d8 | evidence_frame_node_20260515_3a21767e | 胸闷 | 2月前无明显诱因再次出现咳嗽咳痰 | history_of_present_illness(section_005) | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适，遂就诊于当地医院 |
| evidence_20260515_93c57a12 | symptom | respiratory | 2月前无明显诱因再次出现咳嗽咳痰，气短 | 气短 | present | definite | recent_worsening | item_008 | attribute_20260515_ceb30487 | span_item_008 | clinical_object_assertion_20260515_c6e775a8 | evidence_frame_node_20260515_7632404f | evidence_frame_node_20260515_3a21767e | 气短 | 2月前无明显诱因再次出现咳嗽咳痰 | history_of_present_illness(section_005) | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适，遂就诊于当地医院 |
| evidence_20260515_375c8a13 | uncertain | respiratory | 无发热寒战 | 无发热寒战 | absent | definite | recent_worsening | item_008 | attribute_20260515_b8458eba | span_item_008 | clinical_object_assertion_20260515_69f21dc7, clinical_object_assertion_20260515_2a84ed69 | evidence_frame_node_20260515_4096451c |  | 无发热寒战 |  | history_of_present_illness(section_005) | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适，遂就诊于当地医院 |
| evidence_20260515_0edc2df3 | uncertain | respiratory | 无胸痛咯血 | 无胸痛咯血 | absent | definite | recent_worsening | item_008 | attribute_20260515_2243123c | span_item_008 | clinical_object_assertion_20260515_aab360b4, clinical_object_assertion_20260515_174bdc63 | evidence_frame_node_20260515_85de0e9a |  | 无胸痛咯血 |  | history_of_present_illness(section_005) | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适，遂就诊于当地医院 |
| evidence_20260515_5572b41b | uncertain | general | 无恶心呕吐等不适 | 无恶心呕吐等不适 | absent | definite | recent_worsening | item_008 | attribute_20260515_76a73321 | span_item_008 | clinical_object_assertion_20260515_1544fdb3, clinical_object_assertion_20260515_0fd4935d | evidence_frame_node_20260515_011e3059 |  | 无恶心呕吐等不适 |  | history_of_present_illness(section_005) | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适，遂就诊于当地医院 |
| evidence_20260515_77fff507 | uncertain | treatment | 遂就诊于当地医院 | 遂就诊于当地医院 | present | definite | recent_worsening | item_008 |  | span_item_008 | clinical_object_assertion_20260515_5aefb72e | evidence_frame_node_20260515_9c420e83 |  | 遂就诊于当地医院 |  | history_of_present_illness(section_005) | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适，遂就诊于当地医院 |
| evidence_20260515_dcb4c62f | imaging_finding | radiology | 2024年6月11日胸部CT示，双肺间质增粗纹理走形杂乱 | 双肺间质增粗纹理走形杂乱 | present | definite | recent_worsening | item_009 | attribute_20260515_e8c82932, attribute_20260515_3f47b10f | span_item_009 | clinical_object_assertion_20260515_d5aec0f8 | evidence_frame_node_20260515_2494c197 | evidence_frame_node_20260515_3bd2b85b | 双肺间质增粗纹理走形杂乱 | 2024年6月11日胸部CT示 | history_of_present_illness(section_005) | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 |
| evidence_20260515_dd8cea53 | imaging_finding | radiology | 2024年6月11日胸部CT示，肺野密度增高 | 肺野密度增高 | present | definite | recent_worsening | item_009 | attribute_20260515_48c7f591, attribute_20260515_3f47b10f | span_item_009 | clinical_object_assertion_20260515_5fe45635 | evidence_frame_node_20260515_db888672 | evidence_frame_node_20260515_3bd2b85b | 肺野密度增高 | 2024年6月11日胸部CT示 | history_of_present_illness(section_005) | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 |
| evidence_20260515_8870f368 | imaging_finding | radiology | 2024年6月11日胸部CT示，右肺中叶、下叶、左肺舌段条片状实性高密度影 | 右肺中叶、下叶、左肺舌段条片状实性高密度影 | present | definite | recent_worsening | item_009 | attribute_20260515_dd5cd253, attribute_20260515_3f47b10f | span_item_009 | clinical_object_assertion_20260515_7adf509b | evidence_frame_node_20260515_8083cb81 | evidence_frame_node_20260515_3bd2b85b | 右肺中叶、下叶、左肺舌段条片状实性高密度影 | 2024年6月11日胸部CT示 | history_of_present_illness(section_005) | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 |
| evidence_20260515_7099cb2f | imaging_finding | radiology | 2024年6月11日胸部CT示右肺中叶、下叶、左肺舌段条片状实性高密度影，右肺中叶、下叶病灶边缘模糊 | 右肺中叶、下叶、左肺舌段条片状实性高密度影 | present | definite | recent_worsening | item_009 | attribute_20260515_d9049680, attribute_20260515_3f47b10f, attribute_20260515_dd5cd253 | span_item_009 | clinical_object_assertion_20260515_e71af2f0 | evidence_frame_node_20260515_a24a3e26 | evidence_frame_node_20260515_3bd2b85b, evidence_frame_node_20260515_8083cb81 | 右肺中叶、下叶病灶边缘模糊 | 2024年6月11日胸部CT示右肺中叶、下叶、左肺舌段条片状实性高密度影 | history_of_present_illness(section_005) | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 |
| evidence_20260515_633500f2 | diagnosis_history | infectious_disease | 肺部感染 | 肺部感染 | present | possible | recent_worsening | item_010 |  | span_item_010 | clinical_object_assertion_20260515_84bdeb49 | evidence_frame_node_20260515_446ea985 |  | 肺部感染 |  | history_of_present_illness(section_005) | 考虑为“肺部感染” |
| evidence_20260515_78c370bf | treatment | treatment | 治疗上给予抗感染（具体不详）治疗后 | 治疗上给予抗感染（具体不详）治疗后 | present | definite | recent_worsening | item_011 |  | span_item_011 |  | evidence_frame_node_20260515_cf2a558a |  | 治疗上给予抗感染（具体不详）治疗后 |  | history_of_present_illness(section_005) | 治疗上给予抗感染（具体不详）治疗后，胸闷气短症状改善不明显 |
| evidence_20260515_7d67d714 | treatment_response | treatment | 治疗上给予抗感染（具体不详）治疗后，改善不明显 | 改善不明显 | present | definite | recent_worsening | item_011 |  | span_item_011 |  | evidence_frame_node_20260515_e332588c | evidence_frame_node_20260515_cf2a558a | 改善不明显 | 治疗上给予抗感染（具体不详）治疗后 | history_of_present_illness(section_005) | 治疗上给予抗感染（具体不详）治疗后，胸闷气短症状改善不明显 |
| evidence_20260515_0c016146 | diagnosis_history | respiratory | 间质性肺炎 | 间质性肺炎 | present | definite | current | item_012 |  | span_item_012 | clinical_object_assertion_20260515_5f77ab57 | evidence_frame_node_20260515_195aaf43 |  | 间质性肺炎 |  | history_of_present_illness(section_005) | 请我科医师会诊后，以“间质性肺炎，肺部感染”收住我科 |
| evidence_20260515_0b002773 | diagnosis_history | infectious_disease | 肺部感染 | 肺部感染 | present | definite | current | item_012 |  | span_item_012 | clinical_object_assertion_20260515_5ce11770 | evidence_frame_node_20260515_c78265ab |  | 肺部感染 |  | history_of_present_illness(section_005) | 请我科医师会诊后，以“间质性肺炎，肺部感染”收住我科 |
| evidence_20260515_1ff456c2 | sign | general | 神志清 | 神志清 | present | definite | current | item_013 |  | span_item_013 | clinical_object_assertion_20260515_0af2898e | evidence_frame_node_20260515_001bfae2 |  | 神志清 |  | history_of_present_illness(section_005) | 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 |
| evidence_20260515_76241aa2 | sign | general | 精神可 | 精神可 | present | definite | current | item_013 |  | span_item_013 | clinical_object_assertion_20260515_4119e21e | evidence_frame_node_20260515_dea497ea |  | 精神可 |  | history_of_present_illness(section_005) | 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 |
| evidence_20260515_71b0974d | sign | general | 饮食睡眠、大小便正常 | 饮食睡眠、大小便正常 | present | definite | current | item_013 |  | span_item_013 | clinical_object_assertion_20260515_d63a471e | evidence_frame_node_20260515_ca1fd9c1 |  | 饮食睡眠、大小便正常 |  | history_of_present_illness(section_005) | 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 |
| evidence_20260515_f7abc52e | uncertain | general | 无明显变化体重无明显变化 | 体重无明显变化 | absent | definite | current | item_013 |  | span_item_013 | clinical_object_assertion_20260515_9746b5c6 | evidence_frame_node_20260515_8b14e8c4 |  | 无明显变化体重无明显变化 |  | history_of_present_illness(section_005) | 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 |

## Boundary Note

Multi-round support here means the same case_id is reused across rounds with increasing input_order and parent_input_id. Evidence Atomizer remains stateless per round. Cross-round merging, belief revision, and update management belong to later phases.
