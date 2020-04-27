import numpy as np
import os
import random

from collections import deque
from operator import itemgetter,attrgetter

import magic_man_deck as deck
from magic_man_player import Player
from magic_train import load_pool
from magic_man import txt
number_of_players = 4
clear = lambda: os.system('cls')

class Human_Player:
    def __init__(self,id,init_score = 0):
    
        self.round_score = 0
        self.game_score  = 0
        self.id = id
        name_set = False
        while not name_set:
            name_choice = input("Enter name of player {}\n".format(self.id))
            if len(name_choice) < 3:
                print("Name must be at least three characters long")
            else:
                print("Player {} chose the name {}".format(self.id,name_choice))
                self.name = name_choice
                name_set = True
        self.cards = [] #an empty hand so to speak
        self.current_bid = None
        #how high the player is currently bidding


    def __str__(self):
        return self.name
        
    def __repr__(self):
        return "HumanPlayer " + self.name
        

    def clean_hand(self):
        self.cards = []
    
#___________________________________________________________________________________
#estimations

    def bid (self,round_idx,not_legal = None):
        self.cards.sort(key = attrgetter('color','value'),reverse = True)
        print("{}'s turn to bid! Here is your hand:".format(self.name))
        for card_idx in range(len(self.cards)):
            print(self.cards[card_idx])
        print("")
        bid_given = False
        while not bid_given:
            answer = input("How much do you bid {}?\n".format(self.name))
            try:
                answer_int = int(answer)
                if answer_int not in range(round_idx+1):
                    print("Your bid must be possible.")
                elif answer_int == not_legal:
                    print("you can't bid {} because the bids mustn't add up.".format(answer_int))
                else:
                    self.current_bid = answer_int
                    bid_given = True
            except ValueError:
                print("Bid must be a whole Number")
                
        return self.current_bid
    
    
    def play (self):
        idx_range = range(len(self.cards))
        card_played = False
        self.cards.sort(key = attrgetter('color','value'),reverse = True)
        while not card_played:
            print("{}'s turn to play a card! Here is your hand:".format(self.name))
            for card_idx in range(len(self.cards)):
                print("[ {} ]".format(card_idx if self.cards[card_idx].legal else "X"),self.cards[card_idx])
            play_answer = input("what card do you want to play?\n")
            try:
                card_idx = int(play_answer)
                if card_idx not in idx_range:
                    print("Index needs to be within range.")
                elif self.cards[card_idx].legal == False:
                    print("You're not allowed to play that card.")
                else:
                    card_of_choice = self.cards[card_idx]
                    print("You play {}".format(card_of_choice))
                    card_played = True
            except ValueError:
                print("Answer needs to be an index")
            

        played_card = card_of_choice
        self.cards.remove(played_card)
        return played_card

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
		
        random.shuffle(self.players)
        self.players = deque(self.players) #pick from a list of players
    
    def starting_player(self,starting_player):
        self.players.rotate( -self.players.index(starting_player) )
    
    def turn(self,turn_idx): #!!not round
        turn_cards = []

        #____________________________________________________
        #PLAYING
        print("\n\n\n        TURN {}\n_________________________________________________________\n        Trump is still {} \n".format(turn_idx+1,deck.colors[self.trump]))
        
        for player in self.players:
        
            

            if isinstance(player,Player):
                #____________________________________________________
                #progress estimations
                player.info_progress                     = np.array([[0] for i in range(160)],dtype = float)
                player.info_progress[0:(len(self.bids))] = [[bid[0] - (len(player.cards)/4)] for bid in self.bids] #how high all the players bid minus the average expected amount of suits they win
                player.info_progress[4:19]               = [[1] if _ == len(player.cards) else [0] for _ in range(self.max_rounds)]               #how many cards there are in his hand
                player.info_progress[19:23]              = [[1] if _ == self.players.index(player) else [0] for _ in range(number_of_players)]    #what place in the players the player has
                player.info_progress[23:29]				 = [[1] if _ == self.trump else [0] for _ in range(6)]        						     #which color is currently trump
                player.info_progress[29:30]				 = [player.round_score - player.current_bid]
                player.info_progress[30:40]              = player.current_progress
                
                    
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
                
                print("Player {} plays {}".format(player.name,turn_cards[-1]))

            elif isinstance(player, Human_Player):
                print("\n{} has bid {} and scored {} so far.".format(player.name,player.current_bid,player.round_score))
                #print("\nThese cards have been played:")
                #for card in turn_cards:
                #    print(card)
                print("\n")
                current_suit = deck.legal(turn_cards,player.cards,self.trump)
                turn_cards.append(player.play())

            
        deck.tv(turn_cards,turn_cards,self.trump,current_suit) #the turn values of the cards #turn value of the players cards    
        winner = self.players[[card.tv for card in turn_cards].index(max(card.tv for card in turn_cards))]        
        self.starting_player(winner)# --> rearanges the players of the player such that the winner is in the first position
        print("\n        {} won this turn!\n_________________________________________________________".format(winner.name))
        #____________________________________________________
        #SCORING
        
        winner.round_score += 1
        
  
    def round(self,round_idx,lastround = False): #!!not turn
        print("\n        ROUND {}\n____________________________________________________________________\n_________________________________________________________________\n".format(round_idx))
        print("{} starts this round".format(self.players[0]))

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
            print('\nTrump is {}\n'.format(deck.colors[trump_card.color]))
        elif lastround:
            self.trump = 5 #Narr --> kein Trumpf weil letzte Runde
                   
        #print("Note: this ought to be removed for the final version:")
        for player in self.players:
            player.round_score = 0
        #    print(player.name,player.cards)
        
        self.bids = []
        print("\n\n\n        BID PHASE\n_________________________________________________________ \n")
        for player in self.players:

            if isinstance(player,Player):
            #____________________________________________________
            #bid estimation BOTS
                player.info_bid                 = np.array([[0] for i in range(89)],dtype = float)
                player.info_bid.astype(float)
                if self.bids:
                    player.info_bid[0:len(self.bids)]= [[np.float32(bid[0] - (len(player.cards)/4))] for bid in self.bids]   #how high all the players bid minus the average expected amount of suits they win
                player.info_bid[4:19]         = [[1] if _ == len(player.cards) else [0] for _ in range(self.max_rounds)]                 #how many cards there are in his hand
                player.info_bid[19:23]        = [[1] if _ == self.players.index(player) else [0] for _ in range(number_of_players)]      #what place in the players the player has
                player.info_bid[23:29]		  = [[1] if _ == self.trump else [0] for _ in range(6)] #which color is currently trump

                player.info_bid[29:(29+60)]   = [ [1] if card in player.cards else [0] for card in deck.deck  ]
					
                self.bids.append([player.bid(self.current_round)])
                print('bid {} is '.format(player),player.current_bid,'\n')
            #____________________________________________________
            #bid estimation Humans
            elif isinstance(player,Human_Player):
                is_last_bid = (self.players.index(player) == (number_of_players-1))
                if not is_last_bid:
                    self.bids.append([player.bid(self.current_round,not_legal = None)])
                elif is_last_bid:
                    not_legal = int(abs(np.sum(self.bids)-self.current_round))
                    print("{} must not bid {}".format(player.name,not_legal))
                    self.bids.append([ player.bid(self.current_round, not_legal = not_legal) ])
                
            
        print("The players bids are: " , [int(_[0]) for _ in self.bids])
        if not int(self.current_round ) == 1:
            print("The total amount of bids is at {0}, {1} turns will be played.\n_________________________________________________________".format(int(np.sum(self.bids)),int(self.current_round )))
        else:
            print("The total amount of bids is at {0}, {1} turn will be played.\n_________________________________________________________".format(int(np.sum(self.bids)),int(self.current_round )))
        for turn in range(self.current_round):
            self.turn(turn)
			
        print("\n\n\n        SCORES \n_________________________________________________________________\n_________________________________________________________________")
        print("\n\n        This Round \n_________________________________________________________")
        for player in self.players:
            if player.current_bid == player.round_score:
                player.game_score += player.current_bid*10 + 20 #ten point for every turn won and 20 for guessing right
                
                print("Player {0} bid {1} and scored {2}. He recieves {3} points".format(player.name,
                                                                                           player.current_bid,
                                                                                           player.round_score,
                                                                                            (player.current_bid*10 + 20)))
                
            else:
                player.game_score -= abs(player.current_bid-player.round_score)*10 #ten points for every falsly claimed suit
                
                print("Player {0} bid {1} and scored {2}. He loses {3} points".format(player.name,
                                                                                       player.current_bid,
                                                                                       player.round_score,
                                                                                       (abs(player.current_bid - player.round_score) *10)))
		
        print("_________________________________________________________\n\n        Total \n_________________________________________________________")
        for player in self.players:
            print("Player {0}'s score is at {1}".format(player.name,player.game_score))
        print("_________________________________________________________")
        
        for player in self.players:
            player.clean_hand()
                #at this point all hands should be empty anyways
        pausevar = input(str('\n_________________________________________________________________\n____________________________________________________________________\nPress Any Button to continue.\n\n\n\n\n'))
        clear()



       
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
            game.players.rotate(game.players.index(game_pool_copy[i%4]))
            game.round(i)
        else:
            game.players.rotate(game.players.index(game_pool_copy[15%4]))
            game.round(i,lastround = True)
            
    winnerlist = list( game.players.copy() )
    winnerlist.sort(key = lambda x: x.game_score,reverse = True)
    
    
    for _ in range(len(winnerlist)):
        print("Player {0} takes Place {1} with {2} points.".format(
              winnerlist[_],_+1,winnerlist[_].game_score))
			  
			  
			  
			  
if __name__ == "__main__":
	print(txt)
	hmp_given = False
	while not hmp_given:             
		hmp_input = input("How many Human Players want to play?\n")

		try:
			hmp_int = int(hmp_input)
			if hmp_int > 4 or hmp_int < 1:
				print("Must be between 0 and 4!")
			else:
				if not hmp_int == 1:
					print("Game is played with {} Player(s) and {} Bots.".format(hmp_int,(4-hmp_int)))
				else:
					print("Game is played with {} Player and {} Bots.".format(hmp_int,(4-hmp_int)))

				hmp = hmp_int
				hmp_given = True
		except ValueError:
			print("Must be an Integer!")
				
				
				
	real_players = [Human_Player(_) for _ in range(hmp)]
	bot_players  = load_pool(4-hmp) 
	current_pool = []            
	for _ in real_players:
		current_pool.append(_)
	for _ in bot_players:
		current_pool.append(_)
		

	print("Game starts!")
	pausevar = input("\nPress any button to continue")
	clear()
	play_game(current_pool)       
