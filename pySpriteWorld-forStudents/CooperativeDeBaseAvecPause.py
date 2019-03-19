# -*- coding: utf-8 -*-

# Nicolas, 2015-11-18

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
    # pathfindingWorld_MultiPlayer4
    name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer1'
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 10  # frames per second
    game.mainiteration()
    game.mask.allow_overlaping_players = True
    #player = game.player
    
def main():

    #for arg in sys.argv:
    iterations = 500 # default
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
    
    #-------------------------------
    # Placement aleatoire des fioles 
    #-------------------------------
    
    
    # on donne a chaque joueur une fiole a ramasser
    # en essayant de faire correspondre les couleurs pour que ce soit plus simple à suivre

    fioles = [0]*len(initStates)
    print(len(goalStates))
    print(len(initStates))
    
    # Même nombre d'items ramassables et de players
    if(len(goalStates) == len(initStates)):
        for i in range (len(initStates)):
            if i == len(initStates)-1:
                fioles[i] = goalStates[0]
            else:
                fioles[i] = goalStates[i+1]
    # Nombre items < Nombre players (carte 4)
    if(len(goalStates) < len(initStates)):
        for i in range (len(initStates)):
            if i >= len(goalStates):
                print("entree")
                fioles[i] = random.choice(goalStates)
            else:
                fioles[i] = goalStates[i]
    print("fioles = ",fioles)
    
    
    #-------------------------------
    # Boucle principale de déplacements 
    #-------------------------------

#-------------------------------
    # Cooperative Pathfinding
    #-------------------------------
    
    posPlayers = initStates
    print("nbPlayers ",nbPlayers)

    '''pos : 2 14 10
    pos : 0 11 9
    pos : 1 14 10'''

    # Initialisation des chemins au début
    collisions = wallStates
    print("collisions wallStates = ",collisions)
    chemins = []
    pause = [0]*len(initStates)
    # Comment améliorer l'ordre de passage ???
    for j in range(nbPlayers):
        p = Probleme(initStates[j],fioles[j],collisions,'manhattan')
        list = astar(p)
        #print("list = ",list)
        chemins.append(list)
        temp = []
        for c in chemins[j]:
            temp.append(c.etat)
        print("chemins[",j,"] = ",temp)
        print("fioles[",j,"] = ",fioles[j])
        if fioles[j] not in temp:
            pause[j] = 1
            print(j," : je continue à l'initialisation")
            continue
        for n in list:
            print("n.etat = ",n.etat)
            collisions.append(n.etat)
        print("collisions = ",collisions)

    for i in range(iterations):
        for j in range(nbPlayers): # on fait bouger chaque joueur séquentiellement
            if pause[j] == 1:
                p = Probleme(initStates[j],fioles[j],collisions,'manhattan')
                print(j," : premier astar")
                list = astar(p)
                chemins[j] = list
                temp = []
                for c in chemins[j]:
                    temp.append(c.etat)
                if fioles[j] not in temp:
                    pause[j] = 1
                    print(j," : je continue au premier astar")
                    continue
                else:
                    pause[j] = 0
                    for n in list:
                        collisions.append(n.etat)
            list = chemins[j]
            n = list[-2]
            next_row,next_col = n.etat
            players[j].set_rowcol(next_row,next_col)
            print ("pos :", j, next_row,next_col)
            # On enlève la collision arrière (!!!) à chaque déplacement afin de limiter les bouchons
            # MAIS PROBLEME : Chemin pas forcément optimal, voire un très mauvais chemin très loin d'être optimal...
            print("totototo = ",initStates[j])
            if initStates[j] in collisions:
                print(j," : j'enlève ",initStates[j])
                collisions.remove(initStates[j])
            # Malgré cela, il reste des blocages, d'où la stratégie coopérative avancée
            initStates[j] = (next_row,next_col)
            game.mainiteration()

            '''
            # On enlève la collision arrière (!!!) à chaque déplacement afin de limiter les bouchons
            # MAIS PROBLEME : Chemin pas forcément optimal, voire un très mauvais chemin très loin d'être optimal...
            if (next_row,next_col) in collisions:
                collisions.remove((next_row,next_col))
            # Malgré cela, il reste des blocages, d'où la stratégie coopérative avancée
            '''

            del chemins[j][-1] # Sert pour cette ligne de code : list = chemins[j] n = list[-2]
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
                    
                # et on remet un même objet à un autre endroit
                x = random.randint(1,game.spriteBuilder.colsize-1)
                y = random.randint(1,game.spriteBuilder.rowsize-1)
                while (x,y) in wallStates:
                    x = random.randint(1,game.spriteBuilder.colsize-1)
                    y = random.randint(1,game.spriteBuilder.rowsize-1)
                o.set_rowcol(x,y)
                print("Ajout d'un nouveau objet ",o," (",x,",",y,")")
                goalStates.append((x,y)) # on ajoute ce nouveau goalState
                game.layers['ramassable'].add(o)
                game.mainiteration() 
                # Nouveau problème
                initStates[j] = (row,col)
                fioles[j] = (x,y)
                p = Probleme(initStates[j],fioles[j],collisions,'manhattan')
                print("deuxieme astar")
                list = astar(p)
                chemins[j] = list
                temp = []
                for c in chemins[j]:
                    temp.append(c.etat)
                print("chemins[",j,"] = ",temp)
                print("fioles[",j,"] = ",fioles[j])
                if fioles[j] not in temp:
                    pause[j] = 1
                    print(j," : je continue")
                    continue
                for n in list:
                    collisions.append(n.etat)           

            initStates[j] = (row,col)


    print ("scores:", score)
    pygame.quit()
     
    #-------------------------------
    # Moving along the path
    #-------------------------------

if __name__ == '__main__':
    main()
