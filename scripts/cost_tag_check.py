"""
B2, part 2 — implement the cost-tagging check.

Read fixtures/plan.json for the shape of a `terraform show -json` plan: a `resource_changes`
list, where each entry has a `type`, an `address`, and `change.after.tags`.

Implement check_plan() so it:
  - Looks at every resource being created or updated (skip anything whose change.actions
    isn't "create" or "update" — a "no-op"/"read" change, or a "delete" with no `after`
    block at all).
  - Fails (returns a non-zero exit code) if the resource is missing the tag that identifies
    the real billing unit, per README.md's domain model — not whatever tag the resource
    happens to already carry.
  - Is idempotent: running this twice against the same plan file produces the same result,
    with no duplicate output and no flipped pass/fail. This is about a single run being
    stable and repeatable — it does not require remembering anything between runs.
  - Prints which specific resource address(es) are missing the tag.

Run manually: python scripts/cost_tag_check.py fixtures/plan.json

Exit codes: 0 = all checked resources tagged, 1 = at least one missing the tag,
2 = the plan file couldn't be read or parsed (fail closed, never a silent pass).
"""
import json
import sys

# LandlordAccount is the billing unit (README domain model). tenant_id / property_id are NOT
# acceptable substitutes, even though some resources happen to carry them.
REQUIRED_TAG = "landlord_account_id"

CHECKED_ACTIONS = {"create", "update"}

EXIT_OK = 0
EXIT_MISSING_TAG = 1
EXIT_BAD_PLAN = 2


def _is_checked(change: dict) -> bool:
    """Create/update (including replace = ["delete","create"]) with a real `after` block."""
    actions = change.get("actions") or []
    return bool(CHECKED_ACTIONS.intersection(actions)) and isinstance(change.get("after"), dict)


def _has_billing_tag(after: dict) -> bool:
    """True if the resource's effective tags carry a non-blank landlord_account_id.

    `tags_all` is included because tags inherited from the provider's `default_tags` only show up
    there, and AWS bills on the effective tag set.
    """
    for key in ("tags", "tags_all"):
        tags = after.get(key)
        if isinstance(tags, dict):
            value = tags.get(REQUIRED_TAG)
            if isinstance(value, str) and value.strip():
                return True
    return False


def find_untagged(plan: dict) -> tuple[list[str], int]:
    """Return (sorted unique addresses missing the tag, number of unique addresses checked).

    Idempotency key: the resource `address`. Results are collected in sets keyed by address, so a
    resource listed more than once in a plan is reported once, and the output is sorted, so it
    doesn't depend on input order.
    """
    checked: set[str] = set()
    missing: set[str] = set()

    for rc in plan.get("resource_changes") or []:
        if not isinstance(rc, dict):
            continue
        change = rc.get("change") or {}
        if not isinstance(change, dict) or not _is_checked(change):
            continue
        address = rc.get("address")
        if not address:
            continue
        checked.add(address)
        if not _has_billing_tag(change["after"]):
            missing.add(address)

    return sorted(missing), len(checked)


def check_plan(plan_path: str) -> int:
    """
    Returns an exit code: 0 if every resource being created or updated has
    `landlord_account_id`, non-zero otherwise.
    """
    try:
        with open(plan_path, encoding="utf-8") as fh:
            plan = json.load(fh)
        if not isinstance(plan, dict):
            raise ValueError("top-level JSON is not an object")
    except (OSError, ValueError) as exc:
        print(f"ERROR: could not read plan {plan_path!r}: {exc}")
        return EXIT_BAD_PLAN

    missing, checked_count = find_untagged(plan)

    if missing:
        print(f"FAIL: {len(missing)} of {checked_count} resource(s) being created/updated are missing required tag '{REQUIRED_TAG}':")
        for address in missing:
            print(f"  - {address}")
        return EXIT_MISSING_TAG

    print(f"PASS: all {checked_count} resource(s) being created/updated carry '{REQUIRED_TAG}'.")
    return EXIT_OK


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python scripts/cost_tag_check.py <plan.json>")
        sys.exit(EXIT_BAD_PLAN)
    sys.exit(check_plan(sys.argv[1]))
