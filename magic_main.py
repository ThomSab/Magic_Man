import random
import numpy as np

from collections import deque

import magic_man_deck  as deck
from magic_man_player  import Player


number_of_players = 4

class Game:
    def __init__(self,n_players,players,deck):
        self.deck = deck
        self.n_players = n_players
        if (n_players < 3) or (n_players > 6):
            print('INPUT ERROR: Invalid amount of players.')
        self.players = players
        self.max_rounds = int(60/n_players)
        self.current_round = 1
        self.bids = []
        self.trump = 6 #initial value only --> the trump indices only go up to 5
        #score board
        random.shuffle(self.players)
        self.players = deque(self.players) #pick from a list of players
    
    def starting_player(self,starting_player):
        self.players.rotate(  -self.players.index(starting_player) )
    
    def turn(self): #!!not round
        turn_cards = []

        #____________________________________________________
        #PLAYING
        
        for player in self.players:
        
            

            
            #____________________________________________________
            #progress estimations
            player.info_progress                     = np.array([[0] for i in range(160)],dtype = float)
            player.info_progress[0:(len(self.bids))] = [[bid[0] - (len(player.cards)/4)] for bid in self.bids] #how high all the players bid minus the average expected amount of suits they win
            player.info_progress[4:19]               = [[1] if _ == len(player.cards) else [0] for _ in range(self.max_rounds)]               #how many cards there are in his hand
            player.info_progress[19:23]              = [[1] if _ == self.players.index(player) else [0] for _ in range(number_of_players)]    #what place in the players the player has
            player.info_progress[23:29]				 = [[1] if _ == self.trump else [0] for _ in range(6)]        						     #which color is currently trump
            player.info_progress[29:30]				 = [player.round_score - player.current_bid]
            player.info_progress[30:40]               = player.current_progress
			

                
            player.info_progress   [40:(40+60)]           = [ [1] if card in turn_cards   else [0] for card in deck.deck]
            player.info_progress   [(40+60):(40+60+60)]   = [ [1] if card in player.cards else [0] for card in deck.deck] 

            player.progress()
                
            #print('progress {} is '.format(player),player.current_progress[0][0], '\n')

            #____________________________________________________
            #card playing
            player.info_cards                     = np.array([[0] for i in range(160)],dtype = float)
            player.info_cards[0:(len(self.bids))] = [[bid[0] - (len(player.cards)/4)] for bid in self.bids] #how high all the players bid minus the average expected amount of suits they win
            player.info_cards[4:14]                  = player.current_progress
            player.info_cards[14:29]               = [[1] if _ == len(player.cards) else [0] for _ in range(self.max_rounds)]         #how many cards there are in his hand
            player.info_cards[29:33]              = [[1] if _ == self.players.index(player) else [0] for _ in range(number_of_players)]   #what place in the players the player has
            player.info_cards[33:39]			  = [[1] if _ == self.trump else [0] for _ in range(6)] #which color is currently trump
            player.info_cards[39:40]			  = [player.round_score - player.current_bid]
         
            player.info_cards   [40:(40+60)]           = [ [1] if card in turn_cards   else [0] for card in deck.deck ]
            player.info_cards   [(40+60):(40+60+60)]   = [ [1] if card in player.cards else [0] for card in deck.deck ]      
            
            current_suit = deck.legal(turn_cards,player.cards,self.trump)
            turn_cards.append(player.play())
            
            #print("Player {} plays {}".format(player.name,turn_cards[-1]))
            
        deck.tv(turn_cards,turn_cards,self.trump,current_suit) #the turn values of the cards #turn value of the players cards    
        winner = self.players[[card.tv for card in turn_cards].index(max(card.tv for card in turn_cards))]        
        self.starting_player(winner)# --> rearanges the players of the player such that the winner is in the first position
        #print("{} won this turn!".format(winner.name))
        #____________________________________________________
        #SCORING
        
        winner.round_score += 1
        
  
    def round(self,round_idx,lastround = False): #!!not turn
        #print('Runde {}'.format(round))
        self.current_round = round_idx
        random.shuffle(self.deck) 
        round_deck = self.deck.copy()
        
        for _ in range(self.current_round):
            for player in self.players:
                player.cards.append(round_deck.pop(-1)) 
                #pop not only removes the item at index but also returns it
                
        if not lastround:
            trump_card = round_deck.pop(-1)        
            self.trump = trump_card.color  
            #print('Trumpf ist {}'.format(deck.colors[trump_card.color]))
        elif lastround:
            self.trump = 5 #Narr --> kein Trumpf weil letzte Runde
       
        for player in self.players:
            player.round_score = 0
         #   print(player.name,player.cards)
        
        self.bids = []
        
        for player in self.players:

            #____________________________________________________
            #bid estimation BOTS
            player.info_bid                 = np.array([[0] for i in range(89)],dtype = float)
            if self.bids:
                player.info_bid[0:len(self.bids)]= [[bid[0] - (len(player.cards)/4)] for bid in self.bids]  #how high all the players bid minus the average expected amount of suits they win
            player.info_bid[4:19]             = [[1] if _ == len(player.cards) else [0] for _ in range(self.max_rounds)]                 #how many cards there are in his hand
            player.info_bid[19:23]            = [[1] if _ == self.players.index(player) else [0] for _ in range(number_of_players)]      #what place in the players the player has
            player.info_bid[23:29]			  = [[1] if _ == self.trump else [0] for _ in range(6)] #which color is currently trump

            player.info_bid[29:(29+60)]   = [ [1] if card in player.cards else [0] for card in deck.deck  ]
            
            last_player_bool = (True if self.players.index(player) ==  3 else False)
            self.bids.append([player.bid(self.current_round,last_player = last_player_bool)])
            #print('bid {} is '.format(player),player.current_bid,'\n')

            
        for turn in range(self.current_round):
            self.turn()
        
        for player in self.players:
            if player.current_bid == player.round_score:
                player.game_score += player.current_bid*10 + 20 #ten point for every turn won and 20 for guessing right
                """
                print("Player {0} bid {1} and scored {2}. He recieves {3} points".format(player.name,
                                                                                           player.current_bid,
                                                                                           player.round_score,
                                                                                            (player.current_bid*10 + 20)))
                """
            else:
                player.game_score -= abs(player.current_bid-player.round_score)*10 #ten points for every falsly claimed suit
                """
                print("Player {0} bid {1} and scored {2}. He loses {3} points".format(player.name,
                                                                                       player.current_bid,
                                                                                       player.round_score,
                                                                                       (abs(player.current_bid - player.round_score) *10)))
                """
        #for player in self.players:
         #   print("Player {0}'s score is at {1}".format(player.name,player.game_score))
        
        for player in self.players:
            player.clean_hand()
                #at this point all hands should be empty anyways



