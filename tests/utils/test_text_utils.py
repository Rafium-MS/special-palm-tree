from shared.text_utils import simple_diff, slugify


def test_slugify_basic():
    assert slugify("Olá, Mundo!") == "ola-mundo"
    assert slugify("Hello World") == "hello-world"


def test_simple_diff():
    old = "linha1\nlinha2"
    new = "linha1\nlinha3"
    assert simple_diff(old, new) == ["  linha1", "- linha2", "+ linha3"]
