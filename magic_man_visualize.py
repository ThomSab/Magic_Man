import numpy as np
import matplotlib.pyplot as plt
import math
import os
import scipy.stats
from magic_man_player import Player 
from base_path import base_path,lr,bot_dir,dirlist
from magic_man_stats import mov_avg
from magic_train import refresh_max_avg_score, load_avg_scores



def intermediate_rate(intermediate,color = 'r'):
    avgs      = [float(_[0]) for _ in avgscores][-intermediate:]
    ids      = [_ for _ in range(len(avgscores))][-intermediate:]
    slope,intercept,r,p,std = scipy.stats.linregress(ids,avgs)
    plt.plot(ids[-intermediate:],[ int(x)*slope + intercept for x in ids],color)
    print('The learning rate for the last {} Bots is {}'.format(intermediate,slope))


 
    
def scatter_pool(bot_dir ,max_avg):
    avgscores = load_avg_scores(bot_dir = bot_dir)
    avgs    = [float(_[0]) for _ in avgscores]
    ids     = [_ for _ in range(len(avgscores))]
    slope,intercept,r,p,std = scipy.stats.linregress(ids,avgs)
    print('The learning rate over all Bots is {}'.format(slope))

    plt.scatter(ids,avgs,marker = ",",s=1,alpha=0.3)
    #intermediate_rate(250,color = '--')
    #intermediate_rate(500)
    #intermediate_rate(1000,color = '#99DC58')
    plt.show()

def brain(bot_dir,max_avg):
    magic_man = Player(max_avg[1],bot_dir = bot_dir)
    for _ in range(len(magic_man.play_net.weights)):
        plt.imshow(magic_man.play_net.weights[_])
        plt.show()     
    for _ in range(len(magic_man.play_net.biases)):
        ax = plt.subplot(int(str(2*len(magic_man.play_net.biases))+str(1)+str(_ + 1)))
        plt.imshow(magic_man.play_net.biases[_].T)
    plt.tight_layout()
    plt.show()

def real_progress(bot_dir,max_avg):
    learning_rate = bot_dir.split('_')[-1]
    try:
        with np.load(base_path + r'\real_max_progress_{}.npz'.format(learning_rate),allow_pickle = True) as progress:
            progress = list(progress['progress'])
            slope,intercept,r,p,std = scipy.stats.linregress(range(len(progress))[1:],progress[1:])
            print('The real overall progress rate is {}.'.format(slope))
            plt.plot([ int(x)*slope + intercept for x in range(len(progress))],'k--')
            plt.plot(progress,color = 'k')
            plt.show()
    except:
        print("Real Progress Failed.")
    
def progress(bot_dir,max_avg):
    learning_rate = bot_dir.split('_')[-1]
    with np.load(base_path + r'\max_progress_{}.npz'.format(learning_rate),allow_pickle = True) as progress:
        progress = list(progress['progress'])
        slope,intercept,r,p,std = scipy.stats.linregress(range(len(progress))[1:],progress[1:])
        print('The overall progress rate is {}.'.format(slope))
        plt.plot([ int(x)*slope + intercept for x in range(len(progress))],'k--')
        plt.plot(progress,color = 'k')
        plt.show()    
    
def hist(bot_dir,max_avg):
    with np.load(base_path + bot_dir + r'\{}\stat_arr.npz'.format(max_avg[1]),allow_pickle = True) as stats:
        plt.hist(stats['stats'],bins = 50)
        plt.show()
    
	



if __name__ == "__main__":

	local_bot_dir = bot_dir
	avgscores = load_avg_scores(bot_dir = local_bot_dir)
	avgscores.sort(key = lambda x: float(x[1]))
	
	statistics = ["Histogram", "Pool Scatterplot", "Maximum Average Progress", "Maximum Average right before replication Progress", "Bot Brain"]
	fndict = {"Histogram":hist, "Pool Scatterplot":scatter_pool, "Maximum Average Progress":progress, "Maximum Average right before replication Progress":real_progress, "Bot Brain":brain}
	lr_given = True
	stat_given = False
	exit_condition = False
	while not exit_condition:
	
		while not lr_given:
			print("Which Pool do you want to access?")
			for pool in dirlist:
				print("[",dirlist.index(pool),"]", pool)
			lr_answer  = input("\n")
			try:
				lr_idx = int(lr_answer)
				if lr_idx > len(dirlist) or lr_idx < 0:
					print("DIR DOES NOT EXIST")
				else:
					lr = dirlist[lr_idx].split('_')[-1]
					local_bot_dir = '\Bots_{}'.format(lr)
					lr_given = True
			except ValueError:
				print("Answer must be one of the indexes")
		
		while lr_given:
			max_avg = refresh_max_avg_score(bot_directory = local_bot_dir)
			print('The Learning Rate is {}'.format(lr))
			stat_given = False
			
			while not stat_given:
				print("\nWhich statistic would you like to see?")
				for _ in range(len(statistics)):
					print("[",_,"]  ",statistics[_])
				print("[",len(statistics),"]  ","Access different learning Rate")
				print("[",len(statistics)+1,"]  ","Exit")
				stat_answer  = input("\n")
				try:
					stat_idx = int(stat_answer)
					if stat_idx == (len(statistics)):
						print("Changing the learning rate.")
						stat_given = True
						lr_given = False
					elif stat_idx == (len(statistics)+1):
						exit_condition 	= True
						lr_given 		= False
						stat_given 	= True
					elif stat_idx > len(statistics) or stat_idx < 0:
							print("STATISTIC DOES NOT EXIST")
					else:
						stat = statistics[stat_idx]
						stat_given = True
				except ValueError:
					print("Answer must be one of the indexes")
				
			if stat_given and lr_given:
				print(stat)
				fndict[stat](bot_dir=local_bot_dir,max_avg=max_avg)
				stat_given = False
			
		





















