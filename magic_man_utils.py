"""
Utility functions for the Magic_Man project
"""
import json
import numpy as np
from scipy.special import expit
import os
import shutil



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


def save_init_score (bot_name,init_score,directory=cwd):
    """
    ______
    Input:
        bot name
    ______
    Output:
        Saves the initial score for a bot.
        This is usualy zero
    ______
        The score is kept as a list
    """
    if not os.path.exists(directory + r'\Bots\{}'.format(bot_name)):
        os.mkdir(directory + r'\Bots\{}'.format(bot_name))
    try:
        with open(directory + r'\Bots\{}\score.json'.format(bot_name),'x')as score_file: #open mode 'x' creates a file and fails if it already exists
            json.dump({"SCORE":[init_score]},score_file)#initial score is saved as the first entry of a list
        return
    except Exception as exception:
        print("Saving the initial score failed: {}".format(exception))
        

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

def save_generation_species(gen_idx,species,directory=cwd):

    if not os.path.exists(directory + r'\Bots\species.json'): #initial species
        with open(directory + r'\Bots\species.json','w') as species_file:
            try:
                json.dump({str(gen_idx):species},species_file)
            except Exception as exception:
                print("Saving initial species representatives failed: {}, \n Species: {}".format(exception,species))
        return

    try:
        with open(directory + r'\Bots\species.json','r')as species_file: #open mode 'r' read 
            species_obj = json.load(species_file)  
            species_file.close()
            
        if not str(gen_idx) in species_obj:    
            species_obj[str(gen_idx)] = species
        else:
            print(f"Generation Index Conflict: The Species {gen_idx} already exists!")
            return
        
        with open(directory + r'\Bots\species.json','w') as species_file:
            json.dump(species_repr)
            print(f"Species {gen_idx} saved")
            
    except Exception as exception:
        print("Saving species failed: {}".format(exception))            
    


def load_generation_species(gen_idx,directory = cwd):
    with open(directory + r'\Bots\species_repr.json','r') as species_file:
        species_obj = json.load(species_file)
        return species_obj[str(gen_idx)]
        
        
def save_bot_genome(bot_name,genome,directory=cwd):
    with open(directory + r'\Bots\{}\genome.json'.format(bot_name),'w') as genome_file:
        try:
            json.dump(genome,genome_file)
        except Exception as exception:
            print("Saving {} genome failed: {}".format(bot_name,exception))

def load_bot_genome(bot_name,directory=cwd):
    try:
        with open(directory + r'\Bots\{}\genome.json'.format(bot_name),'r') as genome_file:
            return json.load(genome_file)
    except Exception as exception:
        print(f"Loading {bot_name} Genome Failed: {exception}")

def load_bot_score(bot_name,directory=cwd):
    with open(directory + r'\Bots\{}\score.json'.format(bot_name),'r') as score_file:
        return json.load(score_file)["SCORE"]
        
def load_bot_names(directory=cwd):
    bot_dir = os.listdir(cwd +'\Bots')
    return [bot_name for bot_name in bot_dir if bot_name not in ['bid_innovation.json','play_innovation.json','stm_innovation.json','species.json']]

def load_empty_bot_names(gen_idx,directory=cwd):
    with open(directory + r'\names.json','r') as name_file:
        return json.load(name_file)[str(gen_idx)]
    
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
        print("Saving additional score failed: {}".format(exception))
        
    
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
        
    nng_A_matching = [gene for gene in nn_genome_A if gene["INNOVATION"] in nng_B_history] 
    nng_B_matching = [gene for gene in nn_genome_B if gene["INNOVATION"] in nng_A_history]
    #this listcomp does take ~99% of the computing time according to the profiler
    
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



def compatibility_search(bot,c1,c2,c3,compat_thresh,represent = {}):
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
    for representative in represent:
        if bot_compatibility_distance(load_bot_genome(bot),load_bot_genome(representative),c1,c2,c3) < compat_thresh:
            bot.species = representative
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
    
    
def incinerate(bot_name,directory=cwd):
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
        shutil.rmtree(directory + f'\Bots\{botname}')
    except Exception as exception:
        print(f"Incinerating {bot_name} failed: {exception}") 
        return False
    return True
        
        
        
        
        
        
        
    