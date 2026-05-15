# Evidence Event Frame Tree Report Round 001

- case_id: case_20260515_02b36e2b
- input_id: input_20260515_54c25801
- atomization_result_id: atomization_result_20260515_7b24b6b4
- frames: 13
- evidence_atoms: 36

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

Warnings:
- [warning] frame_no_atomizable_node: EvidenceEventFrame contains no atomizable nodes after validation and will not generate coverage units.

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

Warnings:
- [warning] frame_no_atomizable_node: EvidenceEventFrame contains no atomizable nodes after validation and will not generate coverage units.

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

Warnings:
- [warning] frame_missing_treatment_structure: Treatment assertions were present, but the frame did not include mapped treatment_event nodes.

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

Warnings:
- [warning] frame_missing_finding_structure: Finding assertions were present, but the frame did not include mapped object_property, clinical_object, or equivalent structural nodes.

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
