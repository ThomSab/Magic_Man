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




def species_represent(last_gen_species=None):
    """
    ______
    Input:
        species dictionary from last generation
        or no input
    ______
    Output:
        Old Species with new representatives and no members (except for the new representative)
        or one single representative for the initial generation
    """

    

    if last_gen_species != None:
        current_gen_species = last_gen_species.copy()
        for last_gen_species_idx,species in last_gen_species.items():#the species index remains the same but the representative is changed
            new_representative_name = random.choice(species["MEMBERS"])
            current_gen_species[last_gen_species_idx]["REPRESENTATIVE"] = new_representative_name
            current_gen_species[last_gen_species_idx]["MEMBERS"]        = [new_representative_name]
            return current_gen_species
    else:
        print("No seperate Species declared...\n")
        current_gen_species = {}
        representative_name = random.choice(utils.load_bot_names())
        current_gen_species["0"]={"REPRESENTATIVE":representative_name,"MEMBERS":[representative_name]} #first species
        return current_gen_species



def speciation (bots,c1=1,c2=1,c3=0.4,compat_thresh=3,species_dict = {}):
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
        { representative.name : [ all members of the species],  UPDATE THIS COMMENTARY
    ______
        The original set of species is determined by the last generation
        So for each species in the last generation one representative is selected randomly
        and then passed to the speciation function for the next generation.
        For the first generation the species dictionary is empty
        and there is only one species as all bots are equal
    """
    assert type(species_dict)==dict,"Representative Genome was not passed as a dictionary but as {}".format(type(represent))
    assert species_dict

    print("Speciation")
    for bot in bots:
        if utils.compatibility_search(bot,c1,c2,c3,compat_thresh,species_dict):#comp_search assigns the species to the bot but not the bot to the species dict
            species_dict[bot.species]["MEMBERS"].append(bot.name)# from object to name
        else:
            bot.species = str(len(species_dict+1))
            species_dict[str(len(species_dict+1))] = {"REPRESENTATIVE":bot.name,"MEMBERS":[bot.name]} #new representative

    return species_dict
   
   
   
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
    ______
        It might be advantagous to add some to the score of the bot
        Otherwise a negative score might be improved if the bot is inside a large species
    """
    
    for bot in bots:
        bot_score,alpha = diagnostics.score_estim(2,bot.name) #2 is the width of the confidence band around the estim
        assert alpha < 0.5, "The score estimate for {} is insignificant at a level of {}".format(bot.name,alpha) #check whether the estimate is reliable
        bot.fitness = bot_score / len(species[bot.species]["MEMBERS"]) #fitness fn as defined in the paper 


def species_allocation(bots,species_dict,pop_size):
    """
    ______
    Input:
        Bots with assigned fitness
        species dictionary
        size of the overall population
    ______
    Output:
        a dictionary that assigns species size to each 
        species according to its performance
    """

    print(pop_size,"Pop Size")
    
    species_sizes ={}
    pop_fitness_sum = sum([bot.fitness for bot in bots])
    
    for species_idx,species in species_dict.items():
        species_fitness_sum = sum([bot.fitness for bot in bots if bot.species == species_idx])
        
        species_sizes[species_idx] = int(np.round(pop_size * (species_fitness_sum/pop_fitness_sum)))
    
    
    return species_sizes


def mutate_link(nn_node_genome,nn_connection_genome,net_type):
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
        If it does not I'll find an appropriate solution for that
    """

    hidden_nodes_idx = [node["INDEX"] for node in nn_node_genome if node["TYPE"] == "HIDDEN"]
    output_nodes_idx = [node["INDEX"] for node in nn_node_genome if node["TYPE"] == "OUTPUT"]

    """
    in_nodes:
    Intuitively I'd say that an output node should not be connected to another output node,
    but technically there is nothing wrong with that, so I'll leave it as a possibility.
    """
 
    
    link_mutation = {"IN": random.choice(nn_node_genome)["INDEX"],
                     "OUT":random.choice(output_nodes_idx+hidden_nodes_idx),
                     "WEIGHT": np.random.normal(size = 1)[0],
                     "ENABLED":1,
                     "INNOVATION":utils.increment_in(net_type)}


    
    
    if utils.check_for_recursion(nn_connection_genome,link_mutation):#bc now the net might be recursive
        print("Recursive Mutation prevented")
        return mutate_link(nn_node_genome,nn_connection_genome,net_type)

    elif (duplication := utils.check_for_connection_duplication(nn_connection_genome,link_mutation)):
        for gene in duplication:
            print(f"Connection {link_mutation['IN']} --> {link_mutation['OUT']} not added to genome. Connection already exists at innovation {gene['INNOVATION']}")
            return nn_connection_genome,None

    print(f"Connection {link_mutation['IN']} --> {link_mutation['OUT']} added to genome.")
    
    nn_connection_genome.append(link_mutation)
    return nn_connection_genome,link_mutation



    
def mutate_node(nn_node_genome,nn_connection_genome,net_type):
    """
    ______
    Input:
        A Neural Net's Node Genome and its Connection Genome
        the net type in order to track innovation
        -->can be "play" "stm" "bid"
        
    ______
    Output:
        The input Genome with a disabled link,
        an added node in its place and two new link genes
        st. A - B becomes A - NEW - B
        The Mutation to keep track within a generation
    """
    n_nodes = nn_node_genome[-1]["INDEX"]
    #the index of the last added node
    #(could also be len(nn_node_genome) but this is constant time)

    nn_node_genome.append(new_node:={"INDEX" : n_nodes+1, "TYPE" : "HIDDEN","BIAS" : np.random.normal(size = 1)[0]})

    target_link_idx = np.random.randint(len(nn_connection_genome))
    target_link     = nn_connection_genome[target_link_idx]
    nn_connection_genome[target_link_idx]["ENABLED"] = 0 #disable the target link
    
    in_connection,out_connection =  ({"IN": target_link["IN"],
                                     "OUT":new_node["INDEX"],
                                     "WEIGHT":np.random.normal(size = 1)[0],
                                     "ENABLED":1,
                                     "INNOVATION":utils.increment_in(net_type)},
                                     {"IN": new_node["INDEX"],
                                     "OUT":target_link["OUT"],
                                     "WEIGHT":np.random.normal(size = 1)[0],
                                     "ENABLED":1,
                                     "INNOVATION":utils.increment_in(net_type)})
    
    nn_connection_genome.append(in_connection)
    nn_connection_genome.append(out_connection)

    print("Added a new node: ",new_node)
    
    return nn_node_genome,nn_connection_genome,in_connection,out_connection



def mutate_weights(connection_genome,node_genome,random_weight_thresh,pert_rate):
    """
    ______
    Input:
        A Neural Net Connection Genome
        The probability threshold above which the weight is set randomly
        instead of being perturbed
        The strength of perturbation
    ______
    Output:
        The input Genome with all the weights mutated or perturbed
    """
    random_connection_mutation_list = [True if random_chance <= random_weight_thresh else False for random_chance in np.random.uniform(size=len(connection_genome))]
    random_node_mutation_list       = [True if random_chance <= random_weight_thresh else False for random_chance in np.random.uniform(size=len(node_genome))]
    
    for gene_idx,random_mutation in enumerate(random_connection_mutation_list):
        if random_mutation:
            connection_genome[gene_idx]["WEIGHT"]  = np.random.normal(size = 1)[0]
        else:
            connection_genome[gene_idx]["WEIGHT"] += np.random.normal(loc=0,scale=pert_rate,size = 1)[0] #the paper says "uniformly perturbed" but its not exactly defined how

    for gene_idx,random_mutation in enumerate(random_node_mutation_list):
        if random_mutation:
            node_genome[gene_idx]["BIAS"]  = np.random.normal(size = 1)[0]
        else:
            node_genome[gene_idx]["BIAS"] += np.random.normal(loc=0,scale=pert_rate,size = 1)[0] #the paper says "uniformly perturbed" but its not exactly defined how

    print("Weights and Biases mutated.")
    
    return connection_genome



    
def mutation_step(bot_name,link_thresh=0.05,node_thresh= 0.03,weights_mut_thresh=0.8,rand_weight_thresh=0.1,pert_rate=0.1):
    """
    ______
    Input:
        The name of the bot that is mutated
        The probabilities for mutations to ocurr
    ______
    Output:
        None
        The bots genome is changed
    """
    for net in ["stm","bid","play"]:
        thresh_list = [link_thresh,node_thresh,weights_mut_thresh]
        mutate_list = [ chance <= thresh_list[chance_idx] for chance_idx,chance in enumerate(np.random.uniform(size=3))]
        link_mut,node_mut,weights_mut = mutate_list

        if any(mutate_list):
            bot_genome = utils.load_bot_genome(bot_name)
            connection_genome,node_genome = bot_genome["{}_connection_genome".format(net)],bot_genome["{}_node_genome".format(net)]

            if link_mut:
                connection_genome,link_mutation = mutate_link(node_genome,connection_genome,net)
                
            if node_mut:
                node_genome,connection_genome,in_mutation,out_mutation = mutate_node(node_genome,connection_genome,net)

            if weights_mut:
                connection_genome = mutate_weights(connection_genome,node_genome,rand_weight_thresh,pert_rate=pert_rate)#does not need the net type bc no innovation numbers are incremented

            bot_genome["{}_connection_genome".format(net)]   = connection_genome
            bot_genome["{}_node_genome".format(net)]         = node_genome
    
            utils.save_bot_genome(bot_name,bot_genome)


def mutate_species(species_names,link_thresh,node_thresh,weights_mut_thresh,rand_weight_thresh,pert_rate):
    """
    ______
    Input:
        list of bot names that belong to one species
        mutation parameters
    ______
    Output:
        None
    ______
        All bot genomes in the given species are mutated randomly
        except if the species is larger than five, in which case a single champion is spared from mutation

    """
    if len(species_names)>=5:
        species_members = species_names.copy()
        species_member_scores = { bot_name: diagnostics.score_estim(999,bot_name)[0] for bot_name in species_members }
        species_members.sort(key = lambda x : species_member_scores[x],reverse=True)
        for bot in species_members[1:]:
            print(f"Mutating {bot}")
            mutation_step(bot,link_thresh,node_thresh,weights_mut_thresh,rand_weight_thresh,pert_rate)
    else:
        for bot in species_names:
            print(f"Mutating {bot}")
            mutation_step(bot,link_thresh,node_thresh,weights_mut_thresh,rand_weight_thresh,pert_rate)    
    return



def produce_net_connection_offspring(fit_connection_genome,flop_connection_genome):
    """
    ______
    Input:
        two parent connection genomes
    ______
    Output:
        offspring neural net connection genome

    """
    fit_innovations = [gene["INNOVATION"] for gene in fit_connection_genome]
    flop_excess_connections = [gene for gene in flop_connection_genome if gene["INNOVATION"] not in fit_innovations]
    #sets are three times as fast as list comprehensions but dictionarys are unhasheable
    #also the connection genes need to be matched by innovation bc. they might differ in weight
    offspring_connection_genome = fit_connection_genome + flop_excess_connections
    offspring_connection_genome.sort(key = lambda x : x["INNOVATION"])

        

    
    return offspring_connection_genome


def produce_net_node_offspring(fit_node_genome,flop_node_genome):
    """
    ______
    Input:
        two parent node genomes
    ______
    Output:
        offspring neural net node genome
    """
    flop_excess_nodes = [node_gene for node_gene in flop_node_genome if node_gene not in fit_node_genome]

    offspring_node_genome = fit_node_genome + flop_excess_nodes
    offspring_node_genome.sort(key = lambda x : x["INDEX"])
   
    return offspring_node_genome



  
def produce_offspring(parent_a,parent_b):
    """
    ______
    Input:
        two parent genomes
    ______
    Output:
        offspring genome
    ______
        The weights of the more fit parent are kept
        To achieve this it is possible to just
        add the genes that are unique to the flop genome to the fit genome
        
    """
    
    fit_parent,flop_parent = sorted([parent_a,parent_b],key=lambda x : x.fitness,reverse = True) #reverse sort is from highest to lowest
    fit_genome,flop_genome = utils.load_bot_genome(fit_parent.name),utils.load_bot_genome(flop_parent.name)

    offspring_genome = fit_genome

    for net in ['play','bid','stm']:
        fit_connection_genome,flop_connection_genome = fit_genome["{}_connection_genome".format(net)],flop_genome["{}_connection_genome".format(net)]
        fit_node_genome,flop_node_genome = fit_genome["{}_node_genome".format(net)],flop_genome["{}_node_genome".format(net)]
        
        offspring_genome["{}_connection_genome".format(net)] = produce_net_connection_offspring(fit_connection_genome,flop_connection_genome)
        offspring_genome["{}_node_genome".format(net)]       = produce_net_node_offspring(fit_node_genome,flop_node_genome)

    

    #check for recursive structure in the connection genome
    for connection_gene in offspring_genome["{}_connection_genome".format(net)]:
        if utils.check_for_recursion(offspring_genome["{}_connection_genome".format(net)],
                            initial_gene = connection_gene,current_gene=connection_gene):
            return False

    return offspring_genome


def seperate_pool(species,seperations):
    """
    ______
    Input:
        species for this generation
        number of seperations in the pool
    ______
    Output:
        A dictionary that contains that "seperations" seperate sets of bots
        With similar composition of species
    ______
        makes the bots play until each of their score values has
        a significance value of alpha or lower
    """    


    #TODO
    pass



def play_to_significance(bot_names,width=10,alpha_thresh=0.1):
    """
    ______
    Input:
        significance interval
        significance value
    ______
    Output:
        none
    ______
        makes the bots play until each of their score values has
        a significance value of alpha or lower
    """    
    bots = bot_names.copy()
    below_alpha,above_alpha = [],bots
    
    while len(above_alpha)>=4:
        mean,alpha = diagnostics.score_estim(width,(above_bot := above_alpha[0]).name)
        if alpha <= alpha_thresh and alpha != 0:
            below_alpha.append(above_alpha.pop(0))
        else:
            if np.isnan(alpha) or alpha == 0:
                print( f"{above_alpha[0].name}'s score cannot be estimated because he/she has not played yet.")
                alpha = 0.5
            else:    
                print( f"{above_alpha[0].name}'s score estimate of {np.round(mean,2)} has a {np.round(alpha*100,2)}% chance of being off by more than {width}")
            above_alpha_copy = above_alpha.copy()
            above_alpha_copy.remove(above_bot)
            #let them play some games
            n_games = min([100,int(np.ceil((alpha-alpha_thresh)*50/alpha))])
            for game_idx in range(n_games):
            #this just so happens to be approximately appropriate
            #the closer the alpha is the fewer games the bot has to play to significance
            #this is a rough estimate and can be made more precise
                random.shuffle(above_alpha_copy)
                game_pool = [above_bot]+above_alpha_copy[:3]
            
                play_game(game_pool)
            
                #show how the score behaves over those games
                for player in game_pool:
                    utils.add_score(player.name,player.game_score)

                print(f"{game_idx+1}/{n_games}",game_pool)
                


    #The last three bots play with bots that are already significant
    while above_alpha:
        
        for bot in above_alpha:
            mean,alpha = diagnostics.score_estim(width,(above_bot := above_alpha[0]).name)  
            if alpha<=alpha_thresh:
                above_alpha.remove(above_bot)
            else:
                game_pool = above_alpha+bot_names[:4-len(above_alpha)]
                print(above_bot,alpha)

                for game_idx in range(3):
                    play_game(game_pool)
                
                    #show how the score behaves over those games
                    for player in game_pool:
                        utils.add_score(player.name,player.game_score)
                        
                    print(f"Afterburn",game_pool)

          



    
    print("Significance achieved")
    return True
    
    

def reproduce(bots,bot_species,names,species_size,preservation_rate):
    """
    ______
    Input:
        bots --> a list of bot objects
        bot_species --> a list of bot names
    ______
    Output:
        names of the new set of bots of the same size as the input set
    ______
        makes the species of bots reproduce into a new set of bots
        25% of offspring is not crossover i.e. only mutations
        There is no specification as to who mate with who
        The better the score the more offspring a bot produces
        So the first produces another 37.5% of the offspring each
        the Second produces another 18.75%, third produces 9.375% etc.
    """
    
    print("Species Size: ", species_size)
    
    new_generation = []
    bots = [bot for bot in bots if bot.name in bot_species] #from name to object
    bots.sort(key = lambda bot: bot.fitness,reverse = True) #highest score to lowest
    

    for bot in bots[int(np.round(preservation_rate*species_size)):]:
            utils.incinerate(bot.name) #incinerate the bad part of the generation a priori
            
    bots = bots[:int(np.round(preservation_rate*species_size))] #remove the incinerated botnames from the bot list
    
    for bot in bots[:int(np.round(species_size*0.25))]:
        new_generation.append(bot.name)


    """
    This whole bot_count aspect of the reproduction method
    should be gotten rid of
    but I have not the patience for that rn
    """

    percentage = 0.375
    species_offspring_count = 0
    for bot in bots:
        bot_offspring_count = 0
        while bot_offspring_count/species_size <= percentage and int(np.round(percentage*species_size)) > 1:
            if (offspring_genome := produce_offspring(bot,random.choice(bots))):
                utils.save_init_genome(offspring_name:=names[species_offspring_count+bot_offspring_count], produce_offspring(bot,random.choice(bots)))
                utils.save_init_score(offspring_name)
                new_generation.append(offspring_name)
                bot_offspring_count+=1
        species_offspring_count+=bot_offspring_count
        percentage /= 2

    print(f"New Species Size is {len(new_generation)} \n{len(new_generation)-species_size} bots are killed off.")
    new_generation=new_generation[:species_size]#st the species does not get larger than anticipated
    
    
    
    for bot in [bot for bot in bots if bot.name not in new_generation]:
            utils.incinerate(bot.name) #delete the rest of the old generation
    
    return new_generation



def inquiry_step(gen_idx,bots,significance_width,significance_val):

    """
    ______
    Input:
        bots list of objects
        gen_idx
        significance_val
        significance_width
        
    ______
    Output:
        None
        Bots play until significant score
        Progress is logged
    """
    
    play_to_significance(bots,significance_width,significance_val) #verify significance
    gen_max_score,max_score_bot = diagnostics.gen_max_score(significance_width,significance_val)
    gen_max_score_conf = diagnostics.conf_band_width(significance_val,max_score_bot)
    gen_avg_score = diagnostics.gen_avg_score(significance_width,significance_val)
    utils.save_progress(gen_idx,gen_max_score,max_score_bot,gen_max_score_conf,gen_avg_score)#log process in case it wasnt last generation    
    
    return


def progressive_step(gen_idx,bots,population_size,link_thresh,node_thresh,weights_mut_thresh,rand_weight_thresh,pert_rate,preservation_rate):
    """
    ______
    Input:
        gen_idx
        population_size
        all mutation parameters
    ______
    Output:
        None
    ______
        The old generation reproduces and most of its members perish depending on the preservation_rate
        the new generation is speciated and the species dictionary is saved for the next iteration
        
        
    """
    species_dict = utils.load_gen_species(gen_idx-1,assign_species = True, bots = bots)
    fitness(bots = bots,species = species_dict)
    species_sizes=species_allocation(bots=bots,species_dict=species_dict,pop_size=population_size)
    
    print("Spezies Sizes Dict: ", species_sizes)

    names = utils.load_empty_bot_names(gen_idx)      
    name_idx = 0      
    for species_idx,species in species_dict.items():
        species["MEMBERS"] = reproduce(bots,species["MEMBERS"],names[name_idx:len(species["MEMBERS"])],species_sizes[species_idx],preservation_rate) #from name to name
        name_idx+=len(species["MEMBERS"])

        mutate_species(species["MEMBERS"],link_thresh,node_thresh,weights_mut_thresh,rand_weight_thresh,pert_rate)

            
    bots = [Player(bot_name) for bot_name in utils.load_bot_names()] #load the new generation

    new_species_representatives = species_represent(species_dict)
    new_species_dict = speciation(bots=bots,species_dict = new_species_representatives)
    utils.save_generation_species(gen_idx,new_species_dict)#save species under gen idx
    
    return


def generation(gen_idx,significance_width,significance_val,population_size=100,link_thresh=0.05,node_thresh= 0.03,weights_mut_thresh=0.8,rand_weight_thresh=0.1,pert_rate=0.1,preservation_rate = 0.4):
    """
    ______
    Input:
        gen_idx
        significance_width
        significance_val
        population_size
        all mutation parameters
    ______
    Output:
        the species representatives of the new generation
        the new bots need not be returned as they are saved as genomes
        and will have to be loaded anyways in the next gen
    ______
        Basically main: All functions are called st.:
        The Members of the current species train until their scores are significant
        The fittest members then reproduce and mutate

        first generation idx should be one bc the initial species is 0
        
    """

    bots = [Player(bot_name) for bot_name in utils.load_bot_names()]
    inquiry_step(gen_idx-1,bots,significance_width,significance_val)

    progressive_step(gen_idx,bots,population_size,link_thresh,node_thresh,weights_mut_thresh,rand_weight_thresh,pert_rate,preservation_rate)

    bots = [Player(bot_name) for bot_name in utils.load_bot_names()]
    inquiry_step(gen_idx,bots,significance_width,significance_val)

    
    return

def start_training(significance_width=10,significance_val=0.05,population_size=100,link_thresh=0.05,node_thresh= 0.03,weights_mut_thresh=0.8,rand_weight_thresh=0.1,pert_rate=0.1,preservation_rate = 0.4):
    current_gen = utils.current_gen()
        
    while True:
        current_gen +=1
        generation(current_gen,
                   significance_width,significance_val,population_size,
                   link_thresh,node_thresh,weights_mut_thresh,rand_weight_thresh,pert_rate,preservation_rate)


        

if __name__ == "__main__": #so it doesnt run when imported
    print(txt)

    bots = [Player(bot_name) for bot_name in utils.load_bot_names()[:4]]

    #diagnostics.population_progress()
    start_training(significance_val=0.1,significance_width=5,pert_rate=0.5)
    
    
"""
The profiler estimates a game to take ~6.7 sec
Back-of-the-envelope estimation:
6.7 seconds * ~1000 games to significance * 150 specimen / 4 scores per game * ~200 generations = 
about 1.6 years
"""
