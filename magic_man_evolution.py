import random
import os
import shutil
import sys
import numpy as np

from collections import deque
from time import process_time
from zipfile import BadZipFile

import magic_man_diagnostics as diagnostics
import magic_man_utils as utils
from magic_man_player import Player



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
            if len(species["MEMBERS"])==0:
               del current_gen_species[last_gen_species_idx]
            else:
                new_representative_name = random.choice(species["MEMBERS"])
                utils.save_representative(new_representative_name)
                current_gen_species[last_gen_species_idx]["REPRESENTATIVE"] = new_representative_name
                current_gen_species[last_gen_species_idx]["MEMBERS"]        = []#the representative will be added automatically. 
                #(In theory it is possible that the representative of a species is appended to another species, but that is a problem for another day.)
        return current_gen_species
    else:
        print("No seperate Species declared...\n")
        current_gen_species = {}
        representative_name = random.choice(utils.load_bot_names())
        current_gen_species["0"]={"REPRESENTATIVE":representative_name,"MEMBERS":[]} #first species
        utils.save_representative(representative_name)
        return current_gen_species

    

def speciation (bots,pop_size,c1=2,c2=2,c3=0.7,compat_thresh=2.25,species_dict = {}):
    """
    ______
    Input:
        List of Player Objects
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
    assert [len(species["MEMBERS"]) == 0 for species_key,species in species_dict.items()], "Not all species are empty!"

    print(f"Speciation of {len(bots)} bots")
    for bot in bots:
        if utils.compatibility_search(bot,c1,c2,c3,compat_thresh,species_dict):#comp_search assigns the species to the bot but not the bot to the species dict
            species_dict[bot.species]["MEMBERS"].append(bot.name)# from object to name
        else:
            print(f"New species created, represented by {bot}")
            bot.species = str(len(species_dict)) #new species index --> bc the indices start at zero, the lenght is always the highest index plus one
            species_dict[str(len(species_dict))] = {"REPRESENTATIVE":bot.name,"MEMBERS":[bot.name]} #new species with bot as representative
            utils.save_representative(bot.name)
            

    gen_members=[]
    for species_idx,species in species_dict.items():
        gen_members.extend(species["MEMBERS"])
    print(gen_members,len(gen_members))
    assert len(gen_members) == pop_size, "Species dictionary contains too many bots!"
        
    

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
        bot.fitness = (200+ bot_score) / (0.1*len(species[bot.species]["MEMBERS"])) #fitness fn as defined in the paper plus 400 st. fitness is not negative
        if bot.fitness <0:
            bot.fitness = 0


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
    
    while sum([species_size for species_idx,species_size in species_sizes.items()]) > pop_size: #population is oversize
        rs_idx,rs_size = random.choice(list(species_sizes.items()))
        if species_sizes[rs_idx] >= 5:
            species_sizes[rs_idx] -= 1 #random species gets one smaller
            
    while sum([species_size for species_idx,species_size in species_sizes.items()]) < pop_size: #population is undersize
        rs_idx,rs_size = random.choice(list(species_sizes.items()))
        species_sizes[rs_idx] += 1 #random species gets one bigger
            
    assert (dict_size := sum([species_size for species_idx,species_size in species_sizes.items()])) == pop_size, f"Species Dictionary is wrong size: {dict_size}"
    
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
    reset_score_bool=False
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

        if sum(thresh_list)>0:
            reset_score_bool=True
            
    if reset_score_bool:
        utils.reset_score(bot_name)
            

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
    fit_node_indices = [node["INDEX"] for node in fit_node_genome]
    flop_excess_nodes = [node_gene for node_gene in flop_node_genome if node_gene["INDEX"] not in fit_node_indices]

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
            print("Recursive Offspring Prevented")
            return False

    return offspring_genome







    

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

    if species_size <=5: #in case the species is too small to reproduce
        if len(bots) >= 5:
            new_species_names,kill_list_names =[bot.name for bot in bots[:species_size]],[bot for bot in bots[species_size:]]
            return new_species_names,kill_list_names
        else: #just reproduce the best bot as many times as needed for new generation
            bot_offspring_count = 0
            for bot in range(species_size):
                offspring_genome = utils.load_bot_genome(bots[0].name)
                utils.save_init_genome((offspring_name:=names[bot_offspring_count]),offspring_genome)
                utils.save_init_score(offspring_name)
                new_generation.append(offspring_name)
                bot_offspring_count+=1                
            return new_generation,[bot.name for bot in bots]

    kill_list = [bot.name for bot in bots[int(np.round(preservation_rate*species_size)):]]#incinerate the bad part of the generation after speciation
            
    bots = bots[:int(np.round(preservation_rate*species_size))] #remove the incinerated botnames from the bot list
    
    for bot in bots[:int(np.round(species_size*0.25))]:
        new_generation.append(bot.name)


    """
    This whole bot_count aspect of the reproduction method
    should be gotten rid of
    but I have not the patience for that rn
    """
    
    species_offspring_count = 0
    while (len(new_generation)<species_size):
        percentage = 0.375       
        for bot in bots:
            bot_offspring_count = 0
            while bot_offspring_count/species_size <= percentage and int(np.round(percentage*species_size)) >= 1:
                if (offspring_genome := produce_offspring(bot,random.choice(bots))):
                    utils.save_init_genome(offspring_name:=names[species_offspring_count+bot_offspring_count], offspring_genome)
                    utils.save_init_score(offspring_name)
                    new_generation.append(offspring_name)
                    bot_offspring_count+=1
            species_offspring_count+=bot_offspring_count
            percentage /= 2

    print(f"New Species Size is {len(new_generation)}\n{len(new_generation)-species_size} bots are killed off.")
    for bot in new_generation[species_size:]:
        utils.incinerate(bot)
        
    new_generation=new_generation[:species_size]#st the species does not get larger than anticipated
    #print(len(new_generation),species_size)
    assert (len(new_generation) == species_size), f"Species is not the right size!"
    
    kill_list.extend([bot.name for bot in bots if bot.name not in new_generation and bot.name not in kill_list]) #delete the rest of the old generation
    
    return new_generation,kill_list
