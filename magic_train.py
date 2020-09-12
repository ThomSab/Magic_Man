import random
import os
import shutil
import sys
import numpy as np
import multiprocessing

import magic_man_deck as deck
from magic_main import Game
from magic_man import txt
import magic_man_diagnostics as diagnostics
from magic_man_evolution import *

number_of_players = 4

def play_game(game_pool):
    print(game_pool)
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

    for player in game_pool:
        utils.add_score(player.name,player.game_score)

    return



def use_single_core(bot_names,width=10,alpha_thresh=0.1):
    """
    ______
    Input:
        significance interval
        significance value
    ______
    Output:
        none
    ______
        uses one core to make the bots play until each of their score values has
        a significance value of alpha or lower
    """ 
    
    above_alpha = bot_names.copy()
    
    while len(above_alpha)>=4:
        mean,alpha = diagnostics.score_estim(width,(above_bot := above_alpha[0]).name)
        if alpha <= alpha_thresh and alpha != 0:
            print(f"{above_alpha.pop(0)} score is significant")
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
                random.shuffle(above_alpha_copy) #st every bot has a diverse set of enemies
                game_pool = [above_bot]+above_alpha_copy[:3]
            
                play_game(game_pool)
            
                #show how the score behaves over those games
                for player in game_pool:
                    utils.add_score(player.name,player.game_score)

                print(f"{game_idx+1}/{n_games}")

    return



def use_multi_core(bot_names,width=10,alpha_thresh=0.1):
    """
    ______
    Input:
        significance interval
        significance value
    ______
    Output:
        none
    ______
        uses four core to make the bots play until each of their score values has
        a significance value of alpha or lower
    """
    n_cores = multiprocessing.cpu_count()
    above_alpha = bot_names.copy()
        

    while len(above_alpha)>=4:

        score_estim_list = [(diagnostics.score_estim(width,bot_name),bot_name) for bot_name in above_alpha]
        for significant_bot in (significant_scores := [tuple[1] for tuple in score_estim_list if tuple[0][1] < alpha_thresh]):
            print(f"{above_alpha.pop(significant_bot)} score is significant")

        average_alpha = np.mean([tuple[0][1] for tuple in score_estim_list if tuple[0][1] > alpha_thresh])
        n_games = min([50,int(np.ceil((average_alpha-alpha_thresh)*25/average_alpha))])
        

        print( f"The pools score estimates have a {np.round(average_alpha*100,2)}% chance of being off by more than {width}")

        above_alpha_copy = above_alpha.copy()
            #let them play some games

        for game_idx in range(n_games):
        #this just so happens to be approximately appropriate
        #the closer the alpha is the fewer games the bot has to play to significance
        #this is a rough estimate and can be made more precise
            print(f"{game_idx+1}/{n_games}")
            random.shuffle(above_alpha_copy) #st every bot has a diverse set of enemies
            pools = [above_alpha_copy[i:i + 4] for i in range(0, len(above_alpha_copy), 4)]
            if len(pools[-1])<4:#if the last pool is not 4 players
                pools = pools[:-1]

            with multiprocessing.Pool(n_cores) as p:
                p.map(play_game,pools)


            

    return 
                


def play_to_significance(bot_names,width=10,alpha_thresh=0.1,playing_method=use_single_core):
    """
    ______
    Input:
        significance interval
        significance value
        method of training
    ______
    Output:
        none
    ______
        makes the bots play until each of their score values has
        a significance value of alpha or lower
        
    """

    score_estim_list = [(diagnostics.score_estim(width,bot_name),bot_name) for bot_name in bot_names]
    for significant_bot in (significant_scores := [tuple[1] for tuple in score_estim_list if tuple[0][1] < alpha_thresh]):
        bot_names.remove(significant_bot)
    
    playing_method(bot_names,width,alpha_thresh)
                

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

          

    assert not (insignificant_scores := ([tuple[1] for tuple in diagnostics.bot_scores(width) if tuple[0][1] > alpha_thresh]))
    
    
    print("Significance achieved")
    return True



def inquiry_step(gen_idx,bots,significance_width,significance_val,playing_method):

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
    
    play_to_significance(bots,significance_width,significance_val,playing_method) #verify significance
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



def generation(gen_idx,
               significance_width,
               significance_val,
               population_size=100,
               link_thresh= 0.05,
               node_thresh= 0.03,
               weights_mut_thresh=0.8,
               rand_weight_thresh=0.1,
               pert_rate=0.1,
               preservation_rate = 0.4,
               playing_method=use_single_core):
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
    inquiry_step(gen_idx-1,bots,significance_width,significance_val,playing_method)

    progressive_step(gen_idx,bots,population_size,link_thresh,node_thresh,weights_mut_thresh,rand_weight_thresh,pert_rate,preservation_rate)

    bots = [Player(bot_name) for bot_name in utils.load_bot_names()]
    inquiry_step(gen_idx,bots,significance_width,significance_val,playing_method)
  
    return



def start_training(significance_width=10,
                   significance_val=0.05,
                   population_size=100,
                   link_thresh=0.05,
                   node_thresh= 0.03,
                   weights_mut_thresh=0.8,
                   rand_weight_thresh=0.1,
                   pert_rate=0.1,
                   preservation_rate = 0.4,
                   playing_method=use_multi_core):
    
    current_gen = utils.current_gen()
        
    while True:
        current_gen +=1
        generation(current_gen,
                   significance_width,significance_val,population_size,
                   link_thresh,node_thresh,weights_mut_thresh,rand_weight_thresh,pert_rate,preservation_rate,playing_method)




        
if __name__ == "__main__": #so it doesnt run when imported
    print(txt)

    #bots = [Player(bot_name) for bot_name in utils.load_bot_names()[:4]]

    diagnostics.population_progress()
    start_training(significance_val=0.1,significance_width=5,pert_rate=0.5)
    
    
"""
The profiler estimates a game to take ~6.7 sec
Back-of-the-envelope estimation:
6.7 seconds * ~1000 games to significance * 150 specimen / 4 scores per game * ~200 generations = 
about 1.6 years
"""
