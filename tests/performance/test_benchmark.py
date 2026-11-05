import pytest

from .generators.datasets import (
    dense_conflict_dataset,
    no_conflict_dataset,
    same_observation_dataset,
    random_dataset
)

from src.api import get_conflicts

SCALING_CASES = [
    (2, 5),
    (5, 10),
    (10, 10),
    (20, 20),
    (50, 20),
    (50, 50),
]

PLAN_SCALING_CASES = [
    (2, 5),
    (3, 5),
    (4, 5),
    (5, 5),
]

ACTIVITY_SCALING_CASES = [
    (2, 5),
    (2, 6),
    (2, 7),
    (2, 8),
    (2, 9),
    (2, 10),
]

# ==============================================================================
@pytest.mark.parametrize(
    "plan_count,activities_per_plan",
    PLAN_SCALING_CASES,
)
def test_plan_scaling(
    benchmark,
    plan_count,
    activities_per_plan,
):

    bundle = no_conflict_dataset(
        plan_count=plan_count,
        activities_per_plan=activities_per_plan,
    )

    result = benchmark(
        get_conflicts,
        bundle,
    )

    assert result is not None


@pytest.mark.parametrize(
    "plan_count,activities_per_plan",
    ACTIVITY_SCALING_CASES,
)
def test_activity_scaling(
    benchmark,
    plan_count,
    activities_per_plan,
):
    bundle = no_conflict_dataset(
        plan_count=plan_count,
        activities_per_plan=activities_per_plan,
    )

    result = benchmark(
        get_conflicts,
        bundle,
    )

    assert result is not None

# ==============================================================================


@pytest.mark.parametrize(
    "plan_count,activities_per_plan",
    SCALING_CASES,
)
def test_no_conflict_scaling(
    benchmark,
    plan_count,
    activities_per_plan,
):
    bundle = no_conflict_dataset(
        plan_count=plan_count,
        activities_per_plan=activities_per_plan,
    )

    result = benchmark(
        get_conflicts,
        bundle,
    )

    assert result is not None


@pytest.mark.parametrize(
    "plan_count,activities_per_plan",
    SCALING_CASES,
)
def test_dense_conflict_scaling(
    benchmark,
    plan_count,
    activities_per_plan,
):
    bundle = dense_conflict_dataset(
        plan_count=plan_count,
        activities_per_plan=activities_per_plan,
    )

    result = benchmark(
        get_conflicts,
        bundle,
    )

    assert result is not None


@pytest.mark.parametrize(
    "plan_count,activities_per_plan",
    SCALING_CASES,
)
def test_same_observation_scaling(
    benchmark,
    plan_count,
    activities_per_plan,
):
    bundle = same_observation_dataset(
        plan_count=plan_count,
        activities_per_plan=activities_per_plan,
        seed=42,
    )

    result = benchmark(
        get_conflicts,
        bundle,
    )

    assert result is not None


@pytest.mark.parametrize(
    "plan_count,activities_per_plan",
    SCALING_CASES,
)
def test_random_scaling(
    benchmark,
    plan_count,
    activities_per_plan,
):
    bundle = random_dataset(
        plan_count=plan_count,
        activities_per_plan=activities_per_plan,
        observation_count=10,
        seed=42,
    )

    result = benchmark(
        get_conflicts,
        bundle,
    )

    assert result is not None