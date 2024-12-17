import pytest
from unittest.mock import Mock, patch
from balle import creer_balle, servir, deplacer, gerer_collision_raquette

def test_creer_balle(regles):
    vitesse = 10
    balle = creer_balle(vitesse)
    
    assert balle['vitesse'] == vitesse
    assert balle['x'] == regles['LARGEUR_FENETRE'] // 2
    assert balle['y'] == regles['HAUTEUR_FENETRE'] // 2
    assert balle['au_service']
    assert balle['active']

@patch('random.uniform')
def test_deplacer(mock_random, regles):
    mock_random.return_value = 0.5
    balle = creer_balle(10)
    balle['dx'] = 5
    balle['dy'] = 5
    balle['au_service'] = False
    
    nouvelle_balle, point_marque = deplacer(balle)
    
    assert nouvelle_balle['x'] == balle['x'] + 5
    assert nouvelle_balle['y'] == balle['y'] + 5
    assert not point_marque
