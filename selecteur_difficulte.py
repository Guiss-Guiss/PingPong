import pygame
import logging
from regles_tennis_table import creer_regles, obtenir_vitesse_balle_pour_niveau, obtenir_nom_niveau

logger = logging.getLogger('tennis_table')

def creer_selecteur_difficulte(largeur_ecran, hauteur_ecran):
    try:
        logger.debug("Création du sélecteur de difficulté")
        regles = creer_regles()
        curseur_x = (largeur_ecran - regles['LARGEUR_CURSEUR_DIFFICULTE']) // 2
        curseur_y = hauteur_ecran // 2
        
        selecteur = {
            'regles': regles,
            'largeur_ecran': largeur_ecran,
            'hauteur_ecran': hauteur_ecran,
            'largeur_curseur': regles['LARGEUR_CURSEUR_DIFFICULTE'],
            'hauteur_curseur': regles['HAUTEUR_CURSEUR_DIFFICULTE'],
            'curseur_x': curseur_x,
            'curseur_y': curseur_y,
            'rayon_poignee': regles['RAYON_POIGNEE_DIFFICULTE'],
            'poignee_x': curseur_x,
            'poignee_y': curseur_y + regles['HAUTEUR_CURSEUR_DIFFICULTE'] // 2,
            'poignee_en_deplacement': False,
            'difficulte_actuelle': regles['DIFFICULTE_MIN'],
            'vitesse_balle': obtenir_vitesse_balle_pour_niveau(regles, regles['DIFFICULTE_MIN'])
        }
        logger.debug(f"Sélecteur créé: {selecteur}")
        return selecteur
    except Exception as e:
        logger.error(f"Erreur lors de la création du sélecteur: {e}", exc_info=True)
        raise

def obtenir_couleur_difficulte(selecteur):
    try:
        niveau = selecteur['difficulte_actuelle']
        if niveau <= 3:
            return selecteur['regles']['COULEURS_NIVEAU'][0]
        elif niveau <= 6:
            return selecteur['regles']['COULEURS_NIVEAU'][1]
        elif niveau <= 9:
            return selecteur['regles']['COULEURS_NIVEAU'][2]
        else:
            return selecteur['regles']['COULEURS_NIVEAU'][3]
    except Exception as e:
        logger.error(f"Erreur lors de l'obtention de la couleur: {e}", exc_info=True)
        return (255, 255, 255)

def gerer_evenement(selecteur, evenement):
    try:
        nouveau_selecteur = {**selecteur}
        
        if evenement.type == pygame.MOUSEBUTTONDOWN:
            souris_x, souris_y = evenement.pos
            distance = ((souris_x - selecteur['poignee_x']) ** 2 + 
                       (souris_y - selecteur['poignee_y']) ** 2) ** 0.5
            if distance < selecteur['rayon_poignee']:
                nouveau_selecteur['poignee_en_deplacement'] = True
                logger.debug("Début du déplacement de la poignée")
                
        elif evenement.type == pygame.MOUSEBUTTONUP:
            nouveau_selecteur['poignee_en_deplacement'] = False
            logger.debug("Fin du déplacement de la poignée")
            
        elif evenement.type == pygame.MOUSEMOTION and selecteur['poignee_en_deplacement']:
            try:
                nouveau_selecteur['poignee_x'] = max(
                    selecteur['curseur_x'],
                    min(evenement.pos[0], selecteur['curseur_x'] + selecteur['largeur_curseur'])
                )
                
                progression = (nouveau_selecteur['poignee_x'] - selecteur['curseur_x']) / selecteur['largeur_curseur']
                nouvelle_difficulte = round(selecteur['regles']['DIFFICULTE_MIN'] + 
                                       (selecteur['regles']['DIFFICULTE_MAX'] - 
                                        selecteur['regles']['DIFFICULTE_MIN']) * progression)
                
                nouveau_selecteur.update({
                    'difficulte_actuelle': nouvelle_difficulte,
                    'vitesse_balle': obtenir_vitesse_balle_pour_niveau(
                        selecteur['regles'],
                        nouvelle_difficulte
                    )
                })
                logger.debug(f"Nouvelle difficulté: {nouvelle_difficulte}")
            except Exception as e:
                logger.error(f"Erreur lors du calcul de la nouvelle difficulté: {e}")
        
        return nouveau_selecteur
    except Exception as e:
        logger.error(f"Erreur lors de la gestion d'événement: {e}", exc_info=True)
        return selecteur

def dessiner(selecteur, ecran):
    try:
        regles = selecteur['regles']
        
        try:
            police = pygame.font.Font(None, regles['TAILLE_POLICE_PRINCIPALE'])
            titre = police.render("Sélectionnez le Niveau de Difficulté", True, regles['BLANC'])
            rect_titre = titre.get_rect(center=(selecteur['largeur_ecran'] // 2, selecteur['curseur_y'] - 60))
            ecran.blit(titre, rect_titre)

            pygame.draw.rect(ecran, regles['CURSEUR_ARRIERE_PLAN'],
                        (selecteur['curseur_x'], selecteur['curseur_y'],
                         selecteur['largeur_curseur'], selecteur['hauteur_curseur']))

            largeur_remplie = selecteur['poignee_x'] - selecteur['curseur_x']
            pygame.draw.rect(ecran, obtenir_couleur_difficulte(selecteur),
                        (selecteur['curseur_x'], selecteur['curseur_y'],
                         largeur_remplie, selecteur['hauteur_curseur']))

            petite_police = pygame.font.Font(None, regles['TAILLE_POLICE_SECONDAIRE'])
            for i in range(10):
                x = selecteur['curseur_x'] + (i * selecteur['largeur_curseur'] // 9)
                pygame.draw.line(ecran, regles['BLANC'],
                            (x, selecteur['curseur_y'] - 5),
                            (x, selecteur['curseur_y'] + selecteur['hauteur_curseur'] + 5), 2)
                num = petite_police.render(str(i + 1), True, regles['BLANC'])
                rect_num = num.get_rect(center=(x, selecteur['curseur_y'] + 20))
                ecran.blit(num, rect_num)

            pygame.draw.circle(ecran, regles['BLANC'],
                          (int(selecteur['poignee_x']), selecteur['poignee_y']),
                          selecteur['rayon_poignee'])

            texte_difficulte = (f"{obtenir_nom_niveau(regles, selecteur['difficulte_actuelle'])} "
                           f"(Niveau {selecteur['difficulte_actuelle']})")
            surface_diff = police.render(texte_difficulte, True, obtenir_couleur_difficulte(selecteur))
            rect_diff = surface_diff.get_rect(center=(selecteur['largeur_ecran'] // 2, selecteur['curseur_y'] + 60))
            ecran.blit(surface_diff, rect_diff)

            police_standard = pygame.font.Font(None, regles['TAILLE_POLICE_STANDARD'])
            instruction = police_standard.render("Appuyez sur ENTRÉE pour commencer la partie", True, regles['BLANC'])
            rect_instruction = instruction.get_rect(center=(selecteur['largeur_ecran'] // 2, selecteur['curseur_y'] + 120))
            ecran.blit(instruction, rect_instruction)
            
        except Exception as e:
            logger.error(f"Erreur lors du rendu des éléments: {e}")
            
    except Exception as e:
        logger.error(f"Erreur lors du dessin du sélecteur: {e}", exc_info=True)