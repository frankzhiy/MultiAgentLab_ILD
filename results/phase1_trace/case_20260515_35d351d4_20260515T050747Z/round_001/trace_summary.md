# Phase 1 Trace Round 001

- Selected file: data/01.txt
- case_id: case_20260515_35d351d4
- input_id: input_20260515_64e010c7
- parent_input_id: None
- input_order: 1
- case_structuring_result_id: case_structuring_result_20260515_c03490b1
- attribute_extraction_result_id: attribute_extraction_result_20260515_52bdba0f
- atomization_result_id: atomization_result_20260515_40f89e36
- case_structurer_duration: 1 min 14.4 s
- attribute_extractor_duration: 22.27 s
- evidence_atomizer_duration: 2 min 28.5 s
- round_duration: 4 min 5.1 s

## Structuring Summary

- ready_for_attribute_extraction: True
- clinical_sections: 5
- structured_items: 21

## Case Structurer Results

### Stage Context

| stage_id | stage_order | stage_type | relation_to_previous_stage | previous_stage_id | is_initial_stage | classification_confidence | classification_basis |
| --- | --- | --- | --- | --- | --- | --- | --- |
| stage_20260515_5731f41a | 1 | initial_input | new_case_start |  | True | high | First input in the case providing initial patient history and admission details. |

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
| item_010 | 10 | section_005 | symptom | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适 | chronic | definite | present | high | span_item_010 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适 |
| item_011 | 11 | section_005 | exposure | 1年前新冠病毒感染 | past | definite | present | high | span_item_011 | 1年前新冠病毒感染 |
| item_012 | 12 | section_005 | symptom | 再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显 | past | definite | present | high | span_item_012 | 再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显 |
| item_013 | 13 | section_005 | treatment | 于当地诊所输液1周余（具体不详） | past | definite | present | high | span_item_013 | 于当地诊所输液1周余（具体不详） |
| item_014 | 14 | section_005 | treatment_response | 输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 | past | definite | present | high | span_item_014 | 输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| item_015 | 15 | section_005 | symptom | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 | recent_worsening | definite | present | high | span_item_015 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| item_016 | 16 | section_005 | imaging_finding | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 | recent_worsening | definite | present | high | span_item_016 | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 |
| item_017 | 17 | section_005 | diagnosis_history | 考虑为“肺部感染” | recent_worsening | possible | present | high | span_item_017 | 考虑为“肺部感染” |
| item_018 | 18 | section_005 | treatment | 治疗上给予抗感染（具体不详）治疗 | recent_worsening | definite | present | high | span_item_018 | 治疗上给予抗感染（具体不详）治疗 |
| item_019 | 19 | section_005 | treatment_response | 抗感染（具体不详）治疗后，胸闷气短症状改善不明显 | recent_worsening | definite | present | high | span_item_019 | 抗感染（具体不详）治疗后，胸闷气短症状改善不明显 |
| item_020 | 20 | section_005 | diagnosis_history | 以“间质性肺炎，肺部感染”收住我科 | current | definite | present | high | span_item_020 | 以“间质性肺炎，肺部感染”收住我科 |
| item_021 | 21 | section_005 | sign | 患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 | current | definite | present | high | span_item_021 | 患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 |

### Structuring Warnings

| severity | code | message | related_object_id |
| --- | --- | --- | --- |
| No structuring warnings produced. |  |  |  |

## Attribute Extraction Summary

- attribute_extraction_result_id: attribute_extraction_result_20260515_52bdba0f
- clinical_attributes: 14
- ready_for_evidence_atomization: True
- validation_accepted: True

## Attribute Extractor Validation Issues

No validation issues.

## Clinical Attributes

| attribute_id | source_item_id | attribute_role | span_text | normalized_value | normalized_unit | normalized_text | extraction_confidence | source_span_id | source_text |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| attribute_20260515_99f8aee3 | item_001 | sex | 女 |  |  | female | high | span_attr_001 | 女 |
| attribute_20260515_7f4c20ee | item_001 | age | 77岁 | 77 | year |  | high | span_attr_002 | 77岁 |
| attribute_20260515_0ba2abbe | item_002 | symptom_duration | 8年 | 8 | year |  | high | span_attr_003 | 8年 |
| attribute_20260515_182f90ae | item_003 | worsening_interval | 加重2月 | 2 | month |  | high | span_attr_004 | 加重2月 |
| attribute_20260515_d95949ba | item_004 | uncertain_attribute | 良好 |  |  |  | medium | span_attr_005 | 良好 |
| attribute_20260515_7eb199e1 | item_005 | disease_history_duration | 8年 | 8 | year |  | high | span_attr_006 | 8年 |
| attribute_20260515_823cbc4e | item_006 | medication_dose | 2片/次 | 2 | 片/次 |  | high | span_attr_007 | 2片/次 |
| attribute_20260515_8bf75cb6 | item_006 | medication_frequency | 1次/日 | 1 | 次/日 |  | high | span_attr_008 | 1次/日 |
| attribute_20260515_1ac61c4c | item_006 | medication_route | 口服 |  |  | oral | high | span_attr_009 | 口服 |
| attribute_20260515_c547c5fa | item_007 | other_attribute | 糖尿病 |  |  | diabetes mellitus | high | span_attr_010 | 糖尿病 |
| attribute_20260515_f32749ea | item_008 | other_attribute | 冠心病病史 |  |  | coronary heart disease history | high | span_attr_011 | 冠心病病史 |
| attribute_20260515_84cd79fa | item_009 | uncertain_attribute | 40年前 | 40 | 年 |  | high | span_attr_012 | 40年前 |
| attribute_20260515_52a72c8e | item_009 | other_attribute | 左下肢骨折固定术 |  |  | left lower limb fracture fixation surgery | high | span_attr_013 | 左下肢骨折固定术 |
| attribute_20260515_84deab49 | item_010 | onset_time | 8年前 | 8 | 年 |  | high | span_attr_014 | 8年前 |

## Atomization Summary

- atomization_result_id: atomization_result_20260515_40f89e36
- evidence_atoms: 55
- item_to_evidence_links: 21
- deferred_items: 0
- atomization_warnings: 0
- validation_accepted: True

## Evidence Atomizer Validation Issues

No validation issues.

## Evidence Atoms

| evidence_id | evidence_type | clinical_domain | statement | normalized_label | assertion_status | certainty | temporality | source_item_ids | source_attribute_ids | source_span_ids | source_text |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| evidence_20260515_08a87dd1 | demographic | general | 患者***,女,77岁 | 患者***,女,77岁 | present | definite | unknown | item_001 | attribute_20260515_99f8aee3, attribute_20260515_7f4c20ee | span_item_001 | 患者***,女,77岁 |
| evidence_20260515_28a5d929 | symptom | respiratory | 间断咳嗽8年 | 咳嗽 | present | definite | chronic | item_002 | attribute_20260515_0ba2abbe | span_item_002 | 间断咳嗽咳痰伴胸闷气短8年 |
| evidence_20260515_f2b97484 | symptom | respiratory | 间断咳痰8年 | 咳痰 | present | definite | chronic | item_002 | attribute_20260515_0ba2abbe | span_item_002 | 间断咳嗽咳痰伴胸闷气短8年 |
| evidence_20260515_e813b7c0 | symptom | respiratory | 间断胸闷8年 | 胸闷 | present | definite | chronic | item_002 | attribute_20260515_0ba2abbe | span_item_002 | 间断咳嗽咳痰伴胸闷气短8年 |
| evidence_20260515_76c4ae21 | symptom | respiratory | 间断气短8年 | 气短 | present | definite | chronic | item_002 | attribute_20260515_0ba2abbe | span_item_002 | 间断咳嗽咳痰伴胸闷气短8年 |
| evidence_20260515_7f299770 | symptom | respiratory | 加重2月 | 加重2月 | present | definite | recent_worsening | item_003 | attribute_20260515_182f90ae | span_item_003 | 加重2月 |
| evidence_20260515_a3541a57 | uncertain | general | 一般健康状况：良好 | 一般健康状况：良好 | present | definite | current | item_004 | attribute_20260515_d95949ba | span_item_004 | 一般健康状况：良好 |
| evidence_20260515_1e9bf0a3 | comorbidity | cardiovascular | 既往高血压8年 | 高血压 | present | definite | past | item_005 | attribute_20260515_7eb199e1 | span_item_005 | 既往高血压8年 |
| evidence_20260515_8c5b73a4 | medication | treatment | 目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服 | 沙库巴曲缬沙坦片口服 | present | definite | current | item_006 | attribute_20260515_823cbc4e, attribute_20260515_8bf75cb6, attribute_20260515_1ac61c4c | span_item_006 | 目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服 |
| evidence_20260515_37c21354 | comorbidity | general | 糖尿病 | 糖尿病 | present | definite | past | item_007 | attribute_20260515_c547c5fa | span_item_007 | 糖尿病 |
| evidence_20260515_c71cb91d | comorbidity | cardiovascular | 冠心病病史 | 冠心病病史 | present | definite | past | item_008 | attribute_20260515_f32749ea | span_item_008 | 冠心病病史 |
| evidence_20260515_33612cff | procedure | general | 40年前左下肢骨折固定术 | 左下肢骨折固定术 | present | definite | past | item_009 | attribute_20260515_84cd79fa, attribute_20260515_52a72c8e | span_item_009 | 40年前左下肢骨折固定术 |
| evidence_20260515_f63fccbb | symptom | respiratory | 8年前无咳嗽 | 咳嗽 | absent | definite | chronic | item_010 | attribute_20260515_84deab49 | span_item_010 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适 |
| evidence_20260515_0079b2e1 | symptom | respiratory | 8年前无咳痰 | 咳痰 | absent | definite | chronic | item_010 | attribute_20260515_84deab49 | span_item_010 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适 |
| evidence_20260515_db5b57ca | symptom | respiratory | 8年前无胸闷 | 胸闷 | absent | definite | chronic | item_010 | attribute_20260515_84deab49 | span_item_010 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适 |
| evidence_20260515_8d3127e4 | symptom | respiratory | 8年前无气短 | 气短 | absent | definite | chronic | item_010 | attribute_20260515_84deab49 | span_item_010 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适 |
| evidence_20260515_ec53b3fe | symptom | general | 8年前无发热 | 发热 | absent | definite | chronic | item_010 | attribute_20260515_84deab49 | span_item_010 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适 |
| evidence_20260515_67560ecf | symptom | general | 8年前无寒战 | 寒战 | absent | definite | chronic | item_010 | attribute_20260515_84deab49 | span_item_010 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适 |
| evidence_20260515_3a347146 | symptom | general | 8年前无胸痛 | 胸痛 | absent | definite | chronic | item_010 | attribute_20260515_84deab49 | span_item_010 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适 |
| evidence_20260515_2c964e70 | symptom | respiratory | 8年前无咯血 | 咯血 | absent | definite | chronic | item_010 | attribute_20260515_84deab49 | span_item_010 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适 |
| evidence_20260515_a119f6cb | symptom | general | 8年前无乏力 | 乏力 | absent | definite | chronic | item_010 | attribute_20260515_84deab49 | span_item_010 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适 |
| evidence_20260515_e724b7a1 | symptom | general | 8年前无盗汗 | 盗汗 | absent | definite | chronic | item_010 | attribute_20260515_84deab49 | span_item_010 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适 |
| evidence_20260515_7bfae3d1 | symptom | general | 8年前无恶心 | 恶心 | absent | definite | chronic | item_010 | attribute_20260515_84deab49 | span_item_010 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适 |
| evidence_20260515_e7775d51 | symptom | general | 8年前无呕吐 | 呕吐 | absent | definite | chronic | item_010 | attribute_20260515_84deab49 | span_item_010 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适 |
| evidence_20260515_e4a2d84f | exposure | infectious_disease | 1年前新冠病毒感染 | 新冠病毒感染 | present | definite | past | item_011 |  | span_item_011 | 1年前新冠病毒感染 |
| evidence_20260515_9305133f | symptom | respiratory | 再次出现咳嗽 | 咳嗽 | present | definite | past | item_012 |  | span_item_012 | 再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显 |
| evidence_20260515_b3be9581 | symptom | respiratory | 再次出现咳痰 | 咳痰 | present | definite | past | item_012 |  | span_item_012 | 再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显 |
| evidence_20260515_9cdf97f5 | symptom | respiratory | 再次出现胸闷 | 胸闷 | present | definite | past | item_012 |  | span_item_012 | 再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显 |
| evidence_20260515_b616e48b | symptom | respiratory | 再次出现气短 | 气短 | present | definite | past | item_012 |  | span_item_012 | 再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显 |
| evidence_20260515_ca7489de | treatment | treatment | 于当地诊所输液1周余（具体不详） | 输液治疗 | present | definite | past | item_013 |  | span_item_013 | 于当地诊所输液1周余（具体不详） |
| evidence_20260515_bd523a24 | treatment_response | treatment | 输液1周余（具体不详）后感咳嗽改善 | 咳嗽改善 | present | definite | past | item_014 |  | span_item_014 | 输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_ed15bc16 | treatment_response | treatment | 输液1周余（具体不详）后感咳痰改善 | 咳痰改善 | present | definite | past | item_014 |  | span_item_014 | 输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_06291397 | treatment_response | treatment | 输液1周余（具体不详）后感胸闷改善 | 胸闷改善 | present | definite | past | item_014 |  | span_item_014 | 输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_b14ab870 | treatment_response | treatment | 输液1周余（具体不详）后感气短改善 | 气短改善 | present | definite | past | item_014 |  | span_item_014 | 输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_0724b1f2 | symptom | respiratory | 2月前无咳嗽 | 咳嗽 | absent | definite | recent_worsening | item_015 |  | span_item_015 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_35a6bfbd | symptom | respiratory | 2月前无咳痰 | 咳痰 | absent | definite | recent_worsening | item_015 |  | span_item_015 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_e2585802 | symptom | respiratory | 2月前无胸闷 | 胸闷 | absent | definite | recent_worsening | item_015 |  | span_item_015 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_30751548 | symptom | respiratory | 2月前无气短 | 气短 | absent | definite | recent_worsening | item_015 |  | span_item_015 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_b80c2d07 | symptom | general | 2月前无发热 | 发热 | absent | definite | recent_worsening | item_015 |  | span_item_015 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_39fcc444 | symptom | general | 2月前无寒战 | 寒战 | absent | definite | recent_worsening | item_015 |  | span_item_015 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_d261cc13 | symptom | general | 2月前无胸痛 | 胸痛 | absent | definite | recent_worsening | item_015 |  | span_item_015 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_b9e37f74 | symptom | respiratory | 2月前无咯血 | 咯血 | absent | definite | recent_worsening | item_015 |  | span_item_015 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_781d783f | symptom | general | 2月前无恶心 | 恶心 | absent | definite | recent_worsening | item_015 |  | span_item_015 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_e6e0baec | symptom | general | 2月前无呕吐 | 呕吐 | absent | definite | recent_worsening | item_015 |  | span_item_015 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_3defe552 | imaging_finding | radiology | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 | 胸部CT异常 | present | definite | recent_worsening | item_016 |  | span_item_016 | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 |
| evidence_20260515_dbd129a0 | diagnosis_history | infectious_disease | 考虑为“肺部感染” | 肺部感染考虑 | present | possible | recent_worsening | item_017 |  | span_item_017 | 考虑为“肺部感染” |
| evidence_20260515_4fe90870 | treatment | treatment | 治疗上给予抗感染（具体不详）治疗 | 抗感染治疗 | present | definite | recent_worsening | item_018 |  | span_item_018 | 治疗上给予抗感染（具体不详）治疗 |
| evidence_20260515_c7ba9939 | treatment_response | treatment | 抗感染（具体不详）治疗后，胸闷症状改善不明显 | 胸闷症状改善不明显 | present | definite | recent_worsening | item_019 |  | span_item_019 | 抗感染（具体不详）治疗后，胸闷气短症状改善不明显 |
| evidence_20260515_9a3a556b | treatment_response | treatment | 抗感染（具体不详）治疗后，气短症状改善不明显 | 气短症状改善不明显 | present | definite | recent_worsening | item_019 |  | span_item_019 | 抗感染（具体不详）治疗后，胸闷气短症状改善不明显 |
| evidence_20260515_6c48597b | diagnosis_history | respiratory | 以“间质性肺炎，肺部感染”收住我科 | 间质性肺炎，肺部感染收住 | present | definite | current | item_020 |  | span_item_020 | 以“间质性肺炎，肺部感染”收住我科 |
| evidence_20260515_e0fc914d | sign | general | 无患者神志清 | 患者神志清 | absent | definite | current | item_021 |  | span_item_021 | 患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 |
| evidence_20260515_8b4332b1 | sign | general | 无精神可 | 精神可 | absent | definite | current | item_021 |  | span_item_021 | 患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 |
| evidence_20260515_f37ae461 | sign | general | 无饮食睡眠 | 饮食睡眠 | absent | definite | current | item_021 |  | span_item_021 | 患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 |
| evidence_20260515_7212e128 | sign | general | 无大小便正常 | 大小便正常 | absent | definite | current | item_021 |  | span_item_021 | 患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 |
| evidence_20260515_2ad7cbaa | sign | general | 无体重无明显变化 | 体重无明显变化 | absent | definite | current | item_021 |  | span_item_021 | 患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 |

## Boundary Note

Multi-round support here means the same case_id is reused across rounds with increasing input_order and parent_input_id. Evidence Atomizer remains stateless per round. Cross-round merging, belief revision, and update management belong to later phases.
