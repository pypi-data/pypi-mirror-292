from __future__ import annotations

import randovania_scm_version_schema


def test_function_exists():
    assert randovania_scm_version_schema.version_scheme is not None
