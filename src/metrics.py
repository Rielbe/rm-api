# src/metrics.py
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter


def setup_metrics(app):
    Instrumentator().instrument(app).expose(app, include_in_schema=False, should_gzip=True)

# counter label is the sort field name; only known allowed names will be recorded
sort_by_counter = Counter(
    "http_sort_by_requests_total",
    "Number of valid requests grouped by ?sort_by value",
    ["sort_by"],
)