# Vietnamese UI Final Audit — English Leakage Check

Re-scanned all 4 frontend files (`05_SanPham_Demo` and `06_Deployed`,
`index.html` + `app.js`) after translation, using a quoted-string-literal
scanner (flags any ASCII quoted string ≥3 letters with no Vietnamese
diacritics), then manually classified every one of the ~740 raw candidates.
Also re-verified with a second, stricter pass (`test_frontend_vietnamese_ui.py`,
committed as a permanent test) that checks the prompt's specific 20-phrase
forbidden list against *visible HTML text* and *comment-stripped JS* only —
this is the check that actually runs in CI/local test suites going forward.

## Allowed (stays English)

- Canonical names: `FairDispatch`, `MOMAQL`, `Greedy`, `Nearest`, `LAF`,
  `Exact REASSIGN`, `NYC TLC 2013`.
- Technical/API identifiers: JSON field names, endpoint paths
  (`/simulations`, `/replay/ablation`, …), DOM element ids, JS variable/
  function names, CSS class names, file names, SHA-256 hashes.
- Source-code comments (not rendered to any user).
- `Seed` label and `λ`/`γ`/`α` parameter symbols — technical parameter
  identifiers, not prose.

## Not allowed — result

**User-facing English leakage: 0.**

Verified two ways:
1. `test_frontend_vietnamese_ui.py` (new, in both `06_Deployed/tests/` and
   `05_SanPham_Demo/backend/`) — parametrized over `index.html` (visible
   text only, tags/attributes stripped) and `app.js` (comments stripped) —
   checks the prompt's 20-phrase forbidden list. **0 hits**, both products.
2. Manual review of the full raw candidate list (740 quoted-string
   literals across all 4 files) — every remaining item is a DOM id, CSS
   class, JS identifier, code comment, or an allowed canonical/technical
   term. No rendered prose in English remains.

## Backend (Python) leakage

Separately audited `app.py` / `engine_adapter.py` / `replay_adapter.py` in
both products for a pre-existing pattern specific to this codebase:
Vietnamese error messages typed without diacritics (e.g. `"request_limit
vuot gioi han..."`). Found and fixed 20 such messages across both products
(validation errors, 404s, concurrent-step lock message, FastAPI title,
one endpoint docstring shown in `/docs`). Left untouched: `replay_adapter.py`'s
`engine_source.note` and `"label": "VERIFIED TEST EXPERIMENT"` fields —
confirmed via `grep` that `app.js` never reads `.note` or `.label` from
these responses, so they are backend/provenance audit metadata, not
rendered UI copy (same treatment as hashes/commit references under rule
1.1/§12 of the task).

## Verdict

**LOCAL VIETNAMESE UI COMPLETE.**
