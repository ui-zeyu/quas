import numpy as np

from quas.crypto.alphabet import english_upper
from quas.crypto.characterizer import Characterizer
from quas.crypto.ioc import IndexOfCoincidence


def test_ioc_is_characterizer():
    assert isinstance(IndexOfCoincidence(), Characterizer)


def test_ioc_english_text():
    text = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG"
    ioc = IndexOfCoincidence()
    score = ioc.score_text(text)
    assert isinstance(score, float)
    assert 0 < score < 1


def test_ioc_repeated_chars():
    text = "AAAAA"
    ioc = IndexOfCoincidence()
    score = ioc.score_text(text)
    assert score == 1.0


def test_ioc_all_unique():
    text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    ioc = IndexOfCoincidence()
    score = ioc.score_text(text)
    assert score == 0


def test_ioc_short_text():
    ioc = IndexOfCoincidence()

    text = "AB"
    score = ioc.score_text(text)
    assert score == 0

    text = "ABC"
    score = ioc.score_text(text)
    assert 0 <= score <= 1


def test_ioc_empty_text():
    ioc = IndexOfCoincidence()
    indices = np.array([], dtype=np.uint32)
    score = ioc.score(indices)
    assert np.isnan(score)


def test_ioc_indices():
    ioc = IndexOfCoincidence()

    indices = english_upper.encode("HELLO")
    indices = np.array(indices, dtype=np.uint32)
    score = ioc.score(indices)

    assert isinstance(score, float)
    assert 0 <= score <= 1


def test_ioc_non_alpha_chars():
    text = "HELLO WORLD! 123"
    ioc = IndexOfCoincidence()
    score = ioc.score_text(text)
    assert isinstance(score, float)
    assert 0 <= score <= 1
