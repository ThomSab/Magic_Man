import os
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import magic_man_utils as utils

def score_estim(width,bot_name):
    """
    ______
    Input:
        bot name
        width, the width of the confidence band around the estimate
    ______
    Output:
        Returns an estimate for the real mean score of the bot
        and an alpha value, the probability that the real mean score is outside of the confidence band around the estimate
        
    ______
        The real mean score is unknown since the game involves quite a bit of luck
        From personal experience and the games description I'd say that at least half of the
        outcome is determined by luck
        
        I assume the scores to be normally distributed around the mean.
        I can then estimate the probability of the real mean being within
        a set confidence band around the estimated mean
    """
    bot_score = utils.load_bot_score(bot_name)
    mean,std = np.mean(bot_score),np.std(bot_score)
    
    #std deviation of the mean is the sample mean over the root of n
    #the confidence depends then depends on the width entered
    alpha = stats.norm.cdf((width/2)*np.sqrt(len(bot_score))/std)
    
    return mean,alpha
    

def avg_score_converge(bot_name):
    """
    ______
    Input:
        Bot name
    ______
    Output:
        A plot of the bots average score over time.
    
    """
    bot_score = utils.load_bot_score(bot_name)
    plt.plot([np.mean(bot_score[:t+1]) for t in range(len(bot_score))],label = 'AVG over time')
    plt.axhline(np.mean(bot_score),color = 'r',label = 'Current AVG {}'.format(np.round(np.mean(bot_score),2)))
    plt.legend()
    plt.show()
    
def score_hist(bot_name):
    """
    ______
    Input:
        Bot name
    ______
    Output:
        A histogramm of the bots score.
    
    """
    bot_score = utils.load_bot_score(bot_name)
    plt.hist(bot_score,bins=90,range=(-400,500))
    plt.axvline(np.mean(bot_score),color='r',label='Current AVG {}'.format(np.round(np.mean(bot_score)),2))
    plt.legend()
    plt.show()
 

 
def bot_scores(width):
    """
    ______
    Input:
        Width for how close to reality the average score estimate should be
    ______
    Output:
        The name of the bot with the maximum average,
        the bots score mean estimate
        and the significance of the score mean estimate
    """ 
    bot_dir   = os.listdir(os.getcwd()+'\Bots')
    bot_names = [bot_name for bot_name in bot_dir if bot_name not in ['bid_innovation.json','play_innovation.json','stm_innovation.json'] ]
    
    score_tuples = [(score_estim(width,bot_name),bot_name) for bot_name in bot_names]
    
    return score_tuples
 

def maximum_score(width):
    score_tuples = bot_scores(width)
    score_tuples.sort(key = lambda score_tuple: score_tuple[0],reverse = True)
    return score_tuples[0]
    
    
    
    
    
    
    
    