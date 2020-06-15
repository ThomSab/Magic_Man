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
from magic_man_player  import Player
from base_path import base_path,bot_dir
from magic_main import Game
from magic_man_stats import mov_avg
from magic_man import txt
#______________________________________________________________________________    
number_of_players = 4 #for now
clear = lambda: os.system('cls')


"""
The players are named by score
so whenever a bot scores high its children get high scoring names
an average is calculated of the score
so whenever a bot falls below a certain threshold it gets deleted
to prevent the bots from taking up disk space
"""
current_pool = None
highestranking = None  
pool_size = 100
learning_rate = float(bot_dir.split('_')[-1])
kill_bool = 1
kill_margin = -15
pool_size_limit = 500
create_initial_pool_bool = False

def load_pool (pool_size):
    integrity_check = refresh_max_avg_score(integrity_check = True)
    if integrity_check[0] == 'INCINERATE':
        shutil.rmtree(base_path + bot_dir + r'\{}'.format(integrity_check[1]))
        print('Bot {} incinerated'.format(integrity_check[1]))
            
    bot_avgscores = load_avg_scores()
    bot_avgscores.sort(key = lambda x: x[0] , reverse = True)
    current_pool = [Player(score_tuple[1]) for score_tuple in bot_avgscores[:pool_size]]
    current_pool.sort(key = lambda x: int(x.id))
    return current_pool




def load_avg_scores(bot_dir = bot_dir):
    path = base_path + bot_dir 
    bot_dirnames = [dir for dir in os.listdir(path)]
    if 'player_serial_number.txt' in bot_dirnames:
        bot_dirnames.remove('player_serial_number.txt')
    
    bot_avgscores = [ (-100,0) for idx in range(len(bot_dirnames))]
    idx = 0
    for id in bot_dirnames:
        with np.load(path + r'\{}\stat_arr_avg.npz'.format(id),allow_pickle = True) as file:
            bot_avgscores[idx] = (file['avgscore'],id)
            idx+=1
        
    return bot_avgscores




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




def save_clone(id,arg,clone_weights,clone_biases):    
    np.savez(base_path + bot_dir +  r'\{0}\player_{1}\{2}.npz'.format(id,id,arg),weights = clone_weights,biases = clone_biases)




def clone(player,learning_rate,number_of_clones):
    path = base_path + bot_dir    
    max_avgscore_tuple = refresh_max_avg_score()
    current_max_score = max_avgscore_tuple[0]
    
    for clone in range(number_of_clones):# -1 )
        highestid = refresh_player_serial_number()
        clone_id = highestid+1
        create_clone_path = Player(clone_id,init_score = (current_max_score) )
                
        for arg in ['bid','play','progress']:
            with np.load(player.path + r'\{}.npz'.format(arg),allow_pickle = True) as file:
                clone_weights , clone_biases = file['weights'], file['biases']
                
                for _ in range(len(clone_weights)):
                    clone_weights[_] = clone_weights[_] + np.random.normal(0,learning_rate,clone_weights[_].shape)
                for _ in range(len(clone_biases)):
                    clone_biases[_] = clone_biases[_] + np.random.normal(0,learning_rate,clone_biases[_].shape)
                
                save_clone(clone_id,arg,clone_weights,clone_biases)




def refresh_player_serial_number():
    print("Refreshing Player Serial Number")
    path = base_path + bot_dir
    player_filenames = [_ for _ in os.listdir(path)]
    if os.path.exists(path + '\player_serial_number.txt'):
        player_filenames.remove('player_serial_number.txt')
        
    player_filenames.sort(key = lambda x: float(x),reverse = True)
    highest_id = float(player_filenames[0].split('_')[-1])
    
    bsn = open(base_path + bot_dir +  r'\player_serial_number.txt',"w")
    bsn.write(str(int(highest_id)))
    bsn.close()
    
    with open(base_path + bot_dir +  r'\player_serial_number.txt',"r") as bsn:
        current_player_serial = bsn.read()
        print("Highest Serial Number is {}.".format(current_player_serial))
        bsn.close()
    return int(highest_id)




def refresh_max_avg_score(bot_directory = bot_dir,integrity_check = True,attempts = 3,progress_bool = False):
    print("Refreshing Maximum Average Score")
    learning_rate = float(bot_directory.split('_')[-1])
    path = base_path + bot_directory
    dirlist = os.listdir(path)
    dirlist.remove('player_serial_number.txt')
    for bot_id in dirlist:
        if integrity_check:
            try:
                with np.load(path + '\\' + bot_id + '\stat_arr.npz',allow_pickle = True) as stats:
                    stats = stats['stats']
                    avg = sum(stats)/len(stats)
                    np.savez(path + '\\' + bot_id + r'\stat_arr_avg.npz',avgscore = np.array(avg))
                    

            except BadZipFile:
                if attempts > 0:
                    one_less = (attempts-1)
                    print('Failed because of Bot {}. \n{} attempts left.'.format(bot_id,attempts))
                    return refresh_max_avg_score(attempts = one_less)
                else:
                    print('Integrity check failed')
                    shutil.rmtree(base_path + bot_dir + r'\{}'.format(bot_id))
                    print('Bot {} incinerated'.format(bot_id))
                    return ('INCINERATE',bot_id)
            except OSError: 
                print("OSError in {}".format(bot_id))
        else:
            with np.load(path + '\\' + bot_id + '\stat_arr.npz',allow_pickle = True) as stats:
                stats = stats['stats']
                avg = sum(stats)/len(stats)
                np.savez(path + '\\' + bot_id + r'\stat_arr_avg.npz',avgscore = np.array(avg))
    
    avgscores = load_avg_scores(bot_dir = bot_directory)
    avgscores.sort(key = lambda x: float(x[0]) , reverse = True)
    print('Maximum average Score is {} for Bot {}'.format(np.round(avgscores[0][0],3),avgscores[0][1]))

    try:
        with np.load(base_path + r'\max_progress_{}.npz'.format(learning_rate),allow_pickle = True) as progress:
            progress = list(progress['progress'])
            progress.append(float(avgscores[0][0]))
            np.savez(base_path + r'\max_progress_{}.npz'.format(learning_rate),progress = np.array(progress))
    except FileNotFoundError:
        np.savez(base_path + r'\max_progress_{}.npz'.format(learning_rate),progress = np.array([-10]))
    
    if progress_bool:
        try:
            with np.load(base_path + r'\real_max_progress_{}.npz'.format(learning_rate),allow_pickle = True) as progress:
                progress = list(progress['progress'])
                progress.append(float(avgscores[0][0]))
                np.savez(base_path + r'\real_max_progress_{}.npz'.format(learning_rate),progress = np.array(progress))
        except FileNotFoundError:
            np.savez(base_path + r'\real_max_progress_{}.npz'.format(learning_rate),progress = np.array([-10]))
    
    return avgscores[0]

def kill_bad_bots(margin):
    refresh_max_avg_score()
    avgscores = load_avg_scores()
    bad_bot_tuples = [ bot_tuple for bot_tuple in avgscores if bot_tuple[0] <= margin]
    print('{} Bots fall under the margin'.format(len(bad_bot_tuples)))
    bad_bot_dir = [bbtuple[1] for bbtuple in bad_bot_tuples]
    
    for directory in bad_bot_dir:
        shutil.rmtree(base_path + bot_dir + r'\{}'.format(directory))
        print('Bot {} incinerated.'.format(directory))




def resize_full_pool(full_pool_size = 1500):
    refresh_max_avg_score()
    avgscores = load_avg_scores()
    oversize = len(avgscores) - full_pool_size
    if oversize > 0:
        avgscores.sort(key = lambda x: x[0])
        for bot_tuple in avgscores[:oversize]:
            shutil.rmtree(base_path + bot_dir + r'\{}'.format(bot_tuple[1]))
            print('Bot {} had a score of {} and was incinerated.'.format(bot_tuple[1],np.round(bot_tuple[0])))
    else:   
        print('Full pool has size {} and is not oversized'.format(len(avgscores)))




def load_score_dict(pool,entire_dir = False):
    
    if entire_dir:
        print("Loading entire Dictionary")
        path = base_path + bot_dir 
        bot_dirnames = [dir for dir in os.listdir(path)]
        if 'player_serial_number.txt' in bot_dirnames:
            bot_dirnames.remove('player_serial_number.txt')
        pool = load_pool(len(bot_dirnames))
        
    statdata = [0 for _ in range(len(pool))]
    idx = 0 
    for player in pool:
        with np.load(player.player_dir + r'\stat_arr.npz',allow_pickle = True) as player_data:
            statdata[idx] = (list(player_data['stats']),player.id)
            idx += 1
    dict = {statdata[_][1] : statdata[_][0] for _ in range(len(pool))}
    return dict



def match(tuple_arg,dictionary = None):
    player_idx,current_pool,pool_size = tuple_arg

    if dictionary == None:
        try:
            playerstats = load_score_dict(current_pool)
            print("Score Dictionary Loaded")
        except OSError:
            print('OSERROR')
            return
        except BadZipFile:
            print('Bad Zip File in match function')
            integrity_check = refresh_max_avg_score(integrity_check = True)
            return
    elif not dictionary == None:
        playerstats = dictionary
    
    for game in range(pool_size-1): #everyone plays a game with each other player 
        game_pool = [current_pool[player_idx]]
        for _ in range(3):#add the other 3 players
            append_idx = (player_idx + game + _)%pool_size
            if current_pool[append_idx] not in game_pool:
                game_pool.append(current_pool[append_idx])
            else:
                game_pool.append(current_pool[(append_idx+1)%pool_size])

                
        play_game(game_pool)
        for player in game_pool:
             
            playerstats[player.id].append(player.game_score)

    if dictionary == None:
        for player in current_pool:
            np.savez(player.player_dir + r'\stat_arr.npz',stats = np.array(playerstats[player.id]))






def training_session(pool_size = pool_size,learning_rate = learning_rate, n_clones = 0,entire_dir_bool = True,session = '_'):
    refresh_player_serial_number()
    current_pool = load_pool(pool_size)
    for _ in range(1):
        if entire_dir_bool:
            entire_dir = load_score_dict(None,entire_dir = entire_dir_bool)
        else:
            entire_dir = None
            
        print('Match Session {}'.format(_+1))
        print('Learning Rate is', learning_rate)
        print('Playing Magic Man...')
        for player_idx in range(pool_size):
            match((player_idx,current_pool,pool_size),dictionary = entire_dir)
            progress = ((player_idx+1)/pool_size)*100
            clear()
            print('Learning Rate is', learning_rate)
            print(' '+'_'*100)
            print('|'*int(np.round(progress)+1) + '_'*int(np.round(100-progress))+'|')
            print("{} %".format(np.round(progress,decimals=1)))
            if n_clones > 0:
                print("Cloning Session")
            elif n_clones == 0:
                print("Non-Cloning Session ({} more after this)".format(session))
            if entire_dir_bool:
                for player in current_pool:
                    np.savez(player.player_dir + r'\stat_arr.npz',stats = np.array(entire_dir[player.id]))
                    
    refresh_attempts = 0
    refresh_success  = False
    while refresh_attempts <= 3 and not refresh_success:
        try:
            max_avgscore_tuple = refresh_max_avg_score(progress_bool = (True if n_clones > 0 else False))
            refresh_success    = True
        except:
            print('Attempt {} failed to refresh maximum average score after training session finished.'.format(refresh_attempts))
            attempts += 1
    
    
    print("Player {} has the maximum average score after the session and will be cloned.".format(max_avgscore_tuple[1]))
    clone_success = False
    clone_attempts = 0
    while not clone_success and clone_attempts < 3:
        try:
            clone(Player(max_avgscore_tuple[1]),learning_rate,n_clones)
            clone_success = True
        except:
            print('Attempt {} failed to clone after training session finished.'.format(clone_attempts))
            clone_attempts += 1





if __name__ == "__main__": #so it doesnt run when imported
    print(txt)
    if create_initial_pool_bool:
        players = [Player(_,init_sigma = learning_rate) for _ in range(pool_size)]
    refresh_player_serial_number()


    while True:
        kill_count_down = 9
        killed_and_cloned = False
        while not killed_and_cloned and kill_count_down >= 0:#try:
            if kill_count_down == 0:
                print('Kill Countdown is at', kill_count_down)
                refresh_max_avg_score()
                resize_full_pool(full_pool_size = pool_size_limit)
                killed_and_cloned = True
                training_session(n_clones = 50,session = kill_count_down)
            else:
                print('Kill Countdown is at', kill_count_down)
                training_session(session = kill_count_down)
                kill_count_down -= 1
            #except Exception as exc:
            #    print('Training session failed. \n {}'.format(exc))






