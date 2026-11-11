# B2 — AI conversation record

**Tool:** Claude Code (VS Code extension), model Claude Opus 5.5, used for the whole assessment
in one session, recorded on screen.
**Scope of this file:** the B2 part of the session (prompts, what the AI produced, what was
reviewed and changed). The complete raw session transcript is exported alongside as
`full-session-export.txt` (see the note at the bottom).

---

## 1. Context the AI was given

Before any B2 code, the AI read the full starter repo (README, models, seed data, stubs, tests,
fixture) and summarized for me the README points that change the B2 design. I then said these
aloud on the recording:

1. `LandlordAccount` is the billing unit, and a `PropertyManager` is scoped to exactly one. The
   access boundary is the landlord account, not tenant or property.
2. The README warns the existing code uses "whatever ID happened to be on hand". So the cost-tag
   check must require `landlord_account_id`, and a `tenant_id` tag (as on
   `aws_s3_bucket.listing_media`) must still fail.
3. `ScreeningReport` and `Tenant` don't carry `landlord_account_id`, so access has to walk
   report → tenant → property → landlord account and fail closed if any link is missing.
4. Seed data, models, `plan.json` and tfstate must not be modified. Tests use conftest
   fixtures, and custom plans use `tmp_path`.

## 2. Prompt

> **Me:** "said it" *(confirming the README narration above, so the AI could start B2)*

## 3. AI output — B2 part 1 (access control)

The AI wrote `app/access_control.py`:
- `_find_unique()` returns a record only if **exactly one** matches the ID. Absent **or
  duplicated** IDs return `None`.
- `_owning_landlord_account_id()` walks `report.tenant_id → tenant.property_id →
  property.landlord_account_id`.
- `can_access_screening_report()` denies if the actor or report is `None`, if the actor's
  account ID is empty, or if the owning account can't be resolved. Otherwise it compares account
  IDs.

Tests (`tests/test_access_control.py`, 10 cases): pm-001 → rep-002 **denied**, pm-001 →
rep-001 **allowed**, the full 2×2 pm/rep matrix, missing tenant, missing property, duplicate
tenant ID pointing at another account, and a property with an empty `landlord_account_id`.

Result: `10 passed`. Committed as `B2.1: gate screening-report access on owning LandlordAccount, fail closed`.

## 4. AI output — B2 part 2 (cost-tag check)

The AI wrote `scripts/cost_tag_check.py`:
- `REQUIRED_TAG = "landlord_account_id"`. Other tags are never accepted as substitutes.
- A resource is checked when `change.actions` includes `create` or `update` (so replace counts)
  **and** `after` is an object. `no-op`, `read` and pure `delete` (`after: null`) are skipped.
- Passes if `tags` or `tags_all` has a non-blank `landlord_account_id`.
- **Idempotency key = resource `address`**. Checked and missing resources go into sets keyed by
  address, and the output is `sorted()`. There's no state between runs.
- Exit codes: 0 pass, 1 missing tag, 2 unreadable plan (fail closed).

Tests (`tests/test_cost_tag_check.py`, 12 cases): the fixture flags exactly `listing_media` and
`mls_feed_sync`; passes `landlord_media[0]` and `screening_report_export`; `tenant_id` isn't a
substitute; no-op and delete are ignored; two runs give identical output and code; a duplicate
address is reported once; output doesn't depend on input order; an all-tagged plan passes;
replace is checked; blank or null tags fail; `default_tags` via `tags_all` passes; a bad or
missing file fails closed.

First run: `22 passed`.

## 5. Error the AI made — caught and fixed

**What the AI wrote** (in `test_fixture_noop_and_delete_entries_are_ignored_without_crashing`):

```python
assert "4 resource(s)" not in out or "2 of 4" in out  # only the 4 create/update entries counted
assert "2 of 4" in out
```

**What was wrong:** the first assertion is a **tautology**. The output line is
`FAIL: 2 of 4 resource(s) ...`, which always contains both `"4 resource(s)"` and `"2 of 4"`,
so the `or` makes it pass regardless and it verifies nothing. The comment claimed it checked
"only the 4 create/update entries counted", but it didn't. The test suite was green, which is
exactly why this kind of mistake gets through.

**How it was caught:** by re-reading the AI-generated test file line by line before
committing, instead of trusting the green test run. (This was spotted while reviewing the AI's
own output in the session, before the commit.)

**Fix:**

```python
# 6 entries in the fixture; only the 4 create/update ones are counted. If no-op or delete
# were checked, this would read "of 5" / "of 6" (and archive_media would be flagged).
assert "2 of 4 resource(s)" in out
```

**Proof the fixed test actually works (mutation check):** temporarily changed
`CHECKED_ACTIONS` to `{"create", "update", "no-op"}` and re-ran the test. It **failed**
(`archive_media` appeared in the output, `FAIL: 3 of ...`). Then reverted, and all 22 pass. See
`logs/08_b2_mutation_check.txt` and `TERMINAL_LOG.md` §8.

Committed together with part 2 as
`B2.2: idempotent landlord_account_id cost-tag check keyed by resource address`
(the commit message records the fix).

## 6. Other AI suggestions I checked rather than accepted blindly

- **`tags_all` accepted as well as `tags`.** I checked this is correct: `default_tags` from the
  provider only show up in `tags_all`, and billing uses effective tags. Kept, and the alternative
  is documented in `DESIGN_NOTES.md`.
- **Replace = `["delete","create"]` is checked.** I confirmed that the docstring's "create or
  update" should cover replacements, since they are new resources. Kept, with a test.
- **Resources without a `tags` attribute are flagged, not skipped.** This is intentional for
  now. An explicit allowlist of untaggable types is noted as the follow-up in `DESIGN_NOTES.md`.

---

### Full transcript
The complete, unedited session export (all prompts and AI outputs, including B0/B1 and setup)
is in `full-session-export.txt`, produced with Claude Code's `/export` command at the end of the
session.
