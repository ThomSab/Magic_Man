import random
import os
import cProfile
import shutil
import sys
import time
import numpy as np
import multiprocessing

import magic_man_deck as deck
from magic_main import Game
from magic_man import txt
import magic_man_diagnostics as diagnostics
from magic_man_evolution import *

number_of_players = 4

def play_game(game_pool):
    game_pool_copy = game_pool.copy()
    if len(game_pool_copy) != 4:
        sys.exit(f"Bot pool faulty: {game_pool_copy}")
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
        utils.add_seperate_score(player.name,player.game_score)
    print(game_pool)
    
    return



def play_single_round(game_pool,round_idx=14):
    """
    ______
    Input:
        game pool of four players
        index of the round played
    ______
    Output:
        None
    ______
        Adds the seperate score for each player for the played round to their directory
    """


    game_pool_copy = game_pool.copy()
    if len(game_pool_copy) != 4:
        sys.exit(f"Bot pool faulty: {game_pool_copy}")
    try:
        game = Game(number_of_players,game_pool,deck.deck.copy()) #whos playing
    except TypeError:
        print("No Bots loaded yet.")
    for player in game_pool:
        player.game_score = 0

    if not round_idx == 15:
        game.starting_player(game_pool_copy[round_idx%4])
        game.round(round_idx)
    else:
        game.starting_player(game_pool_copy[15%4])
        game.round(round_idx,lastround = True)                                                          

    for player in game_pool:
        utils.add_seperate_score(player.name,player.game_score)
    
    return



def scrape_pool(n_cores,above_alpha):
    """
    ______
    Input:
        number of available cores
        all bots still playing
    ______
    Output:
        time taken to scrape all scores
    ______
        all bots have their seperate scores combined into one main score file
    """
    print(f"Scraping {len(above_alpha)} Scores")
    start_time = time.time()
    with multiprocessing.Pool(n_cores) as p:
        p.map(utils.scrape_scores,above_alpha)
    scrape_time = time.time()-start_time
    print(f"scraped {len(above_alpha)} scores in {scrape_time}")       

    return scrape_time



def play_pool (n_cores,pool_list):
    """
    ______
    Input:
        number of available cores
        list of all game pools
    ______
    Output:
        time taken to play all games
    ______
        every pool in pool list plays one game
    """ 
    start_time = time.time()
    with multiprocessing.Pool(n_cores) as p:    
        p.map(play_single_round,pool_list)
    play_time=time.time()-start_time
    print(f"Played in {play_time}")

    return play_time



def use_multi_core(bots,width=10,alpha_thresh=0.1):
    """
    ______
    Input:
        significance interval
        significance value
        loaded player instances of all bots

    ______
    Output:
        none
    ______
        uses four core to make the bots play until each of their score values has
        a significance value of alpha or lower
    """
    n_cores = multiprocessing.cpu_count()
    above_alpha = bots.copy()    

    while len(above_alpha):
        
        above_alpha = bots.copy()
        score_estim_list = [(diagnostics.score_estim(width,bot.name),bot) for bot in bots]
        for significant_tuple in (significant_tuples := [tuple for tuple in score_estim_list if tuple[0][1] < alpha_thresh]):
            above_alpha.remove(significant_tuple[1])
        print(f"{len(significant_tuples)} out of {len(bots)} scores are significant")

        if not above_alpha: 
            return above_alpha #hacky catch number one
        
        average_alpha = np.mean([tuple[0][1] for tuple in score_estim_list])
        n_games = min([int(np.ceil(average_alpha/alpha_thresh**3)+50)])#a rough estimate, can be made more precise

        if n_games<10:
            n_games=10 #hacky catch number two
            
        print( f"The pools score estimates have a {np.round(average_alpha*100,2)}% chance of being off by more than {width}")

        
        pool_list = []
        
        for game_idx in range(n_games):
            random.shuffle(above_alpha) #st every bot has a diverse set of enemies
            random.shuffle(significant_tuples) #st excess score is distributed more evenly
            pools = [above_alpha[i:i + 4] for i in range(0, len(above_alpha), 4)]
            if (missing_bots := 4 - len(pools[-1])) > 0:#if the last pool is not 4 players
                pools[-1].extend([significant_tuple[1] for significant_tuple in significant_tuples[:missing_bots]])               
            pool_list.extend(pools)

        print(f"All bots play {n_games} games")
        game_time = play_pool(n_cores,pool_list)
        scrape_time = scrape_pool(n_cores,above_alpha)
        utils.save_time_performance(gen_idx=utils.current_gen(),n_games=n_games,pool_size=len(above_alpha),game_time=game_time,scrape_time=scrape_time,n_cores=n_cores)
    
    return above_alpha
                


def play_to_significance(bots,width=10,alpha_thresh=0.1):
    """
    ______
    Input:
        significance interval
        significance value
        method of training
        loaded player instances of all bots
    ______
    Output:
        none
    ______
        makes the bots play until each of their score values has
        a significance value of alpha or lower
        
    """
    
    above_alpha = use_multi_core(bots,width,alpha_thresh)
                        
    scrape_pool(multiprocessing.cpu_count(),bots)#scrape leftover scores
    
    score_tuples = [(diagnostics.score_estim(width,bot.name),bot.name) for bot in bots]
    if [tuple[1] for tuple in score_tuples if tuple[0][1] > alpha_thresh]:
        play_to_significance(bots,width=width,alpha_thresh=alpha_thresh)
        score_tuples = [(diagnostics.score_estim(width,bot.name),bot.name) for bot in bots]
        
    assert not (insignificant_scores := ([tuple[1] for tuple in score_tuples if tuple[0][1] > alpha_thresh])),f"{insignificant_scores} are left over!"
    
    
    print("Significance achieved")
    return True



def assign_scores_to_species(gen_idx):
    """
    assigns a species average score to the species dictionary
    """
    species_dict=utils.load_gen_species(gen_idx)
    for species_idx,species in species_dict.items():
        species_mean_score = np.mean([diagnostics.score_estim(1,botname)[0] for botname in species_dict[species_idx]["MEMBERS"]])
        species_dict[species_idx]["SCORE"] = species_mean_score
    utils.save_generation_species(gen_idx, species_dict)
    return   



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
    assign_scores_to_species(gen_idx)
    diagnostics.population_progress(silent=True)
    
    return



def progressive_step(gen_idx,bots,population_size,link_thresh,node_thresh,weights_mut_thresh,rand_weight_thresh,pert_rate,preservation_rate,improvement_timer):
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
    species_dict = utils.load_gen_species(gen_idx-1,assign_species = True, bots = bots)#if there is a dictionary
    species_dict = utils.clear_empty_species_from_dict(species_dict)
    fitness(bots = bots,species = species_dict)
    species_sizes=species_allocation(bots=bots,species_dict=species_dict,pop_size=population_size,improvement_timer=improvement_timer)
    
    print("Spezies Sizes Dict: ", species_sizes)

 
    names = utils.load_empty_bot_names(gen_idx)
    if population_size>100:
        names = utils.load_boring_names(gen_idx) #bc finding approx. 50000 names isnt as easy as it seems
    
    name_idx = 0
    kill_list,new_members_list = [],[]
    for species_idx,species in species_dict.items():
        species["MEMBERS"],species_kill_list = reproduce(bots,species["MEMBERS"],names[name_idx:],species_sizes[species_idx],preservation_rate) #from name to name
        name_idx+=len(species["MEMBERS"])
        kill_list.extend(species_kill_list)
        new_members_list.extend(species["MEMBERS"])
        
        mutate_species(species["MEMBERS"],link_thresh,node_thresh,weights_mut_thresh,rand_weight_thresh,pert_rate)

    bots = [Player(bot_name) for bot_name in new_members_list if bot_name not in kill_list] #load the new generation
    assert len(bots)==population_size, f"Population size is off: {len(bots)}"
    
    new_species_representatives = species_represent(species_dict)
    utils.incinerate_redundant_representatives(new_species_representatives)

    
    new_species_dict = speciation(bots=bots,pop_size=population_size,species_dict = new_species_representatives)
    utils.save_generation_species(gen_idx,new_species_dict)#save species under gen idx

    for bot in kill_list:
        utils.incinerate(bot)
        
    assert len(bots)==population_size, "Too many bots!!"
    
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
               improvement_timer=10):
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
    
    
    progressive_step(gen_idx,bots,population_size,link_thresh,node_thresh,weights_mut_thresh,rand_weight_thresh,pert_rate,preservation_rate,improvement_timer)

    bots = [Player(bot_name) for bot_name in utils.load_bot_names()]
    inquiry_step(gen_idx,bots,significance_width,significance_val)
    
    return



def start_training(significance_width,
                   significance_val,
                   population_size,
                   link_thresh,
                   node_thresh,
                   weights_mut_thresh,
                   rand_weight_thresh,
                   pert_rate,
                   preservation_rate,
                   improvement_timer):
    current_gen = utils.current_gen()

    true_current_gen = utils.check_for_species_dict(current_gen)
    if true_current_gen > current_gen:
        new_species_representatives = species_represent()#empty representative species
        new_species_dict = speciation(bots=[Player(bot) for bot in utils.load_bot_names()],pop_size=population_size,species_dict = new_species_representatives)
        utils.save_generation_species(current_gen,new_species_dict)


    while True:
        current_gen +=1
        print(f"Training generation {current_gen-1} to produce generation {current_gen}")
        generation(current_gen,
                   significance_width,significance_val,population_size,
                   link_thresh,node_thresh,weights_mut_thresh,rand_weight_thresh,pert_rate,preservation_rate,improvement_timer)



        
if __name__ == "__main__": #so it doesnt run when imported
    print(txt)

    botnames=utils.load_bot_names()
    botnames.sort(key=lambda bot_name : diagnostics.score_estim(10,bot_name)[0],reverse=True)
    bots = [Player(bot_name) for bot_name in botnames]
    
    print(f"{multiprocessing.cpu_count()} cores available.")
    diagnostics.population_progress()

    diagnostics.species_over_time(pop_size=500)
    for _ in range(2):
        diagnostics.graph(bots[_].name,'play')
        diagnostics.graph(bots[_].name,'bid')
        diagnostics.graph(bots[_].name,'stm')
        diagnostics.score_hist(bots[_].name)
  
    
    scrape_pool(4,utils.load_bot_names())
    start_training(significance_val=0.25,
                   significance_width=2,
                   pert_rate=0.3,
                   population_size=500,
                   link_thresh=0.01,
                   node_thresh=0.005,
                   weights_mut_thresh=0.8,
                   rand_weight_thresh=0.05,
                   preservation_rate=0.8,
                   improvement_timer=5)

"""
if it dont work now:
 1.change perturbation rate to 0.3 or something ---> nah
 2.lower the mutation rate further --> 
 3.decrease c_3 in evolution more

"""
