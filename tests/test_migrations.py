from __future__ import annotations

import ast
from pathlib import Path


def _literal_assignment(module: ast.Module, name: str) -> str | None:
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    value = ast.literal_eval(node.value)
                    return value
    return None


def test_migration_files_have_single_head_revision() -> None:
    revisions: dict[str, str | None] = {}
    for path in Path("alembic/versions").glob("*.py"):
        module = ast.parse(path.read_text())
        revision = _literal_assignment(module, "revision")
        down_revision = _literal_assignment(module, "down_revision")
        assert revision is not None
        revisions[revision] = down_revision

    referenced_revisions = {down_revision for down_revision in revisions.values() if down_revision}
    heads = sorted(set(revisions) - referenced_revisions)

    assert heads == ["20260508_0003"]
