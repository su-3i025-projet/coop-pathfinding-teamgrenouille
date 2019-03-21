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
    #name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer_6x6'
    name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer3'
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 5  # frames per second
    game.mainiteration()
    game.mask.allow_overlaping_players = True
    #player = game.player
    
def main():

    #for arg in sys.argv:
    iterations = 50 # default
    if len(sys.argv) == 2:
        iterations = int(sys.argv[1])
    print ("Iterations: ")
    print (iterations)

    init()

    #-------------------------------
    # Initialisation
    #-------------------------------

    reservations = {}
       
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
    print ("Wall states:", wallStates)

    for r in range (game.spriteBuilder.rowsize+1):
        for c in range (game.spriteBuilder.colsize+1):
            for t in range (iterations+1):
                reservations[((r,c),t)] = -1
    
    wallStates.append((6,0))
    wallStates.append((6,1))
    wallStates.append((6,2))
    wallStates.append((6,3))
    wallStates.append((6,4))
    wallStates.append((6,5))
    

    for i in range(game.spriteBuilder.rowsize):
        wallStates.append((game.spriteBuilder.rowsize,i))
    for i in range(game.spriteBuilder.colsize):
        wallStates.append((i,game.spriteBuilder.colsize))
    
    '''
    pos : 0 11 12
    pos : 1 15 8
    pos : 2 14 11
    pos : 0 12 12
    pos : 1 16 8
    pos : 2 13 11
    pos : 0 13 12
    pos : 1 17 8
    pos : 2 13 12
    pos : 0 13 11
    pos : 1 18 8
    pos : 2 13 13
    pos : 0 13 10
    pos : 1 19 8
    Objet trouvé par le joueur  1
    '''

    for i in range(len(wallStates)):
        #row,col = wallStates[i]
        for t in range (iterations):
            #reservations[(row,col,j)] = 1
            reservations[((wallStates[i]),t)] = nbPlayers
    
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
            print(i)
            if i == len(initStates)-1:
                fioles[i] = goalStates[0]
            else:
                fioles[i] = goalStates[i+1]
    # Nombre items < Nombre players (carte 4)
    if(len(goalStates) < len(initStates)):
        for i in range (len(initStates)):
            print(i)
            #print("goalStates[",i,"]=",goalStates[i])
            print("fioles=",fioles)
            if i >= len(goalStates):
                print("entree")
                fioles[i] = random.choice(goalStates)
            else:
                #print("goalStates[",i,"]=",goalStates[i])
                print("lala")
                fioles[i] = goalStates[i]
    print("fioles = ",fioles)
    
    
    #-------------------------------
    # Boucle principale de déplacements 
    #-------------------------------

#-------------------------------
    # Cooperative Pathfinding with three dimensions
    #-------------------------------
    
    posPlayers = initStates
    print("nbPlayers ",nbPlayers)

    '''pos : 2 14 10
    pos : 0 11 9
    pos : 1 14 10'''

    # Initialisation des chemins au début
    collisions = list(wallStates)
    #tototata = wallStates
    #print("collisions wallStates = ",collisions)
    chemins = []
    for j in range(nbPlayers):
        vide = []
        chemins.append(vide)

    print("CHEMINS INITIAUX =",chemins)
    print("ROW = ",game.spriteBuilder.rowsize)
    print("COL = ",game.spriteBuilder.colsize)

    #print(reservations)

    pause = [0]*nbPlayers
    print("pause=",pause)
    # Comment améliorer l'ordre de passage ???
    for j in range(nbPlayers):
        print("Joueur = ",j)
        for t in range (iterations):
            #reservations[((wallStates[i]),t)] = 1
            #wallStates = tototata
            print("DEBUT ITER = ",initStates[j])
            p = Probleme(initStates[j],fioles[j],wallStates,'manhattan')
            print(wallStates)
            listeTemporaire = astar(p)
            print(len(listeTemporaire))
            if(len(listeTemporaire)==1 and listeTemporaire[0].etat == fioles[j]):
                c = listeTemporaire[0].etat
                #next_row,next_col = c
                reservations[(c,t)] = j
                chemins[j].append(listeTemporaire[0])
                break
            elif(len(listeTemporaire)==1 and listeTemporaire[0].etat != fioles[j]):
                pause[j] = 1
                next_row,next_col = initStates[j]
                reservations[((next_row,next_col),t)] = j
                reservations[((next_row,next_col),t+1)] = j
                n = listeTemporaire[-1]
                chemins[j].append(n)
                #initStates[j] = next_row,next_col
                continue

            n = listeTemporaire[-2]
            c = n.etat
            collisions = list(wallStates)
            if(pause[j] == 0): # Si pas de pause
                print("PAUSE 0")
                if reservations[(c,t+1)] != j and reservations[(c,t+1)] != -1: # Si case réservée
                    #print(j)
                    print("RESERVATION = 1")
                    collisions.append(c)
                    print("c avant=",c)
                    print("collisions=",collisions)
                    p = Probleme(initStates[j],fioles[j],collisions,'manhattan')
                    listeTemporaire = astar(p)
                    n = listeTemporaire[-2]
                    c = n.etat
                    print("c apres=",c)
                    if reservations[(c,t+2)] != j and reservations[(c,t+2)] != -1:
                        collisions.append(c)
                        p = Probleme(initStates[j],fioles[j],collisions,'manhattan')
                        listeTemporaire = astar(p)
                        n = listeTemporaire[-2]
                        c = n.etat
                        np = listeTemporaire[-3].etat
                        next_row,next_col = c
                        reservations[(c,t)] = j
                        reservations[(c,t+1)] = j
                        chemins[j].append(n)
                        initStates[j] = next_row,next_col
                        pause[j] = 1
                    else:    
                        np = listeTemporaire[-3].etat
                        next_row,next_col = c
                        reservations[(c,t)] = j
                        reservations[(c,t+1)] = j
                        '''
                        if len(listeTemporaire)>2 and reservations[(listeTemporaire[-3].etat,t)] == -1 :
                            reservations[(listeTemporaire[-3].etat,t)] = j
                            reservations[(listeTemporaire[-3].etat,t+1)] = j
                        '''
                        chemins[j].append(n)
                        initStates[j] = next_row,next_col
                        pause[j] = 1
                else: # Si case non réservée
                    print("RESERVATION = 0")
                    print(reservations[(c,t)])
                    next_row,next_col = c
                    reservations[(c,t)] = j
                    reservations[(c,t+1)] = j
                    if len(listeTemporaire)>2 and reservations[(listeTemporaire[-3].etat,t)] == -1 :
                        #print("j'entre")
                        reservations[(listeTemporaire[-3].etat,t)] = j
                        reservations[(listeTemporaire[-3].etat,t+1)] = j
                        '''
                        if len(listeTemporaire)>3 and reservations[(listeTemporaire[-4].etat,t)] == -1 :
                            reservations[(listeTemporaire[-4].etat,t)] = j
                            reservations[(listeTemporaire[-4].etat,t+1)] = j
                        '''
                    #print("j=",j)
                    #print("chemins=",chemins)
                    chemins[j].append(n)
                    initStates[j] = next_row,next_col
            else: # PAUSE
            #if(pause[j] == 1):
                print("PAUSE 1")
                if reservations[(c,t+1)] != j and reservations[(c,t+1)] != -1 : # Si case réservée
                    print("RESERVATION = 1")
                    collisions.append(c)
                    p = Probleme(initStates[j],fioles[j],collisions,'manhattan')
                    listeTemporaire = astar(p)
                    temp = []

                    n = listeTemporaire[-1]
                    d = n.etat
                    for c in listeTemporaire:
                        temp.append(c.etat)
                    if fioles[j] not in temp:
                        print("FIOLE NOT IN TEMP")
                        pause[j] = 1
                        #next_row,next_col = c
                        next_row,next_col = initStates[j]
                        reservations[((next_row,next_col),t)] = j
                        reservations[((next_row,next_col),t+1)] = j
                        if len(listeTemporaire)>2 and reservations[(listeTemporaire[-3].etat,t)] == -1 :
                            reservations[(listeTemporaire[-3].etat,t)] = j
                            reservations[(listeTemporaire[-3].etat,t+1)] = j
                            '''
                            if len(listeTemporaire)>3 and reservations[(listeTemporaire[-4].etat,t)] == -1 :
                                reservations[(listeTemporaire[-4].etat,t)] = j
                                reservations[(listeTemporaire[-4].etat,t+1)] = j
                            '''
                        n = listeTemporaire[-1]
                        chemins[j].append(n)
                        #print("CHEMIN = ",chemins[j])
                        temp = []
                        for c in chemins[j]:
                            temp.append(c.etat)
                        print("temp chemin = ",temp)
                        #initStates[j] = next_row,next_col
                        continue
                    else:
                        '''
                        pos : 1 13 11
                        pos : 2 14 9
                        pos : 0 10 9
                        pos : 1 13 10
                        pos : 2 14 10
                        pos : 0 11 9
                        pos : 1 14 10
                        pos : 2 14 11
                        '''
                        print("FIOLE IN TEMP")
                        pause[j] = 0
                        next_row,next_col = d
                        print("lol")
                        print(c)
                        print(t)
                        reservations[(d,t)] = j
                        reservations[(d,t+1)] = j
                        if len(listeTemporaire)>2 and reservations[(listeTemporaire[-3].etat,t)] == -1 :
                            reservations[(listeTemporaire[-3].etat,t)] = j
                            reservations[(listeTemporaire[-3].etat,t+1)] = j
                            '''
                            if len(listeTemporaire)>3 and reservations[(listeTemporaire[-4].etat,t)] == -1 :
                                reservations[(listeTemporaire[-4].etat,t)] = j
                                reservations[(listeTemporaire[-4].etat,t+1)] = j
                            '''
                        chemins[j].append(n)
                        initStates[j] = next_row,next_col
                else: # Si case non réservée
                    #p = Probleme(initStates[j],fioles[j],collisions,'manhattan')
                    #listeTemporaire = astar(p)
                    #temp = []
                    #n = listeTemporaire[-2]
                    print("RESERVATION = 0")
                    #print(reservations[(c,t)])
                    d = n.etat
                    temp = []
                    for c in listeTemporaire:
                        temp.append(c.etat)
                    if fioles[j] not in temp:
                        print("FIOLE NOT IN TEMP")
                        pause[j] = 1
                        next_row,next_col = initStates[j]
                        reservations[(next_row,next_col,t)] = j
                        reservations[(next_row,next_col,t+1)] = j

                        if len(listeTemporaire)>2 and reservations[(listeTemporaire[-3].etat,t)] == -1 :
                            reservations[(listeTemporaire[-3].etat,t)] = j
                            reservations[(listeTemporaire[-3].etat,t+1)] = j
                            '''
                            if len(listeTemporaire)>3 and reservations[(listeTemporaire[-4].etat,t)] == -1 :
                                reservations[(listeTemporaire[-4].etat,t)] = j
                                reservations[(listeTemporaire[-4].etat,t+1)] = j
                            '''
                        n = listeTemporaire[-1]
                        chemins[j].append(n)
                        #initStates[j] = next_row,next_col
                        continue
                    else:
                        print("FIOLE IN TEMP")
                        print("temp=",temp)
                        pause[j] = 0
                        next_row,next_col = d
                        reservations[(d,t)] = j
                        reservations[(d,t+1)] = j
                        if len(listeTemporaire)>2 and reservations[(listeTemporaire[-3].etat,t)] == -1 :
                            reservations[(listeTemporaire[-3].etat,t)] = j
                            reservations[(listeTemporaire[-3].etat,t+1)] = j
                            '''
                            if len(listeTemporaire)>3 and reservations[(listeTemporaire[-4].etat,t)] == -1 :
                                reservations[(listeTemporaire[-4].etat,t)] = j
                                reservations[(listeTemporaire[-4].etat,t+1)] = j
                            '''
                        chemins[j].append(n)
                        initStates[j] = next_row,next_col
    pause = [0]*nbPlayers
    #print("DICO=", reservations)

    for i in range(iterations):
        for j in range(nbPlayers): # on fait bouger chaque joueur séquentiellement
            if(pause[j]==1):
                next_row,next_col = initStates[j]
                players[j].set_rowcol(next_row,next_col)
                print ("pos :", j, next_row,next_col)
                game.mainiteration()
                continue
            listeTemporaire = chemins[j]
            #n = listeTemporaire[-2]
            n = listeTemporaire[0]
            #print("attention=",n.etat)
            next_row,next_col = n.etat
            players[j].set_rowcol(next_row,next_col)
            print ("pos :", j, next_row,next_col)
            game.mainiteration()

            # On enlève la collision à chaque déplacement afin de limiter les bouchons
            if (next_row,next_col) in collisions:
                collisions.remove((next_row,next_col))
            # Malgré cela, il reste des blocages, d'où la stratégie coopérative avancée

            #del chemins[j][-1]
            del chemins[j][0]
            col=next_col
            row=next_row
            posPlayers[j]=(row,col)

            # si on a  trouvé un objet on le ramasse
            #if (row,col) in goalStates:
            if (row,col) == fioles[j]:
                o = players[j].ramasse(game.layers)
                game.mainiteration()
                #if(o==None):
                #    continue
                print ("Objet trouvé par le joueur ", j)
                goalStates.remove((row,col)) # on enlève ce goalState de la listeTemporairee
                score[j]+=1
                pause[j] = 1
                '''    
                # et on remet un même objet à un autre endroit
                x = random.randint(1,19)
                y = random.randint(1,19)
                while (x,y) in wallStates:
                    x = random.randint(1,19)
                    y = random.randint(1,19)
                o.set_rowcol(x,y)
                goalStates.append((x,y)) # on ajoute ce nouveau goalState

                # Nouveau problème
                initStates[j] = (row,col)
                fioles[j] = (x,y)
                p = Probleme(initStates[j],fioles[j],collisions,'manhattan')
                listeTemporaire = astar(p)
                chemins[j] = listeTemporaire
                for n in listeTemporaire:
                    print("n.etat = ",n.etat)
                    collisions.append(n.etat)
                game.layers['ramassable'].add(o)
                game.mainiteration()                
                '''
            initStates[j] = (row,col)


    print ("scores:", score)
    pygame.quit()
     
    #-------------------------------
    # Moving along the path
    #-------------------------------

if __name__ == '__main__':
    main()