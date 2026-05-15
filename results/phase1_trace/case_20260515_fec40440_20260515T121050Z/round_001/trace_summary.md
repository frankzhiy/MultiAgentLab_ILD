# Phase 1 Trace Round 001

- Selected file: data/01.txt
- case_id: case_20260515_fec40440
- input_id: input_20260515_fa5358a4
- parent_input_id: None
- input_order: 1
- case_structuring_result_id: case_structuring_result_20260515_9e5f3d65
- attribute_extraction_result_id: attribute_extraction_result_20260515_1c3b24fc
- atomization_result_id: atomization_result_20260515_07c64432
- case_structurer_duration: 1 min 8.3 s
- attribute_extractor_duration: 28.40 s
- evidence_atomizer_duration: 4 min 22.5 s
- round_duration: 5 min 59.2 s

## Structuring Summary

- ready_for_attribute_extraction: True
- clinical_sections: 5
- structured_items: 11

## Case Structurer Results

### Stage Context

| stage_id | stage_order | stage_type | relation_to_previous_stage | previous_stage_id | is_initial_stage | classification_confidence | classification_basis |
| --- | --- | --- | --- | --- | --- | --- | --- |
| stage_20260515_af0dd402 | 1 | initial_input | new_case_start |  | True | high | First input in the case providing initial patient history and admission details. |

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
| item_004 | 4 | section_004 | comorbidity | 疾病史：既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史。40年前左下肢骨折固定术 | past | definite | present | high | span_item_004 | 疾病史：既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史。40年前左下肢骨折固定术 |
| item_005 | 5 | section_005 | symptom | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 | chronic | definite | present | high | span_item_005 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| item_006 | 6 | section_005 | symptom | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 | past | definite | present | high | span_item_006 | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| item_007 | 7 | section_005 | symptom | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 | recent_worsening | definite | present | high | span_item_007 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| item_008 | 8 | section_005 | imaging_finding | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊，考虑为“肺部感染” | recent_worsening | probable | present | high | span_item_008 | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊，考虑为“肺部感染” |
| item_009 | 9 | section_005 | treatment | 治疗上给予抗感染（具体不详）治疗后，胸闷气短症状改善不明显 | recent_worsening | definite | present | high | span_item_009 | 治疗上给予抗感染（具体不详）治疗后，胸闷气短症状改善不明显 |
| item_010 | 10 | section_005 | diagnosis_history | 请我科医师会诊后，以“间质性肺炎，肺部感染”收住我科 | current | definite | present | high | span_item_010 | 请我科医师会诊后，以“间质性肺炎，肺部感染”收住我科 |
| item_011 | 11 | section_005 | sign | 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 | current | definite | present | high | span_item_011 | 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 |

### Structuring Warnings

| severity | code | message | related_object_id |
| --- | --- | --- | --- |
| No structuring warnings produced. |  |  |  |

## Attribute Extraction Summary

- attribute_extraction_result_id: attribute_extraction_result_20260515_1c3b24fc
- clinical_attributes: 18
- ready_for_evidence_atomization: True
- validation_accepted: True

## Attribute Extractor Validation Issues

No validation issues.

## Clinical Attributes

| attribute_id | source_item_id | attribute_role | attribute_scope | span_text | applies_to_text | context_text | normalized_value | normalized_unit | normalized_text | extraction_confidence | source_span_id |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| attribute_20260515_30d2a8c5 | item_001 | sex | item | 女 | 患者***,女,77岁 | 患者***,女,77岁 |  |  | female | high | span_attr_001 |
| attribute_20260515_7128ddb8 | item_001 | age | item | 77岁 | 患者***,女,77岁 | 患者***,女,77岁 | 77 | year |  | high | span_attr_002 |
| attribute_20260515_145dbd4a | item_002 | symptom_duration | local_phrase | 8年 | 间断咳嗽咳痰伴胸闷气短8年 | 主因“间断咳嗽咳痰伴胸闷气短8年，加重2月”入院 | 8 | year |  | high | span_attr_003 |
| attribute_20260515_1accefea | item_002 | worsening_interval | local_phrase | 加重2月 | 加重2月 | 主因“间断咳嗽咳痰伴胸闷气短8年，加重2月”入院 | 2 | month |  | high | span_attr_004 |
| attribute_20260515_217ec4ae | item_004 | disease_history_duration | local_phrase | 8年 | 既往高血压8年 | 疾病史：既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史。40年前左下肢骨折固定术 | 8 | year |  | high | span_attr_005 |
| attribute_20260515_19048dfb | item_004 | medication_dose | local_phrase | 2片/次 | 沙库巴曲缬沙坦片 2片/次 | 疾病史：既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史。40年前左下肢骨折固定术 | 2 | 片/次 |  | high | span_attr_006 |
| attribute_20260515_c349110f | item_004 | medication_frequency | local_phrase | 1次/日 | 1次/日 口服 | 疾病史：既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史。40年前左下肢骨折固定术 | 1 | 次/日 |  | high | span_attr_007 |
| attribute_20260515_53020bf7 | item_004 | medication_route | local_phrase | 口服 | 1次/日 口服 | 疾病史：既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史。40年前左下肢骨折固定术 |  |  | oral | high | span_attr_008 |
| attribute_20260515_69d82a71 | item_005 | onset_time | local_phrase | 8年前 | 患者于8年前无明显诱因出现咳嗽咳痰 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 | 8 | 年 |  | high | span_attr_009 |
| attribute_20260515_bc519241 | item_005 | qualitative_result | local_phrase | 黏白色 | 痰液为黏白色 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |  |  | mucoid white | high | span_attr_010 |
| attribute_20260515_9211f27c | item_005 | qualitative_result | local_phrase | 量少 | 量少 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |  |  | small amount | high | span_attr_011 |
| attribute_20260515_b17b9a37 | item_005 | qualitative_result | local_phrase | 夜间为著 | 夜间为著 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |  |  | worse at night | high | span_attr_012 |
| attribute_20260515_fc2e88e3 | item_006 | onset_time | local_phrase | 1年前 | 1年前新冠病毒感染后再次出现咳嗽咳痰 | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 | 1 | 年 |  | high | span_attr_013 |
| attribute_20260515_260ae032 | item_006 | qualitative_result | local_phrase | 黏白色 | 痰液为黏白色 | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |  |  | mucoid white | high | span_attr_014 |
| attribute_20260515_a4c9250a | item_006 | qualitative_result | local_phrase | 量少 | 量少 | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |  |  | small amount | high | span_attr_015 |
| attribute_20260515_84592730 | item_006 | qualitative_result | local_phrase | 活动后明显 | 伴胸闷气短，活动后明显 | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |  |  | more obvious after activity | high | span_attr_016 |
| attribute_20260515_3d40b901 | item_006 | other_attribute | local_phrase | 1周余 | 于当地诊所输液1周余（具体不详） | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 | 7 | 天 | about 1 week | medium | span_attr_017 |
| attribute_20260515_bc547d6f | item_007 | onset_time | local_phrase | 2月前 | 2月前无明显诱因再次出现咳嗽咳痰 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 | 2 | 月 |  | high | span_attr_018 |

## Atomization Summary

- atomization_result_id: atomization_result_20260515_07c64432
- evidence_atoms: 59
- item_to_evidence_links: 11
- deferred_items: 0
- atomization_warnings: 6
- validation_accepted: True

## Evidence Atomizer Validation Issues

| severity | code | message | related_item_id | related_attribute_id | related_evidence_id | related_span_id |
| --- | --- | --- | --- | --- | --- | --- |
| warning | source_text_not_found_in_source_span | EvidenceAtom.source_text was not found in referenced source span text or raw_text after whitespace-normalized matching. |  |  | evidence_20260515_542610b3 |  |
| warning | source_text_not_found_in_source_span | EvidenceAtom.source_text was not found in referenced source span text or raw_text after whitespace-normalized matching. |  |  | evidence_20260515_a187c218 |  |
| warning | source_text_not_found_in_source_span | EvidenceAtom.source_text was not found in referenced source span text or raw_text after whitespace-normalized matching. |  |  | evidence_20260515_6ad5dd2f |  |
| warning | present_atom_has_negation_surface | EvidenceAtom statement begins with a negation expression while assertion_status is present. |  |  | evidence_20260515_0ee38210 |  |

## Evidence Atoms

| evidence_id | evidence_type | clinical_domain | statement | normalized_label | assertion_status | certainty | temporality | source_item_ids | source_attribute_ids | source_span_ids | source_contexts | source_text |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| evidence_20260515_65f98de0 | demographic | general | 患者***，女性，77岁 | female, 77 years old | present | definite | unknown | item_001 | attribute_20260515_30d2a8c5, attribute_20260515_7128ddb8 | span_item_001 | demographics(section_001) | 患者***,女,77岁 |
| evidence_20260515_d6655dcf | symptom | respiratory | 主因间断咳嗽，持续8年，加重2月 | intermittent cough for 8 years, worsened for 2 months | present | definite | chronic | item_002 | attribute_20260515_145dbd4a, attribute_20260515_1accefea | span_item_002 | chief_complaint(section_002) | 主因“间断咳嗽咳痰伴胸闷气短8年，加重2月”入院 |
| evidence_20260515_565c49fa | symptom | respiratory | 主因咳痰，持续8年，加重2月 | sputum for 8 years, worsened for 2 months | present | definite | chronic | item_002 | attribute_20260515_145dbd4a, attribute_20260515_1accefea | span_item_002 | chief_complaint(section_002) | 主因“间断咳嗽咳痰伴胸闷气短8年，加重2月”入院 |
| evidence_20260515_90de67aa | symptom | respiratory | 主因胸闷，持续8年，加重2月 | chest tightness for 8 years, worsened for 2 months | present | definite | chronic | item_002 | attribute_20260515_145dbd4a, attribute_20260515_1accefea | span_item_002 | chief_complaint(section_002) | 主因“间断咳嗽咳痰伴胸闷气短8年，加重2月”入院 |
| evidence_20260515_17db8a25 | symptom | respiratory | 主因气短，持续8年，加重2月 | shortness of breath for 8 years, worsened for 2 months | present | definite | chronic | item_002 | attribute_20260515_145dbd4a, attribute_20260515_1accefea | span_item_002 | chief_complaint(section_002) | 主因“间断咳嗽咳痰伴胸闷气短8年，加重2月”入院 |
| evidence_20260515_b4847d17 | symptom | respiratory | 症状加重2月 | worsening for 2 months | present | definite | chronic | item_002 | attribute_20260515_145dbd4a, attribute_20260515_1accefea | span_item_002 | chief_complaint(section_002) | 加重2月 |
| evidence_20260515_81adf4c1 | other | general | 一般健康状况良好 | general health good | present | definite | current | item_003 |  | span_item_003 | uncertain(section_003) | 一般健康状况：良好 |
| evidence_20260515_f8fa24c6 | comorbidity | cardiovascular | 既往高血压8年，现口服沙库巴曲缬沙坦片2片/次，1次/日，口服；糖尿病；冠心病病史；40年前左下肢骨折固定术 | hypertension 8 years, taking sacubitril valsartan 2 tablets per dose, once daily orally; diabetes; coronary heart disease; left lower limb fracture fixation 40 years ago | present | definite | past | item_004 | attribute_20260515_217ec4ae, attribute_20260515_19048dfb, attribute_20260515_c349110f, attribute_20260515_53020bf7 | span_item_004 | past_medical_history(section_004) | 疾病史：既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史。40年前左下肢骨折固定术 |
| evidence_20260515_a2063736 | symptom | respiratory | 患者于8年前无明显诱因出现咳嗽 | cough onset 8 years ago | present | definite | chronic | item_005 | attribute_20260515_69d82a71, attribute_20260515_bc519241, attribute_20260515_9211f27c, attribute_20260515_b17b9a37 | span_item_005 | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_08f6c6c0 | symptom | respiratory | 患者于8年前无明显诱因出现咳痰 | sputum onset 8 years ago | present | definite | chronic | item_005 | attribute_20260515_69d82a71, attribute_20260515_bc519241, attribute_20260515_9211f27c, attribute_20260515_b17b9a37 | span_item_005 | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_c9be7061 | uncertain | respiratory | 痰液为黏白色 | sputum mucoid white | present | definite | chronic | item_005 | attribute_20260515_69d82a71, attribute_20260515_bc519241, attribute_20260515_9211f27c, attribute_20260515_b17b9a37 | span_item_005 | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_ef0c42e6 | uncertain | respiratory | 痰量少 | small amount | present | definite | chronic | item_005 | attribute_20260515_69d82a71, attribute_20260515_bc519241, attribute_20260515_9211f27c, attribute_20260515_b17b9a37 | span_item_005 | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_328d2ab3 | uncertain | respiratory | 痰易咳出 | easy to cough out sputum | present | definite | chronic | item_005 | attribute_20260515_69d82a71, attribute_20260515_bc519241, attribute_20260515_9211f27c, attribute_20260515_b17b9a37 | span_item_005 | history_of_present_illness(section_005) | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_7f1771d4 | symptom | respiratory | 伴胸闷 | chest tightness | present | definite | chronic | item_005 | attribute_20260515_69d82a71, attribute_20260515_bc519241, attribute_20260515_9211f27c, attribute_20260515_b17b9a37 | span_item_005 | history_of_present_illness(section_005) | 伴胸闷气短 |
| evidence_20260515_9c7fb48d | symptom | respiratory | 伴气短 | shortness of breath | present | definite | chronic | item_005 | attribute_20260515_69d82a71, attribute_20260515_bc519241, attribute_20260515_9211f27c, attribute_20260515_b17b9a37 | span_item_005 | history_of_present_illness(section_005) | 伴胸闷气短 |
| evidence_20260515_6caf0548 | uncertain | respiratory | 夜间症状加重 | worse at night | present | definite | chronic | item_005 | attribute_20260515_69d82a71, attribute_20260515_bc519241, attribute_20260515_9211f27c, attribute_20260515_b17b9a37 | span_item_005 | history_of_present_illness(section_005) | 夜间为著 |
| evidence_20260515_f5f2f464 | symptom | respiratory | 无发热 | no fever | absent | definite | chronic | item_005 | attribute_20260515_69d82a71, attribute_20260515_bc519241, attribute_20260515_9211f27c, attribute_20260515_b17b9a37 | span_item_005 | history_of_present_illness(section_005) | 无发热寒战 |
| evidence_20260515_07695f2b | symptom | respiratory | 无寒战 | no chills | absent | definite | chronic | item_005 | attribute_20260515_69d82a71, attribute_20260515_bc519241, attribute_20260515_9211f27c, attribute_20260515_b17b9a37 | span_item_005 | history_of_present_illness(section_005) | 无发热寒战 |
| evidence_20260515_d79d8a0e | symptom | respiratory | 无胸痛 | no chest pain | absent | definite | chronic | item_005 | attribute_20260515_69d82a71, attribute_20260515_bc519241, attribute_20260515_9211f27c, attribute_20260515_b17b9a37 | span_item_005 | history_of_present_illness(section_005) | 无胸痛咯血 |
| evidence_20260515_a1689233 | symptom | respiratory | 无咯血 | no hemoptysis | absent | definite | chronic | item_005 | attribute_20260515_69d82a71, attribute_20260515_bc519241, attribute_20260515_9211f27c, attribute_20260515_b17b9a37 | span_item_005 | history_of_present_illness(section_005) | 无胸痛咯血 |
| evidence_20260515_61ef9bc8 | symptom | respiratory | 无午后低热 | no afternoon low-grade fever | absent | definite | chronic | item_005 | attribute_20260515_69d82a71, attribute_20260515_bc519241, attribute_20260515_9211f27c, attribute_20260515_b17b9a37 | span_item_005 | history_of_present_illness(section_005) | 无午后低热 |
| evidence_20260515_542610b3 | symptom | general | 无乏力 | no fatigue | absent | definite | chronic | item_005 | attribute_20260515_69d82a71, attribute_20260515_bc519241, attribute_20260515_9211f27c, attribute_20260515_b17b9a37 | span_item_005 | history_of_present_illness(section_005) | 无乏力 |
| evidence_20260515_a187c218 | symptom | general | 无盗汗 | no night sweats | absent | definite | chronic | item_005 | attribute_20260515_69d82a71, attribute_20260515_bc519241, attribute_20260515_9211f27c, attribute_20260515_b17b9a37 | span_item_005 | history_of_present_illness(section_005) | 无盗汗 |
| evidence_20260515_2bfe7bac | symptom | general | 无恶心 | no nausea | absent | definite | chronic | item_005 | attribute_20260515_69d82a71, attribute_20260515_bc519241, attribute_20260515_9211f27c, attribute_20260515_b17b9a37 | span_item_005 | history_of_present_illness(section_005) | 无恶心呕吐等不适 |
| evidence_20260515_947c8158 | symptom | general | 无呕吐 | no vomiting | absent | definite | chronic | item_005 | attribute_20260515_69d82a71, attribute_20260515_bc519241, attribute_20260515_9211f27c, attribute_20260515_b17b9a37 | span_item_005 | history_of_present_illness(section_005) | 无恶心呕吐等不适 |
| evidence_20260515_0ee38210 | uncertain | treatment | 未予重视及诊疗 | no attention or treatment given | present | definite | chronic | item_005 | attribute_20260515_69d82a71, attribute_20260515_bc519241, attribute_20260515_9211f27c, attribute_20260515_b17b9a37 | span_item_005 | history_of_present_illness(section_005) | 未予重视及诊疗 |
| evidence_20260515_55de5096 | symptom | respiratory | 1年前新冠病毒感染后再次出现咳嗽 | cough reappeared 1 year ago after COVID-19 infection | present | definite | past | item_006 | attribute_20260515_fc2e88e3, attribute_20260515_260ae032, attribute_20260515_a4c9250a, attribute_20260515_84592730, attribute_20260515_3d40b901 | span_item_006 | history_of_present_illness(section_005) | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_e62f0f48 | symptom | respiratory | 1年前新冠病毒感染后再次出现咳痰 | sputum reappeared 1 year ago after COVID-19 infection | present | definite | past | item_006 | attribute_20260515_fc2e88e3, attribute_20260515_260ae032, attribute_20260515_a4c9250a, attribute_20260515_84592730, attribute_20260515_3d40b901 | span_item_006 | history_of_present_illness(section_005) | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_3d104b34 | uncertain | respiratory | 痰液为黏白色 | sputum mucoid white | present | definite | past | item_006 | attribute_20260515_fc2e88e3, attribute_20260515_260ae032, attribute_20260515_a4c9250a, attribute_20260515_84592730, attribute_20260515_3d40b901 | span_item_006 | history_of_present_illness(section_005) | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_10bc9de6 | uncertain | respiratory | 痰量少 | small amount | present | definite | past | item_006 | attribute_20260515_fc2e88e3, attribute_20260515_260ae032, attribute_20260515_a4c9250a, attribute_20260515_84592730, attribute_20260515_3d40b901 | span_item_006 | history_of_present_illness(section_005) | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_d43d2cf7 | uncertain | respiratory | 痰易咳出 | easy to cough out sputum | present | definite | past | item_006 | attribute_20260515_fc2e88e3, attribute_20260515_260ae032, attribute_20260515_a4c9250a, attribute_20260515_84592730, attribute_20260515_3d40b901 | span_item_006 | history_of_present_illness(section_005) | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_7fc456b7 | symptom | respiratory | 伴胸闷，活动后明显 | chest tightness, more obvious after activity | present | definite | past | item_006 | attribute_20260515_fc2e88e3, attribute_20260515_260ae032, attribute_20260515_a4c9250a, attribute_20260515_84592730, attribute_20260515_3d40b901 | span_item_006 | history_of_present_illness(section_005) | 伴胸闷气短，活动后明显 |
| evidence_20260515_095a8382 | symptom | respiratory | 伴气短，活动后明显 | shortness of breath, more obvious after activity | present | definite | past | item_006 | attribute_20260515_fc2e88e3, attribute_20260515_260ae032, attribute_20260515_a4c9250a, attribute_20260515_84592730, attribute_20260515_3d40b901 | span_item_006 | history_of_present_illness(section_005) | 伴胸闷气短，活动后明显 |
| evidence_20260515_fae4b94c | uncertain | respiratory | 活动后症状明显 | more obvious after activity | present | definite | past | item_006 | attribute_20260515_fc2e88e3, attribute_20260515_260ae032, attribute_20260515_a4c9250a, attribute_20260515_84592730, attribute_20260515_3d40b901 | span_item_006 | history_of_present_illness(section_005) | 活动后明显 |
| evidence_20260515_e4f99f8a | treatment | treatment | 于当地诊所输液1周余（具体不详） | infusion at local clinic for about 1 week | present | definite | past | item_006 | attribute_20260515_fc2e88e3, attribute_20260515_260ae032, attribute_20260515_a4c9250a, attribute_20260515_84592730, attribute_20260515_3d40b901 | span_item_006 | history_of_present_illness(section_005) | 于当地诊所输液1周余（具体不详） |
| evidence_20260515_04b683e7 | treatment_response | treatment | 后感咳嗽咳痰、胸闷气短有所改善 | symptoms of cough, sputum, chest tightness and shortness of breath improved | present | definite | past | item_006 | attribute_20260515_fc2e88e3, attribute_20260515_260ae032, attribute_20260515_a4c9250a, attribute_20260515_84592730, attribute_20260515_3d40b901 | span_item_006 | history_of_present_illness(section_005) | 后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_65a89e16 | symptom | respiratory | 2月前无明显诱因再次出现咳嗽 | cough reappeared 2 months ago | present | definite | recent_worsening | item_007 | attribute_20260515_bc547d6f | span_item_007 | history_of_present_illness(section_005) | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_62f8155c | symptom | respiratory | 2月前无明显诱因再次出现咳痰 | sputum reappeared 2 months ago | present | definite | recent_worsening | item_007 | attribute_20260515_bc547d6f | span_item_007 | history_of_present_illness(section_005) | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_65ca9fd4 | symptom | respiratory | 伴胸闷 | chest tightness | present | definite | recent_worsening | item_007 | attribute_20260515_bc547d6f | span_item_007 | history_of_present_illness(section_005) | 伴胸闷气短 |
| evidence_20260515_f1bf9399 | symptom | respiratory | 伴气短 | shortness of breath | present | definite | recent_worsening | item_007 | attribute_20260515_bc547d6f | span_item_007 | history_of_present_illness(section_005) | 伴胸闷气短 |
| evidence_20260515_5344d782 | symptom | respiratory | 无发热 | no fever | absent | definite | recent_worsening | item_007 | attribute_20260515_bc547d6f | span_item_007 | history_of_present_illness(section_005) | 无发热寒战 |
| evidence_20260515_bca530f9 | symptom | respiratory | 无寒战 | no chills | absent | definite | recent_worsening | item_007 | attribute_20260515_bc547d6f | span_item_007 | history_of_present_illness(section_005) | 无发热寒战 |
| evidence_20260515_a1067f23 | symptom | respiratory | 无胸痛 | no chest pain | absent | definite | recent_worsening | item_007 | attribute_20260515_bc547d6f | span_item_007 | history_of_present_illness(section_005) | 无胸痛咯血 |
| evidence_20260515_66baed62 | symptom | respiratory | 无咯血 | no hemoptysis | absent | definite | recent_worsening | item_007 | attribute_20260515_bc547d6f | span_item_007 | history_of_present_illness(section_005) | 无胸痛咯血 |
| evidence_20260515_b30def81 | symptom | general | 无恶心 | no nausea | absent | definite | recent_worsening | item_007 | attribute_20260515_bc547d6f | span_item_007 | history_of_present_illness(section_005) | 无恶心呕吐等不适 |
| evidence_20260515_9b78f641 | symptom | general | 无呕吐 | no vomiting | absent | definite | recent_worsening | item_007 | attribute_20260515_bc547d6f | span_item_007 | history_of_present_illness(section_005) | 无恶心呕吐等不适 |
| evidence_20260515_8481cc0d | imaging_finding | radiology | 胸部CT示双肺间质增粗纹理走形杂乱 | bilateral lung interstitial thickening and distorted texture | present | probable | recent_worsening | item_008 |  | span_item_008 | history_of_present_illness(section_005) | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊，考虑为“肺部感染” |
| evidence_20260515_ac4e0c87 | imaging_finding | radiology | 胸部CT示肺野密度增高 | increased lung field density | present | probable | recent_worsening | item_008 |  | span_item_008 | history_of_present_illness(section_005) | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊，考虑为“肺部感染” |
| evidence_20260515_1292b3bc | imaging_finding | radiology | 胸部CT示右肺中叶、下叶、左肺舌段条片状实性高密度影 | patchy solid high-density shadows in right middle and lower lobes and left lingular segment | present | probable | recent_worsening | item_008 |  | span_item_008 | history_of_present_illness(section_005) | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊，考虑为“肺部感染” |
| evidence_20260515_5f325b68 | imaging_finding | radiology | 右肺中叶、下叶病灶边缘模糊 | blurred lesion margins in right middle and lower lobes | present | probable | recent_worsening | item_008 |  | span_item_008 | history_of_present_illness(section_005) | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊，考虑为“肺部感染” |
| evidence_20260515_753a2331 | uncertain | infectious_disease | 考虑为肺部感染 | possible pulmonary infection | unknown | probable | recent_worsening | item_008 |  | span_item_008 | history_of_present_illness(section_005) | 考虑为“肺部感染” |
| evidence_20260515_ad879cd4 | symptom | respiratory | 胸闷症状 | chest tightness | present | definite | recent_worsening | item_009 |  | span_item_009 | history_of_present_illness(section_005) | 治疗上给予抗感染（具体不详）治疗后，胸闷气短症状改善不明显 |
| evidence_20260515_8ff60a0c | symptom | respiratory | 气短症状 | shortness of breath | present | definite | recent_worsening | item_009 |  | span_item_009 | history_of_present_illness(section_005) | 治疗上给予抗感染（具体不详）治疗后，胸闷气短症状改善不明显 |
| evidence_20260515_d0b31d8c | diagnosis_history | respiratory | 以间质性肺炎收住我科 | admitted with interstitial pneumonia | present | definite | current | item_010 |  | span_item_010 | history_of_present_illness(section_005) | 以“间质性肺炎，肺部感染”收住我科 |
| evidence_20260515_495e887f | diagnosis_history | infectious_disease | 以肺部感染收住我科 | admitted with pulmonary infection | present | definite | current | item_010 |  | span_item_010 | history_of_present_illness(section_005) | 以“间质性肺炎，肺部感染”收住我科 |
| evidence_20260515_5eec798e | sign | general | 神志清 | clear consciousness | present | definite | current | item_011 |  | span_item_011 | history_of_present_illness(section_005) | 神志清 |
| evidence_20260515_64ee7a10 | sign | general | 精神可 | good spirit | present | definite | current | item_011 |  | span_item_011 | history_of_present_illness(section_005) | 精神可 |
| evidence_20260515_615345f4 | sign | general | 饮食睡眠、大小便正常 | normal diet, sleep, urination and defecation | present | definite | current | item_011 |  | span_item_011 | history_of_present_illness(section_005) | 饮食睡眠、大小便正常 |
| evidence_20260515_6ad5dd2f | sign | general | 体重无明显变化 | no significant weight change | absent | definite | current | item_011 |  | span_item_011 | history_of_present_illness(section_005) | 无体重无明显变化 |

## Boundary Note

Multi-round support here means the same case_id is reused across rounds with increasing input_order and parent_input_id. Evidence Atomizer remains stateless per round. Cross-round merging, belief revision, and update management belong to later phases.
