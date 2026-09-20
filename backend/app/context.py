"""Bundles every table a detector or the priority queue needs, loaded
once per request. Every registered detector's `detect(context)` takes
exactly this and nothing else.
"""

from dataclasses import dataclass

import pandas as pd

from app.db import load_table


@dataclass(frozen=True)
class Context:
    constituents: pd.DataFrame
    gifts: pd.DataFrame
    interactions: pd.DataFrame
    staff: pd.DataFrame
    opportunities: pd.DataFrame


def build_context() -> Context:
    return Context(
        constituents=load_table("constituents"),
        gifts=load_table("gifts"),
        interactions=load_table("interactions"),
        staff=load_table("staff"),
        opportunities=load_table("opportunities"),
    )
