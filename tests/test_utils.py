import pytest
import pygame

def test_pygame_initialisation():
    assert pygame.get_init()
    assert pygame.display.get_init()

def test_couleurs(regles):
    assert regles['BLANC'] == (255, 255, 255)
    assert regles['NOIR'] == (0, 0, 0)
    assert regles['VERT'] == (0, 164, 0)