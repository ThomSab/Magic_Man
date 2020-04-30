import numpy as np
import os
import magic_man_deck as deck
from scipy.special import expit
from base_path import base_path,bot_dir

def logit_bidding (p):
	bid_factor = 0.3*np.log(p/(1-p)) + 1
	if bid_factor < 0 :
		return [[0]]
	elif bid_factor > 4:
		return [[4]]
	else:
		return bid_factor

#______________________________________________________________________________
#Player Class constructor
#initialy a four player bot is tnorained
class Network:
    def __init__ (self,player,load,arg,layers,init_sigma=1): #layers is the design of the network e.g. [21,30,30,1] --> [input,hidden_1,hidden_2,output]

        if not load:
            layers = layers.copy()
        
            self.weights    = np.array([ np.random.normal(0,init_sigma,(layers[i+1],layers[i])) for i in range(len(layers)-1) ])
            self.biases     = np.array([ np.random.normal(0,init_sigma,(layers[i+1],1))         for i in range(len(layers)-1) ])
            
            np.savez(player.path + r'\{}.npz'.format(arg),weights = self.weights, biases = self.biases)
        else:
            with np.load(player.path + r'\{}.npz'.format(arg),allow_pickle = True) as file:
                self.weights , self.biases = file['weights'], file['biases']
            



    def __new__(cls,player,load,arg,layers,init_sigma):
    
        if isinstance(player,Player):
            return super(Network, cls).__new__(cls)
        else:
            raise TypeError('Player argument expected, {} was given.'.format(str(type(layers))))
    
    
        if isinstance(layers,list):
            return super(Network, cls).__new__(cls)
        else:
            raise TypeError('List argument expected, {} was given.'.format(str(type(layers))))
            
            

class Player:
    def __init__(self,id,bot_dir=bot_dir,init_score = 0,init_sigma = 1):
    
        self.round_score = 0
        self.game_score  = 0
        self.name = 'Player_{}'.format(id)
        self.cards = [] #an empty hand so to speak
        self.id = id
        self.player_dir = base_path+ bot_dir + r'\{}'.format(self.id)
        self.path = self.player_dir + '\{}'.format(self.name)
        self.init_sigma = init_sigma
        
        if not os.path.exists(self.player_dir):
            os.mkdir(self.player_dir)

        if not os.path.exists(self.path):
            os.mkdir(self.path)
            self.bid_net        = Network(self,load = False,arg = 'bid',        layers = [89,59,1]  ,init_sigma=self.init_sigma) #network architecture changed from [90,30,30,1]
            self.progress_net   = Network(self,load = False,arg = 'progress',   layers = [160,59,10],init_sigma=self.init_sigma)
            self.play_net       = Network(self,load = False,arg = 'play',       layers = [160,59,60],init_sigma=self.init_sigma)
            
            np.savez(self.player_dir + r'\stat_arr.npz',stats = np.array([init_score for _ in range(100)]))
            np.savez(self.player_dir + r'\stat_arr_avg.npz',avgscore = np.array([init_score]))
            
            print('{} created'.format(self.name))
            
        else:
            self.bid_net =  Network(self,load = True,arg = 'bid',  layers = [], init_sigma = None) #if load is True then the rest doesnt matter
            self.progress_net =  Network(self,load = True,arg = 'progress',  layers = [], init_sigma = None)
            self.play_net = Network(self,load = True,arg = 'play', layers = [], init_sigma = None)
            print('{} loaded'.format(self.name))

            
        
        #______________________________________________________________________________
        #first try is blackbox attempt beacuse its "easier" to code
        #each player ESTIMATES:
        
        
        
        #how many turns to claim        
        self.info_bid = np.array([[0] for i in range(89)],dtype = float) #--> 21 items of information
        #infoblocks for how high to bid
        self.current_bid = None
        #how high the player is currently bidding
        
        #wether he wants attempt to win the suit
        self.info_progress = np.array([[0] for i in range(150)],dtype = float)
        #infoblock for wether to attempt to win the suit
        self.current_progress = np.array([[0] for i in range(10)],dtype = float)
        #how much the player is expecting a turn to win
        
        #which card to play
        self.info_cards = np.array([[0] for i in range(151)],dtype = float)
        #infoblocks for which cards to play


    def __str__(self):
        return self.name
        
    def __repr__(self):
        return self.name
        

    def clean_hand(self):
        self.cards = []
    
#______________________________________________________________________________
#estimations

    def bid (self,round_idx,last_player = False): #equivalent to a feed forward function of a neunet
        activation = self.info_bid
        for layer in range(len(self.bid_net.weights)):
            activation = expit(np.dot(self.bid_net.weights[layer], activation) + self.bid_net.biases[layer])
            #_______________
            #for diagnostics
            #print(activation,'activation \n',self.bid_net.weights[layer],'weights \n',self.bid_net.biases[layer],'bias \n')
        
        self.current_activation = ((logit_bidding(activation)[0][0]*round_idx)/4)
            #multiply by the number of card in hand
            #then divide by the amount of players 
            #to have a better starting point for the bots
        self.current_bid = np.round(self.current_activation)
        if last_player:
            if self.current_bid + np.sum([_ + (round_idx/4) for _ in self.info_bid[0:3]]) == round_idx: 
            #if the desired bid is not possible because the bids would add up to the number of cards in all hands
                if self.current_activation - np.round(self.current_activation) > 0: #if bid value was rounded down
                    self.current_bid = self.current_bid + 1 #bc tencency is up
                elif self.current_bid == 0:
	                self.current_bid = self.current_bid + 1 #bc tendency is down but he cant go down any further
                else:
                    self.current_bid = self.current_bid -1 #bc tendency is down




        return self.current_bid
    
    def progress (self):
        activation = self.info_progress
        for layer in range(len(self.progress_net.weights)):
            activation = expit(np.dot(self.progress_net.weights[layer], activation) + self.progress_net.biases[layer])
        self.current_progress = activation
        return activation
       
    def play (self):
        activation = self.info_cards
        for layer in range(len(self.play_net.weights)):
            activation = expit(np.dot(self.play_net.weights[layer], activation) + self.play_net.biases[layer])
        
        hand_cards = np.array([ [1] if (card in self.cards and card.legal) else [0] for card in deck.deck ])
        card_activation = hand_cards*activation #sort out those that the player cant play
        bestcard_idx = np.where(card_activation == card_activation.max())[0][0]
        played_card = deck.deck[bestcard_idx]
        self.cards.remove(played_card)
        return played_card
 

     
