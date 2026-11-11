# Design Notes

## B2 — idempotency key

State exactly what key your `cost_tag_check.py` uses to decide whether two resources in the
same run are "the same" for dedup purposes, and why running it twice against an unchanged
plan file produces identical output and exit code without the script keeping any record
between runs. Use the word "idempotency" in your explanation.

**The idempotency key is the Terraform resource `address`** (`resource_changes[].address`, for
example `aws_s3_bucket.listing_media` or `aws_s3_bucket.landlord_media[0]`, including any
`module.` prefix and the `[index]` or `["key"]` instance suffix).

Why `address`:
- It's Terraform's own unique identity for a resource instance within a plan. Two entries with
  the same address are the same resource, and two different addresses are always different
  resources, even when they share `type`, `name` or bucket name.
- `type` or `name` alone would merge different instances (`landlord_media[0]` vs
  `landlord_media[1]`). The bucket name or function name isn't always known at plan time, and two
  resources could share it.

How idempotency is guaranteed with no state between runs:
1. **Dedup within a run.** Checked and missing resources are collected into `set`s keyed by
   `address`, so if the same address appears more than once in `resource_changes` it's counted
   and printed once (`test_duplicate_address_in_one_plan_is_reported_once`).
2. **Deterministic output.** Missing addresses are printed `sorted()`, so the output doesn't
   depend on JSON order (`test_output_is_independent_of_input_order`).
3. **Pure function of the input.** `check_plan()` only reads the plan file. It writes no files,
   keeps no cache or "already reported" list, and reads no clock, environment or random value.
   The output and exit code depend only on the file's contents, so running it again against an
   unchanged plan gives byte-identical output and the same exit code. In `TERMINAL_LOG.md`, both
   runs produce the same SHA-256 hash and exit 1.

Keeping a record of already-reported resources between runs would actually *break* idempotency.
The second run would print nothing and could flip from fail to pass on an unchanged plan.

## Any other decision with a non-obvious alternative

**Access control: boundary = LandlordAccount, resolved by walking the hierarchy.**
`ScreeningReport` and `Tenant` don't carry `landlord_account_id`, so access is decided by
`report.tenant_id → Tenant.property_id → Property.landlord_account_id == actor.landlord_account_id`.
- *Alternative:* compare tenant or property IDs, or add `landlord_account_id` to the report.
  Rejected. The README says the landlord account is the scope, and the models and seed data must
  not be modified. Denormalising the ID onto the report would also create a second source of
  truth that can drift.

**Access control: duplicate or ambiguous IDs fail closed.**
If more than one tenant (or property) matches an ID, access is denied instead of trusting the
first match.
- *Alternative:* `next()` on the first match. Simpler, but list order would then decide a
  security outcome (`test_fails_closed_when_tenant_id_is_ambiguous`). An empty
  `landlord_account_id` on either side also denies, so `"" == ""` can never grant access.

**Tag check: which actions are checked.**
A resource is checked if `change.actions` contains `create` or `update` **and** `after` is an
object. This includes replace (`["delete","create"]`), because a replacement is a new resource
that must be tagged. `no-op`, `read` and pure `delete` (`after: null`) are skipped.
- *Alternative:* require `actions == ["create"]` or `["update"]` exactly. That would let replaced
  resources through untagged (`test_replace_action_is_checked`).

**Tag check: `tags` OR `tags_all` satisfies the requirement.**
Tags inherited from the provider's `default_tags` appear only in `tags_all`, and AWS cost
allocation uses the effective tag set.
- *Alternative:* `tags` only. Stricter (it forces an explicit per-resource tag), but it would
  wrongly fail correctly billed resources that use `default_tags`, which is the idiomatic pattern
  for this.

**Tag check: what counts as "missing".**
An absent key, a `null` tag map, or a blank or whitespace value all count as missing. Any other
tag (`tenant_id`, `property_id`) is ignored. This is the README's "ID on hand" trap:
`listing_media` is tagged `tenant_id` and fails.
- *Alternative:* validate the value against known landlord account IDs. That's a stronger check,
  but it needs a source of truth for valid accounts that the plan doesn't contain. I left it as
  a follow-up.

**Tag check: exit codes.** `0` pass, `1` missing tag, `2` unreadable or invalid plan. A broken
plan file fails closed and is distinguishable from a tagging failure in CI.

**Tag check: resources that can't be tagged are not exempted.**
Every created or updated resource is held to the rule. In a real plan that would also flag
resource types with no `tags` argument (for example `aws_s3_bucket_lifecycle_configuration`).
- *Alternative:* skip resources whose `after` has no `tags` key, or keep an allowlist of
  untaggable types. That's the right next step for real plans, but it isn't needed for this
  fixture. An implicit skip based on a missing key would risk silently passing a taggable
  resource whose tags were simply omitted, so I'd use an explicit, reviewed allowlist instead.

**B0: `for_each` + `moved` blocks rather than `terraform state mv`.**
`moved` blocks are declarative and reviewed in the PR, and they apply in every environment and
workspace automatically. `state mv` is a manual, per-environment step that's easy to miss.

**B1: Intelligent-Tiering rather than Standard-IA as the first tier for sold photos.**
Standard-IA still has a 30-day minimum duration. Intelligent-Tiering has none, which removes
early-delete risk completely during the deletion-request window, at the cost of a small
per-object monitoring fee.
