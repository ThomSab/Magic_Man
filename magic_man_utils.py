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

def save (name,directory=cwd,genome=False,score_data=False,generate=False):
    """
    ______
    Input:
        Score_data, Location, Bot-Name
        Optional specification for json or .npz(Numpy Arrays)
            [Json is up to 25 times faster than pickle according to 
            https://konstantin.blog/2010/pickle-vs-json-which-is-faster/ ]
    ______
    Output:
        Failiure if saving
        Nothing on Success
    """
    if generate and not os.path.exists(directory + r'\{}'.format(name)):
        os.mkdir(directory + r'\{}'.format(name))
    
    if genome:
        try:
            with open(directory + r'\{}\genome.json'.format(name),'w')as safe_file:
                json.dump(genome,safe_file)
        except Exception as exception:
            print("Saving the genome failed: {}".format(exception))
                  
    if score_data:
        try:
            with open(directory + r'\{}\score_data.json'.format(name),'w')as safe_file:
                json.dump(score_data,safe_file)              
        except Exception as exception:
            print("Saving the score_data failed: {}".format(exception))
            




        
        
    
      
    
    
    