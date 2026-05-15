# Phase 1 Trace Round 001

- Selected file: data/01.txt
- case_id: case_20260515_fa3552fe
- input_id: input_20260515_e9018bf3
- parent_input_id: None
- input_order: 1
- case_structuring_result_id: case_structuring_result_20260515_3f674584
- attribute_extraction_result_id: attribute_extraction_result_20260515_9795a67c
- atomization_result_id: atomization_result_20260515_48a48bd5
- case_structurer_duration: 1 min 26.2 s
- attribute_extractor_duration: 33.67 s
- evidence_atomizer_duration: 2 min 30.9 s
- round_duration: 4 min 30.8 s

## Structuring Summary

- ready_for_attribute_extraction: True
- clinical_sections: 5
- structured_items: 13

## Case Structurer Results

### Stage Context

| stage_id | stage_order | stage_type | relation_to_previous_stage | previous_stage_id | is_initial_stage | classification_confidence | classification_basis |
| --- | --- | --- | --- | --- | --- | --- | --- |
| stage_20260515_dedff8ec | 1 | initial_input | new_case_start |  | True | high | First input in the case providing initial patient history and admission details. |

### Clinical Sections

| section_id | section_order | section_type | title | parent_section_id | classification_confidence | source_span_ids | normalized_text |
| --- | --- | --- | --- | --- | --- | --- | --- |
| section_001 | 1 | demographics |  |  | high | span_section_001 | 患者***,女,77岁 |
| section_002 | 2 | chief_complaint |  |  | high | span_section_002 | 主因“间断咳嗽咳痰伴胸闷气短8年，加重2月”入院 |
| section_003 | 3 | uncertain |  |  | high | span_section_003 | 一般健康状况：良好 |
| section_004 | 4 | past_medical_history |  |  | high | span_section_004 | 既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史。40年前左下肢骨折固定术 |
| section_005 | 5 | history_of_present_illness |  |  | high | span_section_005 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗。1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善。2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适，遂就诊于当地医院，完善2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊，考虑为“肺部感染”，治疗上给予抗感染（具体不详）治疗后，胸闷气短症状改善不明显，为进一步诊治，遂就诊于我院，详阅当地胸部CT，请我科医师会诊后，以“间质性肺炎，肺部感染”收住我科。病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化。 |

### Structured Clinical Items

| item_id | item_order | section_id | item_type | label | temporality | certainty | negation | classification_confidence | source_span_ids | source_text |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| item_001 | 1 | section_001 | demographic | 患者***,女,77岁 | unknown | definite | present | high | span_item_001 | 患者***,女,77岁 |
| item_002 | 2 | section_002 | symptom | 间断咳嗽咳痰伴胸闷气短8年 | chronic | definite | present | high | span_item_002 | 间断咳嗽咳痰伴胸闷气短8年 |
| item_003 | 3 | section_002 | symptom | 加重2月 | recent_worsening | definite | present | high | span_item_003 | 加重2月 |
| item_004 | 4 | section_003 | uncertain | 一般健康状况：良好 | current | definite | present | high | span_item_004 | 一般健康状况：良好 |
| item_005 | 5 | section_004 | comorbidity | 既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史 | chronic | definite | present | high | span_item_005 | 既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史 |
| item_006 | 6 | section_004 | procedure | 40年前左下肢骨折固定术 | past | definite | present | high | span_item_006 | 40年前左下肢骨折固定术 |
| item_007 | 7 | section_005 | symptom | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 | chronic | definite | present | high | span_item_007 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| item_008 | 8 | section_005 | symptom | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 | past | definite | present | high | span_item_008 | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| item_009 | 9 | section_005 | symptom | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 | recent_worsening | definite | present | high | span_item_009 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| item_010 | 10 | section_005 | imaging_finding | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊，考虑为“肺部感染” | recent_worsening | possible | present | high | span_item_010 | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊，考虑为“肺部感染” |
| item_011 | 11 | section_005 | treatment | 治疗上给予抗感染（具体不详）治疗后，胸闷气短症状改善不明显 | recent_worsening | definite | present | high | span_item_011 | 治疗上给予抗感染（具体不详）治疗后，胸闷气短症状改善不明显 |
| item_012 | 12 | section_005 | diagnosis_history | 以“间质性肺炎，肺部感染”收住我科 | current | possible | present | high | span_item_012 | 以“间质性肺炎，肺部感染”收住我科 |
| item_013 | 13 | section_005 | sign | 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 | current | definite | present | high | span_item_013 | 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 |

### Structuring Warnings

| severity | code | message | related_object_id |
| --- | --- | --- | --- |
| No structuring warnings produced. |  |  |  |

## Attribute Extraction Summary

- attribute_extraction_result_id: attribute_extraction_result_20260515_9795a67c
- clinical_attributes: 23
- ready_for_evidence_atomization: True
- validation_accepted: True

## Attribute Extractor Validation Issues

No validation issues.

## Clinical Attributes

| attribute_id | source_item_id | attribute_role | attribute_scope | span_text | applies_to_text | context_text | normalized_value | normalized_unit | normalized_text | extraction_confidence | source_span_id |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| attribute_20260515_1a9049f8 | item_001 | sex | local_phrase | 女 | 患者*** | 患者***,女,77岁 |  |  | female | high | span_attr_001 |
| attribute_20260515_71a56b64 | item_001 | age | local_phrase | 77岁 | 患者*** | 患者***,女,77岁 | 77 | year |  | high | span_attr_002 |
| attribute_20260515_ce14370e | item_002 | symptom_duration | coordinated_objects | 8年 | 间断咳嗽咳痰伴胸闷气短 | 间断咳嗽咳痰伴胸闷气短8年 | 8 | year |  | high | span_attr_003 |
| attribute_20260515_aa7a5233 | item_003 | worsening_interval | item | 2月 | 加重 | 加重2月 | 2 | month |  | high | span_attr_004 |
| attribute_20260515_9f0e916f | item_005 | disease_history_duration | item | 8年 | 既往高血压 | 既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史 | 8 | year |  | high | span_attr_005 |
| attribute_20260515_630cccb4 | item_005 | medication_dose | item | 2片/次 | 沙库巴曲缬沙坦片 | 既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史 | 2 | 片/次 |  | high | span_attr_006 |
| attribute_20260515_877df203 | item_005 | medication_frequency | item | 1次/日 | 沙库巴曲缬沙坦片 | 既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史 | 1 | 次/日 |  | high | span_attr_007 |
| attribute_20260515_2957c107 | item_006 | onset_time | item | 40年前 | 左下肢骨折固定术 | 40年前左下肢骨折固定术 | 40 | 年 |  | high | span_attr_008 |
| attribute_20260515_318da445 | item_007 | onset_time | item | 8年前 | 出现咳嗽咳痰 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 | 8 | 年 |  | high | span_attr_009 |
| attribute_20260515_4c219fc8 | item_007 | uncertain_attribute | local_phrase | 黏白色 | 痰液 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |  |  | 粘稠白色 | high | span_attr_010 |
| attribute_20260515_40ab7815 | item_007 | uncertain_attribute | local_phrase | 量少 | 痰液 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |  |  | 少量 | high | span_attr_011 |
| attribute_20260515_09acfd68 | item_007 | uncertain_attribute | local_phrase | 夜间为著 | 胸闷气短 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |  |  | 夜间明显 | high | span_attr_012 |
| attribute_20260515_e98e460f | item_008 | onset_time | item | 1年前 | 新冠病毒感染后再次出现咳嗽咳痰 | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 | 1 | 年 |  | high | span_attr_013 |
| attribute_20260515_0927332d | item_008 | uncertain_attribute | local_phrase | 黏白色 | 痰液 | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |  |  | 粘稠白色 | high | span_attr_014 |
| attribute_20260515_89b572ab | item_008 | uncertain_attribute | local_phrase | 量少 | 痰液 | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |  |  | 少量 | high | span_attr_015 |
| attribute_20260515_aad3129b | item_008 | uncertain_attribute | local_phrase | 活动后明显 | 胸闷气短 | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |  |  | 活动后加重 | high | span_attr_016 |
| attribute_20260515_05689af6 | item_008 | other_attribute | local_phrase | 1周余 | 输液 | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 | 1 | 周 |  | medium | span_attr_017 |
| attribute_20260515_36a8bdc6 | item_009 | onset_time | item | 2月前 | 再次出现咳嗽咳痰 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 | 2 | 月 |  | high | span_attr_018 |
| attribute_20260515_a946e37b | item_010 | uncertain_attribute | item | 2024年6月11日 | 胸部CT示 | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊，考虑为“肺部感染” | 2024-06-11 |  |  | high | span_attr_019 |
| attribute_20260515_fbc194cd | item_010 | qualitative_result | local_phrase | 双肺间质增粗纹理走形杂乱 | 胸部CT示 | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊，考虑为“肺部感染” |  |  | 双肺间质增粗，纹理走形杂乱 | high | span_attr_020 |
| attribute_20260515_42f93b53 | item_010 | qualitative_result | local_phrase | 肺野密度增高 | 胸部CT示 | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊，考虑为“肺部感染” |  |  | 肺野密度增高 | high | span_attr_021 |
| attribute_20260515_84f9772c | item_010 | qualitative_result | local_phrase | 右肺中叶、下叶、左肺舌段条片状实性高密度影 | 胸部CT示 | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊，考虑为“肺部感染” |  |  | 右肺中叶、下叶、左肺舌段条片状实性高密度影 | high | span_attr_022 |
| attribute_20260515_04d0d89a | item_010 | qualitative_result | local_phrase | 病灶边缘模糊 | 右肺中叶、下叶病灶 | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊，考虑为“肺部感染” |  |  | 边缘模糊 | high | span_attr_023 |

## Atomization Summary

- atomization_result_id: atomization_result_20260515_48a48bd5
- evidence_atoms: 45
- item_to_evidence_links: 13
- deferred_items: 0
- atomization_warnings: 0
- validation_accepted: True

## Evidence Atomizer Validation Issues

No validation issues.

## Evidence Atoms

| evidence_id | evidence_type | clinical_domain | statement | normalized_label | assertion_status | certainty | temporality | source_item_ids | source_attribute_ids | source_span_ids | source_text |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| evidence_20260515_31e003dd | demographic | general | 患者***,女,77岁 | female, 77 years old | present | definite | unknown | item_001 | attribute_20260515_1a9049f8, attribute_20260515_71a56b64 | span_item_001 | 患者***,女,77岁 |
| evidence_20260515_10b41850 | symptom | respiratory | 间断咳嗽8年 | intermittent cough for 8 years | present | definite | chronic | item_002 | attribute_20260515_ce14370e | span_item_002 | 间断咳嗽咳痰伴胸闷气短8年 |
| evidence_20260515_d9039029 | symptom | respiratory | 间断咳痰8年 | intermittent sputum production for 8 years | present | definite | chronic | item_002 | attribute_20260515_ce14370e | span_item_002 | 间断咳嗽咳痰伴胸闷气短8年 |
| evidence_20260515_8cb2c627 | symptom | respiratory | 胸闷8年 | chest tightness for 8 years | present | definite | chronic | item_002 | attribute_20260515_ce14370e | span_item_002 | 间断咳嗽咳痰伴胸闷气短8年 |
| evidence_20260515_2c46a328 | symptom | respiratory | 气短8年 | shortness of breath for 8 years | present | definite | chronic | item_002 | attribute_20260515_ce14370e | span_item_002 | 间断咳嗽咳痰伴胸闷气短8年 |
| evidence_20260515_c6e0f28f | symptom | respiratory | 加重2月 | worsening for 2 months | present | definite | recent_worsening | item_003 | attribute_20260515_aa7a5233 | span_item_003 | 加重2月 |
| evidence_20260515_3631ae7a | uncertain | general | 一般健康状况：良好 | general health status: good | present | definite | current | item_004 |  | span_item_004 | 一般健康状况：良好 |
| evidence_20260515_b8c5cb47 | comorbidity | cardiovascular | 既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史 | history of hypertension for 8 years, currently taking sacubitril valsartan tablets 2 tablets per dose, once daily; history of diabetes and coronary heart disease | present | definite | chronic | item_005 | attribute_20260515_9f0e916f, attribute_20260515_630cccb4, attribute_20260515_877df203 | span_item_005 | 既往高血压8年，目前口服沙库巴曲缬沙坦片 2片/次 1次/日 口服、糖尿病、冠心病病史 |
| evidence_20260515_85840e0c | procedure | general | 40年前左下肢骨折固定术 | left lower limb fracture fixation surgery 40 years ago | present | definite | past | item_006 | attribute_20260515_2957c107 | span_item_006 | 40年前左下肢骨折固定术 |
| evidence_20260515_a587a26c | symptom | respiratory | 无咳嗽，8年前，痰液为黏白色，量少，夜间为著 | no cough since 8 years ago, sputum sticky white, small amount, worse at night | absent | definite | chronic | item_007 | attribute_20260515_318da445, attribute_20260515_4c219fc8, attribute_20260515_40ab7815, attribute_20260515_09acfd68 | span_item_007 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_c7f0a91e | symptom | respiratory | 无咳痰，8年前，痰液为黏白色，量少，夜间为著 | no sputum since 8 years ago, sputum sticky white, small amount, worse at night | absent | definite | chronic | item_007 | attribute_20260515_318da445, attribute_20260515_4c219fc8, attribute_20260515_40ab7815, attribute_20260515_09acfd68 | span_item_007 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_434607e5 | symptom | respiratory | 无胸闷，8年前，痰液为黏白色，量少，夜间为著 | no chest tightness since 8 years ago, sputum sticky white, small amount, worse at night | absent | definite | chronic | item_007 | attribute_20260515_318da445, attribute_20260515_4c219fc8, attribute_20260515_40ab7815, attribute_20260515_09acfd68 | span_item_007 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_0fe40dc3 | symptom | respiratory | 无气短，8年前，痰液为黏白色，量少，夜间为著 | no shortness of breath since 8 years ago, sputum sticky white, small amount, worse at night | absent | definite | chronic | item_007 | attribute_20260515_318da445, attribute_20260515_4c219fc8, attribute_20260515_40ab7815, attribute_20260515_09acfd68 | span_item_007 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_5e5e21c4 | symptom | general | 无发热，8年前，痰液为黏白色，量少，夜间为著 | no fever since 8 years ago, sputum sticky white, small amount, worse at night | absent | definite | chronic | item_007 | attribute_20260515_318da445, attribute_20260515_4c219fc8, attribute_20260515_40ab7815, attribute_20260515_09acfd68 | span_item_007 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_4cc951b0 | symptom | general | 无寒战，8年前，痰液为黏白色，量少，夜间为著 | no chills since 8 years ago, sputum sticky white, small amount, worse at night | absent | definite | chronic | item_007 | attribute_20260515_318da445, attribute_20260515_4c219fc8, attribute_20260515_40ab7815, attribute_20260515_09acfd68 | span_item_007 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_0f3fa970 | symptom | respiratory | 无胸痛，8年前，痰液为黏白色，量少，夜间为著 | no chest pain since 8 years ago, sputum sticky white, small amount, worse at night | absent | definite | chronic | item_007 | attribute_20260515_318da445, attribute_20260515_4c219fc8, attribute_20260515_40ab7815, attribute_20260515_09acfd68 | span_item_007 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_f8feb49d | symptom | respiratory | 无咯血，8年前，痰液为黏白色，量少，夜间为著 | no hemoptysis since 8 years ago, sputum sticky white, small amount, worse at night | absent | definite | chronic | item_007 | attribute_20260515_318da445, attribute_20260515_4c219fc8, attribute_20260515_40ab7815, attribute_20260515_09acfd68 | span_item_007 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_46d27902 | symptom | general | 无乏力，8年前，痰液为黏白色，量少，夜间为著 | no fatigue since 8 years ago, sputum sticky white, small amount, worse at night | absent | definite | chronic | item_007 | attribute_20260515_318da445, attribute_20260515_4c219fc8, attribute_20260515_40ab7815, attribute_20260515_09acfd68 | span_item_007 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_97c43e2e | symptom | general | 无盗汗，8年前，痰液为黏白色，量少，夜间为著 | no night sweats since 8 years ago, sputum sticky white, small amount, worse at night | absent | definite | chronic | item_007 | attribute_20260515_318da445, attribute_20260515_4c219fc8, attribute_20260515_40ab7815, attribute_20260515_09acfd68 | span_item_007 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_b06f01b9 | symptom | general | 无恶心，8年前，痰液为黏白色，量少，夜间为著 | no nausea since 8 years ago, sputum sticky white, small amount, worse at night | absent | definite | chronic | item_007 | attribute_20260515_318da445, attribute_20260515_4c219fc8, attribute_20260515_40ab7815, attribute_20260515_09acfd68 | span_item_007 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_c070dcde | symptom | general | 无呕吐，8年前，痰液为黏白色，量少，夜间为著 | no vomiting since 8 years ago, sputum sticky white, small amount, worse at night | absent | definite | chronic | item_007 | attribute_20260515_318da445, attribute_20260515_4c219fc8, attribute_20260515_40ab7815, attribute_20260515_09acfd68 | span_item_007 | 患者于8年前无明显诱因出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，夜间为著，无发热寒战，无胸痛咯血，无午后低热、乏力、盗汗，无恶心呕吐等不适，未予重视及诊疗 |
| evidence_20260515_4edce8b9 | symptom | respiratory | 咳嗽，1年前新冠病毒感染后再次出现，痰液为黏白色，量少，活动后明显，输液1周余后有所改善 | cough 1 year ago after COVID-19 infection, sputum sticky white, small amount, worsened after activity, improved after about 1 week infusion | present | definite | past | item_008 | attribute_20260515_e98e460f, attribute_20260515_0927332d, attribute_20260515_89b572ab, attribute_20260515_aad3129b, attribute_20260515_05689af6 | span_item_008 | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_80d0efee | symptom | respiratory | 咳痰，1年前新冠病毒感染后再次出现，痰液为黏白色，量少，活动后明显，输液1周余后有所改善 | sputum production 1 year ago after COVID-19 infection, sputum sticky white, small amount, worsened after activity, improved after about 1 week infusion | present | definite | past | item_008 | attribute_20260515_e98e460f, attribute_20260515_0927332d, attribute_20260515_89b572ab, attribute_20260515_aad3129b, attribute_20260515_05689af6 | span_item_008 | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_994b19a5 | symptom | respiratory | 胸闷，1年前新冠病毒感染后再次出现，痰液为黏白色，量少，活动后明显，输液1周余后有所改善 | chest tightness 1 year ago after COVID-19 infection, sputum sticky white, small amount, worsened after activity, improved after about 1 week infusion | present | definite | past | item_008 | attribute_20260515_e98e460f, attribute_20260515_0927332d, attribute_20260515_89b572ab, attribute_20260515_aad3129b, attribute_20260515_05689af6 | span_item_008 | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_31f93551 | symptom | respiratory | 气短，1年前新冠病毒感染后再次出现，痰液为黏白色，量少，活动后明显，输液1周余后有所改善 | shortness of breath 1 year ago after COVID-19 infection, sputum sticky white, small amount, worsened after activity, improved after about 1 week infusion | present | definite | past | item_008 | attribute_20260515_e98e460f, attribute_20260515_0927332d, attribute_20260515_89b572ab, attribute_20260515_aad3129b, attribute_20260515_05689af6 | span_item_008 | 1年前新冠病毒感染后再次出现咳嗽咳痰，痰液为黏白色，量少，易咳出，伴胸闷气短，活动后明显，于当地诊所输液1周余（具体不详）后感咳嗽咳痰、胸闷气短有所改善 |
| evidence_20260515_dbab3ac7 | symptom | respiratory | 2月前无咳嗽 | no cough 2 months ago | absent | definite | recent_worsening | item_009 | attribute_20260515_36a8bdc6 | span_item_009 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_4b09e9f3 | symptom | respiratory | 2月前无咳痰 | no sputum 2 months ago | absent | definite | recent_worsening | item_009 | attribute_20260515_36a8bdc6 | span_item_009 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_c33559b5 | symptom | respiratory | 2月前无胸闷 | no chest tightness 2 months ago | absent | definite | recent_worsening | item_009 | attribute_20260515_36a8bdc6 | span_item_009 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_41483d10 | symptom | respiratory | 2月前无气短 | no shortness of breath 2 months ago | absent | definite | recent_worsening | item_009 | attribute_20260515_36a8bdc6 | span_item_009 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_c74fdb9d | symptom | general | 2月前无发热 | no fever 2 months ago | absent | definite | recent_worsening | item_009 | attribute_20260515_36a8bdc6 | span_item_009 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_5bd08769 | symptom | general | 2月前无寒战 | no chills 2 months ago | absent | definite | recent_worsening | item_009 | attribute_20260515_36a8bdc6 | span_item_009 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_c4c7302d | symptom | respiratory | 2月前无胸痛 | no chest pain 2 months ago | absent | definite | recent_worsening | item_009 | attribute_20260515_36a8bdc6 | span_item_009 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_04280395 | symptom | respiratory | 2月前无咯血 | no hemoptysis 2 months ago | absent | definite | recent_worsening | item_009 | attribute_20260515_36a8bdc6 | span_item_009 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_159d25e8 | symptom | general | 2月前无恶心 | no nausea 2 months ago | absent | definite | recent_worsening | item_009 | attribute_20260515_36a8bdc6 | span_item_009 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_0b6f2980 | symptom | general | 2月前无呕吐 | no vomiting 2 months ago | absent | definite | recent_worsening | item_009 | attribute_20260515_36a8bdc6 | span_item_009 | 2月前无明显诱因再次出现咳嗽咳痰，伴胸闷气短，无发热寒战，无胸痛咯血，无恶心呕吐等不适 |
| evidence_20260515_cb106149 | imaging_finding | radiology | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊 | Chest CT on 2024-06-11 shows bilateral lung interstitial thickening with distorted texture, increased lung field density, patchy solid high-density shadows in right middle and lower lobes and left lingual segment, with blurred lesion edges in right middle and lower lobes | present | possible | recent_worsening | item_010 | attribute_20260515_a946e37b, attribute_20260515_fbc194cd, attribute_20260515_42f93b53, attribute_20260515_84f9772c, attribute_20260515_04d0d89a | span_item_010 | 2024年6月11日胸部CT示：双肺间质增粗纹理走形杂乱，肺野密度增高，右肺中叶、下叶、左肺舌段条片状实性高密度影，其中右肺中叶、下叶病灶边缘模糊，考虑为“肺部感染” |
| evidence_20260515_1fd2ed9b | treatment_response | treatment | 治疗上给予抗感染（具体不详）治疗后，胸闷症状改善不明显 | chest tightness symptom improved not obvious after anti-infective treatment (details unknown) | present | definite | recent_worsening | item_011 |  | span_item_011 | 治疗上给予抗感染（具体不详）治疗后，胸闷气短症状改善不明显 |
| evidence_20260515_a4ec82ee | treatment_response | treatment | 治疗上给予抗感染（具体不详）治疗后，气短症状改善不明显 | shortness of breath symptom improved not obvious after anti-infective treatment (details unknown) | present | definite | recent_worsening | item_011 |  | span_item_011 | 治疗上给予抗感染（具体不详）治疗后，胸闷气短症状改善不明显 |
| evidence_20260515_f6637aeb | diagnosis_history | respiratory | 以“间质性肺炎，肺部感染”收住我科 | admitted to our department with 'interstitial pneumonia, pulmonary infection' | present | possible | current | item_012 |  | span_item_012 | 以“间质性肺炎，肺部感染”收住我科 |
| evidence_20260515_ca3a5865 | sign | general | 无病程中 | no during course of disease | absent | definite | current | item_013 |  | span_item_013 | 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 |
| evidence_20260515_8dfc6e6a | sign | general | 无患者神志清 | no patient consciousness clear | absent | definite | current | item_013 |  | span_item_013 | 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 |
| evidence_20260515_f5898f05 | sign | general | 无精神可 | no good spirit | absent | definite | current | item_013 |  | span_item_013 | 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 |
| evidence_20260515_253ce74b | sign | general | 无饮食睡眠 | no eating and sleeping | absent | definite | current | item_013 |  | span_item_013 | 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 |
| evidence_20260515_12159c71 | sign | general | 无大小便正常 | no normal urination and defecation | absent | definite | current | item_013 |  | span_item_013 | 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 |
| evidence_20260515_7efe9da1 | sign | general | 无体重无明显变化 | no significant weight change | absent | definite | current | item_013 |  | span_item_013 | 病程中，患者神志清，精神可，饮食睡眠、大小便正常 ，体重无明显变化 |

## Boundary Note

Multi-round support here means the same case_id is reused across rounds with increasing input_order and parent_input_id. Evidence Atomizer remains stateless per round. Cross-round merging, belief revision, and update management belong to later phases.
