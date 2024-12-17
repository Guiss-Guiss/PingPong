# test_regles.py
import pytest
from regles_tennis_table import est_avantage, est_gagnant_jeu, est_gagnant_match

def test_est_avantage(regles):
    assert est_avantage(regles, 10, 10)
    assert est_avantage(regles, 11, 10)
    assert not est_avantage(regles, 9, 8)

def test_est_gagnant_jeu(regles):
    assert est_gagnant_jeu(regles, 11, 9) == 1
    assert est_gagnant_jeu(regles, 9, 11) == 2
    assert est_gagnant_jeu(regles, 10, 10) is None