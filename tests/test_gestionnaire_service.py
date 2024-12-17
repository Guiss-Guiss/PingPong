import pytest
from gestionnaire_service import creer_gestionnaire_service, mettre_a_jour_compte_service

@pytest.fixture
def gestionnaire():
    return creer_gestionnaire_service()

def test_mettre_a_jour_compte_service(gestionnaire):
    nouveau_gestionnaire = mettre_a_jour_compte_service(gestionnaire, 1, 0)
    
    assert nouveau_gestionnaire['compte_service'] == 1
    assert not nouveau_gestionnaire['est_egalite']