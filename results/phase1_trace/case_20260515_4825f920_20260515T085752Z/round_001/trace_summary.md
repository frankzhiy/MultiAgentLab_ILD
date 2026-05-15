# Phase 1 Trace Round 001

- Selected file: data/01.txt
- case_id: case_20260515_4825f920
- input_id: input_20260515_8c80fff4
- parent_input_id: None
- input_order: 1
- case_structuring_result_id: case_structuring_result_20260515_e6a78159
- attribute_extraction_result_id: attribute_extraction_result_20260515_44c16dff
- atomization_result_id: atomization_result_20260515_2b471bb9
- case_structurer_duration: 1 min 13.9 s
- attribute_extractor_duration: 12.20 s
- evidence_atomizer_duration: 3 min 5.6 s
- round_duration: 4 min 31.7 s

## Structuring Summary

- ready_for_attribute_extraction: True
- clinical_sections: 5
- structured_items: 18

## Case Structurer Results

### Stage Context

| stage_id | stage_order | stage_type | relation_to_previous_stage | previous_stage_id | is_initial_stage | classification_confidence | classification_basis |
| --- | --- | --- | --- | --- | --- | --- | --- |
| stage_20260515_50a4a238 | 1 | initial_input | new_case_start |  | True | high | First input in the case providing initial patient history and admission details. |

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
| item_002 | 2 | section_002 | symptom | 间断咳嗽咳痰伴胸闷气短8年 | chronic | definite | present | high | span_item_002 | 间断咳嗽咳痰伴胸闷气短8年 |
| item_003 | 3 | section_002 | symptom | 加重2月 | recent_worsening | definite | present | high | span_item_003 | 加重2月 |
| item_004 | 4 | section_003 | uncertain | 一般健康状况：良好 | current | definite | present | high | span_item_004 | 一般健康状况：良好 |
| item_005 | 5 | section_004 | comorbidity | 既往高血压8年 | past | definite | present | high | span_item_005 | 既往高血压8年 |
| item_006 | 6 | section_004 | medication | 目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服 | current | definite | present | high | span_item_006 | 目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服 |
| item_007 | 7 | section_004 | comorbidity | 糖尿病 | past | definite | present | high | span_item_007 | 糖尿病 |
| item_008 | 8 | section_004 | comorbidity | 冠心病病史 | past | definite | present | high | span_item_008 | 冠心病病史 |
| item_009 | 9 | section_004 | procedure | 40年前左下肢骨折固定术 | past | definite | present | high | span_item_009 | 40年前左下肢骨折固定术 |
| item_010 | 10 | section_005 | symptom | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 | chronic | definite | present | high | span_item_010 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| item_011 | 11 | section_005 | symptom | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 | past | definite | present | high | span_item_011 | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| item_012 | 12 | section_005 | symptom | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 | recent_worsening | definite | present | high | span_item_012 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| item_013 | 13 | section_005 | imaging_finding | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 | current | definite | present | high | span_item_013 | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 |
| item_014 | 14 | section_005 | diagnosis_history | 考虑为“肺部感染” | current | possible | present | medium | span_item_014 | 考虑为“肺部感染” |
| item_015 | 15 | section_005 | treatment | 治疗上给予抗感染（具体不详）治疗 | current | definite | present | high | span_item_015 | 治疗上给予抗感染（具体不详）治疗 |
| item_016 | 16 | section_005 | treatment_response | 治疗后，胸闷气短症状改善不明显 | follow_up | definite | present | high | span_item_016 | 治疗后，胸闷气短症状改善不明显 |
| item_017 | 17 | section_005 | diagnosis_history | 以“间质性肺炎，肺部感染”收住我科 | current | definite | present | high | span_item_017 | 以“间质性肺炎，肺部感染”收住我科 |
| item_018 | 18 | section_005 | sign | 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 | current | definite | present | high | span_item_018 | 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 |

### Structuring Warnings

| severity | code | message | related_object_id |
| --- | --- | --- | --- |
| No structuring warnings produced. |  |  |  |

## Attribute Extraction Summary

- attribute_extraction_result_id: attribute_extraction_result_20260515_44c16dff
- clinical_attributes: 9
- ready_for_evidence_atomization: True
- validation_accepted: True

## Attribute Extractor Validation Issues

No validation issues.

## Clinical Attributes

| attribute_id | source_item_id | attribute_role | attribute_scope | span_text | applies_to_text | context_text | normalized_value | normalized_unit | normalized_text | extraction_confidence | source_span_id |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| attribute_20260515_9fd84509 | item_001 | sex | local_phrase | 女 | 患者*** | 患者***,女,77岁 |  |  | female | high | span_attr_001 |
| attribute_20260515_70a0413d | item_001 | age | local_phrase | 77岁 | 患者*** | 患者***,女,77岁 | 77 | year |  | high | span_attr_002 |
| attribute_20260515_15219d9a | item_002 | symptom_duration | coordinated_objects | 8年 | 间断咳嗽咳痰伴胸闷气短 | 间断咳嗽咳痰伴胸闷气短8年 | 8 | year |  | high | span_attr_003 |
| attribute_20260515_91621e0e | item_003 | worsening_interval | item | 2月 | 加重 | 加重2月 | 2 | month |  | high | span_attr_004 |
| attribute_20260515_0b42e1f2 | item_005 | disease_history_duration | item | 8年 | 既往高血压 | 既往高血压8年 | 8 | year |  | high | span_attr_005 |
| attribute_20260515_3bce3a19 | item_006 | medication_dose | item | 2片/次 | 沙库巴曲缬沙坦片 | 目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服 | 2 | 片/次 |  | high | span_attr_006 |
| attribute_20260515_d41e7d74 | item_006 | medication_frequency | item | 1次/日 | 沙库巴曲缬沙坦片 | 目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服 | 1 | 次/日 |  | high | span_attr_007 |
| attribute_20260515_a73885f0 | item_009 | onset_time | item | 40年前 | 左下肢骨折固定术 | 40年前左下肢骨折固定术 | 40 | 年 |  | high | span_attr_008 |
| attribute_20260515_491f07d1 | item_013 | onset_time | item | 2024年6月11日 | 胸部CT示 | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 | 2024-06-11 |  |  | high | span_attr_009 |

## Atomization Summary

- atomization_result_id: atomization_result_20260515_2b471bb9
- evidence_atoms: 50
- item_to_evidence_links: 18
- deferred_items: 0
- atomization_warnings: 0
- validation_accepted: True

## Evidence Atomizer Validation Issues

No validation issues.

## Evidence Atoms

| evidence_id | evidence_type | clinical_domain | statement | normalized_label | assertion_status | certainty | temporality | source_item_ids | source_attribute_ids | source_span_ids | source_text |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| evidence_20260515_8c1808d8 | demographic | general | 患者***为女性，年龄77岁 | 患者***女性77岁 | present | definite | unknown | item_001 | attribute_20260515_9fd84509, attribute_20260515_70a0413d | span_item_001 | 患者***,女,77岁 |
| evidence_20260515_070a2d1b | symptom | respiratory | 间断咳嗽持续8年 | 间断咳嗽8年 | present | definite | chronic | item_002 | attribute_20260515_15219d9a | span_item_002 | 间断咳嗽咳痰伴胸闷气短8年 |
| evidence_20260515_ab7e4873 | symptom | respiratory | 间断咳痰持续8年 | 间断咳痰8年 | present | definite | chronic | item_002 | attribute_20260515_15219d9a | span_item_002 | 间断咳嗽咳痰伴胸闷气短8年 |
| evidence_20260515_fbc243ab | symptom | respiratory | 胸闷持续8年 | 胸闷8年 | present | definite | chronic | item_002 | attribute_20260515_15219d9a | span_item_002 | 间断咳嗽咳痰伴胸闷气短8年 |
| evidence_20260515_00be9a6b | symptom | respiratory | 气短持续8年 | 气短8年 | present | definite | chronic | item_002 | attribute_20260515_15219d9a | span_item_002 | 间断咳嗽咳痰伴胸闷气短8年 |
| evidence_20260515_5fa054c2 | symptom | respiratory | 症状加重持续2月 | 加重2月 | present | definite | recent_worsening | item_003 | attribute_20260515_91621e0e | span_item_003 | 加重2月 |
| evidence_20260515_148994d2 | uncertain | general | 一般健康状况良好 | 一般健康状况良好 | present | definite | current | item_004 |  | span_item_004 | 一般健康状况：良好 |
| evidence_20260515_49d083fc | comorbidity | cardiovascular | 既往高血压病史持续8年 | 既往高血压8年 | present | definite | past | item_005 | attribute_20260515_0b42e1f2 | span_item_005 | 既往高血压8年 |
| evidence_20260515_b5b1a0e1 | medication | cardiovascular | 目前口服沙库巴曲缬沙坦片，剂量2片/次，频率1次/日 | 口服沙库巴曲缬沙坦片 2片/次 1次/日 | present | definite | current | item_006 | attribute_20260515_3bce3a19, attribute_20260515_d41e7d74 | span_item_006 | 目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服 |
| evidence_20260515_2d055fa0 | comorbidity | cardiovascular | 既往糖尿病病史 | 糖尿病 | present | definite | past | item_007 |  | span_item_007 | 糖尿病 |
| evidence_20260515_883e88b4 | comorbidity | cardiovascular | 既往冠心病病史 | 冠心病病史 | present | definite | past | item_008 |  | span_item_008 | 冠心病病史 |
| evidence_20260515_e85d8c11 | procedure | general | 40年前左下肢骨折固定术 | 左下肢骨折固定术 40年前 | present | definite | past | item_009 | attribute_20260515_a73885f0 | span_item_009 | 40年前左下肢骨折固定术 |
| evidence_20260515_845899c8 | symptom | respiratory | 8年前无明显诱因出现咳嗽，否认咳嗽 | 无咳嗽 | absent | definite | chronic | item_010 |  | span_item_010 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_cfe635c9 | symptom | respiratory | 8年前无明显诱因出现咳痰，否认咳痰 | 无咳痰 | absent | definite | chronic | item_010 |  | span_item_010 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_1ed88dee | symptom | respiratory | 8年前无明显诱因出现胸闷，否认胸闷 | 无胸闷 | absent | definite | chronic | item_010 |  | span_item_010 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_46da795d | symptom | respiratory | 8年前无明显诱因出现气短，否认气短 | 无气短 | absent | definite | chronic | item_010 |  | span_item_010 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_de9ab7eb | symptom | infectious_disease | 8年前无发热 | 无发热 | absent | definite | chronic | item_010 |  | span_item_010 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_206351d9 | symptom | infectious_disease | 8年前无寒战 | 无寒战 | absent | definite | chronic | item_010 |  | span_item_010 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_48fde0fd | symptom | respiratory | 8年前无胸痛 | 无胸痛 | absent | definite | chronic | item_010 |  | span_item_010 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_3b32db09 | symptom | respiratory | 8年前无咯血 | 无咯血 | absent | definite | chronic | item_010 |  | span_item_010 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_1362687b | symptom | general | 8年前无乏力 | 无乏力 | absent | definite | chronic | item_010 |  | span_item_010 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_d3bdfa4d | symptom | general | 8年前无盗汗 | 无盗汗 | absent | definite | chronic | item_010 |  | span_item_010 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_64a81f90 | symptom | general | 8年前无恶心 | 无恶心 | absent | definite | chronic | item_010 |  | span_item_010 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_ed97680f | symptom | general | 8年前无呕吐 | 无呕吐 | absent | definite | chronic | item_010 |  | span_item_010 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_af9751d6 | symptom | respiratory | 1年前新冠病毒感染后出现咳嗽 | 咳嗽 | present | definite | past | item_011 |  | span_item_011 | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_0e1c08f3 | symptom | respiratory | 1年前新冠病毒感染后出现咳痰 | 咳痰 | present | definite | past | item_011 |  | span_item_011 | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_ee37288c | symptom | respiratory | 1年前新冠病毒感染后出现胸闷 | 胸闷 | present | definite | past | item_011 |  | span_item_011 | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_fdad95a6 | symptom | respiratory | 1年前新冠病毒感染后出现气短 | 气短 | present | definite | past | item_011 |  | span_item_011 | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_284f2387 | symptom | respiratory | 2月前无明显诱因再次出现咳嗽，否认咳嗽 | 无咳嗽 | absent | definite | recent_worsening | item_012 |  | span_item_012 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_1164d5cd | symptom | respiratory | 2月前无明显诱因再次出现咳痰，否认咳痰 | 无咳痰 | absent | definite | recent_worsening | item_012 |  | span_item_012 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_e13e34b8 | symptom | respiratory | 2月前无明显诱因再次出现胸闷，否认胸闷 | 无胸闷 | absent | definite | recent_worsening | item_012 |  | span_item_012 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_62865483 | symptom | respiratory | 2月前无明显诱因再次出现气短，否认气短 | 无气短 | absent | definite | recent_worsening | item_012 |  | span_item_012 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_060de3a5 | symptom | infectious_disease | 2月前无发热 | 无发热 | absent | definite | recent_worsening | item_012 |  | span_item_012 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_96cdaa8b | symptom | infectious_disease | 2月前无寒战 | 无寒战 | absent | definite | recent_worsening | item_012 |  | span_item_012 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_580d3eb5 | symptom | respiratory | 2月前无胸痛 | 无胸痛 | absent | definite | recent_worsening | item_012 |  | span_item_012 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_86d19667 | symptom | respiratory | 2月前无咯血 | 无咯血 | absent | definite | recent_worsening | item_012 |  | span_item_012 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_308dc345 | symptom | general | 2月前无恶心 | 无恶心 | absent | definite | recent_worsening | item_012 |  | span_item_012 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_22ab7d29 | symptom | general | 2月前无呕吐 | 无呕吐 | absent | definite | recent_worsening | item_012 |  | span_item_012 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_81726244 | imaging_finding | radiology | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 | 胸部CT示双肺间质增粗纹理走形杂乱肺野密度增高 | present | definite | current | item_013 | attribute_20260515_491f07d1 | span_item_013 | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 |
| evidence_20260515_1a41a0e0 | diagnosis_history | infectious_disease | 考虑为“肺部感染” | 肺部感染考虑 | present | possible | current | item_014 |  | span_item_014 | 考虑为“肺部感染” |
| evidence_20260515_8ccfaa7f | treatment | treatment | 治疗上给予抗感染（具体不详）治疗 | 抗感染治疗 | present | definite | current | item_015 |  | span_item_015 | 治疗上给予抗感染（具体不详）治疗 |
| evidence_20260515_bf7175d3 | treatment_response | respiratory | 治疗后，胸闷症状改善不明显 | 胸闷症状改善不明显 | present | definite | follow_up | item_016 |  | span_item_016 | 治疗后，胸闷气短症状改善不明显 |
| evidence_20260515_07a9a1a3 | treatment_response | respiratory | 治疗后，气短症状改善不明显 | 气短症状改善不明显 | present | definite | follow_up | item_016 |  | span_item_016 | 治疗后，胸闷气短症状改善不明显 |
| evidence_20260515_8516b58b | diagnosis_history | respiratory | 以“间质性肺炎，肺部感染”收住我科 | 间质性肺炎肺部感染收住我科 | present | definite | current | item_017 |  | span_item_017 | 以“间质性肺炎，肺部感染”收住我科 |
| evidence_20260515_142dcd32 | sign | general | 病程中无相关异常 | 无病程中异常 | absent | definite | current | item_018 |  | span_item_018 | 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 |
| evidence_20260515_fdd37518 | sign | general | 病程中无患者神志清 | 无患者神志清 | absent | definite | current | item_018 |  | span_item_018 | 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 |
| evidence_20260515_643c42d3 | sign | general | 病程中无精神可 | 无精神可 | absent | definite | current | item_018 |  | span_item_018 | 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 |
| evidence_20260515_df55276b | sign | general | 病程中无饮食睡眠异常 | 无饮食睡眠 | absent | definite | current | item_018 |  | span_item_018 | 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 |
| evidence_20260515_99683b15 | sign | general | 病程中无大小便异常 | 无大小便正常 | absent | definite | current | item_018 |  | span_item_018 | 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 |
| evidence_20260515_8433e60f | sign | general | 病程中无体重明显变化 | 无体重无明显变化 | absent | definite | current | item_018 |  | span_item_018 | 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 |

## Boundary Note

Multi-round support here means the same case_id is reused across rounds with increasing input_order and parent_input_id. Evidence Atomizer remains stateless per round. Cross-round merging, belief revision, and update management belong to later phases.
