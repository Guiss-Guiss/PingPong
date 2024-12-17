import pytest
from gestionnaire_match import creer_gestionnaire_match, incrementer_jeux_joueur

@pytest.fixture
def gestionnaire():
    return creer_gestionnaire_match()

def test_incrementer_jeux_joueur(gestionnaire):
    score_final = (11, 9)
    nouveau_gestionnaire = incrementer_jeux_joueur(gestionnaire, 1, score_final)
    
    assert nouveau_gestionnaire['jeux_joueur1'] == 1
    assert nouveau_gestionnaire['jeux_joueur2'] == 0
    assert score_final in nouveau_gestionnaire['historique_jeux']