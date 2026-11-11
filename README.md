# Haven — Platform Infrastructure Assessment

Haven is a multi-tenant real estate platform.

## Domain model

```
LandlordAccount  (the billing unit)
  └── Property
        └── Tenant
              └── ScreeningReport  (SSN, credit score)

PropertyManager  (scoped to exactly one LandlordAccount)
```

A `LandlordAccount` is the billing unit — every property, every tenant, every report underneath
it rolls up to exactly one. A `PropertyManager` is scoped to exactly one `LandlordAccount` and
everything under it.

This codebase currently tags and checks access using whatever ID happened to be on hand when
each piece was written — that reflects how it was built, not a spec to replicate.

## What not to modify

`app/seed_data.py`, `app/models.py`, `fixtures/plan.json`, `terraform/terraform.tfstate` — the
assignment's checks assume this data is unchanged.

`terraform/terraform.tfstate` is checked in deliberately, not an accident — it's a seeded state
representing 4 already-provisioned landlord media buckets, standing in for a real AWS account so
B0 can be reproduced with `terraform plan` instead of just reasoned about. See `terraform/main.tf`
for how to use it.

## Where things are

| Path | Task |
|---|---|
| `terraform/main.tf` | B0 |
| `terraform/lifecycle.tf` | B1 |
| `app/access_control.py`, `scripts/cost_tag_check.py` | B2 — stubs to implement |

---

## Submission — Sameer Khan

**Screen recording (continuous, unedited, narrated):** [Google Drive — screen recording](https://drive.google.com/drive/folders/1e4WX3aAOob0nOtnqxnIyzjT8Tc7LKJcP?usp=sharing)

| Deliverable | Where |
|---|---|
| B0 — `count` trap: answer + `for_each`/`moved` fix | [`B0.md`](B0.md), [`terraform/main.tf`](terraform/main.tf) |
| B1 — Glacier early-deletion cost + lifecycle redesign | [`B1.md`](B1.md), [`terraform/lifecycle.tf`](terraform/lifecycle.tf) |
| B2.1 — screening-report access check | [`app/access_control.py`](app/access_control.py), [`tests/test_access_control.py`](tests/test_access_control.py) |
| B2.2 — idempotent `landlord_account_id` cost-tag check | [`scripts/cost_tag_check.py`](scripts/cost_tag_check.py), [`tests/test_cost_tag_check.py`](tests/test_cost_tag_check.py) |
| Idempotency key + design decisions | [`DESIGN_NOTES.md`](DESIGN_NOTES.md) |
| Setup output, both B2 test runs, tag check run twice | [`TERMINAL_LOG.md`](TERMINAL_LOG.md) (raw captures in [`logs/`](logs/)) |
| AI prompts/output for B2, incl. an AI error caught and fixed | [`.ai-conversations/`](.ai-conversations/) |

### Reproduce

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m pytest -v                               # 22 passed
.venv\Scripts\python scripts/cost_tag_check.py fixtures/plan.json  # exits 1: listing_media, mls_feed_sync
cd terraform; terraform init; terraform plan -refresh=false     # 4 moved, 0 to destroy
```
