import random
import os
import shutil
import cProfile
import sys

import numpy as np
from collections import deque
from time import process_time
from zipfile import BadZipFile
import matplotlib.pyplot as plt


import magic_man_deck as deck
import magic_man_diagnostics as diagnostics
import magic_man_utils as utils
from magic_man_player  import Player
from magic_main import Game
from magic_man import txt
#______________________________________________________________________________    
number_of_players = 4 #for now
clear = lambda: os.system('cls')

bot_dir = '0'

"""
The players are named by score
so whenever a bot scores high its children get high scoring names
an average is calculated of the score
so whenever a bot falls below a certain threshold it gets deleted
to prevent the bots from taking up disk space
"""

pool_size = 150

def play_game(game_pool):
    game_pool_copy = game_pool.copy()
    try:
        game = Game(number_of_players,game_pool,deck.deck.copy()) #whos playing
    except TypeError:
        print("No Bots loaded yet.")
    for player in game_pool:
        player.game_score = 0
    for i in range(1,16): #how many rounds
        if not i == 15:
            game.starting_player(game_pool_copy[i%4])
            game.round(i)
        else:
            game.starting_player(game_pool_copy[15%4])
            game.round(i,lastround = True)
            
    winnerlist = list( game.players.copy() )
    winnerlist.sort(key = lambda x: x.game_score,reverse = True)
    
    """
    for _ in range(len(winnerlist)):
        print("Player {0} takes Place {1} with {2} points.".format(winnerlist[_],
                                                                   _+1,
                                                                   winnerlist[_].game_score
                                                                   ))
    """                                                           




def species_represent(species_last_gen=None):
    """
    ______
    Input:
        species dictionary from last generation
        or no input
    ______
    Output:
        New Species representatives
        or one single representative for the initial generation
    """

    species_current_gen = {}

    if species_last_gen != None:      
        for species in species_last_gen:
            representative_name = random.choice(load_bot_names())
            species_current_gen[representative_name] = [representative_name]
            return species_current_gen
    else:
        print("First Generation, no seperate Species...\n")
        representative_name = random.choice(utils.load_bot_names())
        species_current_gen[representative_name] = [representative_name]
        return species_current_gen



def speciation (c1,c2,c3,compat_thresh,bots,species = {}):
    """
    ______
    Input:
        The set compatibility threshold
        the compatibility matrix
        the representatives of each species in a dictonary
    ______
    Output:
        Assigns each specimen in the population to a species
        returns a dictionary for the speciation
        { representative.name : [ all members of the species], ... }
    ______
        The original set of species is determined by the last generation
        So for each species in the last generation one representative is selected randomly
        and then passed to the speciation function for the next generation.
        For the first generation the species dictionary is empty
        and there is only one species as all bots are equal
    """
    assert type(species)==dict,"Representative Genome was not passed as a dictionary but as {}".format(type(represent))
    assert species
        
    for bot in bots:
        if utils.compatibility_search(bot,c1,c2,c3,compat_thresh,species):#comp_search assigns the species to the bot but not the bot to the species dict
            species[bot.species].append(bot.name)
        else:
            species[bot.name] = [bot.name] #new representative
   

            
    return species
   
   
   
def fitness (bots,species = {}):
    """
    ______
    Input:
        An average score estimate
        the amount of specimen in the same species
    ______
    Output:
        Nothing
        Assigns the adjusted fitness to each bot
    """
    
    for bot in bots:
        bot_score,alpha = diagnostics.score_estim(2,bot.name) #2 is the width of the confidence band around the estim
        assert alpha < 0.5, "The score estimate for {} is insignificant at a level of {}".format(bot.name,alpha) #check whether the estimate is reliable
        bot.fitness = bot_score / len(species[bot.species]) #fitness fn as defined in the paper 



def mutate_link(nn_genome):
    """
    ______
    Input:
        A Neural Net Genome 
    ______
    Output:
        The input Genome with an added link Gene
        The added Gene
    ______
        Adding links might add closed loops
        st. A - B - C - A
        To prevent this I'll test-activate the net and see if it works first
        If it does not it will reset and mutate randomly until it does work
    """

    #in_nodes = [node for node in nn_node_genome if node["TYPE"] not "OUTPUT"]
    out_nodes = [node for node in nn_node_genome if node["TYPE"] not "SENSOR"] #Sensor nodes have no recieving links from the nn
    """
    in_nodes:
    Intuitively I'd say that an output node should not be connected to another output node,
    but technically there is nothing wrong with that, so I'll leave it as a possibility.
    """

    
    
    nn_connection_genome.append(link_mutation :=
                                {"IN": random.choice(nn_node_genome)["INDEX"],
                                 "OUT":random.choice(out_nodes)["INDEX"],
                                 "WEIGHT": np.random.normal(size = 1)[0],
                                 "ENABLED":1,
                                 "INNOVATION":"UNCONFIRMED"}) #bc the net might now be recursive
    
    return nn_connection_genome,link_mutation



    
def mutate_node(nn_node_genome,nn_connection_genome,net_type):
    """
    ______
    Input:
        A Neural Net's Node Genome and its Connection Genome
        
    ______
    Output:
        The input Genome with a disabled link,
        an added node in its place and two new link genes
        st. A - B becomes A - NEW - B
        The Mutation to keep track within a generation
    """
    n_nodes = nn_node_genome[-1]["INDEX"]
    #the index of the last added node (could also be len(nn_node_genome) but this is constant time)

    nn_node_genome.append(new_node:={"INDEX" = n_nodes+1, "TYPE" = "HIDDEN"})

    target_link_idx = np.random.randint(len(nn_connection_genome))
    target_link     = nn_connection_genome[target_link_index]
    nn_connection_genome[target_link_idx]["ENABLED"] = 0 #disable the target link
    
    in_connection,out_connection =  {"IN": target_link["IN"],
                                     "OUT":new_node["INDEX"],
                                     "WEIGHT":np.random.normal(size = 1)[0],
                                     "ENABLED":1,
                                     "INNOVATION":utils.increment_in(net_type)},
                                    {"IN": new_node["INDEX"],
                                     "OUT":target_link["OUT"],
                                     "WEIGHT":np.random.normal(size = 1)[0],
                                     "ENABLED":1,
                                     "INNOVATION":utils.increment_in(net_type)}
    
    nn_connection_genome.append(in_connection)
    nn_connection_genome.append(out_connection)

    return nn_node_genome,nn_connection_genome,[in_connection,out_connection]

def produce_offspring(parent_a_genome,parent_b_genome):
    """
    ______
    Input:
        two parent genomes
    ______
    Output:
        offspring genome
    """
    pass

if __name__ == "__main__": #so it doesnt run when imported
    print("Magic Man")
    bots = [Player(bot_name) for bot_name in utils.load_bot_names()]
    game_pool_copy = bots.copy()
    
    #let them play some games
    for game_idx in range(5000):
        random.shuffle(game_pool_copy)
        play_game(game_pool_copy[:4])
    
        #show how the score behaves over those games
        for player in game_pool_copy[:4]:
            utils.add_score(player.name,player.game_score)

        print(game_pool_copy[:4])


        
    species_repr = species_represent()
    species_dict = speciation(1,1,1,1,bots,species_repr)
    fitness(bots,species_dict)
