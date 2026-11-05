import cProfile
import pstats

from tests.performance.generators.datasets import no_conflict_dataset
from src.api import get_conflicts


bundle = no_conflict_dataset(
    plan_count=5,
    activities_per_plan=5,
)

profiler = cProfile.Profile()

profiler.enable()

get_conflicts(bundle)

profiler.disable()

stats = pstats.Stats(profiler)

stats.sort_stats("cumulative")
stats.print_stats(30)