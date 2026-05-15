# Evidence Event Frame Tree Report Round 001

- case_id: case_20260515_1ef422a9
- input_id: input_20260515_220232a8
- atomization_result_id: atomization_result_20260515_b67bf980
- frames: 13
- evidence_atoms: 57

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

Warnings:
- [warning] frame_builder_fallback_used: No ClinicalObjectAssertions were available for a complex candidate, so the fallback frame was marked non-atomizable and deferred.

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

Warnings:
- [warning] frame_orphan_modifier: Symptom modifier frame node does not have a clear modifier target.
- [warning] frame_no_atomizable_node: EvidenceEventFrame contains no atomizable nodes after validation and will not generate coverage units.

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

Warnings:
- [warning] frame_builder_fallback_used: No ClinicalObjectAssertions were available, so a simple single-node fallback frame was used for this candidate.

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

Warnings:
- [warning] frame_builder_fallback_used: No ClinicalObjectAssertions were available, so a simple single-node fallback frame was used for this candidate.

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

Warnings:
- [warning] frame_builder_fallback_used: A conservative assertion-grounded EvidenceEventFrame fallback was used after draft validation failed. Each ClinicalObjectAssertion was preserved as its own frame node or context node.
- [warning] frame_builder_fallback_mapping_warning: A finding assertion was conservatively mapped to a clinical_object node because no safe parent relation was available in fallback mode.
- [warning] frame_builder_fallback_mapping_warning: A finding assertion was conservatively mapped to a clinical_object node because no safe parent relation was available in fallback mode.

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
