import pytest
from raquette import creer_raquette, deplacer as deplacer_raquette, definir_velocite

def test_creer_raquette(regles):
    x, y = 100, 200
    vitesse = 12
    raquette = creer_raquette(x, y, vitesse)
    
    assert raquette['rect'].x == x
    assert raquette['rect'].y == y
    assert raquette['vitesse'] == vitesse

def test_deplacer_raquette(regles):
    raquette = creer_raquette(100, 200, 12)
    raquette['dx'] = 5
    raquette['dy'] = 5
    
    nouvelle_raquette = deplacer_raquette(raquette)
    
    assert nouvelle_raquette['rect'].x == 105
    assert nouvelle_raquette['rect'].y == 205