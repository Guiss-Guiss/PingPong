import pytest
from score import creer_score, incrementer_joueur1, incrementer_joueur2

@pytest.fixture
def score():
    return creer_score()

def test_incrementer_joueur1(score):
    nouveau_score = incrementer_joueur1(score)
    assert nouveau_score['score_joueur1'] == 1
    assert nouveau_score['score_joueur2'] == 0

def test_avantage(score):
    score['score_joueur1'] = 10
    score['score_joueur2'] = 10
    nouveau_score = incrementer_joueur1(score)
    assert nouveau_score['est_avantage']