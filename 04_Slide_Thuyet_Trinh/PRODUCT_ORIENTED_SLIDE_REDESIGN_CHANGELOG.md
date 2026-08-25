# Product-Oriented Slide Redesign — Changelog

No experiment rerun. No raw numerical value changed. Backups of the pre-redesign deck kept as
`index_pre_product_redesign_<timestamp>.html.bak`, `styles_pre_product_redesign_<timestamp>.css.bak`,
`speaker_notes_pre_product_redesign_<timestamp>.md.bak` (the older `index.html.bak` from the
earlier 37→32 slide trim is also still present, untouched).

## Old slide count

32 slides, single flat storyline: Problem & Replication Scope → Methodology & Experimental
Setup → Experimental Results & Analysis → Held-out Test Evidence → Replication Assessment &
Conclusion → Product Demo (placeholder-ish, positioned last, research-first framing).

## New main slide count

**Main deck (`index.html`): 29 slides** — 28 content slides (1–28) + 1 closing "Cảm ơn"/Q&A
slide (29). This is the only file presented in the 10–15 minute talk.

## Appendix slide count

**Appendix deck (`appendix.html`): 13 slides** (A–M, plus 1 cover slide not counted in the 13 —
same convention as the main deck's own title slide not being called out separately). Fully
split into its own HTML file (see Addendum below) so it never appears in, or inflates, the main
presentation's slide count.

**Total archived content: 42 slides** (29 main + 13 appendix), but the presentation flow a
viewer actually steps through is **29 slides**.

## Major structural changes

Storyline rebuilt from **Paper → Method → Experiment → Experiment → Experiment → Test → Demo**
(research-first) to **Motivation → Product Value → Product Packaging → Product Architecture →
Research Evidence → Held-out Test → Demo → Conclusion** (product-packaging-first,
research-backed), per the redesign brief. Six sections instead of five; Product Demo moved from
a trailing afterthought to Phần 5, positioned after all research evidence and before the final
Conclusion — no longer visually or narratively separate from the "product" story.

## New product-oriented slides (did not exist before)

- Slide 3 — Motivation (bài toán vận hành, framed as an operating decision, not a paper
  citation).
- Slide 4 — "FairDispatch phục vụ ai, mang lại value gì?" (3 user personas + 5 value bullets).
- Slide 5 — "FairDispatch là gì?" positioning (what it is / is not).
- Slide 6 — 5-module packaging (Data & Scenario, Simulation Engine, Policy Layer,
  Evaluation/Backtest, Operator Control Room).
- Slide 7 — Module Input/Process/Output table.
- Slide 8 — End-to-end architecture diagram (NYC TLC Data → ... → Control Room Demo).
- Slide 26 — Determinants slide (Technical skills / Product packaging / Engineering mindset),
  answering the manager's stated evaluation criteria directly and explicitly.

## Slides rewritten in place (content kept, framing changed)

- Policy Layer (slide 10): was a pure score-function table; now leads with 1-sentence business
  meaning per policy, formula moved to Phụ lục C.
- MOMAQL decision logic (slide 11), Metric Layer (slide 12): reused with lighter, more
  product-facing phrasing; numbers unchanged.
- Long-horizon (slide 16): the two old separate Validation charts (Utility line chart +
  Fairness/Gini line chart) compressed into **one** slide — Utility chart kept as the visual,
  the Gini/fairness reversal kept as a bold caveat line underneath (not deleted, not softened;
  the full Gini chart is preserved verbatim in Phụ lục J for anyone who wants to see it).
- Product Demo (slides 23–25): the old single "demo will be completed after the research is
  finalized" placeholder slide (already known to be stale) is now 3 real slides describing
  actually-implemented capabilities (Operator Control Room, continuous live-simulation
  playback, Why This Driver + Compare Policies), sourced from `05_SanPham_Demo/README.md` and
  `OPERATOR_CONTROL_ROOM_PLAN.md`.

## Slides moved to appendix (kept, not deleted)

| Appendix | Content | Was |
|---|---|---|
| A | Paper vs Implementation deviation table | old slide 7 |
| B | Simulator invariants & test suite | old slide 10 |
| C | 5 policy score functions (full formulas) | old slide 9 |
| D | R1 per-seed baseline (range bars) | old slide 15 |
| E | Empirical λ / Pareto sweep (scatter) | old slide 16 |
| F | Ablation per-seed summary (range bars) | old slide 18 |
| G | Variance / CV | old slide 19 |
| H | MLP benchmark details | old slide 20 |
| I | Full multi-horizon table (11 checkpoints) | old slide 23 |
| J | Long-horizon fairness line chart (full detail) | old slide 22 |
| K | Fleet-scale headline chart | old slide 26 |
| L | Fleet-scale raw table | old slide 27 |
| M | Reproducibility commands (new, lightweight — headline commands + TechDoc pointer) | new |

Two old slides were **not** carried forward even to the appendix, by design: the standalone
"Why Look-ahead Matters" mechanism-intuition slide (its idea is now folded into the MOMAQL
decision-logic slide) and the standalone "6-claim list" slide (redundant with the self-contained
Final Claim Matrix, which already names each claim in full).

## Demo slide updates

Replaced the outdated placeholder text ("Demo flow và product output sẽ được hoàn thiện sau
khi phần trình bày nghiên cứu hoàn tất") — no longer true, the demo is built and verified this
session — with 3 slides describing real, implemented capabilities: Operator Control Room
(map, Service Health, Fairness Guardrail, Alert Center, Run/Pause/Step), Live Simulation
(continuous clock, 0.5×–8× speed), Why This Driver + Compare Policies (real
`_score()` decomposition, replay-backed policy comparison). Each explicitly states the demo is
a decision-support prototype, not a production dispatch system, and that it uses the
Validation/demo slice by default, never `test.parquet`.

## Key numbers verified (unchanged from source, re-grepped after rebuild)

Raw Test 195,510 · Final evaluated 195,506 · Duration repaired 32 · Invalid zero-trip excluded
1 · Boundary excluded 3 · MOMAQL Validation Utility 1,422,441 / Gini 0.2037 · MOMAQL Test
Utility 1,454,053 / Gini 0.2011 · Full vs No-Forecast Utility Val +22.4% / Test +17.1% ·
Long-horizon Day 21 Val +5.1% / Test +1.2%, Day 37 Val +20.2% / Test +13.4% · "13/13 findings
generalized."

## Scientific wording checks (grepped post-rebuild)

- No instance of "6/6 paper claims reproduced" anywhere in the deck.
- C4 = **Not Reproduced** (paper column) everywhere it appears (main Final Claim Matrix slide
  22, appendix J footer).
- C5 = Partial — "Utility improves; Fairness does not improve (No Forecast fairer)" — exact
  required wording, no reversion to the old buggy "both improve" phrasing.
- C6 = Partial — "Inequality reproduced; Utility not reproduced" — exact required wording.
- "No Forecast is fairer than Full" stated explicitly on both the Validation ablation slide (15)
  and the held-out ablation slide (19).
- "MOMAQL is a balanced operating point, not fairness champion" — stated on slide 14
  (Validation baseline) in Vietnamese ("MOMAQL là điểm cân bằng mạnh — không phải policy công
  bằng nhất").
- Final verdict sentence — **"Strong Partial Trend Replication with held-out temporal
  support"** — appears verbatim on the Final Conclusion slide (28) and in the updated
  `speaker_notes.md` / presentation script.
- "Demo là decision-support prototype, không phải production dispatch system" — the one grep
  hit for the substring "production dispatch system" is this correct negation, not a violation.

## Files updated

- `04_Slide_Thuyet_Trinh/index.html` — full rewrite; then (Addendum) trimmed to exactly 29
  `<section class="slide">` blocks after the appendix split (see below). Tag balance verified:
  div/section/table/svg all open==close.
- `04_Slide_Thuyet_Trinh/speaker_notes.md` — full rewrite matching the new storyline, App/
  Product-manager tone, honest about limitations, explicit 13/13-vs-6/6 explanation; updated
  again in the Addendum to point at `appendix.html` as a separate file instead of "slides
  further down this deck."
- `04_Slide_Thuyet_Trinh/FairDispatch_Final_Presentation_Script_With_Heldout_Test.md` — full
  rewrite: slide-by-slide script for the 29-slide main deck, core message, simple concept
  explanations, key phrases, Q&A (including product-management questions: is the demo
  deployed, what would deploying it for real require), short (10–15 min) and full (20–25 min)
  versions.
- `04_Slide_Thuyet_Trinh/script.js` — one comment updated (Addendum) to describe the new
  two-file reality; no logic changed (see "Not changed" below).

## Files created

- `04_Slide_Thuyet_Trinh/appendix.html` (Addendum) — standalone deck, own `<head>`/title/cover
  slide, links back to `index.html`; loads the same `styles.css` and `script.js`.
- `04_Slide_Thuyet_Trinh/PRODUCT_ORIENTED_SLIDE_REDESIGN_CHANGELOG.md` — this file.
- Three timestamped `.bak` backups of the pre-redesign `index.html`, `styles.css`,
  `speaker_notes.md` (from before the storyline redesign; a separate untouched `index.html.bak`
  from the earlier 37→32 trim also still exists).

## Not changed

- `04_Slide_Thuyet_Trinh/styles.css` — no edits needed at any point. The existing palette
  (`--navy #17365D`, `--gray`, `--full`/`--noforecast`/`--nofairness`/`--laf`, Arial font) and
  component classes (`.claim-chip`, `.cards`/`.card`, `.table-wrap table.data`,
  `.flow`/`.flow-step`, `.status`, `.verdict-badge`, `.vchart`, `.statrows`) already match the
  design language of the manager's reference `Slide (1).html` closely enough that every new
  slide, in both `index.html` and `appendix.html`, could be built by reusing existing
  components — no new CSS classes were needed, and both files share the one stylesheet.
- `script.js`'s actual logic — untouched; it always counted whatever `.slide` elements exist in
  the page that loaded it, so splitting the appendix into its own file required **zero logic
  changes**: `index.html` now naturally shows "1 / 29", `appendix.html` naturally shows its own
  "1 / 14" — each file counts only its own slides. Only the stale explanatory comment (which
  used to say "main + former appendix... one continuous deck") was corrected to describe the
  two-file setup.

## Known limitations of this redesign pass

- No real browser screenshot was taken (no browser-automation tool available in this
  environment) — structural verification only (tag balance, grep-based content/wording checks).
  Recommend opening both `index.html` and `appendix.html` once in a real browser before
  presenting.
- The appendix count (13, A–M) is larger than the 8-item example list in the original redesign
  brief; this is intentional — every appendix slide maps to real, already-audited content from
  the prior 32-slide deck, and nothing was deleted outright, only relocated, consistent with
  this project's standing "never fabricate, never silently drop verified content" discipline.

---

## Addendum — split Appendix A–M into a separate `appendix.html` file

First redesign pass (above) put Appendix A–M inside `index.html` itself (slides 30–42 of a
42-slide single file). User feedback: presenting a 42-slide deck to an App/Product manager
looks too long at a glance, even if only 1–29 are actually walked through. Fixed:

1. **`index.html`** now contains exactly **29** `<section class="slide">` blocks (1–28 content
   + 29 "Cảm ơn"/Q&A) — the old Appendix A–M block (was lines ~652–1001) was cut entirely from
   this file. Verified: `grep -c 'class="slide"' index.html` → 29; div/table/svg tag balance
   still open==close after the cut.
2. **`appendix.html`** (new file) holds all 13 appendix slides verbatim — same content, same
   numbers, same wording, byte-identical HTML for each slide block — plus one new cover slide
   ("Phụ lục", subtitle explaining it's split from the main 29-slide deck, with a link back to
   `index.html`). Loads the same `styles.css` and `script.js` as the main deck, so it navigates
   (arrow keys, Home/End, prev/next buttons) exactly the same way.
3. Slide 29 ("Cảm ơn") in `index.html` gained one line: *"Appendix available separately if
   needed — xem `appendix.html` (Phụ lục A–M)."*, with an actual `<a href="appendix.html">`
   link.
4. `script.js` required **no logic change** (see "Not changed" above) — only its explanatory
   comment was corrected, since it previously (harmlessly, but now misleadingly) described a
   single-file "main + former appendix" setup that no longer matches reality.
5. `speaker_notes.md` updated: header now states the main talk is `index.html`'s 29 slides,
   and that Phụ lục A–M live in a separate `appendix.html`, opened only on request — not "slides
   further down the same deck."
6. Nothing in `FairDispatch_Final_Presentation_Script_With_Heldout_Test.md` needed changing —
   it already only scripted slides 1–29 and treated the appendix as reference material, never
   assigning it slide numbers 30+.

No raw numbers, wording, or scientific content changed in this pass — purely a file-structure
split. Re-verified after the split: banned-phrase grep clean, all key numbers and C4/C5/C6
exact wording still present and unchanged in both files.

---

## Addendum 2 — trim main deck 29 → 25 slides

User feedback: 29 slides still too long for a 10–15 min App/Product-manager talk. Fixed by
merging 4 slide-pairs/groups in `index.html` only — `appendix.html` and `script.js` untouched,
no experiment rerun, no number/conclusion changes.

**Old main slide count: 29** (28 content + 1 Cảm ơn/Q&A).
**New main slide count: 25** (24 content + 1 Cảm ơn/Q&A).

**Slides merged:**

| Old slides | Old content | New slide | New title |
|---|---|---|---|
| 4, 5, 6, 7 | Phục vụ ai/value gì + FairDispatch là gì + 5 module + Input/Process/Output | 4, 5 | "…phục vụ ai, mang lại value gì, và nó là gì?" / "Product Packaging: 5 module chính" (table Module→Input→Output, Process column dropped) |
| 9, 10 | Dispatch Engine + Policy Layer | 7 | "Dispatch Engine + Policy Layer: cùng engine, 5 cách chấm điểm khác nhau" |
| 21, 22 | Validation vs Test Summary + Final Claim Matrix | 18 | "13/13 findings generalized to Test — nhưng KHÔNG có nghĩa 6/6 claim paper reproduced" (single-column condensed claim table) |

("Why This Driver + Compare Policies" was already one slide from Addendum 1 — no merge needed
this pass.) Net: 4 slide-groups (10 old slides) → 3 new slides, −4 total.

All content the user flagged as must-keep (3 personas, positioning line, 5 modules table, batch/
ETA/Hungarian rule, 5-policy table, 13/13-vs-6/6 distinction, condensed C1–C6 verdicts incl.
C4 Not Reproduced / C5 Partial Utility✓ Fairness✗ / C6 Partial Inequality✓ Utility✗) preserved,
sentences trimmed rather than cut. No new slides added; no number or scientific-conclusion
changed. Post-edit QA: `grep -c 'class="slide' index.html` → 25; div/table/svg tag balance
open==close; zero hits for "6/6 paper claims reproduced"; C4/C5/C6 exact wording present;
"điểm cân bằng mạnh" (MOMAQL balanced-point) and "Test không dùng để tune" wording present.

**Files updated (this pass):**
- `04_Slide_Thuyet_Trinh/index.html` — 3 merge edits + 3 section-boundary comment fixes
  (`PHẦN 4` slide range 13-22→10-18, `PHẦN 5` 23-25→19-21, `PHẦN 6` 26-28→22-24).
- `04_Slide_Thuyet_Trinh/speaker_notes.md` — full rewrite, renumbered 1–25 matching new
  `index.html`, header states "25 slide chính."
- `04_Slide_Thuyet_Trinh/FairDispatch_Final_Presentation_Script_With_Heldout_Test.md` — full
  rewrite, renumbered 1–25, merged-slide scripts condensed, short/full version slide lists
  recomputed for 25 slides, "28 slide chính" references updated to 25.

**Not changed:** `appendix.html` (still 14: 1 cover + 13 A–M content), `script.js` (dynamic
per-document counting, no logic change needed — shows "1 / 25" automatically), `styles.css`.
**Total archived content:** 25 main + 14 appendix = 39; presentation flow a viewer steps
through is now **25 slides**.

---

## Addendum 3 — remove appendix from the presentation entirely, all-Vietnamese rewrite, single demo slide, add fleet-scale

User feedback: the 25-slide deck from Addendum 2 was still not right — section kickers used
English phase names (Motivation/Overview, Product Packaging, Research Evidence, Held-out
Test), a few AI-sounding phrases had crept in ("không tô hồng"), the demo was split across 3
slides, and a fleet-scale finding (forecast value depends on fleet size) that used to live only
in the appendix was missing from the main story. Fixed with a full rewrite of `index.html` —
same 25-slide budget, same numbers, same C1–C6 verdicts, no experiment rerun.

**Old main slide count: 25. New main slide count: 25** (structure changed, count unchanged).

**Appendix: removed from the presentation.** `appendix.html` is no longer linked or mentioned
anywhere in `index.html` (the old "Cảm ơn"/Q&A footnote pointing to it is gone). The file
itself was **left on disk, untouched**, rather than deleted — it is simply outside the
presented flow now, per the user's own instruction to prefer "để nguyên file nhưng không
link/nhắc tới" over destroying prior verified content. If it is truly no longer wanted, deleting
`appendix.html` is a separate, explicit follow-up the user can request.

**Demo slides reduced:** 3 (Operator Control Room / Live Simulation / Why This Driver +
Compare) → **1** single "DEMO" slide (new slide 22), short bullet list only, presenter demos
live instead of walking through slides.

**Fleet-scale headline slide added:** new slide 16, brought forward from the old Phụ lục K
chart (`reports/fleet_scale_results.csv`, 3 seed) — Utility advantage of Full vs No-Forecast:
100 drivers +41,9%, 200 drivers +23,3%, 400 drivers +0,01% (~0%). Same real numbers as the
appendix chart, no new computation.

**Removed:** the standalone "Trước khi mở khóa Test / freeze protocol / Data Quality Gate"
slide (old slide 17, with its 195.510→195.506 row-count table) — the underlying idea ("Test
không dùng để chọn tham số") is now folded as a one-line note into the data-and-test slide
(new slide 12) and the Test-intro slide (new slide 17), per explicit instruction not to spend a
whole slide on freeze-protocol mechanics.

**All section titles rewritten in Vietnamese** — kickers now read "Phần 1 · Bài toán và mục
tiêu", "Phần 2 · Hệ thống FairDispatch", "Phần 3 · Cách điều phối và chỉ số đánh giá", "Phần 4 ·
Kết quả thực nghiệm", "Phần 5 · Demo sản phẩm", "Phần 6 · Giới hạn và kết luận" — no more
English phase names (Motivation/Overview, Product Packaging, Product Architecture, Research
Evidence, Held-out Test, Conclusion) anywhere in the deck.

**English terms explained in parentheses on first use:** Utility (hiệu quả tổng thể), Fairness
(công bằng thu nhập), Gini (độ chênh lệch thu nhập), Hungarian Assignment (thuật toán ghép tối
ưu), Deadhead (quãng đường chạy rỗng), Look-ahead (nhìn trước tương lai), Generalize (giữ cùng
xu hướng khi chuyển sang dữ liệu mới). Policy names (Greedy/Nearest/LAF/REASSIGN/MOMAQL) kept
as proper names with a one-clause description, not translated. Bare English "policy" replaced
with "chiến lược điều phối" throughout body copy.

**AI-sounding phrases removed:** "Không tô hồng" (old slide-27 title), "manager-facing",
"robust behavior" — none of these appear anywhere in the new file. The Final Claim Matrix
(new slide 21) header row now reads "Nội dung kiểm chứng / Kết quả" in plain Vietnamese instead
of "Claim / Paper Replication Verdict".

**Determinants slide removed:** the old "Technical skills / Product packaging / Engineering
mindset" table (old slide 22) is gone — its content is not required by the new structure and
the literal English determinant names were explicitly flagged as not to appear as slide
content.

Content the user flagged as must-keep is still present, just relocated: Utility/Fairness
trade-off (slide 3), 3 personas + value (slide 4), positioning (slide 5), 5-part packaging
(slide 6), architecture flow (slide 7), simulator mechanics (slide 8), 5-policy table (slide
9), MOMAQL formula (slide 10), metrics (slide 11), Train/Val/Test counts (slide 12), MOMAQL
balance point + scatter chart (slide 13), forecast ablation (slide 14), long-horizon (slide
15), fleet-scale (slide 16, new), Test intro (slide 17), Test baseline/ablation/long-horizon
(slides 18–20), condensed C1–C6 claim table (slide 21), demo (slide 22), limitations + next
steps (slide 23), 6-point conclusion + frozen verdict sentence as a small closing line, not a
headline (slide 24), thank-you (slide 25).

**Post-edit QA (grepped after rebuild):**
- `grep -c 'class="slide' index.html` → **25**.
- Zero hits for "appendix" or "phụ lục" (case-insensitive) anywhere in `index.html`.
- Exactly 1 slide titled "DEMO".
- Exactly 1 fleet-scale slide (100/200/400 driver bars).
- Zero hits for "không tô hồng", "không bịa", "robust behavior", "manager-facing", "6/6 paper
  claims reproduced", "Forecast improves fairness", "No Fairness increases Utility".
- Zero hits for the English phase titles (Motivation / Overview, Product Packaging, Research
  Evidence, Held-out Test) and for "Technical skills"/"Engineering mindset" as slide content.
- C4 = "Chưa đạt" (red/`status not`), C5 = "Đạt Utility, chưa đạt Fairness" (amber), C6 = "Đạt
  phần bất bình đẳng, chưa đạt phần Utility" (amber) — all present, unchanged in meaning from
  the frozen C4/C5/C6 wording used in every prior round.
- Verdict sentence "Strong Partial Trend Replication with held-out temporal support" present
  once, as a small closing note under the Slide 24 conclusion list, not as the slide headline.
- Key numbers re-verified present and unchanged: 195.510 / 195.508 / 912.375 · 1.422.441 /
  0,2037 · 1.454.053 / 0,2011 · +22,4% / +17,1% · +5,1% / +20,2% / +1,2% / +13,4% · 13/13 ·
  +41,9% / +23,3% / +0,01%.
- div/section/table/svg/ul/ol tag balance: all open == close.

**Files updated (this pass):**
- `04_Slide_Thuyet_Trinh/index.html` — full rewrite (25 slides, single deck, all Vietnamese
  section titles, no appendix references).
- `04_Slide_Thuyet_Trinh/speaker_notes.md` — full rewrite matching the new 25-slide structure
  and section names.
- `04_Slide_Thuyet_Trinh/FairDispatch_Final_Presentation_Script_With_Heldout_Test.md` — full
  rewrite, same treatment.
- `04_Slide_Thuyet_Trinh/PRODUCT_ORIENTED_SLIDE_REDESIGN_CHANGELOG.md` — this addendum.

**Not changed:** `04_Slide_Thuyet_Trinh/styles.css` (no new CSS classes needed — every new
slide reuses existing components: `.cards`, `.table-wrap table.data`, `.flow`, `.vchart`,
`.chart-svg-wrap`, `.status`, `.two-col`, `.title-slide`); `04_Slide_Thuyet_Trinh/script.js`
(dynamic per-document slide counting, unaffected by content changes); `appendix.html` (left on
disk, 14 slides, simply no longer part of the presented flow — see above).

---

## Addendum 4 — drop the C1–C6 claim-assessment slide, wording softened to "xu hướng" (trend) first

Two small follow-up rounds after Addendum 3, both on user feedback while reviewing the
rendered deck.

**Round A — soften C1–C6 wording.** User felt "Đạt / Chưa đạt" (pass/fail) on the claim table
(old slide 21) read too strict for a trend-level result. Reworded the whole table from binary
pass/fail language to trend language, same underlying verdicts, no scientific-conclusion
change:

| Claim | Old wording | New wording |
|---|---|---|
| C1 | Đạt | Đúng xu hướng |
| C2 | Đạt trong phạm vi baseline đã dựng | Đúng xu hướng, trong phạm vi baseline đã dựng |
| C3 | Đạt một phần | Đúng xu hướng một phần |
| C4 | Chưa đạt | Không thấy xu hướng này |
| C5 | Đạt Utility, chưa đạt Fairness | Utility đúng xu hướng, Fairness thì không |
| C6 | Đạt phần bất bình đẳng, chưa đạt phần Utility | Bất bình đẳng đúng xu hướng, Utility thì không |

Table header changed from "Kết quả" to "Xu hướng quan sát được"; the note under the table
changed from "không phải mọi tuyên bố đều được xác nhận" to "không phải mọi xu hướng đều khớp".
Same edit applied to `speaker_notes.md` and the presentation script (Slide 21 section + Q&A
Q4). C4 still reads as the one claim that did not hold, C5/C6 still split Utility vs Fairness —
only the surface wording softened.

**Round B — remove the slide entirely.** User then decided the slide (softened or not) wasn't
needed. Cut outright: **old slide 21 (C1–C6 claim-assessment table) removed from
`index.html`.** Everything after it shifted down by one:

| Old slide # | New slide # | Content |
|---|---|---|
| 22 (DEMO) | 21 | unchanged |
| 23 (Giới hạn và hướng phát triển) | 22 | unchanged |
| 24 (Kết luận) | 23 | unchanged |
| 25 (Cảm ơn) | 24 | unchanged |

**New main slide count: 24** (down from 25). No other slide content, number, or wording
changed. The "13/13 xu hướng chính giữ cùng chiều trên Test" finding (slide 17, slide 23
conclusion) is untouched — it was never dependent on the removed claim table, it is a
standalone finding about trend stability, not a per-claim breakdown.

**Post-edit QA:** `grep -c 'class="slide' index.html` → **24**; div/section/table/svg/ul/ol tag
balance open==close; zero hits for "appendix", "phụ lục", or any claim-table leftover
(`test_claim_assessment`, "Nội dung kiểm chứng") in `index.html`; verdict sentence "Strong
Partial Trend Replication with held-out temporal support" present once in `index.html`,
`speaker_notes.md`, and the presentation script; key numbers (195.510, 912.375, 1.422.441,
1.454.053, +22,4%, +17,1%, 13/13, +41,9%) all still present and unchanged.

**Files updated (this round):**
- `04_Slide_Thuyet_Trinh/index.html` — removed the C1–C6 slide, renumbered comment headers for
  Phần 5 (slide 22→21) and Phần 6 (slide 23-24→22-23).
- `04_Slide_Thuyet_Trinh/speaker_notes.md` — removed the Slide 21 section, renumbered Phần
  4/5/6 headers and all slide numbers from 21 onward, reworded Q4 to not reference a removed
  slide.
- `04_Slide_Thuyet_Trinh/FairDispatch_Final_Presentation_Script_With_Heldout_Test.md` — same
  treatment: removed the Slide 21 script paragraph, renumbered Phần 4/5/6 and all slide
  references, updated the "13/13 ≠ paper fully confirmed" explanation in Section 1 to drop its
  now-invalid "xem ở Slide 21" pointer, all "25 slide" → "24 slide" references updated.

**Not changed:** `appendix.html`, `styles.css`, `script.js` (dynamic per-document slide
counting — `index.html` now shows "1 / 24" with no code change needed).
