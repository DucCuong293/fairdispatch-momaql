# Final Project Consistency Audit — Held-out Test Documentation Set

No experiment rerun. No raw numerical value changed by this audit — only wording
was checked and, where a gap was found, only wording was edited (one instance,
listed below). Method: extracted the full text of both `.docx` files via
`python-docx` (paragraphs + table cells) to a scratch dump, then `grep`'d that
dump plus `index.html`, `speaker_notes.md`, and the new speaker script for
every required number and every banned phrase.

## Files checked

- `03_Source_Code_Va_Ket_Qua/docs/docx_report/Bao_Cao_Nghien_Cuu_FairDispatch_MOMAQL.docx`
- `03_Source_Code_Va_Ket_Qua/docs/techdoc/Technical_Documentation.docx`
- `04_Slide_Thuyet_Trinh/index.html` (32-slide deck — trimmed from 37 after
  this audit was written; see `SLIDE_UPDATE_CHANGELOG.md` addendum. Numbers
  and banned-phrase checks below are unaffected by the trim, only slide count
  changed)
- `04_Slide_Thuyet_Trinh/speaker_notes.md`
- `04_Slide_Thuyet_Trinh/FairDispatch_Final_Presentation_Script_With_Heldout_Test.md`
- `final_test/FINAL_TEST_MENTOR_SUMMARY.md`, `test_claim_assessment.csv`,
  `validation_vs_test.csv`, `test_quality_transform_manifest.json` (source of truth,
  used to verify every number above, not re-derived)

## (a) Key numbers — cross-check result: MATCH everywhere they are stated

| Number | Report | TechDoc | Slides | Speaker Script |
|---|---|---|---|---|
| Raw test rows 195,510 | ✓ | ✓ | ✓ | ✓ |
| Final evaluated 195,506 | ✓ | ✓ | ✓ | ✓ |
| Duration repaired 32 | ✓ | ✓ | ✓ | ✓ |
| Duration excluded 1 | ✓ | ✓ | ✓ | ✓ |
| Boundary excluded 3 | ✓ | ✓ | ✓ | ✓ |
| MOMAQL Validation 1,422,441 / 0.2037 | ✓ | — | ✓ | ✓ |
| MOMAQL Test 1,454,053 / 0.2011 | ✓ | — | ✓ | ✓ |
| Full vs No-Forecast Utility Val +22.4% / Test +17.1% | ✓ | — | ✓ | ✓ |
| Long-horizon Day 21 Val +5.1% / Test +1.2% | ✓ | — | ✓ | ✓ |
| Long-horizon Day 37 Val +20.2% / Test +13.4% | ✓ | — | ✓ | ✓ |
| "13/13 findings generalized" | ✓ | — | ✓ | ✓ |
| Final verdict sentence, verbatim | ✓ | — | ✓ | ✓ |

TechDoc rows marked "—" are not a mismatch: TechDoc Sec. 8 is scoped to
protocol/data-quality/commands/artifact-map/metric-definitions/limitations by
design (per the original task spec) and deliberately does not restate result
values — those live in the Research Report. Checked that TechDoc contains no
*contradictory* number in place of them (none found).

Vietnamese docs use `.` as thousands separator (195.510), English/TechDoc uses
`,` (195,510) — this is a locale-formatting difference, not a value mismatch;
the underlying integers match in every case checked.

## (b) Banned phrasings — result: NONE found anywhere

Searched (case-insensitive) across all 5 files for: "6/6 paper claims
reproduced", "Forecast improves fairness", "Full is fairer than No Forecast",
"Test was used for tuning", "This is exact reproduction" (as an affirmative
claim), "MOMAQL is best on every metric", "No Fairness increases Utility".

- Zero affirmative hits. The only string matches were legitimate: negations
  ("KHÔNG PHẢI... exact reproduction"), a section title ("9. Exact
  Reproduction Commands" / "3.1 Exact reproduction vs. trend replication" —
  both naming a command list / a conceptual distinction, not claiming exact
  reproduction happened), and the speaker script's own explicit instruction
  to the presenter *not* to say the banned phrase (e.g. "KHÔNG nói 'Forecast
  improves fairness'").
- C4 is stated as **Not Reproduced** everywhere it appears (Report Sec. 10,
  TechDoc Sec. 8.5 cross-reference, slide claim matrix, speaker script).
- C5 wording is correct everywhere: "Utility component reproduced/generalized;
  Fairness component NOT reproduced (No Forecast is fairer)" — the earlier
  "Utility improves, Fairness improves" bug does not appear in any of the 4
  documents.
- "6/6 claim đã được kiểm thử" (tested) appears in slides/speaker script —
  this is the permitted phrasing (tested ≠ reproduced) and is always paired
  with the dual-axis explanation nearby.

## (c) Product demo scope statement — one gap found and fixed

- Research Report: does not mention the product demo at all (out of scope for
  a research document) — not a contradiction, just silent.
- TechDoc Sec. 8.6: states correctly — "The product demo (05_SanPham_Demo)
  uses the Validation/demo slice by default, never test.parquet." Also
  restated in the Data Contract table (Sec. 4).
- Speaker script (Slide 35 note): states correctly — "Phần demo... dùng dữ
  liệu Validation/demo mặc định — không dùng Test."
- **Slide deck (`index.html`), Product Demo slide**: had only the generic
  placeholder text, with no explicit statement about which data slice it
  uses. **Fixed** — added one line: "Demo dùng dữ liệu Validation/demo slice
  mặc định — không chạy trên test.parquet. Test được giữ riêng cho đánh giá
  khoa học ở Phần 4–5, không lộ ra trong Control Room tương tác." Text-only
  change, no numbers touched.

## (d) Raw-immutability / transform-before-outcome statement — result: MATCH

All four documents state, consistently: raw `test.parquet` is never
overwritten (checksum verified unchanged), 32 rows repaired from timestamps,
1 row excluded as irrecoverable, 3 rows excluded for the strict temporal
boundary, and the quality-transform rule was frozen **before** any policy
outcome on Test was inspected. Verified present in: Report (Sec. 9.2 +
Sec. 8/9 prose), TechDoc (Sec. 8.2), slide 14 (Test Data Quality Gate), and
the speaker script's "Data Quality Gate" explanation paragraph.

## Inconsistencies found

1. Slide deck's Product Demo slide missing the "uses Validation/demo slice,
   never Test" statement that the other 3 documents already carry — see (c).

## Fixes applied

1. Added the one-line data-scope statement to the Product Demo slide in
   `index.html` (text only, no numeric change, no rerun).

## Remaining caveats (not inconsistencies — documented limitations, unchanged)

- NYC TLC 2013 dataset, not the paper's 2016 data — trend replication scope,
  stated consistently everywhere.
- 5 seeds only, no formal statistical significance claimed.
- No λ sweep run on Test (canonical λ=0.5 only, by protocol design).
- Reconstructed implementation (tabular Q, not the paper's 3-layer MLP;
  modified scalarisation) — approximation, not exact reproduction, stated
  consistently everywhere.
- Sanity-layer test-suite caveat (record_trace default False) — stated in
  Report/TechDoc/slides/speaker script, unaffected by this Held-out Test work.

## Final go/no-go

**GO.** All four public-facing documents (Research Report, Technical
Documentation, Slide Deck, Speaker Script) now report the Held-out Test
results with matching numbers, consistent claim verdicts (dual-axis
`heldout_generalization` / `paper_replication_verdict`, never merged), no
banned overclaiming phrase, and a correct, consistent statement of the
product demo's data scope. Final verdict sentence — **"Strong Partial Trend
Replication with held-out temporal support"** — appears verbatim in Report,
Slides, and Speaker Script.
