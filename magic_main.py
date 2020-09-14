import random
import numpy as np

from collections import deque

import magic_man_deck  as deck
from magic_man_player  import Player

"""
Currently all activations are passed in lists
so its
node.activation = [1] instead of
node.activation = 1

--> ToDo
"""

number_of_players = 4

class Game:
    """
    The Game Class
    No Documentation
    ______
        Recent Features:
        True Trump:
            In the original game, a new trump is chosen for each new round
            While it is fun, this has no real effect on the game
        No True Trump:
            The game keeps a single trump - in this case red, for no reason but red beeing trump "0"
            This way it should be a lot easier for the bots to learn
            Otherwise they would have to be a lot more complex bc the cards do different things each round
    
    """
    def __init__(self,n_players,players,deck,true_trump=False):

        self.deck = deck
        self.n_players = n_players
        if (n_players < 3) or (n_players > 6):
            print('INPUT ERROR: Invalid amount of players.')
        self.players = players
        self.max_rounds = int(60/n_players)
        self.current_round = 1
        self.bids = []
        self.true_trump = true_trump
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
            player.stm_net.list_input(0,[bid[0] - (len(player.cards)/4) for bid in self.bids]) #how high all the players bid, minus the average expected amount of suits they win            
            player.stm_net.list_input(4,[1 if _ == len(player.cards) else 0 for _ in range(self.max_rounds)])   #how many cards there are in his hand
            player.stm_net.list_input(19,[1 if _ == self.players.index(player) else 0 for _ in range(number_of_players)])   #what place in the players order the player has
            player.stm_net.list_input(23,[1 if _ == self.trump else 0 for _ in range(6)])   #which color is currently trump
            """
            Which color is trump might be too complex for the net.
            It would have to connect a node from this one to all colors.
            E.g. if green is trump [Color Sensor Node] --> [Decision Making Nodes] --> [All green cards]
            However at the cost of one additional sensor node it is probably sensible to keep both of them in there.
            """
            player.stm_net.list_input(29,[player.round_score - player.current_bid]) #how many suits the player has-how many he bid (if neg then he has too many
            player.stm_net.list_input(30,player.current_stm)    #current short term memory information block
			
            """
            Does the bot understand which color is currently trump?
            Instead of telling the bot that the color is [red,green,yellow,blue,fool,magic man],
            one location in the information block should be reserved for the trump color.
            The rest of the information block is then reserved for the other three colors.
            Since there no difference in between the other colors their order doesn't matter
            This would be possible by sorting the deck as the trump is determined for the round
            st. the trump cards are always in the same place.

            The problem here is that in the case of the fool, there is no trump.
            The net could possibly solve this problem by knowing it has no trump cards and whether a color is trump (see above)
            """
                
            player.stm_net.list_input(40,[ 1 if card in turn_cards   else 0 for card in deck.deck]) #which cards have been played
            player.stm_net.list_input((40+60),[ 1 if card in player.cards else 0 for card in deck.deck])#cards in hand

            player.stm()
                
            #print('progress {} is '.format(player),player.current_progress[0][0], '\n')

            #____________________________________________________
            #card playing
            player.play_net.list_input(0,[bid [0] - (len(player.cards)/4) for bid in self.bids]) #how high all the players bid minus the average expected amount of suits they win
            player.play_net.list_input(4,player.current_stm) #current short term memory
            player.play_net.list_input(14,[1 if _ == len(player.cards) else 0 for _ in range(self.max_rounds)])      #how many cards there are in his hand
            player.play_net.list_input(29,[1 if _ == self.players.index(player) else 0 for _ in range(number_of_players)])   #what place in the players the player has
            player.play_net.list_input(33,[1 if _ == self.trump else 0 for _ in range(6)]) #which color is currently trump
            player.play_net.list_input(39,[player.round_score - player.current_bid]) #current bid
         
            player.play_net.list_input(40,[ 1 if card in turn_cards   else 0 for card in deck.deck ]) # which cards have been played
            player.play_net.list_input((40+60),[ 1 if card in player.cards else 0 for card in deck.deck ] ) #which cards are in the players hand  
            
            current_suit = deck.legal(turn_cards,player.cards,self.trump)
            turn_cards.append(player.play())
            
            #print("Player {} plays {}".format(player.name,turn_cards[-1]))
            
        deck.tv(turn_cards,turn_cards,self.trump,current_suit) #turn value of the players cards    
        winner = self.players[[card.tv for card in turn_cards].index(max(card.tv for card in turn_cards))]        
        self.starting_player(winner)# --> rearanges the players of the player such that the winner is in the first position
        #print("{} won this turn!".format(winner.name))
        #____________________________________________________
        #SCORING
        
        winner.round_score += 1 #winner of the suit
        
  
    def round(self,round_idx,lastround = False): #!!not turn
        #print('Runde {}'.format(round))
        self.current_round = round_idx
        random.shuffle(self.deck) 
        round_deck = self.deck.copy()
        
        for _ in range(self.current_round):
            for player in self.players:
                player.cards.append(round_deck.pop(-1)) 
                #pop not only removes the item at index but also returns it
        
        if self.true_trump:
            if not lastround:
                trump_card = round_deck.pop(-1)        
                self.trump = trump_card.color  

            elif lastround:
                self.trump = 5 #Narr --> kein Trumpf weil letzte Runde
        elif not self.true_trump:
            self.trump = 0 #trump is red every time so the bots have a better time learning
            
        #print('Trump is {}'.format(deck.colors[self.trump]))
           
        for player in self.players:
            player.round_score = 0
         #   print(player.name,player.cards)
        
        self.bids = []
        
        for player in self.players:

            #____________________________________________________
            #bid estimation BOTS
            player.bid_net.list_input(0,[0,0,0,0]) #s.t. bids that are not yet given become 0 (the average bid height)
            if self.bids:
                player.bid_net.list_input(0,[bid[0] - (len(player.cards)/4) for bid in self.bids])  #how high all the players bid minus the average expected amount of suits they win
            player.bid_net.list_input(4,[1 if _ == len(player.cards) else 0 for _ in range(self.max_rounds)])                 #how many cards there are in his hand
            player.bid_net.list_input(19,[1 if _ == self.players.index(player) else 0 for _ in range(number_of_players)])      #what place in the players the player has
            player.bid_net.list_input(23,[1 if _ == self.trump else 0 for _ in range(6)]) #which color is currently trump

            player.bid_net.list_input(29,[ 1 if card in player.cards else 0 for card in deck.deck  ])# cards in hand
            
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



