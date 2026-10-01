"""Evolution engine: a flaky action is fixed by the retry mutation."""

import pytest
from unittest.mock import patch

from app.genealogy.evolve import evolve, fitness
from tests.test_api import TestingSessionLocal, setup_test_db  # noqa: F401
from app.models import WorkflowModel
from examples import INVOICE_PROCESSING


@pytest.mark.asyncio
async def test_fitness_and_evolve_shape():
    nodes, edges = INVOICE_PROCESSING["nodes"], INVOICE_PROCESSING["edges"]
    f = await fitness("t", nodes, edges, trials=1)
    assert 0.0 <= f <= 1.0

    db = TestingSessionLocal()
    row = WorkflowModel(id="evo", name="evo", nodes=nodes, edges=edges)
    db.add(row); db.commit()
    try:
        with patch("app.genealogy.cross_pollination.enrich_with_llm", return_value=None):
            r = await evolve(db, row, trials=1)
        assert r["variants"] == sorted(r["variants"], key=lambda v: -v["fitness"])
        assert any("retry_count=3" in v["description"] for v in r["variants"])
    finally:
        db.delete(row); db.commit(); db.close()
