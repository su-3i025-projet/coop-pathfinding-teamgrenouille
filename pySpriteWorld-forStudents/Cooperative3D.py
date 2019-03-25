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
    #name = _boardname if _boardname is not None else 'map' #NON
    #name = _boardname if _boardname is not None else 'map2' #NON
    #name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer_6x6' #YES
    #name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer_bomberman' #YES
    #name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer_impossible'
    #name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer_incroyable'
    #name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer_labyrinthe2'
    #name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer_labyrinthe3'
    name = _boardname if _boardname is not None else 'thirst'

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
    #print ("Wall states:", wallStates)

    # Initialisation des réservations par défaut

    # Toutes les cases à -1
    for r in range (game.spriteBuilder.rowsize+1):
        for c in range (game.spriteBuilder.colsize+1):
            for t in range (iterations+1):
                reservations[((r,c),t)] = -1

    # Pour éviter les bugs, mettre des murs tout autour de la map
    for i in range(game.spriteBuilder.rowsize):
        wallStates.append((game.spriteBuilder.rowsize,i))
    for i in range(game.spriteBuilder.colsize):
        wallStates.append((i,game.spriteBuilder.colsize))

    # Réservations des murs à nbPlayers
    for i in range(len(wallStates)):
        for t in range (iterations):
            reservations[((wallStates[i]),t)] = nbPlayers
    
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
    '''

    #-------------------------------
    # Boucle principale de déplacements 
    #-------------------------------

#-------------------------------
    # Cooperative Pathfinding with three dimensions
    #-------------------------------
    
    posPlayers = initStates
    print("nbPlayers ",nbPlayers)

    # Initialisation des chemins au début
    collisions = list(wallStates)
    chemins = [[] for j in range(nbPlayers)]

    collisionsJ = [[] for _ in range(nbPlayers)]

    cpt = 0
    pause = [0]*nbPlayers

    # Initialisation des chemins réservées

    for j in range(nbPlayers):
        print("Joueur = ",j)
        for t in range (iterations):

            collisionsJ[j] = list(wallStates)

            # On ajoute dans les collisions au temps t, les cases des fioles des autres joueurs
            # si elles ont été prises, et si leurs cases sont occupées
            for p in range(nbPlayers):
                if p != j:
                    if reservations[(fioles[p],t)] != -1 and reservations[(fioles[p],t)] != j:
                        if fioles[j] not in collisionsJ[j]:
                            collisionsJ[j].append(fioles[p])

            # Problème initial au temps t
            p = Probleme(initStates[j],fioles[j],collisionsJ[j],'manhattan')
            listeTemporaire = astar(p)

            # Si le joueur a atteint sa case fiole, il arrête de jouer
            #il réserve sa case jusqu'à la fin
            # et il arrête d'itérer
            if(len(listeTemporaire)==1 and listeTemporaire[0].etat == fioles[j]):
                c = listeTemporaire[0].etat
                chemins[j].append(listeTemporaire[0])
                for a in range(t,iterations):
                    reservations[(c,a)] = j
                break

            # Sinon il fait une pause, et il reste sur sa position à ce temps t
            elif(len(listeTemporaire)==1 and listeTemporaire[0].etat != fioles[j]):
                pause[j] = 1
                next_row,next_col = initStates[j]
                reservations[((next_row,next_col),t)] = j
                reservations[((next_row,next_col),t+1)] = j
                n = listeTemporaire[-1]
                chemins[j].append(n)
                continue


            n = listeTemporaire[-2]
            c = n.etat
            collisions = list(collisionsJ[j])
            if(pause[j] == 0): # Si pas de pause

                # Si case réservée au temps t+1
                # ATTENTION PAS DE PAUSE
                if reservations[(c,t+1)] != j and reservations[(c,t+1)] != -1:
                    collisions.append(c) # On ajoute dans sa liste de collisions la case réservée, et on crée un nouveau problème
                    p = Probleme(initStates[j],fioles[j],collisions,'manhattan') # Le problème prend en compte la case réservée
                    listeTemporaire = astar(p)
                    n = listeTemporaire[-2]
                    c = n.etat
                    # On revérifie à la case réservée au temps t+2, et même processus (nouveau problème) pour éviter les collisions
                    if reservations[(c,t+2)] != j and reservations[(c,t+2)] != -1:
                        collisions.append(c)
                        p = Probleme(initStates[j],fioles[j],collisions,'manhattan')
                        listeTemporaire = astar(p)
                        n = listeTemporaire[-2]
                        c = n.etat
                        next_row,next_col = c
                        reservations[(c,t)] = j
                        reservations[(c,t+1)] = j
                        chemins[j].append(n)
                        initStates[j] = next_row,next_col
                        pause[j] = 1 # Si la case a été réservée, on fait attention et on met son boolean pause à 1

                    else: # Sinon on continue sur le premier problème
                        next_row,next_col = c
                        reservations[(c,t)] = j
                        reservations[(c,t+1)] = j
                        chemins[j].append(n)
                        initStates[j] = next_row,next_col
                        pause[j] = 1

                # ATTENTION PAS DE PAUSE
                else: # Si case non réservée au temps t+1
                    next_row,next_col = c
                    reservations[(c,t)] = j
                    reservations[(c,t+1)] = j
                    if len(listeTemporaire)>2 and reservations[(listeTemporaire[-3].etat,t)] == -1 :
                        # Si la taille de la liste des coups est supérieure à 2, on réserve aussi une deuxième case d'avance pour éviter les collisions
                        reservations[(listeTemporaire[-3].etat,t)] = j
                        reservations[(listeTemporaire[-3].etat,t+1)] = j
                    chemins[j].append(n)
                    initStates[j] = next_row,next_col

            else: # Si le joueur a été en pause
                # Le joueur recalcule un problème
                if reservations[(c,t+1)] != j and reservations[(c,t+1)] != -1 : # Si case réservée
                    collisions.append(c)
                    p = Probleme(initStates[j],fioles[j],collisions,'manhattan')
                    listeTemporaire = astar(p)
                    temp = []

                    n = listeTemporaire[-1]
                    d = n.etat
                    for c in listeTemporaire:
                        temp.append(c.etat)
                    # ATTENTION EN PAUSE
                    if fioles[j] not in temp: # Si la fiole n'est pas dans son parcours = son chemin est bloqué + réservations aux temps t, t+1
                        pause[j] = 1 # Le joueur est en pause
                        next_row,next_col = initStates[j]
                        reservations[((next_row,next_col),t)] = j
                        reservations[((next_row,next_col),t+1)] = j
                        if len(listeTemporaire)>2 and reservations[(listeTemporaire[-3].etat,t)] == -1 :
                            # Si la taille de la liste des coups est supérieure à 2, on réserve aussi une deuxième case d'avance pour éviter les collisions
                            reservations[(listeTemporaire[-3].etat,t)] = j
                            reservations[(listeTemporaire[-3].etat,t+1)] = j

                        n = listeTemporaire[-1]
                        chemins[j].append(n)

                        temp = []
                        for c in chemins[j]:
                            temp.append(c.etat)
                        continue

                    # ATTENTION EN PAUSE
                    else: # Sinon (chemin trouvé jusqu'à sa fiole) au prochain coup, il ne fait pas de pause, et il avance + réservations aux temps t, t+1
                        pause[j] = 0
                        next_row,next_col = d
                        reservations[(d,t)] = j
                        reservations[(d,t+1)] = j
                        if len(listeTemporaire)>2 and reservations[(listeTemporaire[-3].etat,t)] == -1 :
                            # Si la taille de la liste des coups est supérieure à 2, on réserve aussi une deuxième case d'avance pour éviter les collisions
                            reservations[(listeTemporaire[-3].etat,t)] = j
                            reservations[(listeTemporaire[-3].etat,t+1)] = j
                        chemins[j].append(n)
                        initStates[j] = next_row,next_col
                # ATTENTION EN PAUSE
                else: # Si case non réservée
                    d = n.etat
                    temp = []
                    for c in listeTemporaire:
                        temp.append(c.etat)
                    # ATTENTION EN PAUSE
                    if fioles[j] not in temp:
                        pause[j] = 1
                        next_row,next_col = initStates[j]
                        reservations[(next_row,next_col,t)] = j
                        reservations[(next_row,next_col,t+1)] = j

                        if len(listeTemporaire)>2 and reservations[(listeTemporaire[-3].etat,t)] == -1 :
                            # Si la taille de la liste des coups est supérieure à 2, on réserve aussi une deuxième case d'avance pour éviter les collisions
                            reservations[(listeTemporaire[-3].etat,t)] = j
                            reservations[(listeTemporaire[-3].etat,t+1)] = j
                        n = listeTemporaire[-1]
                        chemins[j].append(n)
                        continue
                    # ATTENTION EN PAUSE
                    else: # Sinon (chemin trouvé jusqu'à sa fiole) au prochain coup, il ne fait pas de pause, et il avance + réservations aux temps t, t+1
                        pause[j] = 0
                        next_row,next_col = d
                        reservations[(d,t)] = j
                        reservations[(d,t+1)] = j
                        if len(listeTemporaire)>2 and reservations[(listeTemporaire[-3].etat,t)] == -1 :
                            # Si la taille de la liste des coups est supérieure à 2, on réserve aussi une deuxième case d'avance pour éviter les collisions
                            reservations[(listeTemporaire[-3].etat,t)] = j
                            reservations[(listeTemporaire[-3].etat,t+1)] = j
                        chemins[j].append(n)
                        initStates[j] = next_row,next_col

    pause = [0]*nbPlayers

    cpt = 0

    for i in range(iterations):
        for j in range(nbPlayers): # on fait bouger chaque joueur séquentiellement

            if(pause[j]==1):
                next_row,next_col = initStates[j]
                players[j].set_rowcol(next_row,next_col)
                print ("pos :", j, next_row,next_col)
                game.mainiteration()
                continue

            listeTemporaire = chemins[j]
            n = listeTemporaire[0]
            next_row,next_col = n.etat
            players[j].set_rowcol(next_row,next_col)
            print ("pos :", j, next_row,next_col)
            game.mainiteration()

            del chemins[j][0]
            col=next_col
            row=next_row
            posPlayers[j]=(row,col)

            if (row,col) == fioles[j]:
                o = players[j].ramasse(game.layers)
                game.mainiteration()
                print ("Objet trouvé par le joueur ", j)
                goalStates.remove((row,col)) # on enlève ce goalState de la listeTemporairee
                score[j]+=1
                pause[j] = 1
                cpt += 1
                if cpt == nbPlayers:
                    break # On arrête la boucle for

            initStates[j] = (row,col)
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