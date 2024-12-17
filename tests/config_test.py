import pytest
import pygame
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(scope="session")
def regles():
    from regles_tennis_table import creer_regles
    return creer_regles()

@pytest.fixture(autouse=True)
def initialiser_pygame():
    pygame.init()
    yield
    pygame.quit()

