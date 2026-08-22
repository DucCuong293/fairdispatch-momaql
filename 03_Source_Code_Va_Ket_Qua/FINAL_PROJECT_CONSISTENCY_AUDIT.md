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

---

## Addendum — TechDoc deep-check pass (post-audit, user-requested)

A follow-up request asked to verify TechDoc against the actual code and
fix anything stale in the parent folder. Found and fixed (text/build-script
logic only; no experiment rerun, no raw result changed):

1. **Real bug — false "20/20 tests pass, chạy lại thật" claim.**
   `build_research_report.py` hard-coded "20/20 ... chạy lại thật" as literal
   text (never actually ran pytest), and `build_technical_documentation.py`
   *did* run pytest live but its output-parsing (`"passed" in line`) grabbed
   an unrelated line when the run errored, producing a nonsense table cell
   ("passed to a binary file/buffer, a wrapper is inserted"). Running the
   suite for real inside this bundle gives **20 errors** (`FileNotFoundError:
   data/train.parquet` — parquet is gitignored/not shipped, by design; the
   suite itself has no skip-guard for this). Fixed: both scripts now run
   pytest live, parse the real summary line by shape (regex), and — when it
   errors on the known missing-data cause — say so plainly instead of
   grabbing garbage or asserting an unverified pass count. Both docx files
   rebuilt; both submission-bundle mirrors (`01_Tai_Lieu_Ky_Thuat/`,
   `02_Bao_Cao_Du_An/`) re-synced. Heading numbering re-verified unchanged in
   both.
2. **Stale cross-references from the earlier Held-out Test section
   insertion.** TechDoc Sec. 2's repository tree and Sec. 11.3's
   troubleshooting bullet both still said "Sec. 9" for the dataset-checksum
   table, which moved to Sec. 10 when Sec. 8 (Final Test Protocol) was
   inserted — never caught in the original renumbering pass. Fixed both.
3. **Stale project name + missing folders in repository-structure trees.**
   TechDoc's title page and Sec. 2 tree, plus `03_Source_Code_Va_Ket_Qua/README.md`'s
   own tree, hard-coded the root as `fairdispatch_v3_clean` (the pre-rename
   dev-repo name) and never listed the `scripts/final_test/` or `final_test/`
   directories added by the Held-out Test work, despite TechDoc Sec. 8
   citing paths inside both. Fixed: both trees now show the real bundle root
   name with a note explaining the dev-repo layout is identical, and both
   new directories are listed.
4. **`03_Source_Code_Va_Ket_Qua/README.md` predated the Held-out Test work
   entirely** and still carried the old, buggy C5 wording ("Reproduced" full
   stop) and a merged C3/C4 bullet with a blended verdict. Fixed: split into
   individual C1–C6 bullets matching the frozen verdicts exactly (C4 **Not
   Reproduced**, C5/C6 Partial with the correct component-level wording), and
   added a short paragraph pointing to the Held-out Test / 13-13-generalized
   result and the dual-axis claim table, without duplicating the full detail
   already in the Report/TechDoc.
5. **Root `README.md`** referenced "Mục 9" of the Research Report for the
   claim-by-claim table — stale after Sec. 9 became "Final Held-out Test
   Evaluation" and the claim table moved to Sec. 10. Fixed to cite both
   Mục 9 and Mục 10 correctly.

Not touched (deliberately): `src/simulator.py`/`policies.py` docstrings still
say "for fairdispatch_v3_clean" — left as-is because these files' SHA-256 is
frozen and cited by name in multiple places (Report, TechDoc, FINAL_TEST_PROTOCOL.md);
editing even a comment would change the hash and invalidate every citation of
it for a cosmetic gain not worth that risk. `scripts/final_test/*.py` and
`05_SanPham_Demo/**` correctly hardcode `fairdispatch_v3_clean/data/` as the
sibling dev-repo path for the large parquet files — that folder genuinely
still exists under that name on disk and is the real, intentional data
source; not a bug.

---

## Addendum 2 — missing figures, dev-repo consolidation, cold-reader clarity

User confirmed `FairDispatch_MOMAQL_Fair_Ride_Hailing_Dispatch_Replication` is
the one canonical parent folder (report + original code + product), and asked
to (a) fix any remaining missing-figure placeholders, (b) bring over anything
project-related still only living in the old `fairdispatch_v3_clean` dev
repo, and (c) make sure Report and TechDoc individually read clearly enough
that a cold reader understands the project and its results without needing
both open at once.

**(a) Missing figures — real bug, fixed.** All 6 Research Report figures and
1 TechDoc figure were rendering as red "[Missing figure: ...]" placeholders:
`docs/docx_report/figures/` did not exist in this bundle (its two sibling
LaTeX output dirs did). `add_figure()` degrades to a placeholder instead of
crashing, so the build silently "succeeded" with 7 holes. Fixed by running
`make_report_figures.py` (reads only `reports/*.csv`, no parquet needed) to
regenerate all 7 PNGs into all 3 output dirs, then rebuilding both docx.
Verified 0 missing-figure paragraphs remain in either file; heading numbering
unchanged.

**(b) Dev-repo consolidation.** Diffed `fairdispatch_v3_clean` (the pre-bundle
dev repo, still a separate live git repo at `D:\ProjectVSF\fairdispatch_v3_clean`)
against this bundle's `03_Source_Code_Va_Ket_Qua/`, excluding `data/`
(gitignored parquet, correctly absent from the bundle by design) and VCS/cache
dirs. Result: the bundle's own `build_research_report.py` /
`build_technical_documentation.py` / their `.docx` outputs / `README.md` are
all newer and more complete than the dev repo's copies (they lack the
Held-out Test work and the fixes in Addendum 1) — nothing pulled back from
the dev repo there. The only genuinely dev-repo-only, project-related content
was 12 markdown files under `fairdispatch_v3_clean/docs/` — Claude-prompt
specs used to build pieces of the product demo, the Final Test master plan,
the documentation-update master plan, and an earlier mentor presentation
playbook. Copied all 12 into a new `docs/dev_process_prompts/` folder in this
bundle, with an index `README.md` explaining what each one is and noting they
are internal development history, not polished deliverables (those remain
`01_`–`05_`). Not migrated: `fairdispatch_v3_clean`'s own `.gitignore` (this
bundle has its own, equivalent, at the root).

**(c) Cold-reader clarity.** Read the Research Report's Executive
Summary/Introduction/Original Study/Replication Scope (Sec. 0–3) end to end:
already strong — motivation, research question, the paper's own claim table,
a full paper-vs-replication deviation table, and an honest scope statement
all appear before any result. No changes needed there. TechDoc's Sec. 1
"System Overview", by contrast, opened directly into pipeline mechanics with
no framing at all (what MOMAQL is, which paper, why it matters) — a reader
opening only the TechDoc had no way to know what the project was for. Added
one framing paragraph at the top of Sec. 1 (paper citation, one-line problem
statement, dataset size, and an explicit pointer to the Report for the
scientific verdict) so each document is independently intelligible, while
keeping the actual claim-by-claim science exclusively in the Report (no
duplication of the verdict logic into TechDoc).

No raw experiment numbers were touched by any of the above; only build-script
prose/logic, one regenerated figure set, and file organization changed.

---

## Addendum 3 — full Vietnamese, no English/Vietnamese mixing

User confirmed scope: both the Research Report and the Technical Documentation
should read as fully Vietnamese documents — no bare English section headings,
no full English sentences dropped into otherwise-Vietnamese prose. Established
technical/domain terms already used as loanwords throughout this project's
Vietnamese writing (Utility, Fairness, Gini, Q-table, seed, checksum, MOMAQL,
Hungarian, TD(0), Full/No-Forecast/No-Fairness, Validation/Test, and the
frozen verdict tokens Reproduced/Not Reproduced/Partially Reproduced/
Generalized/Partial) were kept as-is — translating those would break the
cross-document verbatim consistency already established with the Slides,
Speaker Script, and the CSVs those tokens are read from live, and Vietnamese
technical writing conventionally keeps such terms untranslated.

**Technical Documentation** was previously 100% English, front to back.
Rewrote `build_technical_documentation.py` so every rendered string (title
page, all 11 section headings, every paragraph, every table header and cell,
every bullet, and inline comments inside the pseudocode/tree `code_block`s)
is Vietnamese, following the same "Vietnamese heading + (English term)"
convention the Research Report already used for section titles (e.g. "4. Hợp
đồng Dữ liệu (Data Contract)"). Actual code identifiers, file paths, function
names, class names, config constant names, and literal shell/Python commands
were left untouched (they refer to real code, not prose). Rebuilt; verified 0
missing-figure placeholders and the full 1→11 heading sequence intact; synced
to `01_Tai_Lieu_Ky_Thuat/`.

**Research Report** was already Vietnamese-primary but mixed in 14 fully-
English section headings (e.g. "1. Introduction", "9. Final Held-out Test
Evaluation", "10. Replication Assessment -- Paper vs. Ours, claim by claim")
plus a handful of embedded English sentences/table headers: the `pytest_line()`
helper's explanatory fallback text (added in Addendum 1, itself in English),
two claim-table cells ("Proposed method tạo trade-off...", "RL-based
methods...", "w/o Fairness là extreme utility/unfairness case"), and the
paper's-own-Table-1 quotation headers ("Method", "Total Utility"). Fixed all
of the above; kept the two rows quoting the paper's own baseline/ablation
method *names* (REASSIGN, LAF, "Balance Ride-Pooling", "Proposed (Full)",
"w/o Prediction") verbatim since those are the paper's own proper nouns, not
prose to translate. Also fixed the dual-verdict claim table's column headers
("Held-out generalization" / "Paper replication verdict" → "Generalize trên
Held-out Test" / "Kết luận tái lập so với paper"). Rebuilt; verified 0
missing-figure placeholders and all 33 headings/subheadings intact; synced to
`02_Bao_Cao_Du_An/`.

Searched both build scripts for residual English sentence fragments (regex
over common English function words: "the", "which", "does not", "is a", "of
the", "for the", etc., restricted to rendered string literals) after the
fixes above — zero hits remaining outside Python docstrings/comments (which
are not rendered into the docx and were left alone).
