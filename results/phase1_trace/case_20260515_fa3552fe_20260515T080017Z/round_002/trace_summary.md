# Phase 1 Trace Round 002

- Selected file: data/02.txt
- case_id: case_20260515_fa3552fe
- input_id: input_20260515_c6713d31
- parent_input_id: input_20260515_e9018bf3
- input_order: 2
- case_structuring_result_id: case_structuring_result_20260515_3084519f
- attribute_extraction_result_id: attribute_extraction_result_20260515_7a2c561f
- atomization_result_id: atomization_result_20260515_d1c57fee
- case_structurer_duration: 1 min 1.8 s
- attribute_extractor_duration: 26.88 s
- evidence_atomizer_duration: 1 min 54.7 s
- round_duration: 3 min 23.4 s

## Structuring Summary

- ready_for_attribute_extraction: True
- clinical_sections: 3
- structured_items: 16

## Case Structurer Results

### Stage Context

| stage_id | stage_order | stage_type | relation_to_previous_stage | previous_stage_id | is_initial_stage | classification_confidence | classification_basis |
| --- | --- | --- | --- | --- | --- | --- | --- |
| stage_20260515_3063309f | 2 | new_test_result | adds_information |  | False | high | Detailed diagnostic test results following initial input, providing new clinical data. |

### Clinical Sections

| section_id | section_order | section_type | title | parent_section_id | classification_confidence | source_span_ids | normalized_text |
| --- | --- | --- | --- | --- | --- | --- | --- |
| section_001 | 1 | imaging |  |  | high | span_section_001 | 入院后完善检查：胸部CT：1、双肺间质性增粗；2、右肺中叶、下叶感染性病灶；3、左肺舌段局限性不张。 |
| section_002 | 2 | pulmonary_function_test |  |  | high | span_section_002 | A1.通气功能：中度呼吸储备功能(最大通气量)减损；轻度阻塞性通气功能障碍，V-V曲线符合阻塞性改变；残气容积占肺总量百分比增高。2.换气功能：中度弥散功能障碍。3.脉冲振荡：呼吸总阻抗Zrs增高，气道总阻力R5、外周阻力R5-R20及近端阻力R35增高，中心阻力R20正常；中心阻抗Rc及周边阻抗Rp均增大，Rp>Rc；电抗X5负值增大；共振频率Fres增高，电抗面积AX增大；Ers正常。 |
| section_003 | 3 | laboratory_test |  |  | high | span_section_003 | 血常规）:风湿相关检验无异常，淋巴细胞百分比LYM% 17.7%,单核细胞绝对值# 0.65*109/L,肝功四项:ALB 31.04g/L, 肾功四项:eGFR 70.88ml/(min*1.73m^2), 新型冠状病毒IgG/IgM抗体:2019-nCoV IgG 10.926S/CO,D2聚体:D-D 0.71ug/mL FEU,术前八项:HBeAb 1.790index,HBcAb 2.010index血沉CRP 41.8mg/L,结核感染T细胞(IFN-γ)检测: 阳性,其余检查无明显异常。 |

### Structured Clinical Items

| item_id | item_order | section_id | item_type | label | temporality | certainty | negation | classification_confidence | source_span_ids | source_text |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| item_001 | 1 | section_001 | imaging_finding | 双肺间质性增粗 | current | definite | present | high | span_item_001 | 双肺间质性增粗 |
| item_002 | 2 | section_001 | imaging_finding | 右肺中叶、下叶感染性病灶 | current | definite | present | high | span_item_002 | 右肺中叶、下叶感染性病灶 |
| item_003 | 3 | section_001 | imaging_finding | 左肺舌段局限性不张 | current | definite | present | high | span_item_003 | 左肺舌段局限性不张 |
| item_004 | 4 | section_002 | pulmonary_function | 中度呼吸储备功能(最大通气量)减损；轻度阻塞性通气功能障碍，V-V曲线符合阻塞性改变；残气容积占肺总量百分比增高 | current | definite | present | high | span_item_004 | 中度呼吸储备功能(最大通气量)减损；轻度阻塞性通气功能障碍，V-V曲线符合阻塞性改变；残气容积占肺总量百分比增高 |
| item_005 | 5 | section_002 | pulmonary_function | 中度弥散功能障碍 | current | definite | present | high | span_item_005 | 中度弥散功能障碍 |
| item_006 | 6 | section_002 | pulmonary_function | 呼吸总阻抗Zrs增高，气道总阻力R5、外周阻力R5-R20及近端阻力R35增高，中心阻力R20正常；中心阻抗Rc及周边阻抗Rp均增大，Rp>Rc；电抗X5负值增大；共振频率Fres增高，电抗面积AX增大；Ers正常 | current | definite | present | high | span_item_006 | 呼吸总阻抗Zrs增高，气道总阻力R5、外周阻力R5-R20及近端阻力R35增高，中心阻力R20正常；中心阻抗Rc及周边阻抗Rp均增大，Rp>Rc；电抗X5负值增大；共振频率Fres增高，电抗面积AX增大；Ers正常 |
| item_007 | 7 | section_003 | lab_result | 风湿相关检验无异常 | current | definite | absent | high | span_item_007 | 风湿相关检验无异常 |
| item_008 | 8 | section_003 | lab_result | 淋巴细胞百分比LYM% 17.7% | current | definite | present | high | span_item_008 | 淋巴细胞百分比LYM% 17.7% |
| item_009 | 9 | section_003 | lab_result | 单核细胞绝对值# 0.65*109/L | current | definite | present | high | span_item_009 | 单核细胞绝对值# 0.65*109/L |
| item_010 | 10 | section_003 | lab_result | 肝功四项:ALB 31.04g/L | current | definite | present | high | span_item_010 | 肝功四项:ALB 31.04g/L |
| item_011 | 11 | section_003 | lab_result | 肾功四项:eGFR 70.88ml/(min*1.73m^2) | current | definite | present | high | span_item_011 | 肾功四项:eGFR 70.88ml/(min*1.73m^2) |
| item_012 | 12 | section_003 | lab_result | 新型冠状病毒IgG/IgM抗体:2019-nCoV IgG 10.926S/CO | current | definite | present | high | span_item_012 | 新型冠状病毒IgG/IgM抗体:2019-nCoV IgG 10.926S/CO |
| item_013 | 13 | section_003 | lab_result | D2聚体:D-D 0.71ug/mL FEU | current | definite | present | high | span_item_013 | D2聚体:D-D 0.71ug/mL FEU |
| item_014 | 14 | section_003 | lab_result | 术前八项:HBeAb 1.790index,HBcAb 2.010index | current | definite | present | high | span_item_014 | 术前八项:HBeAb 1.790index,HBcAb 2.010index |
| item_015 | 15 | section_003 | lab_result | 血沉CRP 41.8mg/L | current | definite | present | high | span_item_015 | 血沉CRP 41.8mg/L |
| item_016 | 16 | section_003 | lab_result | 结核感染T细胞(IFN-γ)检测: 阳性 | current | definite | present | high | span_item_016 | 结核感染T细胞(IFN-γ)检测: 阳性 |

### Structuring Warnings

| severity | code | message | related_object_id |
| --- | --- | --- | --- |
| No structuring warnings produced. |  |  |  |

## Attribute Extraction Summary

- attribute_extraction_result_id: attribute_extraction_result_20260515_7a2c561f
- clinical_attributes: 21
- ready_for_evidence_atomization: True
- validation_accepted: True

## Attribute Extractor Validation Issues

No validation issues.

## Clinical Attributes

| attribute_id | source_item_id | attribute_role | attribute_scope | span_text | applies_to_text | context_text | normalized_value | normalized_unit | normalized_text | extraction_confidence | source_span_id |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| attribute_20260515_a7d27348 | item_004 | abnormal_direction | local_phrase | 中度 | 呼吸储备功能(最大通气量)减损 | 中度呼吸储备功能(最大通气量)减损；轻度阻塞性通气功能障碍，V-V曲线符合阻塞性改变；残气容积占肺总量百分比增高 |  |  | moderate | high | span_attr_001 |
| attribute_20260515_2d448c2a | item_004 | abnormal_direction | local_phrase | 轻度 | 阻塞性通气功能障碍 | 中度呼吸储备功能(最大通气量)减损；轻度阻塞性通气功能障碍，V-V曲线符合阻塞性改变；残气容积占肺总量百分比增高 |  |  | mild | high | span_attr_002 |
| attribute_20260515_75c88b48 | item_004 | abnormal_direction | local_phrase | 增高 | 残气容积占肺总量百分比 | 中度呼吸储备功能(最大通气量)减损；轻度阻塞性通气功能障碍，V-V曲线符合阻塞性改变；残气容积占肺总量百分比增高 |  |  | increased | high | span_attr_003 |
| attribute_20260515_81a2eda4 | item_005 | abnormal_direction | local_phrase | 中度 | 弥散功能障碍 | 中度弥散功能障碍 |  |  | moderate | high | span_attr_004 |
| attribute_20260515_d5814d76 | item_006 | abnormal_direction | coordinated_objects | 增高 |  | 呼吸总阻抗Zrs增高，气道总阻力R5、外周阻力R5-R20及近端阻力R35增高，中心阻力R20正常；中心阻抗Rc及周边阻抗Rp均增大，Rp>Rc；电抗X5负值增大；共振频率Fres增高，电抗面积AX增大；Ers正常 |  |  | increased | high | span_attr_005 |
| attribute_20260515_146c04e5 | item_006 | abnormal_direction | local_phrase | 正常 | 中心阻力R20 | 呼吸总阻抗Zrs增高，气道总阻力R5、外周阻力R5-R20及近端阻力R35增高，中心阻力R20正常；中心阻抗Rc及周边阻抗Rp均增大，Rp>Rc；电抗X5负值增大；共振频率Fres增高，电抗面积AX增大；Ers正常 |  |  | normal | high | span_attr_006 |
| attribute_20260515_e17d1a33 | item_006 | abnormal_direction | coordinated_objects | 增大 | 中心阻抗Rc及周边阻抗Rp | 呼吸总阻抗Zrs增高，气道总阻力R5、外周阻力R5-R20及近端阻力R35增高，中心阻力R20正常；中心阻抗Rc及周边阻抗Rp均增大，Rp>Rc；电抗X5负值增大；共振频率Fres增高，电抗面积AX增大；Ers正常 |  |  | increased | high | span_attr_007 |
| attribute_20260515_5a2509c7 | item_006 | abnormal_direction | local_phrase | 负值增大 | 电抗X5 | 呼吸总阻抗Zrs增高，气道总阻力R5、外周阻力R5-R20及近端阻力R35增高，中心阻力R20正常；中心阻抗Rc及周边阻抗Rp均增大，Rp>Rc；电抗X5负值增大；共振频率Fres增高，电抗面积AX增大；Ers正常 |  |  | increased negative value | high | span_attr_008 |
| attribute_20260515_3272aac1 | item_006 | abnormal_direction | local_phrase | 增高 | 共振频率Fres | 呼吸总阻抗Zrs增高，气道总阻力R5、外周阻力R5-R20及近端阻力R35增高，中心阻力R20正常；中心阻抗Rc及周边阻抗Rp均增大，Rp>Rc；电抗X5负值增大；共振频率Fres增高，电抗面积AX增大；Ers正常 |  |  | increased | high | span_attr_009 |
| attribute_20260515_daa75034 | item_006 | abnormal_direction | local_phrase | 增大 | 电抗面积AX | 呼吸总阻抗Zrs增高，气道总阻力R5、外周阻力R5-R20及近端阻力R35增高，中心阻力R20正常；中心阻抗Rc及周边阻抗Rp均增大，Rp>Rc；电抗X5负值增大；共振频率Fres增高，电抗面积AX增大；Ers正常 |  |  | increased | high | span_attr_010 |
| attribute_20260515_f2d4caa1 | item_006 | abnormal_direction | local_phrase | 正常 | Ers | 呼吸总阻抗Zrs增高，气道总阻力R5、外周阻力R5-R20及近端阻力R35增高，中心阻力R20正常；中心阻抗Rc及周边阻抗Rp均增大，Rp>Rc；电抗X5负值增大；共振频率Fres增高，电抗面积AX增大；Ers正常 |  |  | normal | high | span_attr_011 |
| attribute_20260515_7998921c | item_008 | numeric_result | local_phrase | 17.7% | 淋巴细胞百分比LYM% | 淋巴细胞百分比LYM% 17.7% | 17.7 | % |  | high | span_attr_012 |
| attribute_20260515_18e95d03 | item_009 | numeric_result | local_phrase | 0.65*109/L | 单核细胞绝对值# | 单核细胞绝对值# 0.65*109/L | 0.65 | 10^9/L |  | high | span_attr_013 |
| attribute_20260515_1ada489e | item_010 | numeric_result | local_phrase | 31.04g/L | ALB | 肝功四项:ALB 31.04g/L | 31.04 | g/L |  | high | span_attr_014 |
| attribute_20260515_2c081e39 | item_011 | numeric_result | local_phrase | 70.88ml/(min*1.73m^2) | eGFR | 肾功四项:eGFR 70.88ml/(min*1.73m^2) | 70.88 | ml/(min*1.73m^2) |  | high | span_attr_015 |
| attribute_20260515_19957b6b | item_012 | numeric_result | local_phrase | 10.926S/CO | 2019-nCoV IgG | 新型冠状病毒IgG/IgM抗体:2019-nCoV IgG 10.926S/CO | 10.926 | S/CO |  | high | span_attr_016 |
| attribute_20260515_3c74d669 | item_013 | numeric_result | local_phrase | 0.71ug/mL FEU | D-D | D2聚体:D-D 0.71ug/mL FEU | 0.71 | ug/mL FEU |  | high | span_attr_017 |
| attribute_20260515_ab025e65 | item_014 | numeric_result | local_phrase | 1.790index | HBeAb | 术前八项:HBeAb 1.790index,HBcAb 2.010index | 1.79 | index |  | high | span_attr_018 |
| attribute_20260515_b7c3442f | item_014 | numeric_result | local_phrase | 2.010index | HBcAb | 术前八项:HBeAb 1.790index,HBcAb 2.010index | 2.01 | index |  | high | span_attr_019 |
| attribute_20260515_c4d950ac | item_015 | numeric_result | local_phrase | 41.8mg/L | 血沉CRP | 血沉CRP 41.8mg/L | 41.8 | mg/L |  | high | span_attr_020 |
| attribute_20260515_87d72199 | item_016 | qualitative_result | local_phrase | 阳性 | 结核感染T细胞(IFN-γ)检测 | 结核感染T细胞(IFN-γ)检测: 阳性 |  |  | positive | high | span_attr_021 |

## Atomization Summary

- atomization_result_id: atomization_result_20260515_d1c57fee
- evidence_atoms: 30
- item_to_evidence_links: 16
- deferred_items: 0
- atomization_warnings: 0
- validation_accepted: True

## Evidence Atomizer Validation Issues

No validation issues.

## Evidence Atoms

| evidence_id | evidence_type | clinical_domain | statement | normalized_label | assertion_status | certainty | temporality | source_item_ids | source_attribute_ids | source_span_ids | source_text |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| evidence_20260515_5738cc19 | imaging_finding | radiology | 双肺间质性增粗 | 双肺间质性增粗 | present | definite | current | item_001 |  | span_item_001 | 双肺间质性增粗 |
| evidence_20260515_698bdc72 | imaging_finding | radiology | 右肺中叶、下叶感染性病灶 | 右肺中叶、下叶感染性病灶 | present | definite | current | item_002 |  | span_item_002 | 右肺中叶、下叶感染性病灶 |
| evidence_20260515_37c1b218 | imaging_finding | radiology | 左肺舌段局限性不张 | 左肺舌段局限性不张 | present | definite | current | item_003 |  | span_item_003 | 左肺舌段局限性不张 |
| evidence_20260515_afb83e7f | pulmonary_function | pulmonary_function | 中度呼吸储备功能(最大通气量)减损；轻度阻塞性通气功能障碍，V-V曲线符合阻塞性改变；残气容积占肺总量百分比增高 | 中度呼吸储备功能(最大通气量)减损；轻度阻塞性通气功能障碍；残气容积占肺总量百分比增高 | present | definite | current | item_004 | attribute_20260515_a7d27348, attribute_20260515_2d448c2a, attribute_20260515_75c88b48 | span_item_004 | 中度呼吸储备功能(最大通气量)减损；轻度阻塞性通气功能障碍，V-V曲线符合阻塞性改变；残气容积占肺总量百分比增高 |
| evidence_20260515_15d34118 | pulmonary_function | pulmonary_function | 中度弥散功能障碍 | 中度弥散功能障碍 | present | definite | current | item_005 | attribute_20260515_81a2eda4 | span_item_005 | 中度弥散功能障碍 |
| evidence_20260515_30bf45f7 | pulmonary_function | pulmonary_function | 呼吸总阻抗Zrs增高 | 呼吸总阻抗Zrs增高 | present | definite | current | item_006 | attribute_20260515_d5814d76, attribute_20260515_146c04e5, attribute_20260515_e17d1a33, attribute_20260515_5a2509c7, attribute_20260515_3272aac1, attribute_20260515_daa75034, attribute_20260515_f2d4caa1 | span_item_006 | 呼吸总阻抗Zrs增高，气道总阻力R5、外周阻力R5-R20及近端阻力R35增高，中心阻力R20正常；中心阻抗Rc及周边阻抗Rp均增大，Rp>Rc；电抗X5负值增大；共振频率Fres增高，电抗面积AX增大；Ers正常 |
| evidence_20260515_479db047 | pulmonary_function | pulmonary_function | 气道总阻力R5增高 | 气道总阻力R5增高 | present | definite | current | item_006 | attribute_20260515_d5814d76, attribute_20260515_146c04e5, attribute_20260515_e17d1a33, attribute_20260515_5a2509c7, attribute_20260515_3272aac1, attribute_20260515_daa75034, attribute_20260515_f2d4caa1 | span_item_006 | 呼吸总阻抗Zrs增高，气道总阻力R5、外周阻力R5-R20及近端阻力R35增高，中心阻力R20正常；中心阻抗Rc及周边阻抗Rp均增大，Rp>Rc；电抗X5负值增大；共振频率Fres增高，电抗面积AX增大；Ers正常 |
| evidence_20260515_d665efc5 | pulmonary_function | pulmonary_function | 外周阻力R5-R20增高 | 外周阻力R5-R20增高 | present | definite | current | item_006 | attribute_20260515_d5814d76, attribute_20260515_146c04e5, attribute_20260515_e17d1a33, attribute_20260515_5a2509c7, attribute_20260515_3272aac1, attribute_20260515_daa75034, attribute_20260515_f2d4caa1 | span_item_006 | 呼吸总阻抗Zrs增高，气道总阻力R5、外周阻力R5-R20及近端阻力R35增高，中心阻力R20正常；中心阻抗Rc及周边阻抗Rp均增大，Rp>Rc；电抗X5负值增大；共振频率Fres增高，电抗面积AX增大；Ers正常 |
| evidence_20260515_7ffe02c4 | pulmonary_function | pulmonary_function | 近端阻力R35增高 | 近端阻力R35增高 | present | definite | current | item_006 | attribute_20260515_d5814d76, attribute_20260515_146c04e5, attribute_20260515_e17d1a33, attribute_20260515_5a2509c7, attribute_20260515_3272aac1, attribute_20260515_daa75034, attribute_20260515_f2d4caa1 | span_item_006 | 呼吸总阻抗Zrs增高，气道总阻力R5、外周阻力R5-R20及近端阻力R35增高，中心阻力R20正常；中心阻抗Rc及周边阻抗Rp均增大，Rp>Rc；电抗X5负值增大；共振频率Fres增高，电抗面积AX增大；Ers正常 |
| evidence_20260515_ce22ae26 | pulmonary_function | pulmonary_function | 中心阻力R20正常 | 中心阻力R20正常 | present | definite | current | item_006 | attribute_20260515_146c04e5 | span_item_006 | 呼吸总阻抗Zrs增高，气道总阻力R5、外周阻力R5-R20及近端阻力R35增高，中心阻力R20正常；中心阻抗Rc及周边阻抗Rp均增大，Rp>Rc；电抗X5负值增大；共振频率Fres增高，电抗面积AX增大；Ers正常 |
| evidence_20260515_ee3df0b3 | pulmonary_function | pulmonary_function | 中心阻抗Rc增大 | 中心阻抗Rc增大 | present | definite | current | item_006 | attribute_20260515_e17d1a33 | span_item_006 | 呼吸总阻抗Zrs增高，气道总阻力R5、外周阻力R5-R20及近端阻力R35增高，中心阻力R20正常；中心阻抗Rc及周边阻抗Rp均增大，Rp>Rc；电抗X5负值增大；共振频率Fres增高，电抗面积AX增大；Ers正常 |
| evidence_20260515_2fb9b57c | pulmonary_function | pulmonary_function | 周边阻抗Rp增大 | 周边阻抗Rp增大 | present | definite | current | item_006 | attribute_20260515_e17d1a33 | span_item_006 | 呼吸总阻抗Zrs增高，气道总阻力R5、外周阻力R5-R20及近端阻力R35增高，中心阻力R20正常；中心阻抗Rc及周边阻抗Rp均增大，Rp>Rc；电抗X5负值增大；共振频率Fres增高，电抗面积AX增大；Ers正常 |
| evidence_20260515_5ed2a376 | pulmonary_function | pulmonary_function | 电抗X5负值增大 | 电抗X5负值增大 | present | definite | current | item_006 | attribute_20260515_5a2509c7 | span_item_006 | 呼吸总阻抗Zrs增高，气道总阻力R5、外周阻力R5-R20及近端阻力R35增高，中心阻力R20正常；中心阻抗Rc及周边阻抗Rp均增大，Rp>Rc；电抗X5负值增大；共振频率Fres增高，电抗面积AX增大；Ers正常 |
| evidence_20260515_f5ef9523 | pulmonary_function | pulmonary_function | 共振频率Fres增高 | 共振频率Fres增高 | present | definite | current | item_006 | attribute_20260515_3272aac1 | span_item_006 | 呼吸总阻抗Zrs增高，气道总阻力R5、外周阻力R5-R20及近端阻力R35增高，中心阻力R20正常；中心阻抗Rc及周边阻抗Rp均增大，Rp>Rc；电抗X5负值增大；共振频率Fres增高，电抗面积AX增大；Ers正常 |
| evidence_20260515_6cd5da25 | pulmonary_function | pulmonary_function | 电抗面积AX增大 | 电抗面积AX增大 | present | definite | current | item_006 | attribute_20260515_daa75034 | span_item_006 | 呼吸总阻抗Zrs增高，气道总阻力R5、外周阻力R5-R20及近端阻力R35增高，中心阻力R20正常；中心阻抗Rc及周边阻抗Rp均增大，Rp>Rc；电抗X5负值增大；共振频率Fres增高，电抗面积AX增大；Ers正常 |
| evidence_20260515_334ed85f | pulmonary_function | pulmonary_function | Ers正常 | Ers正常 | present | definite | current | item_006 | attribute_20260515_f2d4caa1 | span_item_006 | 呼吸总阻抗Zrs增高，气道总阻力R5、外周阻力R5-R20及近端阻力R35增高，中心阻力R20正常；中心阻抗Rc及周边阻抗Rp均增大，Rp>Rc；电抗X5负值增大；共振频率Fres增高，电抗面积AX增大；Ers正常 |
| evidence_20260515_1a5898fa | lab_result | laboratory | 风湿相关检验无异常 | 风湿相关检验无异常 | absent | definite | current | item_007 |  | span_item_007 | 风湿相关检验无异常 |
| evidence_20260515_95340417 | lab_result | laboratory | 淋巴细胞百分比LYM% 17.7% | 淋巴细胞百分比LYM% 17.7% | present | definite | current | item_008 | attribute_20260515_7998921c | span_item_008 | 淋巴细胞百分比LYM% 17.7% |
| evidence_20260515_3610181b | lab_result | laboratory | 单核细胞绝对值# 0.65*109/L | 单核细胞绝对值# 0.65*109/L | present | definite | current | item_009 | attribute_20260515_18e95d03 | span_item_009 | 单核细胞绝对值# 0.65*109/L |
| evidence_20260515_5aeae1cf | lab_result | laboratory | ALB 31.04 g/L | ALB 31.04 g/L | present | definite | current | item_010 | attribute_20260515_1ada489e | span_item_010 | 肝功四项:ALB 31.04g/L |
| evidence_20260515_cfcd913e | lab_result | laboratory | eGFR 70.88 ml/(min*1.73m^2) | eGFR 70.88 ml/(min*1.73m^2) | present | definite | current | item_011 | attribute_20260515_2c081e39 | span_item_011 | 肾功四项:eGFR 70.88ml/(min*1.73m^2) |
| evidence_20260515_19ea85b3 | lab_result | laboratory | 新型冠状病毒IgG/IgM抗体 2019-nCoV | 新型冠状病毒IgG/IgM抗体 2019-nCoV | present | definite | current | item_012 | attribute_20260515_19957b6b | span_item_012 | 新型冠状病毒IgG/IgM抗体:2019-nCoV IgG 10.926S/CO |
| evidence_20260515_ae3acb67 | lab_result | laboratory | IgG 10.926 S/CO | IgG 10.926 S/CO | present | definite | current | item_012 | attribute_20260515_19957b6b | span_item_012 | 新型冠状病毒IgG/IgM抗体:2019-nCoV IgG 10.926S/CO |
| evidence_20260515_23e3bcbe | lab_result | laboratory | D2聚体 | D2聚体 | present | definite | current | item_013 | attribute_20260515_3c74d669 | span_item_013 | D2聚体:D-D 0.71ug/mL FEU |
| evidence_20260515_af190eb9 | lab_result | laboratory | D-D 0.71 ug/mL | D-D 0.71 ug/mL | present | definite | current | item_013 | attribute_20260515_3c74d669 | span_item_013 | D2聚体:D-D 0.71ug/mL FEU |
| evidence_20260515_3f60dfe0 | lab_result | laboratory | HBeAb 1.790 index | HBeAb 1.790 index | present | definite | current | item_014 | attribute_20260515_ab025e65, attribute_20260515_b7c3442f | span_item_014 | 术前八项:HBeAb 1.790index,HBcAb 2.010index |
| evidence_20260515_5a113fc5 | lab_result | laboratory | HBcAb 2.010 index | HBcAb 2.010 index | present | definite | current | item_014 | attribute_20260515_ab025e65, attribute_20260515_b7c3442f | span_item_014 | 术前八项:HBeAb 1.790index,HBcAb 2.010index |
| evidence_20260515_28d1f1ee | lab_result | laboratory | 血沉CRP 41.8 mg/L | 血沉CRP 41.8 mg/L | present | definite | current | item_015 | attribute_20260515_c4d950ac | span_item_015 | 血沉CRP 41.8mg/L |
| evidence_20260515_7c884c97 | lab_result | laboratory | 结核感染T细胞(IFN-γ)检测 | 结核感染T细胞(IFN-γ)检测 | present | definite | current | item_016 | attribute_20260515_87d72199 | span_item_016 | 结核感染T细胞(IFN-γ)检测: 阳性 |
| evidence_20260515_9e27a4d1 | lab_result | laboratory | 检测 阳性 | 检测 阳性 | present | definite | current | item_016 | attribute_20260515_87d72199 | span_item_016 | 结核感染T细胞(IFN-γ)检测: 阳性 |

## Boundary Note

Multi-round support here means the same case_id is reused across rounds with increasing input_order and parent_input_id. Evidence Atomizer remains stateless per round. Cross-round merging, belief revision, and update management belong to later phases.
