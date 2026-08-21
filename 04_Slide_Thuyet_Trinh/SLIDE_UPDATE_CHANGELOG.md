# Slide Deck Update Changelog — Held-out Test Integration

No experiment rerun. No raw numerical value changed. `index.html` edited in place;
original backed up to `index.html.bak` before any edit. `script.js` unchanged —
slide counter/nav count `.slide` sections dynamically, so no code change needed
for the new slide count.

## Slide count

32 → **37** slides (target was ~28–32; 5 net new slides added, none removed,
under the explicit hard cap of 40). Breakdown of the 5 new slides:

1. Test Data Quality Gate (inserted after "Dataset & Protocol", Phần 2)
2. Held-out Test — Freeze + Baseline (Phần 4, new)
3. Held-out Test — Ablation (Phần 4, new)
4. Held-out Test — Long-Horizon (Phần 4, new)
5. Validation vs Test Summary (Phần 4, new)

## Slides added

- **Test Data Quality Gate** — raw 195,510 → boundary-excluded 3 → repaired 32
  (kept) → excluded 1 → final 195,506; states raw checksum immutable and rule
  decided before any policy ran on Test.
- **Held-out Baseline** — MOMAQL Validation (1,422,441 / 0.2037) vs Test
  (1,454,053 / 0.2011) side by side; "operating point stable" framing.
- **Held-out Ablation** — Full vs No-Forecast Utility (Val +22.4% / Test
  +17.1%); No-Forecast fairer on both splits; No-Fairness worse inequality
  and lower Utility on both.
- **Held-out Long-Horizon** — Day 21 (Val +5.1% / Test +1.2%), Day 37 (Val
  +20.2% / Test +13.4%).
- **Validation vs Test Summary** — headline "13/13 findings generalized
  directionally" + explicit caveat (with the C4 worked example) that this is
  not the same as all paper claims being reproduced.

## Slides moved

None physically relocated — Product Demo (now labeled Phần 6) was already
positioned after the final scientific-conclusion slides (Claim Matrix,
Limitations & Conclusion), so no reorder was needed there. The 5 new Test
slides were inserted as a new Phần 4, between existing Validation results
(Phần 3, ends at Fleet-Scale Raw) and the existing Replication Assessment
section (now Phần 5), so Test results sit in narrative position — not
appended mechanically at the end.

## Slides removed

None.

## Claim matrix slide (was Slide 28) — rebuilt

Table changed from 1 verdict column to 2 independent columns matching
`final_test/test_claim_assessment.csv` exactly:

| Claim | Held-out Test | Paper Replication |
|---|---|---|
| C1 | Generalized | Reproduced |
| C2 | Generalized | Reproduced (adapted-baseline scope) |
| C3 | Generalized | Partially Reproduced — strengthened by Test |
| C4 | Generalized* | **Not Reproduced** |
| C5 | Generalized | Partial — Utility improves; Fairness does not improve (No Forecast fairer) |
| C6 | Generalized | Partial — Inequality reproduced; Utility not reproduced |

`*` footnote on C4 explains it is the *discrepancy with the paper* that
generalizes, not the paper's own claim. The banned phrase "6/6 paper claims
reproduced" does not appear anywhere in the deck; the old single-column
verdict slide's "6/6 claim đã được kiểm thử" framing is preserved only where
it means "tested", never "reproduced" (also fixed in the closing slides).

## Other text fixes for consistency

- Agenda slide: added Phần 4 "Held-out Test Evidence" between Results and
  Replication Assessment; Product Demo renumbered to Phần 6.
- Limitations & Conclusion slide: final verdict updated to the exact required
  sentence — **"Strong Partial Trend Replication with held-out temporal
  support"** — with a Strong/Partial/held-out-temporal-support explanation
  clause.
- Overall Project Conclusion slide: added "13/13 phát hiện xác nhận lại trên
  held-out Test sau khi freeze"; verdict badge updated to the same exact
  sentence.

## Design guidelines followed

Reused the deck's existing visual language only (`.claim-chip`, `.table-wrap
table.data`, `.status.reproduced/.partial/.not`, `.verdict-badge`) — no new
colors, no gradients, no icons, no dense tables beyond what the existing deck
already uses. No `final_test/figures/*.png` were embedded as images (the deck
draws its own inline SVG/HTML charts elsewhere); the new Test slides use the
same hand-built HTML table/badge components as the rest of the deck for
visual consistency, kept deliberately simple (few rows, no dashboard-ification).

## Product Demo

Left as the existing single placeholder slide — its own on-slide note already
states "chưa audit sản phẩm đầu ra — không tự invent chi tiết". Expanding it
to 2–3 slides would require inventing demo content not present in any
`final_test/` or `reports/` artifact, which violates the project's no-fabrication
rule; deferred until the product demo itself is audited.

## speaker_notes.md

Updated: header now says 37 slides and flags that the old per-slide numbering
(1/32 … 32/32) no longer matches physical position after the 5 insertions —
points to the new `FairDispatch_Final_Presentation_Script_With_Heldout_Test.md`
(Prompt 4 deliverable) as the authoritative numbered script. Added a new
"PHẦN 4 (MỚI) — Held-out Test Evidence" notes section (Purpose/What to
say/Caveat per new slide) and rewrote the Claim-by-Claim slide's notes to
match the new dual-column table and the exact C5 wording fix.

## No rerun confirmation

Confirmed — only `index.html` and `speaker_notes.md` (presentation assets)
were edited. No script under `scripts/final_test/` was executed, no CSV under
`final_test/` or `reports/` was modified.

---

## Addendum — second pass: trim to 32 slides (user request)

Per explicit user request, removed 5 more slides from the 37-slide deck built
above, bringing it back to **32 slides** (matching the original ~28–32
target). No numbers changed — only slide-level content removed and 4 stale
in-deck cross-references (footer/note pointers using hardcoded slide numbers)
fixed.

**Removed:**
- Slide 12 — "Công thức đầy đủ: project score & TD(0) update" (formula detail
  slide; the high-level score explanation stays on the MOMAQL Decision Logic
  slide, full TD(0) formula now pointed to the source file instead).
- Slide 14 — Test Data Quality Gate (the raw/repaired/excluded/final numbers
  are still spoken, per the updated speaker script, during the Dataset &
  Protocol slide or the Held-out Baseline slide — not shown on their own
  slide anymore).
- Slide 25 — Mechanism Probe (policy disagreement / |ΔQ| bars).
- Slide 26 — Mechanism Diagnostics chi tiết (Q-table convergence, weekly-cycle
  hypothesis, spatial candidate pool).
- Slide 32 — Validation vs Test Summary (the "13/13 generalized ≠ 6/6
  reproduced" caveat, with the C4 worked example, is still carried by the
  Claim Matrix slide's own note paragraph and by the speaker script — not
  lost, just no longer a standalone slide).

**Stale references fixed** (all were pointing at now-removed or renumbered
slides; fixed to either a generic "slide sau" pointer or a direct source-code
pointer, to avoid the same fragility on a future edit):
- "Why Look-ahead Matters" slide footer: was "kiểm chứng ở Mechanism Probe
  (slide 24)" (Mechanism Probe removed) → reworded to a generic Phần-3
  pointer.
- "5 Policy Definitions" slide, MOMAQL row: was "Xem slide 12" (removed) →
  "Xem slide sau".
- "MOMAQL Decision Logic" slide note: was "Công thức đầy đủ + TD(0) update:
  slide 12" (removed) → now points to `src/policies.py, class MOMAQLPolicy`
  directly.
- Long-horizon Utility slide source line: was "bảng đầy đủ: slide 23" (target
  renumbered) → "bảng đầy đủ: slide sau".

Verified after removal: 32 `<section class="slide">` blocks, tag balance
clean (div/section/table open==close), no remaining hardcoded `slide N`
references left dangling (`grep "slide [0-9]" index.html` → empty).

`speaker_notes.md` and `FairDispatch_Final_Presentation_Script_With_Heldout_Test.md`
both updated to the new 32-slide numbering; the speaker script is the
authoritative numbered reference going forward.
