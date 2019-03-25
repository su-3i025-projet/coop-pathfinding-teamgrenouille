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

import copy
import heapq
import functools
import time

def distManhattan(p1,p2):
    """ calcule la distance de Manhattan entre le tuple 
        p1 et le tuple p2
        """
    (x1,y1)=p1
    (x2,y2)=p2
    return abs(x1-x2)+abs(y1-y2)

def trueDistance():
    """ calcule la vraie distance :
        la plus courte distance jusqu'à la destination
        en prenant au compte les obstacles
        mais ignore les autres joueurs.
        Plus exactement la longueur du chemin (optimal)
        donné par A*
        En d'autres termes : la distance d'un chemin "normal"
        que l'algorithme pourrait donné pour la destination
        """
    pass


###############################################################################

class Probleme():
    """ On definit un probleme comme étant: 
        - un état initial
        - un état but
        - une heuristique
        """
        
    def __init__(self,init,but,obstacles,heuristique):
        self.init=init
        self.but=but
        self.obstacles = obstacles
        self.heuristique=heuristique
        
    def estBut(self,e):
        """ retourne vrai si l'état e est un état but
            """
        return (self.but==e)
          
    def cost(self,e1,e2):
        """ donne le cout d'une action entre e1 et e2, 
            """
        return 1

    def estObstacle(self,e):
        """ retorune vrai si l'état est un obstacle
            """
        if (e in self.obstacles):
            return True
        else:
            return False

    def estDehors(self,etat):
        """retourne vrai si en dehors de la grille
            """
        #(s,_)=self.grid.shape
        (next_row,next_col)=etat
        return next_row<0 or next_row>20 or next_col<0 or next_col>20

    def successeurs(self,etat):
        """ retourne une liste avec les successeurs possibles
            """
        current_x,current_y = etat
        d = [(0,1),(1,0),(0,-1),(-1,0)]
        etatsApresMove = [(current_x+inc_x,current_y+inc_y) for (inc_x,inc_y) in d]
        return [e for e in etatsApresMove if not(self.estDehors(e)) and not(self.estObstacle(e))]

    def immatriculation(self,etat):
        """ génère une chaine permettant d'identifier un état de manière unique
            """
        s=""
        (x,y)= etat
        s+=str(x)+str(y)
        return s

    def h_value(self,e1,e2):
        """ applique l'heuristique pour le calcul 
            """
        if self.heuristique=='manhattan':
            h = distManhattan(e1,e2)
        elif self.heuristique=='uniform':
            h = 1
        elif self.heuristique=='trueDistance':
            h = trueDistance
        return h


    '''
    def h_valueTD(self,e1,e2,p):
        #p = Probleme(initStates[j],fioles[j],collisions,'manhattan')
        listeTemporaire = astar(p)
        res = len(listeTemporaire) - 1
        print("totot")
        return res
    '''


###############################################################################

@functools.total_ordering # to provide comparison of nodes
class Noeud:
    def __init__(self, etat, g, pere=None):
        self.etat = etat
        self.g = g
        self.pere = pere
        
    def __str__(self):
        return str(self.etat) + "valeur=" + str(self.g)
        
    def __eq__(self, other):
        return str(self) == str(other)
        
    def __lt__(self, other):
        return str(self) < str(other)
        
    def expand(self,p):
        """ étend un noeud avec ces fils
            pour un probleme de taquin p donné
            """
        nouveaux_fils = [Noeud(s,self.g+p.cost(self.etat,s),self) for s in p.successeurs(self.etat)]
        return nouveaux_fils
        
    def expandNext(self,p,k):
        """ étend un noeud unique, le k-ième fils du noeud n
            ou liste vide si plus de noeud à étendre
            """
        nouveaux_fils = self.expand(p)
        if len(nouveaux_fils)<k: 
            return []
        else: 
            return self.expand(p)[k-1]
            
    def trace(self,p):
        """ affiche tous les ancetres du noeud
            """
        n = self
        c=0 
        while n!=None :
            n = n.pere
            c+=1
        print ("Nombre d'étapes de la solution:", c-1)
        return

    def traceRes(self,p):
        """ affiche tous les ancetres du noeud
            """
        n = self
        c=0 
        res = []
        while n!=None :
            res.append(n)
            n = n.pere
            c+=1
        print ("Nombre d'étapes de la solution:", c-1)
        return res

###############################################################################

def astar(p):
    """ application de l'algorithme a-star sur un probleme donné
        """
    nodeInit = Noeud(p.init,0,None)
    frontiere = [(nodeInit.g+p.h_value(nodeInit.etat,p.but),nodeInit)] 
    reserve = {}        
    bestNoeud = nodeInit
    solutions = []

    while frontiere != [] and not p.estBut(bestNoeud.etat):           
        (min_f,bestNoeud) = heapq.heappop(frontiere)   
        
    # Suppose qu'un noeud en réserve n'est jamais ré-étendu 
    # Hypothèse de consistence de l'heuristique
    # ne gère pas les duplicatas dans la frontière
    
        if p.immatriculation(bestNoeud.etat) not in reserve:            
            reserve[p.immatriculation(bestNoeud.etat)] = bestNoeud.g #maj de reserve
            nouveauxNoeuds = bestNoeud.expand(p)
            for n in nouveauxNoeuds:
                f = n.g+p.h_value(n.etat,p.but)
                heapq.heappush(frontiere, (f,n))
    solutions = bestNoeud.traceRes(p)
            
    return solutions

###############################################################################

def astarTD(p): # CATASTROPHIQUE
    """ application de l'algorithme a-star sur un probleme donné
        """
    nodeInit = Noeud(p.init,0,None)
    frontiere = [(nodeInit.g+p.h_valueTD(nodeInit.etat,p.but,p),nodeInit)] 
    reserve = {}        
    bestNoeud = nodeInit
    solutions = []

    while frontiere != [] and not p.estBut(bestNoeud.etat):           
        (min_f,bestNoeud) = heapq.heappop(frontiere)   
        
    # Suppose qu'un noeud en réserve n'est jamais ré-étendu 
    # Hypothèse de consistence de l'heuristique
    # ne gère pas les duplicatas dans la frontière
    
        if p.immatriculation(bestNoeud.etat) not in reserve:            
            reserve[p.immatriculation(bestNoeud.etat)] = bestNoeud.g #maj de reserve
            nouveauxNoeuds = bestNoeud.expand(p)
            for n in nouveauxNoeuds:
                f = n.g+p.h_valueTD(n.etat,p.but,p)
                heapq.heappush(frontiere, (f,n))
    solutions = bestNoeud.traceRes(p)
            
    return solutions

###############################################################################