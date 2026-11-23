"""Architecture test.

Vérifie que tous les appels à `to_csv` faits dans le package
`formation_mlops_2` sont bien appelés avec l'argument `index=False`.

Cela évite d'écrire l'index du DataFrame dans les fichiers CSV générés
(données, prédictions, etc.).
"""

import ast
from pathlib import Path

PACKAGE_ROOT = Path(__file__).parents[2] / "formation_mlops_2"


def find_to_csv_calls_without_index_false(source: str) -> list[int]:
    """Renvoie les numéros de ligne des appels `.to_csv(...)` sans `index=False`."""
    violations = []
    for node in ast.walk(ast.parse(source)):
        # On ne garde que les appels de la forme `<objet>.to_csv(...)`
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr != "to_csv":
            continue
        has_index_false = any(
            kw.arg == "index" and isinstance(kw.value, ast.Constant) and kw.value.value is False
            for kw in node.keywords
        )
        if not has_index_false:
            violations.append(node.lineno)
    return violations


def test_to_csv_called_with_index_false():
    # Given
    python_files = sorted(PACKAGE_ROOT.rglob("*.py"))
    assert python_files, f"Aucun fichier Python trouvé dans {PACKAGE_ROOT}"

    # When
    violations = [
        f"{path.relative_to(PACKAGE_ROOT.parent)}:{line}"
        for path in python_files
        for line in find_to_csv_calls_without_index_false(path.read_text())
    ]

    # Then
    assert not violations, "to_csv appelé sans index=False :\n" + "\n".join(violations)


def test_detector_flags_missing_or_wrong_index():
    source = (
        "df.to_csv('a.csv')\n"
        "df.to_csv('b.csv', index=True)\n"
        "df.to_csv('c.csv',\n"
        "          sep=';', index=False)\n"
    )
    assert find_to_csv_calls_without_index_false(source) == [1, 2]
