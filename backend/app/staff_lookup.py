"""Resolves an assigned_staff_id into a display name (G3)."""

import pandas as pd


def officer_names(staff: pd.DataFrame) -> dict[int, str]:
    """Active staff only; an inactive assignment is treated as unassigned."""
    active = staff[staff["active"] == 1]
    return dict(zip(active["id"], active["display_name"]))


def assigned_officer_name(assigned_staff_id, names: dict[int, str]) -> str | None:
    if pd.isna(assigned_staff_id):
        return None
    return names.get(int(assigned_staff_id))
