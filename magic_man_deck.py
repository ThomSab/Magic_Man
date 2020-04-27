import numpy as np


#______________________________________________________________________________________
#deck constructor

colors = {0 : 'Red', 1 : 'Yellow', 2 : 'Blue', 3 : 'Green', 4 : 'Magic Man', 5 : 'Fool'}

class Card:
    def __init__(self,color,value): #color input is integer between 0 and 3
        self.color = color
        self.value = value
        self.tv = 'N/A' # Turn Value --> the value of the card in context of trump and suit
        self.rv = 'N/A' # Round Value --> the value of the card in context of trump
        self.legal = True
        
        if self.value == 0:
            self.name = '{} Fool'.format(colors[self.color])
            self.color = 5
        elif self.value == 14:
            self.name = '{} Magic Man'.format(colors[self.color])
            self.color = 4
        else:
            self.name = '{0} {1}'.format(colors[self.color],self.value)
    
    def __str__ (self):
        return self.name
    
    def __repr__(self):
        return self.name 
        
deck = [Card(j,i) for j in range(4) for i in range(15)]

#______________________________________________________________________________________
#methods

def rv(cards,trump): #round value --> what the cards are worth at the start of the round independend of suit
    for card in cards:
        if   card.value == 14:
            card.rv = 58.25
            
        elif card.value == 0:
            card.rv = 2.5
            
        elif card.color == trump:
            card.rv = 43 + card.value
            
        elif card.color != trump and card.value not in (0,14):
            card.rv = 3*card.value + 3
           
        else:
            return 'ERROR invalid card turn value'
    else:
        card.tv = 'N/A' #to be disregarded

    


def tv (played,cards,trump,current_suit): #turn value --> value is the index in the winning order of cards --> value of the first magic man should be the ceiling and the last jester is the floor
    
    if current_suit != None:
        suit = current_suit #suit --> welche farbe angespielt wurde
    
    for card in cards:
        if card.legal:
            if   card.value == 14:
                card.tv = 60 - played.index(card)
                
            elif card.value == 0:
                card.tv = 4  - played.index(card)
                
            elif card.color == trump:
                card.tv = 43 + card.value
                
            elif len(played) == 0 or card.color == current_suit:
                card.tv = 30 + card.value
            
            elif card.color != current_suit and card.color != trump:
                card.tv = 2*card.value + 3.5
                
            else:
                return 'ERROR invalid card turn value'
        else:
            card.tv = 'N/A' #to be disregarded


 
def legal (played,hand,trump): #legal to play in this turn --> wich cards are allowed and which aren't

    for card in hand:
        card.legal = True

    suit = None
    can_serve_suit = False

    foolean = True #bool for "there have only been fools played so far" --> this is True when there havent been played any cards yet
    count   = 0    #how many fools have been played
    while foolean:
        if len(played) > count and count < 4:
            if played[count].color != 5: #something else that fool or magic man is played
                suit = played[count].color #suit --> welche farbe angespielt wurde
                foolean = False
            elif played[count].color == 4: #no suit when a wizard is played before any other card
                suit = None
                foolean = False
            elif played[count].color == 5: #a fool is played
                count += 1
        else:#the suit is empty
            foolean = False#bool is set to false to end the loop
            

    if suit in [0,1,2,3] and suit not in [4,5]:
        for card in hand:
            if card.color == suit:
                can_serve_suit = True
                
        if can_serve_suit:
            for card in hand:
                if card.color != suit and card.color not in [4,5]: #magic men and jesters are always legal
                    card.legal = False
	
    return suit

def net_arr_trans(list_arg,length):#network array transform
    lis = [0 for i in range(length)]
    lis[0:len(list_arg)] = [card.tv for card in list_arg]
    return np.array([[item] for item in lis])
    #transforms the turncards into a format
    #that is feedable into the network


deck.sort(key = lambda x: x.value)








