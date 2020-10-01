"""
Utility functions for the Magic_Man project
"""
import json
import numpy as np
from scipy.special import expit
import os
import sys
import shutil
import time



cwd = os.getcwd()
N_bid_sensors  = 89
N_bid_outputs  = 1
N_play_sensors = 160
N_play_outputs = 60
N_stm_sensors  = 160
N_stm_outputs  = 10
init_list = [N_bid_sensors,N_bid_outputs,N_play_sensors,N_play_outputs,N_stm_sensors,N_stm_outputs]
init_innovation_numbers = {'bid':N_bid_sensors*N_bid_outputs,'play':N_play_sensors*N_play_outputs,'stm':N_stm_sensors*N_stm_outputs}



def logit_bidding (p):
    """
    Alternative sigmoid function
    The Output constrains the output to values that are appropriate
    i.e.: between 0 and 4
    s.t. the bot anticipates to get between no suits and all suits.
    ______
    Input:
    Raw Activation of the output Node
    Output:
    Adjusted Output
    """
    bid_factor = 0.3*np.log(p/(1-p))+1
    if bid_factor < 0 :
        return 0
    elif bid_factor > 4:
        return 4
    else:
        return bid_factor

def save_init_genome(bot_name,init_genome,directory=cwd):
    """
    ______
    Input:
        Score_data, Location, Bot-Name
        Optional specification for json or .npz(Numpy Arrays)

    ______
    Output:
        Failiure if saving
        Nothing on Success
    ______
        [Json is up to 25 times faster than pickle according to 
        https://konstantin.blog/2010/pickle-vs-json-which-is-faster/ ]
    """
    if not os.path.exists(directory + r'\Bots'):
        os.mkdir(directory + r'\Bots')
    if not os.path.exists(directory + r'\Bots\{}'.format(bot_name)):
        os.mkdir(directory + r'\Bots\{}'.format(bot_name))
    try:
        with open(directory + r'\Bots\{}\genome.json'.format(bot_name),'x')as genome_file: #open mode 'x' creates a file and fails if it already exists
            json.dump(init_genome,genome_file)#initial score is saved as the first entry of a list
            print(f"Generated new Bot: {bot_name}")

        return
        
    except Exception as exception:
        print("Saving the initial score failed: {}".format(exception))


def save_init_score (bot_name,directory=cwd):
    """
    ______
    Input:
        bot name
    ______
    Output:
        Saves the initial score for a bot.
        This is a dictionary containing an empty list
    ______
        The score is kept as a list
    """
    if not os.path.exists(directory + r'\Bots\{}'.format(bot_name)):
        os.mkdir(directory + r'\Bots\{}'.format(bot_name))
    try:
        with open(directory + r'\Bots\{}\score.json'.format(bot_name),'x')as score_file: #open mode 'x' creates a file and fails if it already exists
            json.dump({"SCORE":[]},score_file)#initial score is saved as the first entry of a list
        return
    except Exception as exception:
        print("Saving the initial score failed: {}".format(exception))
    

def reset_score (bot_name,directory=cwd):
    """
    ______
    Input:
        bot name
    ______
    Output:
        Overwrites the old score with empty score
    ______
    """
    assert (os.path.exists(directory + r'\Bots\{}'.format(bot_name))),f"{bot_name} has no score file and cannot be reset"
    try:
        with open(directory + r'\Bots\{}\score.json'.format(bot_name),'w')as score_file:
            json.dump({"SCORE":[]},score_file)
        return
    except Exception as exception:
        print(f"Reseting {bot_name}'s score failed: {exception}")
        

def save_init_time_performance(directory=cwd):
    try:
        with open(directory + r'\Bots\time_perform.json','x')as progress_file: #open mode 'x' creates a file and fails if it already exists
            json.dump([{"GEN":0,"NGAMES":0,"POOLSIZE":0,"GAMETIME":0,"SCRAPETIME":0,"NCORES":0}],progress_file)#initial progress is saved as the first entry of a list
        return
    except Exception as exception:
        print("Saving the initial time performance failed: {}".format(exception))   
    


def save_init_progress(directory=cwd):
    try:
        with open(directory + r'\Bots\progress.json','x')as progress_file: #open mode 'x' creates a file and fails if it already exists
            json.dump([{"GEN":0,"MAX":0,"BOT":"NOBOT","CONF":0,"AVG":0}],progress_file)#initial progress is saved as the first entry of a list
        return
    except Exception as exception:
        print("Saving the initial progress failed: {}".format(exception))


def save_init_innovation(nn_type,init_innovation,directory=cwd):
    """
    ______
    Input:
        nn_type
        can be ['play','bid','stm']
    ______
    Output:
        Saves the initial innovation number for a neural net.
        How high this number is depends on the initial size of the neural net.
    ______
        Historical marking is a globals variable.
        It is not an attribute of any single bot but instead of one kind of evolutional process.
        There is one history for each neural net i.e. bidding, stm, play.
        Each neural net has an individual innovation number bc changes to the neural net only apply to that kind of neural net        

    """
    if not os.path.exists(directory + r'\Bots'):
        os.mkdir(directory + r'\Bots')
    try:
        with open(directory + r'\Bots\{}_innovation.json'.format(nn_type),'x')as init_innovation_file: #open mode 'x' creates a file and fails if it already exists
            json.dump(init_innovation,init_innovation_file)
        return
    except Exception as exception:
        print("Saving the initial innovation number failed: {}".format(exception))


def init_representative_dir(directory=cwd):
    if not os.path.exists(directory + r'\Bots\Species_Representatives'):
        os.mkdir(directory + r'\Bots\Species_Representatives')
    return

def save_time_performance(gen_idx,n_games,pool_size,game_time,scrape_time,n_cores,directory=cwd):
    try:
        with open(directory + r'\Bots\time_perform.json','r')as time_perform_file: #open mode 'r' read 
            time_perform_obj = json.load(time_perform_file)
            time_perform_file.close()
        
        time_perform_obj.append({"GEN":gen_idx,"NGAMES":n_games,"POOLSIZE":pool_size,"GAMETIME":game_time,"SCRAPETIME":scrape_time,"NCORES":n_cores})
        
        with open(directory + r'\Bots\time_perform.json','w') as time_perform_file:
            json.dump(time_perform_obj,time_perform_file)
            print(f"Time performance saved")
            
    except Exception as exception:
        print("Saving time performance failed: {}".format(exception))       

def save_generation_species(gen_idx,species_dict,directory=cwd):

    if not os.path.exists(directory + r'\Bots\species.json'): #initial species
        with open(directory + r'\Bots\species.json','w') as species_file:
            try:
                json.dump({("GEN_"+str(gen_idx)):species_dict},species_file)
            except Exception as exception:
                print("Saving initial species representatives failed: {}, \n Species: {}".format(exception,species))
        return

    try:
        with open(directory + r'\Bots\species.json','r')as species_file: #open mode 'r' read 
            species_obj = json.load(species_file)  
            species_file.close()
            
        if not str(gen_idx) in species_obj:    
            species_obj[("GEN_"+str(gen_idx))] = species_dict
        else:
            print(f"Generation Index Conflict: The species dictionary for generation{gen_idx} already exists!")
            return
        
        with open(directory + r'\Bots\species.json','w') as species_file:
            json.dump(species_obj,species_file)
            print(f"Species dictionary for generation {gen_idx} saved")
            
    except Exception as exception:
        print("Saving species failed: {}".format(exception))            
    
def save_progress(gen_idx,max_score,max_bot,max_score_conf,avg_score,directory=cwd):
    try:
        with open(directory + r'\Bots\progress.json','r')as progress_file: #open mode 'r' read 
            progress_obj = json.load(progress_file)
            progress_file.close()
        
        if (progress_duplicates:= [progress_dict for progress_dict in progress_obj if progress_dict["GEN"] == gen_idx]):
            gen_progress = progress_duplicates[0] #i assume that there is only one duplicate at any time
            gen_progress["MAX"] = max_score
            gen_progress["BOT"] = max_bot
            gen_progress["CONF"] = max_score_conf
            gen_progress["AVG"] = avg_score
        
        else:
            progress_obj.append({"GEN":gen_idx,"MAX":max_score,"BOT":max_bot,"CONF":max_score_conf,"AVG":avg_score})
        
        with open(directory + r'\Bots\progress.json','w') as progress_file:
            json.dump(progress_obj,progress_file)
            print(f"Progress of Generation {gen_idx} saved")
            
    except Exception as exception:
        print("Saving progress failed: {}".format(exception))     

       
        
def save_bot_genome(bot_name,genome,directory=cwd):
    with open(directory + r'\Bots\{}\genome.json'.format(bot_name),'w') as genome_file:
        try:
            json.dump(genome,genome_file)
        except Exception as exception:
            print("Saving {} genome failed: {}".format(bot_name,exception))


def save_representative(bot_name,directory=cwd):
    try:
        shutil.copytree(directory + f'\Bots\{bot_name}',directory + f'\Bots\Species_Representatives\{bot_name}')   
        return
    except FileExistsError:
        print("Saving representative {} copy failed: {}".format(bot_name,"FileExistError"))
        return
    except Exception as exception:
        print("Saving representative {} copy failed: {}".format(bot_name,exception))
        sys.exit("Unhandled Error")
        

def load_gen_species(gen_idx,assign_species=False,bots=None,directory = cwd):
    """
    Can assign species to Bots!
    """
    with open(directory + r'\Bots\species.json','r') as species_file:
        species_obj = json.load(species_file)
        species_file.close()
    
    if assign_species==True:
        assert bots , "No Bots were given to assign species to."
        for species_idx,species in species_obj[("GEN_"+str(gen_idx))].items():
            for bot in [bot for bot in bots if bot.name in species["MEMBERS"]]:
                bot.species = species_idx
    
    return species_obj[("GEN_"+str(gen_idx))]

def load_bot_genome(bot_name,directory= (cwd+r'\Bots' )):
    if type(bot_name)!=str:
        print(f"{str(bot_name)} not string type: {type(bot_name)}")
        bot_name = bot_name.name
    try:
        with open(directory + '\{}\genome.json'.format(bot_name),'r') as genome_file:
            return json.load(genome_file)
    except Exception as exception:
        print(f"Loading {bot_name}'s Genome Failed: {exception}")
        sys.exit(f"{bot_name}'s Genome file is inaccessable.")

def load_bot_score(bot_name,directory=cwd):
    try:
        with open(directory + r'\Bots\{}\score.json'.format(bot_name),'r') as score_file:
            return json.load(score_file)["SCORE"]
    
    except Exception as exception:#if the integrity of the botfile is compromised its important to know in which bot it is
        print(f"Loading {bot_name}'s score failed: {exception}")
        sys.exit(f"{bot_name}'s score file is inaccessable.")       
        
def load_bot_names(directory=(cwd + r'\Bots')):
    bot_dir = os.listdir(directory)
    return [bot_name for bot_name in bot_dir if bot_name not in ['Species_Representatives','bid_innovation.json','play_innovation.json','stm_innovation.json','species.json','progress.json','time_perform.json']]

def load_empty_bot_names(gen_idx,directory=cwd):
    with open(directory + r'\names.json','r') as name_file:
        return json.load(name_file)[str(gen_idx%26)]

def load_progress(directory=cwd):
    try:
        with open(directory + r'\Bots\progress.json','r')as progress_file: #open mode 'r' read 
            progress_obj = json.load(progress_file)
            progress_file.close()  
        return progress_obj
        
    except Exception as exception:
        print("Saving progress failed: {}".format(exception))    

def load_innovation_number(nn_type,directory=cwd):
    #nn_type can be ['play','bid','stm']
    return json.load(open(directory + r'\Bots\{}_innovation.json'.format(nn_type),'r'))



            
def add_score (bot_name,add_score,directory=cwd):
    try:
        with open(directory + r'\Bots\{}\score.json'.format(bot_name),'r')as score_file: #open mode 'r' read 
            score_obj = json.load(score_file)  
            score_file.close()
        score_obj["SCORE"].append(add_score)
        with open(directory + r'\Bots\{}\score.json'.format(bot_name),'w')as score_file: #open mode 'w' to write - there has to be a better way
            json.dump(score_obj,score_file)
            score_file.close()
            
        return
            
    except Exception as exception:
        print(f"Saving {bot_name}'s additional score failed: {exception}")
        
   
def add_seperate_score(bot_name,add_score,directory=cwd):
    """
    ______
    Input:
        bot name,score_to add
    ______
    Output:
        Saves an additional seperate score for a bot.
    ______
        The score is kept as a list
    """
    if not os.path.exists(directory + r'\Bots\{}'.format(bot_name)):
        os.mkdir(directory + r'\Bots\{}'.format(bot_name))
    try:
        filename=("SCORE_"+str(time.time())).replace('.','')
        with open(directory + r'\Bots\{}\{}.json'.format(bot_name,filename),'x') as score_file: #open mode 'x' creates a file and fails if it already exists
            json.dump({"SCORE":[add_score]},score_file)#seperate score is saved in a dict
        return
    except Exception as exception:
        print("Saving the additional seperate score failed: {}".format(exception))  


def scrape_scores(bot_name,directory=cwd):
    """
    ______
    Input:
        bot name
    ______
    Output:
        Saves all the seperate score for a bot in the single score file
    ______
        list the directory score files
        add them all to the score one after another so the score file does not break
        
        
        !!dont forget to check the profiler this might cost too much time!!
    """
    print(f"Scraping {bot_name}'s scores")
    
    bot_dir = os.listdir(cwd + f'\Bots\{bot_name}')
    score_files = [scorefile for scorefile in bot_dir if "SCORE_" in scorefile]
    
    try:
        bot_scores=[]
        for score_file_name in score_files:
            with open(directory + f'\Bots\{bot_name}\{score_file_name}','r') as score_file:
                bot_scores.append(json.load(score_file)["SCORE"][0])
            os.remove(directory + f'\Bots\{bot_name}\{score_file_name}')  
            
        for score in bot_scores:
            add_score(bot_name,score)
        
    except Exception as exception:#if the integrity of the botfile is compromised its important to know in which bot it is
        print(f"Scraping{bot_name}'s score failed: {exception}")
        sys.exit(f"{bot_name}'s score file is inaccessable.") 
    
    pass
    
   
def increment_in(nn_type,directory=cwd):
    """
    ______
    Input:
        nn_type can be "bid" "play" "stm"
    ______
    Output:
        The current global innovation number
        Increments the global innovation by one
    """

    try:
        with open(directory + r'\Bots\{}_innovation.json'.format(nn_type),'r') as innovation_file:#open mode 'w+' read AND writes a file    
            incremented_in = json.load(innovation_file)[0]+1
        with open(directory + r'\Bots\{}_innovation.json'.format(nn_type),'w') as innovation_file:
            json.dump([incremented_in],innovation_file)
        return incremented_in
            
    except Exception as exception:
        print("Incrementing the innovation number failed: {}".format(exception))
    
            
    


def bot_compatibility_distance(genome_A,genome_B,c_1,c_2,c_3):
    """
    ______
    Input:
        Two Genomes containing three neural net genomes each
        one for each operation 
    ______
    Output:
        Compatibility Distance between the two genomes
    ______
        Compatibility distance is calculated for all neural nets together
        This is bc the decisions might be interlinked i.e.
        The stm and the playing strategy might not be seperable
        
    """
    return  sum([nn_compatibility_distance(genome_A[nn_genome],genome_B[nn_genome],c_1,c_2,c_3) 
                for nn_genome in ["bid_connection_genome","play_connection_genome","stm_connection_genome"]])
    
    


 
    
def nn_compatibility_distance(nn_genome_A,nn_genome_B,c_1,c_2,c_3):
    """
    ______
    Input:
        Two neural net Genomes
    ______
    Output:
        Compatibility distance between the two neural net genomes
    """
    nng_A_history,nng_B_history = [gene["INNOVATION"] for gene in nn_genome_A],[gene["INNOVATION"] for gene in nn_genome_B] 
    
    if nng_A_history[-1] >= nng_B_history[-1]:# 'history[-1] instead of max(history) bc history list should be sorted
        excess_genes = len([ inn_num for inn_num in nng_A_history if inn_num >  nng_B_history[-1]])
    else:
        excess_genes = len([ inn_num for inn_num in nng_B_history if inn_num >  nng_A_history[-1]])
    #How many genes the newer genome has that have a higher innovation number than the highest one from the older genome
    #this is E, the number of excess genes

    nng_A_dict = {gene["INNOVATION"]:gene for gene in nn_genome_A}#the data structure should have been like this from the start but its too late now
    nng_B_dict = {gene["INNOVATION"]:gene for gene in nn_genome_B}

    matching_innovations = list(set(nng_A_history).intersection(set(nng_B_history)))
        
    nng_A_matching = [nng_A_dict[innovation] for innovation in matching_innovations] 
    nng_B_matching = [nng_B_dict[innovation] for innovation in matching_innovations]
    #instead of the listcompt that would take ~99% of the computing time according to the profiler
    
    disjoint_genes = (len(nng_A_history)-len(nng_A_matching)) + (len(nng_B_history)-len(nng_B_matching)) - excess_genes

    """
    number of disjoint genes are the amount of genes that are not matching with any gene from the other genome by innovation number
    excess genes are substracted bc. they are not both disjoint AND excess genes
    """

    weights_A,weights_B = np.array([gene["WEIGHT"] for gene in nng_A_matching]),np.array([gene["WEIGHT"] for gene in nng_B_matching])
    weight_diff = abs(weights_A-weights_B)         #all absolute differences in weight in matching genes
    avg_wd_mg = np.mean(weight_diff)                #average weight difference of matching genes or W bar   
    N = max([len(nn_genome_A),len(nn_genome_B)])    #the amount of genes in the larger genome
    
    return ((c_1*excess_genes+c_2*disjoint_genes)/N + c_3*avg_wd_mg) #the compatibility distance or delta
    


def compatibility_mat(c1,c2,c3):
    """
    ______
    Input:
        Coefficients for the compatibility distance function
    ______
    Output:
        Matrix containing the compatibility distances between all bots
        first row is the comp. distance between bot_names[0] and all other bots in bot_names
    ______
        Since the distance doesn't have a direction,
        and the distance of a bot to itself is zero,
        only values to one side of the diagonal need to be calculated
        
        Nonetheless this funtion is incredibly slow
        This might not be feasible for large populations :(
    ______
        This function might be redundant since i dont have to calculate all distances
        just the ones that i need to assign the specimen to a species
    """
    bot_names = load_bot_names()
    comp_mat = np.full((len(bot_names),len(bot_names)),np.NaN)
    for bot_idx,bot_name_a in enumerate(bot_names):
        comp_mat[bot_idx][bot_idx+1::] = [bot_compatibility_distance(load_bot_genome(bot_name_a),load_bot_genome(bot_name_b),c1,c2,c3)
                              for bot_name_b in bot_names[bot_idx+1::]]#bot_idx+1 s.t. the diagonal isn't calculated

    
    return bot_names,comp_mat
    #passing bot list and the comp matrix seperately is not so nice
    #but numpy arrays can not store string so this is more practical



def compatibility_search(bot,c1,c2,c3,compat_thresh,species_dict = {}):
    """
    ______
    Input:
        A Player object, the species representatives
        and the parameters for the compatibility distance function
        (c1,c2,c3,delta)
    ______
    Output:
        Returns species that is compatible with the genome of the input bot
        Assigns the species to the bot
    """    
    for species_idx,species in species_dict.items():
        representative_name=species_dict[species_idx]["REPRESENTATIVE"]
        bcd = bot_compatibility_distance(load_bot_genome(bot.name),load_bot_genome(representative_name,directory = (cwd + r'\Bots\Species_Representatives')),c1,c2,c3)
        print(f'Bot {bot} has a compatibility distance of {np.round(bcd,3)} to the species represented by {representative_name}')
        if  bcd < compat_thresh:
            bot.species = species_idx
            return bot.species
    return False


def check_for_recursion(bot_connection_genome,initial_gene,current_gene=None):
    """
    ______
    Input:
        The initial gene whose addition is to be checked for recursion
        A Neural Net Connection Genome WITHOUT THE NEW GENE IN IT
        A Gene for a single connection for the bot that is requesting input
        
    ______
    Output:
        True if there are recursive sets of connections
        False if there are no recursive sets of connections
    ______
        The function is recursive
        it follows all connections leading into the initial gene
        if on this journey through the net it happens to stumble upon itself
        the function passes True through all previous function calls
    """
    if current_gene == None:
        bot_connection_genome= bot_connection_genome.copy()
        bot_connection_genome.append(initial_gene)
        current_gene = initial_gene
    
    for connection_gene in bot_connection_genome:
        if connection_gene["OUT"] == current_gene["IN"]:
            if connection_gene["INNOVATION"] == initial_gene["INNOVATION"]:
                return True #connected to the initial gene --> recursion!!
            elif check_for_recursion(bot_connection_genome,initial_gene,current_gene=connection_gene):
                return True
    return False
    
    
    
def check_for_connection_duplication(bot_connection_genome,connection_gene):
    """
    ______
    Input:
        A Neural Net Connection Genome
        A Gene for a single connection for the bot
    ______
    Output:
        A list of the duplicate connection genes if the connection is already in the net
        False if the connection is new
    """
    if (dubs := [gene for gene in bot_connection_genome if (gene["IN"] == connection_gene["IN"] and gene["OUT"] == connection_gene["OUT"])]):
        return dubs
    return False



def incinerate_redundant_representatives(new_species_representatives):
    #kill off unnecessary representatives
    for bot in os.listdir(cwd + r'\Bots\Species_Representatives'):
        present = False
        for species_idx,species in new_species_representatives.items():        
            if species["REPRESENTATIVE"] == bot:
                present=True
        if not present:
            incinerate(bot,directory=cwd+r'\Bots\Species_Representatives')   

  
def incinerate(bot_name,directory=cwd+'\Bots'):
    """
    ______
    Input:
        A bots Name
    ______
    Output:
        True or False depending on incineration success
    ______
        Deletes a bot and all his files
        Genome and Score
    """   
    
    try:
        shutil.rmtree(directory + f'\{bot_name}')
        print(f"Incinerated {bot_name}.")
    except Exception as exception:
        print(f"Incinerating {bot_name} failed: {exception}") 
        return False

def current_gen(directory=cwd):
    """
    Input:
        cwd to load the species_dict
    Output:
        the index of the youngest generation
    """
    with open(directory + r'\Bots\species.json','r') as species_file:
        species_obj = json.load(species_file)
        species_file.close()
    
    return max([int(gen_idx.split('_')[-1]) for gen_idx,species_dict in species_obj.items()])   


    
def check_for_species_dict(current_gen_idx):
    """
    Possible states:
        1 - last gen created new bots but didnt delete the old ones
        2 - last gen created new bots but did not save the species dictionary
        3 - last gen created new bots and created the species dictionary
    """
    try:
        bot_names =load_bot_names()
        gen_species_dict = load_gen_species(current_gen_idx)
        incinerate_redundant_representatives(gen_species_dict)
        
        bots_in_species_dict = []
        for species_idx,species in gen_species_dict.items():
            bots_in_species_dict.extend([botname for botname in species["MEMBERS"]]) #fails if the bots in the dictionary are not in the pool anymore
        bot_names.sort()
        bots_in_species_dict.sort()

        
        
        unspeciated = [bot for bot in bot_names if bot not in bots_in_species_dict]
        if unspeciated:
            print(len(bot_names), len(bots_in_species_dict))
            if len(bot_names) > len(bots_in_species_dict):
                print("Last generation reproduced but the old bots were not incinerated: Deleting old Bots")
                for bot in unspeciated:
                    incinerate(bot)

                
                return check_for_species_dict(current_gen_idx)
            
            else:
                print("Last generation reproduced but was not speciated: Generating new species_dict")
                return current_gen_idx+1
            
        else:
            return current_gen_idx
            
    except Exception as exception:
        sys.exit(f"Error in species dictionary check: {exception}")    
  
        
        
        
        
    
