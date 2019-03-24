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
    #name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer2'
    #name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer3'
    #name = _boardname if _boardname is not None else '10x10'
    #name = _boardname if _boardname is not None else 'Lab_15x15'
    #name = _boardname if _boardname is not None else 'map'
    #name = _boardname if _boardname is not None else 'map2'
    #name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer_6x6'
    #name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer_bomberman'
    #name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer_impossible'
    #name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer_incroyable'
    #name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer_labyrinthe2'
    #name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer_labyrinthe3'
    #name = _boardname if _boardname is not None else 'thirst'
    
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 10  # frames per second
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

    # Pour éviter les bugs, mettre des murs tout autour la map
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
            
            #fioles[i] = goalStates[i]


    # Nombre items < Nombre players (carte 4)
    '''
    if(len(goalStates) < len(initStates)):
        for i in range (len(initStates)):
            print(i)
            if i >= len(goalStates):
                fioles[i] = random.choice(goalStates)
            else:
                fioles[i] = goalStates[i]
    print("fioles = ",fioles)
    '''

    
    #-------------------------------
    # Boucle principale de déplacements 
    #-------------------------------

#-------------------------------
    # Building the best path with A* SANS COLLISION => OPPORTUNISTE
    #-------------------------------
    
    posPlayers = list(initStates)
    print("nbPlayers ",nbPlayers)

    cpt = 0 # Compteur pour arrêter les boucles for
    # afin d'afficher le nombre d'iétrations utilisées

    for i in range(iterations):
        for j in range(nbPlayers): # on fait bouger chaque joueur séquentiellement
            if posPlayers[j] == fioles[j]: # Si le joueur a déjà atteint sa fiole, il reste sur sa case
                next_row,next_col = posPlayers[j]
                players[j].set_rowcol(next_row,next_col)
                print ("pos :", j, next_row,next_col)
                continue
            collisions = wallStates + posPlayers
            p = Probleme(posPlayers[j],fioles[j],collisions,'manhattan')
            listeTemporaire = astar(p)
            #print("Vraie distance = ",len(listeTemporaire))
            n = listeTemporaire[-2]
            next_row,next_col = n.etat
            players[j].set_rowcol(next_row,next_col)
            print ("pos :", j, next_row,next_col)
            game.mainiteration()

            col=next_col
            row=next_row
            posPlayers[j]=(row,col)

            # si on a  trouvé un objet on le ramasse
            #if (row,col) in goalStates:
            if (row,col) == fioles[j]:
                o = players[j].ramasse(game.layers)
                game.mainiteration()
                print ("Objet ",o," trouvé par le joueur ", j)
                goalStates.remove((row,col)) # on enlève ce goalState de la liste
                score[j]+=1
                cpt +=1
                if cpt == nbPlayers:
                    break # On arrête la boucle for

                # A DECOMMENTER SI FIOLES BONUS QUI REAPPARAISSENT
                '''
                if o != None: # Si le joueur est arrivé à temps pour ramasser l'objet avant ses adversaires
                    goalStates.remove((row,col)) # on enlève ce goalState de la liste
                    score[j]+=1
                    
                    # et on remet un même objet à un autre endroit
                    x = random.randint(1,game.spriteBuilder.colsize-1)
                    y = random.randint(1,game.spriteBuilder.rowsize-1)
                    while (x,y) in wallStates:
                        x = random.randint(1,game.spriteBuilder.colsize-1)
                        y = random.randint(1,game.spriteBuilder.rowsize-1)
                    o.set_rowcol(x,y)
                    goalStates.append((x,y)) # on ajoute ce nouveau goalState
                    fioles[j] = (x,y)
                    game.layers['ramassable'].add(o)
                    game.mainiteration()
                else: # Si le joueur n'est pas arrivé à temps
                    fioles[j] = random.choice(goalStates)
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