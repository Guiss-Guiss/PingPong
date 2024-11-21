def dessiner_jeu(ecran: pygame.Surface, etat_jeu: EtatJeu):
    """Dessine tous les éléments du jeu"""
    # Effacer l'écran
    ecran.fill(CONFIG_JEU['COULEURS']['NOIR'])
    
    # Dessiner la table
    dessiner_table(ecran)
    
    # Dessiner les raquettes
    dessiner_raquette(ecran, etat_jeu.raquette_gauche)
    dessiner_raquette(ecran, etat_jeu.raquette_droite)
    
    # Dessiner la balle
    dessiner_balle(ecran, etat_jeu.balle)
    
    # Dessiner le score
    dessiner_score(ecran, etat_jeu)

def dessiner_table(ecran: pygame.Surface):
    """Dessine la table de tennis de table"""
    # Calculer les dimensions de la table
    largeur_table = CONFIG_JEU['LARGEUR_FENETRE'] * (CONFIG_JEU['LARGEUR_TABLE_POURCENT'] / 100)
    hauteur_table = CONFIG_JEU['HAUTEUR_FENETRE'] * 0.50
    table_x = (CONFIG_JEU['LARGEUR_FENETRE'] - largeur_table) / 2
    table_y = (CONFIG_JEU['HAUTEUR_FENETRE'] - hauteur_table) / 2

    # Rectangle principal de la table
    pygame.draw.rect(ecran, CONFIG_JEU['COULEURS']['VERT'],
        (table_x, table_y, largeur_table, hauteur_table))

    # Bordures de la table
    lignes = [
        ((table_x, table_y), (table_x + largeur_table, table_y)),
        ((table_x, table_y + hauteur_table), 
         (table_x + largeur_table, table_y + hauteur_table)),
        ((table_x, table_y), (table_x, table_y + hauteur_table)),
        ((table_x + largeur_table, table_y), 
         (table_x + largeur_table, table_y + hauteur_table))
    ]
    
    for debut, fin in lignes:
        pygame.draw.line(ecran, CONFIG_JEU['COULEURS']['BLANC'], debut, fin, 2)

    # Filet
    centre_x = table_x + largeur_table / 2
    pygame.draw.line(ecran, CONFIG_JEU['COULEURS']['BLANC'],
                    (centre_x, table_y),
                    (centre_x, table_y + hauteur_table), 2)

def dessiner_raquette(ecran: pygame.Surface, raquette: Raquette):
    """Dessine une raquette"""
    rect = pygame.Rect(
        raquette.position[0] - raquette.dimensions[0] // 2,
        raquette.position[1] - raquette.dimensions[1] // 2,
        raquette.dimensions[0],
        raquette.dimensions[1]
    )
    pygame.draw.rect(ecran, CONFIG_JEU['COULEURS']['BLANC'], rect)

def dessiner_balle(ecran: pygame.Surface, balle: Balle):
    """Dessine la balle"""
    pygame.draw.circle(ecran, CONFIG_JEU['COULEURS']['BLANC'],
                     (int(balle.position[0]), int(balle.position[1])),
                     balle.rayon)

def dessiner_score(ecran: pygame.Surface, etat_jeu: EtatJeu):
    """Dessine le score et les informations de jeu"""
    police = pygame.font.Font(None, 74)
    police_info = pygame.font.Font(None, 36)
    
    # Score principal
    texte_score = f"{etat_jeu.score[0]} - {etat_jeu.score[1]}"
    surface_score = police.render(texte_score, True, CONFIG_JEU['COULEURS']['BLANC'])
    rect_score = surface_score.get_rect(center=(CONFIG_JEU['LARGEUR_FENETRE'] // 2, 50))
    ecran.blit(surface_score, rect_score)
    
    # Score des jeux
    texte_jeux = f"Jeux : {etat_jeu.jeux_gagnes[0]} - {etat_jeu.jeux_gagnes[1]}"
    surface_jeux = police_info.render(texte_jeux, True, CONFIG_JEU['COULEURS']['GRIS'])
    rect_jeux = surface_jeux.get_rect(center=(CONFIG_JEU['LARGEUR_FENETRE'] // 2, 100))
    ecran.blit(surface_jeux, rect_jeux)
    
    # Information sur le service
    if etat_jeu.balle.au_service:
        texte_service = f"Joueur {etat_jeu.serveur_actuel} au service"
        surface_service = police_info.render(texte_service, True, CONFIG_JEU['COULEURS']['JAUNE'])
        rect_service = surface_service.get_rect(center=(CONFIG_JEU['LARGEUR_FENETRE'] // 2, 150))
        ecran.blit(surface_service, rect_service)

def verifier_fin_jeu(score: Score) -> Optional[int]:
    """Vérifie si un jeu est terminé et retourne le gagnant si c'est le cas"""
    if max(score) >= CONFIG_JEU['POINTS_POUR_GAGNER']:
        if abs(score[0] - score[1]) >= CONFIG_JEU['DIFFERENCE_MIN_POINTS']:
            return 1 if score[0] > score[1] else 2
    return None

def verifier_fin_match(jeux_gagnes: Score) -> Optional[int]:
    """Vérifie si le match est terminé et retourne le gagnant si c'est le cas"""
    if max(jeux_gagnes) >= CONFIG_JEU['JEUX_POUR_GAGNER']:
        return 1 if jeux_gagnes[0] > jeux_gagnes[1] else 2
    return None

def boucle_principale():
    """Boucle principale du jeu"""
    pygame.init()
    ecran = pygame.display.set_mode((CONFIG_JEU['LARGEUR_FENETRE'], 
                                   CONFIG_JEU['HAUTEUR_FENETRE']))
    pygame.display.set_caption(CONFIG_JEU['TITRE_FENETRE'])
    horloge = pygame.time.Clock()
    
    etat_jeu = creer_etat_initial()
    en_cours = True
    
    while en_cours:
        # Gestion des événements
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                en_cours = False
            elif evenement.type == pygame.KEYDOWN:
                if evenement.key == pygame.K_r:
                    etat_jeu = creer_etat_initial()
        
        # Mise à jour de l'état du jeu
        touches = pygame.key.get_pressed()
        delta_temps = horloge.get_time() / 1000.0
        etat_jeu = mettre_a_jour_etat_jeu(etat_jeu, touches, delta_temps)
        
        # Vérification de fin de jeu/match
        gagnant_jeu = verifier_fin_jeu(etat_jeu.score)
        if gagnant_jeu:
            nouveau_jeux_gagnes = (
                etat_jeu.jeux_gagnes[0] + (1 if gagnant_jeu == 1 else 0),
                etat_jeu.jeux_gagnes[1] + (1 if gagnant_jeu == 2 else 0)
            )
            gagnant_match = verifier_fin_match(nouveau_jeux_gagnes)
            
            if gagnant_match:
                # Fin du match
                etat_jeu = EtatJeu(
                    balle=etat_jeu.balle,
                    raquette_gauche=etat_jeu.raquette_gauche,
                    raquette_droite=etat_jeu.raquette_droite,
                    score=(0, 0),
                    jeux_gagnes=nouveau_jeux_gagnes,
                    serveur_actuel=etat_jeu.serveur_actuel,
                    compte_services=0,
                    phase_jeu='MATCH_TERMINE'
                )
            else:
                # Nouveau jeu
                etat_jeu = EtatJeu(
                    balle=creer_etat_initial().balle,
                    raquette_gauche=etat_jeu.raquette_gauche,
                    raquette_droite=etat_jeu.raquette_droite,
                    score=(0, 0),
                    jeux_gagnes=nouveau_jeux_gagnes,
                    serveur_actuel=3 - etat_jeu.serveur_actuel,  # Changer de serveur
                    compte_services=0,
                    phase_jeu='PRET_A_SERVIR'
                )
        
        # Rendu
        dessiner_jeu(ecran, etat_jeu)
        pygame.display.flip()
        horloge.tick(CONFIG_JEU['IPS'])
    
    pygame.quit()

if __name__ == "__main__":
    boucle_principale()