import pytest
from tableau_score import creer_tableau_score, construire_texte_score

def test_creer_tableau_score(regles):
    largeur_ecran = 800
    tableau = creer_tableau_score(largeur_ecran)
    
    assert tableau['largeur_ecran'] == largeur_ecran
    assert 'polices' in tableau
    assert 'principale' in tableau['polices']
    assert 'secondaire' in tableau['polices']

def test_construire_texte_score():
    donnees_jeu = {
        'score_joueur1': 5,
        'score_joueur2': 3,
        'est_avantage': False
    }
    
    texte = construire_texte_score(donnees_jeu)
    assert texte == "5 - 3"