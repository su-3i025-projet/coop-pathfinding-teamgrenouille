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
    name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer2' #NON
    name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer3'
    name = _boardname if _boardname is not None else '10x10'
    name = _boardname if _boardname is not None else 'Lab_15x15'
    #name = _boardname if _boardname is not None else 'map'
    #name = _boardname if _boardname is not None else 'map2'
    #name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer_6x6' #NON
    #name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer_bomberman' #YES
    #name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer_impossible'
    #name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer_incroyable'
    #name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer_labyrinthe2'
    #name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer_labyrinthe3' #NON
    #name = _boardname if _boardname is not None else 'thirst'

    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 10  # frames per second
    game.mainiteration()
    game.mask.allow_overlaping_players = True
    #player = game.player
    
def main():

    #for arg in sys.argv:
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
    
    
    # on donne a chaque joueur une fiole a ramasser

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

    # Initialisation des chemins au début
    collisions = list(wallStates)

    chemins = []
    pause = [0]*len(initStates)

    # INITIALISATION
    for j in range(nbPlayers):
        p = Probleme(initStates[j],fioles[j],collisions,'manhattan')
        listeTemporaire = astar(p)
        chemins.append(listeTemporaire)
        temp = []

        for c in chemins[j]:
            temp.append(c.etat)

        if fioles[j] not in temp:
            pause[j] = 1
            continue

        for n in listeTemporaire:
            collisions.append(n.etat)

    cpt = 0

    for i in range(iterations):
        for j in range(nbPlayers): # on fait bouger chaque joueur séquentiellement
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

                p = Probleme(posPlayers[j],fioles[j],collisions,'manhattan')
                listeTemporaire = astar(p)
                chemins[j] = listeTemporaire
                temp = []
                for c in chemins[j]:
                    temp.append(c.etat)
                if fioles[j] not in temp:
                    pause[j] = 1
                    continue
                else:
                    pause[j] = 0
                    for n in listeTemporaire:
                        collisions.append(n.etat)

            listeTemporaire = chemins[j]
            n = listeTemporaire[-2]
            next_row,next_col = n.etat
            players[j].set_rowcol(next_row,next_col)
            print ("pos :", j, next_row,next_col)
            # On enlève la collision arrière (!!!) à chaque déplacement afin de limiter les bouchons
            # MAIS PROBLEME : Chemin pas forcément optimal, voire un très mauvais chemin très loin d'être optimal...
            if posPlayers[j] in collisions:
                collisions.remove(posPlayers[j])
            # Malgré cela, il reste des blocages, d'où la stratégie coopérative avancée
            posPlayers[j] = (next_row,next_col)
            game.mainiteration()

            '''
            # On enlève la collision arrière (!!!) à chaque déplacement afin de limiter les bouchons
            # MAIS PROBLEME : Chemin pas forcément optimal, voire un très mauvais chemin très loin d'être optimal...
            if (next_row,next_col) in collisions:
                collisions.remove((next_row,next_col))
            # Malgré cela, il reste des blocages, d'où la stratégie coopérative avancée
            '''

            del chemins[j][-1] # Sert pour cette ligne de code : listeTemporaire = chemins[j] n = listeTemporaire[-2]
            col=next_col
            row=next_row
            posPlayers[j]=(row,col)

            # si on a  trouvé un objet on le ramasse
            if (row,col) == fioles[j]:
                o = players[j].ramasse(game.layers)
                game.mainiteration()
                print ("Objet ",o," trouvé par le joueur ", j)
                goalStates.remove((row,col)) # on enlève ce goalState de la liste
                score[j]+=1
                pause[j] = 1
                cpt += 1
                if cpt == nbPlayers:
                    break # On arrête la boucle for        

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
