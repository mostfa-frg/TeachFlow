"""Isolated synthetic generator for the browser regression."""
from app.api.v1.router import get_roadmap_generator
from app.main import app
from test_api import StubGenerator
from test_graph import proposal

app.dependency_overrides[get_roadmap_generator] = lambda: StubGenerator(proposal())
