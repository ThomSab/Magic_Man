"""
Utility functions for the Magic_Man project
"""
import json
import numpy as np
from scipy.special import expit
import os
cwd = os.getcwd()

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



def load_bot_genome(bot_name,directory=cwd):
    with open(directory + r'\Bots\{}\genome.json'.format(bot_name),'r') as genome_file:
        return json.load(genome_file)


def load_bot_score(bot_name,directory=cwd):
    with open(directory + r'\Bots\{}\score.json'.format(bot_name),'r') as score_file:
        return json.load(score_file)["SCORE"]

def load_bot_names(directory=cwd):
    bot_dir = os.listdir(cwd +'\Bots')
    return [bot_name for bot_name in bot_dir if bot_name not in ['bid_innovation.json','play_innovation.json','stm_innovation.json']]


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
        nn_type
    ______
    Output:
        None
        Increments the global innovation by one
    """

    try:
        with open(directory + r'\Bots\{}_innovation.json'.format(nn_type),'r') as innovation_file:#open mode 'w+' read AND writes a file
            innovation_number = json.load(innovation_file)         
            innovation_number += 1
        with open(directory + r'\Bots\{}_innovation.json'.format(nn_type),'w') as innovation_file:
            json.dump(genome,innovation_file)
        return
            
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
    nng_B_matching = [gene for gene in nn_genome_A if gene["INNOVATION"] in nng_A_history]
    
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
    ______
        Since the distance doesn't have a direction,
        and the distance of a bot to itself is zero,
        only values to one side of the diagonal need to be calculated
        
        Nonetheless this funtion is incredibly slow
        This might not be feasible for large populations :(
    """
    bot_names = load_bot_names()
    comp_mat = np.full((len(bot_names),len(bot_names)),np.NaN)
    for bot_idx,bot_name_a in enumerate(bot_names):
        comp_mat[bot_idx][bot_idx+1::] = [bot_compatibility_distance(load_bot_genome(bot_name_a),load_bot_genome(bot_name_b),c1,c2,c3)
                              for bot_name_b in bot_names[bot_idx+1::]]#bot_idx+1 s.t. the diagonal isn't calculated

    
    return index_mat
  

def speciation (compat_thresh,compat_mat,represent = []):
    """
    ______
    Input:
        The set compatibility threshold
        and the compatibility matrix
    ______
    Output:
        Assigns each specimen in the population a species
    """
    assert type(represent)==list,"Representative Genome was not passed as a list but as {}".format(type(represent))
        
    
    pass

  
   
def fitness (score,speciation):
    """
    ______
    Input:
        An average score estimate
        the amount of specimen in the same species
    ______
    Output:
        Adjusted fitness
    """
    
    pass
    
    
    
    

    
    