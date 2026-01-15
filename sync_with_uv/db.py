"""Dependency mapping for pre-commit hooks."""

DEPENDENCY_MAPPING = {
    "autopep8": {
        "repo": "https://github.com/pre-commit/mirrors-autopep8",
        "rev": "v${rev}",
    },
    "bandit": {
        "repo": "https://github.com/PyCQA/bandit",
        "rev": "${rev}",
    },
    "black": {
        "repo": "https://github.com/psf/black",
        "rev": "${rev}",
    },
    "commitizen": {
        "repo": "https://github.com/commitizen-tools/commitizen",
        "rev": "v${rev}",
    },
    "flake8": {
        "repo": "https://github.com/pycqa/flake8",
        "rev": "${rev}",
    },
    "flakeheaven": {
        "repo": "https://github.com/flakeheaven/flakeheaven",
        "rev": "${rev}",
    },
    "isort": {
        "repo": "https://github.com/pycqa/isort",
        "rev": "${rev}",
    },
    "mypy": {
        "repo": "https://github.com/pre-commit/mirrors-mypy",
        "rev": "v${rev}",
    },
    "pyupgrade": {
        "repo": "https://github.com/asottile/pyupgrade",
        "rev": "v${rev}",
    },
    "check-jsonschema": {
        "repo": "https://github.com/python-jsonschema/check-jsonschema",
        "rev": "${rev}",
    },
    "ruff": {
        "repo": "https://github.com/astral-sh/ruff-pre-commit",
        "rev": "v${rev}",
    },
    "deptry": {"repo": "https://github.com/fpgmaas/deptry.git", "rev": "${rev}"},
    "licenseheaders": {
        "repo": "https://github.com/johann-petrak/licenseheaders.git",
        "rev": "v${rev}",
    },
    "sqlfluff": {"repo": "https://github.com/sqlfluff/sqlfluff", "rev": "${rev}"},
    "tombi": {
        "repo": "https://github.com/tombi-toml/tombi-pre-commit",
        "rev": "v${rev}",
    },
}
