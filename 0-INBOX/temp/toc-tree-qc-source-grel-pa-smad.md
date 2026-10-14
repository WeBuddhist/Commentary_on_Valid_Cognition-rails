# TOC tree vs. source QC report

issues: 3

## Issues

- 4.1 དང་པོར་གྲངས་ལ་ལོག་པར་རྟོགས་པ་བསལ་བར་བྱ་བ: pointer is [[?]] — unresolved anchor, not a clean tree
- 8 ཕྱི་རོལ་དངོས་པོ་ལས་གཞན་མ་ཡིན་པའམ། གཞན་ཉི: title attested in the source but not near pointer [[3175]] (found near line 4019) — possible cursor loss
- pointer [[1353]] is shared by 4 nodes (4, 4.2, 4.3, 4.4) — repeated-pointer collision, the extractor likely lost its cursor partway through this run

## Notes (not counted as issues)

- (none)

---
issues_before: 3
issues_after: 3
repair_rounds: 3 (all rejected — each increased issues; round-0 tree restored)
repair_model: gemini
