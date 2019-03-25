from __future__ import absolute_import, print_function, unicode_literals
from gameclass import Game,check_init_game_done
from spritebuilder import SpriteBuilder
from players import Player
from sprite import MovingSprite
from ontology import Ontology
from itertools import chain
import pygame
import glo

import random 
import numpy as np
import sys

from projet import *
import copy
import heapq
import functools
import time

# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()

def init(_boardname=None):

    global player,game

    name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer1'
    #name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer2' #NON
    #name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer3'
    #name = _boardname if _boardname is not None else '10x10'
    #name = _boardname if _boardname is not None else 'Lab_15x15' #NON
    #name = _boardname if _boardname is not None else 'map' #NON
    #name = _boardname if _boardname is not None else 'map2' #NON
    #name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer_6x6' #NON
    #name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer_bomberman' #YES
    #name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer_impossible'
    #name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer_incroyable'
    #name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer_labyrinthe2'
    #name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer_labyrinthe3' #NON
    #name = _boardname if _boardname is not None else 'thirst' #NON

    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 20  # frames per second
    game.mainiteration()
    game.mask.allow_overlaping_players = True
    #player = game.player
    
def main():

    iterations = 100 # default
    if len(sys.argv) == 2:
        iterations = int(sys.argv[1])
    print ("Iterations: ")
    print (iterations)

    init()

    #-------------------------------
    # Initialisation
    #-------------------------------
       
    players = [o for o in game.layers['joueur']]
    nbPlayers = len(players)
    score = [0]*nbPlayers
    
    # on localise tous les états initiaux (loc du joueur)
    initStates = [o.get_rowcol() for o in game.layers['joueur']]
    print ("Init states:", initStates)
    
    # on localise tous les objets ramassables
    goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
    print ("Goal states:", goalStates)
        
    # on localise tous les murs
    wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
    #print ("Wall states:", wallStates)

    # Pour éviter les bugs, mettre des murs tout autour de la map
    for i in range(game.spriteBuilder.rowsize):
        wallStates.append((game.spriteBuilder.rowsize,i))
    for i in range(game.spriteBuilder.colsize):
        wallStates.append((i,game.spriteBuilder.colsize))
    
    #-------------------------------
    # Placement aleatoire des fioles 
    #-------------------------------
    
    
    # on donne a chaque joueur une fiole à ramasser
    
    fioles = [0]*len(initStates)

    # Même nombre d'items ramassables et de players
    if(len(goalStates) == len(initStates)):
        for i in range (len(initStates)):
            if i == len(initStates)-1:
                fioles[i] = goalStates[0]
            else:
                fioles[i] = goalStates[i+1]

    # Nombre items < Nombre players (carte 4)
    '''
    if(len(goalStates) < len(initStates)):
        for i in range (len(initStates)):
            if i >= len(goalStates):
                print("entree")
                fioles[i] = random.choice(goalStates)
            else:
                fioles[i] = goalStates[i]
    print("fioles = ",fioles)
    '''
    
    
    #-------------------------------
    # Boucle principale de déplacements 
    #-------------------------------

#-------------------------------
    # Cooperative Pathfinding
    #-------------------------------
    
    posPlayers = initStates
    print("nbPlayers ",nbPlayers)

    
    parcours = []
    for j in range(nbPlayers):
        vide = []
        parcours.append(vide)

    # Initialisation des chemins au début
    collisions = list(wallStates)
    chemins = []
    pause = [0]*len(initStates)

    # Initialisation des chemins optimaux réservés pour chaque joueur

    cpt = 0

    for j in range(nbPlayers):
        p = Probleme(initStates[j],fioles[j],wallStates,'manhattan')
        listeTemporaire = astar(p)
        chemins.append(listeTemporaire)
        temp = []

        for c in chemins[j]:
            temp.append(c.etat)

        # Permet de savoir s'il faut faire passer le joueur en question
        # ou de le mettre en pause pour le début

        for t in temp:
            if t in collisions:
                pause[j] = 1
                break
        if pause[j] == 1:
            continue

        for n in listeTemporaire:
            collisions.append(n.etat)
            parcours[j].append(n.etat)

    for i in range(iterations):
        for j in range(nbPlayers): # on fait bouger chaque joueur séquentiellement

            # Si pas de pause, le joueur peut bouger
            if pause[j] == 0:
                listeTemporaire = list(chemins[j])
                n = listeTemporaire[-2]
                next_row,next_col = n.etat
                players[j].set_rowcol(next_row,next_col)
                print ("pos :", j, next_row,next_col)
                game.mainiteration()

            # Si pause, le joueur va attendre sur sa position initiale
            # jusqu'à qu'aucun joueur ne soit sur son chemin

            if pause[j] == 1:

                if posPlayers[j] == fioles[j]:
                    # Si le joueur est en pause sur la case de sa fiole
                    # Cela signifie qu'il l'a déjà ramassée
                    # Donc il attend sur sa position
                    next_row,next_col = posPlayers[j]
                    players[j].set_rowcol(next_row,next_col)
                    print ("pos :", j, next_row,next_col)
                    game.mainiteration()
                    continue

                pause[j] = 0
                listeTemporaire = []
                for c in chemins[j]:
                    listeTemporaire.append(c.etat)

                # Teste si on doit continuer à faire la pause
                # cad si les autres joueurs ont libéré leur case
                # sur le chemin du joueur qui attend depuis le début
                for p in listeTemporaire:
                    for i in range(0,nbPlayers):
                        if i !=j:
                            if p in parcours[i]:
                                pause[j] = 1
                                break
                    if pause[j] == 1:
                        break

                if pause[j] == 1:
                    listeTemporaire = list(chemins[j])
                    n = listeTemporaire[-1]
                    next_row,next_col = n.etat
                    players[j].set_rowcol(next_row,next_col)
                    print ("pos in :", j, next_row,next_col)
                    game.mainiteration()
                    continue

                else : # Le joueur arrête sa pause
                    listeTemporaire = list(chemins[j])
                    for l in listeTemporaire:
                        parcours[j].append(l.etat)

                    if (len(listeTemporaire)==1):
                        n = listeTemporaire[0]
                    else :
                        n = listeTemporaire[-2]
                    next_row,next_col = n.etat
                    players[j].set_rowcol(next_row,next_col)
                    print ("pos out :", j, next_row,next_col)
                    game.mainiteration()

            del chemins[j][-1] # Sert pour cette ligne de code : listeTemporaire = chemins[j] n = listeTemporaire[-2]
            if len(parcours[j]) > 1:
                    del parcours[j][-1]
            col=next_col
            row=next_row
            posPlayers[j]=(row,col)

            # si on a  trouvé un objet on le ramasse
            #if (row,col) in goalStates:
            if (row,col) == fioles[j]:
                o = players[j].ramasse(game.layers)
                game.mainiteration()
                print ("Objet ",o," trouvé par le joueur ", j)
                goalStates.remove((row,col)) # on enlève ce goalState de la listeTemporairee
                score[j]+=1
                pause[j] = 1
                cpt += 1
                if cpt == nbPlayers:
                    break # On arrête la boucle for
                '''
                for d in parcours[j]:
                    #d = d.etat
                    if d not in collisions:
                        continue
                    else:
                        collisions.remove(d)
                '''     
            posPlayers[j] = (row,col)
        if cpt == nbPlayers:
            break # On arrête la seconde boucle for

    print ("scores:", score)
    print("Nombre d'itérartions utilisées :", i)
    pygame.quit()
     
    #-------------------------------
    # Moving along the path
    #-------------------------------

if __name__ == '__main__':
    main()
