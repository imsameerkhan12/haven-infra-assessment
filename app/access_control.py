"""
B2, part 1 — implement can_access_screening_report().

Read README.md's domain model first. A ScreeningReport belongs to a Tenant, a Tenant belongs to
a Property, and a Property belongs to a LandlordAccount. A PropertyManager is scoped to exactly
one LandlordAccount.

Work out from that hierarchy which boundary actually gates access to a ScreeningReport.

Answer: the LandlordAccount. Neither ScreeningReport nor Tenant carries landlord_account_id, so
the owning account is resolved by walking report -> tenant -> property -> landlord_account_id and
comparing that with the actor's landlord_account_id. Every lookup fails closed.
"""
from typing import Optional, TypeVar

from app.models import PropertyManager, ScreeningReport, Property, Tenant

T = TypeVar("T", Property, Tenant)


def _find_unique(records: list[T], record_id: str) -> Optional[T]:
    """Return the single record with this id, or None if it's absent OR ambiguous.

    A duplicated id means we can't be sure which parent the child really belongs to, so it is
    treated the same as "not found" (fail closed) rather than trusting whichever matched first.
    """
    if not record_id:
        return None
    matches = [r for r in (records or []) if r is not None and r.id == record_id]
    return matches[0] if len(matches) == 1 else None


def _owning_landlord_account_id(
    report: ScreeningReport, *, properties: list[Property], tenants: list[Tenant]
) -> Optional[str]:
    tenant = _find_unique(tenants, report.tenant_id)
    if tenant is None:
        return None
    prop = _find_unique(properties, tenant.property_id)
    if prop is None:
        return None
    return prop.landlord_account_id or None


def can_access_screening_report(
    actor: PropertyManager,
    report: ScreeningReport,
    *,
    properties: list[Property],
    tenants: list[Tenant],
) -> bool:
    """
    actor: the PropertyManager requesting access
    report: the ScreeningReport they're trying to view
    properties: all known Property records
    tenants: all known Tenant records

    Return True if actor may view report, False otherwise. Fail closed — if anything needed to
    make this determination is missing (tenant not found, property not found), return False.
    """
    if actor is None or report is None:
        return False

    actor_account = actor.landlord_account_id
    if not actor_account:
        return False

    report_account = _owning_landlord_account_id(report, properties=properties, tenants=tenants)
    if report_account is None:
        return False

    return actor_account == report_account
