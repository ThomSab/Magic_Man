import numpy as np
import os
import json
import magic_man_deck as deck
import magic_man_utils as utils
from scipy.special import expit

base_path = os.getcwd()

#______________________________________________________________________________
#Player Class constructor
#initialy a four player bot is trained       

class Player:
    """
    Player class constructor
    ________
    Input:
    json datatype:
    
    [{"name"                  : "botname"}]
    
    [{
    
    "bid_node_genome"       :[{"INDEX":1,"TYPE":"SENSOR"},
                              {"INDEX":2,"TYPE":"HIDDEN"},
                              {"INDEX":3,"TYPE":"OUTPUT"}]
    "bid_connection_genome" :[{"IN": 1, "OUT": 2, "WEIGHT": 0.2, "ENABLED": 1, "INNOVATION": 1},
                              {"IN": 1, "OUT": 3, "WEIGHT": 0.3, "ENABLED": 0, "INNOVATION": 2},
                              {"IN": 2, "OUT": 3, "WEIGHT": -0.9, "ENABLED": 1, "INNOVATION": 3}]
    "play_node_genome"       :[{"INDEX":1,"TYPE":"SENSOR"},
                               {"INDEX":2,"TYPE":"HIDDEN"},
                               {"INDEX":3,"TYPE":"OUTPUT"}]
    "play_connection_genome" :[{"IN": 1, "OUT": 2, "WEIGHT": 0.5, "ENABLED": 1, "INNOVATION": 1},
                               {"IN": 1, "OUT": 3, "WEIGHT": 1.3, "ENABLED": 0, "INNOVATION": 2},
                               {"IN": 2, "OUT": 3, "WEIGHT": 0.1, "ENABLED": 1, "INNOVATION": 3}]
    "stm_node_genome"       :[{"INDEX":1,"TYPE":"SENSOR"},
                              {"INDEX":2,"TYPE":"HIDDEN"},
                              {"INDEX":3,"TYPE":"OUTPUT"}]
    "stm_connection_genome" :[{"IN": 1, "OUT": 2, "WEIGHT": 0.5, "ENABLED": 1, "INNOVATION": 1},
                              {"IN": 1, "OUT": 3, "WEIGHT": 0.4, "ENABLED": 0, "INNOVATION": 2},
                              {"IN": 2, "OUT": 3, "WEIGHT": 0.5, "ENABLED": 1, "INNOVATION": 3}]
    }]
    
    [{"score_data"        :[12,123,34,456,56,234,67,567,78,34,89,163,100]}]
    
    is loaded and then used to generate a neural net for bid, play, progress etc.
    The connections currently have no bias parameter but it can be added easily
    """
    def __init__(self,name,sigmoid_function=expit):
    
        self.round_score = 0
        self.game_score  = 0
        self.name = name
        self.cards = [] #an empty hand so to speak
        self.current_stm = [0 for _ in range(10)] #Initiating stm
        self.sigmoid = sigmoid_function
        
        if os.path.exists(base_path+'\Bots\{}'.format(self.name)):
            with open(base_path+'\Bots\{}\genome.json'.format(name)) as genome_file:
                genome = json.load(genome_file)
                
            bid_node_genome, bid_connection_genome  = genome["bid_node_genome"], genome["bid_connection_genome"]
            play_node_genome,play_connection_genome = genome["play_node_genome"],genome["play_connection_genome"]
            stm_node_genome, stm_connection_genome  = genome["stm_node_genome"], genome["stm_connection_genome"]

            self.bid_net  = self.Network(bid_node_genome, bid_connection_genome,net_sigmoid_function = self.sigmoid)
            self.play_net = self.Network(play_node_genome,play_connection_genome,net_sigmoid_function = self.sigmoid)
            self.stm_net  = self.Network(stm_node_genome, stm_connection_genome,net_sigmoid_function = self.sigmoid)

            print('{} loaded'.format(self.name))
            
        else:   
            print("ERRROR: Player {} Directory does not exist.".format(name))
            

            
        


    def __str__     (self):
        return self.name        
    def __repr__    (self):
        return self.name
    def clean_hand(self):
        self.cards = []  


    #______________________________________________________________________________
    #Output Calculation methods
    def bid (self,round_idx,last_player = False):
        activation = self.bid_net.activation()
        
        self.current_activation = ((utils.logit_bidding(activation[0])*round_idx)/4)
            #multiply by the number of card in hand
            #then divide by the amount of players 
            #to have a better starting point for the bots
        self.current_bid = np.round(self.current_activation)
        if last_player:
            if self.current_bid + np.sum([sensor_node.activation[0] + (round_idx/4) for sensor_node in self.bid_net.sensor_nodes[0:3]]) == round_idx:
            #sensor nodes 0:3 are how high every player has bid including self
            #if the desired bid is not possible because the bids would add up to the number of cards in all hands
                if self.current_activation - np.round(self.current_activation) > 0: #if bid value was rounded down
                    self.current_bid = self.current_bid + 1 #bc tencency is up
                elif self.current_bid == 0:
	                self.current_bid = self.current_bid + 1 #bc tendency is down but he cant go down any further
                else:
                    self.current_bid = self.current_bid -1 #bc tendency is down




        return self.current_bid
    
    def stm (self):#Short Term Memory
        self.current_stm = self.stm_net.activation()       
        return self.current_stm
       
    def play (self):
        activation = self.play_net.activation()
        
        hand_cards = np.array([ [1] if (card in self.cards and card.legal) else [0] for card in deck.deck ])
        card_activation = hand_cards*activation #sort out those that the player cant play
        bestcard_idx = np.where(card_activation == card_activation.max())[0][0]
        played_card = deck.deck[bestcard_idx]
        self.cards.remove(played_card)
        return played_card



    class Network:
        """
        Neural Network Class Constructor
        The Network Constructor initiates a Node Class instance for each gene in the node genome
        It then goes through the connection genome and determines the Local Input Nodes for each Node
        This is for performance reasons.
        If the LINs weren't predefined they'd have to be redetermined for every activation of the NN.
        Instead they are predefined for each node.
        
        ________
        Input:
        node_genome,connection_genome
        ________
        Output:
        Generates a NN
        """
        def __init__ (self,node_genome,connection_genome,net_sigmoid_function):
            self.nodes = [self.Node(node["INDEX"],node["TYPE"],net_sigmoid_function) for node in node_genome]

            #could also be a oneliner:
            for node in self.nodes:
                for connection in connection_genome:
                    if connection["OUT"] == node.index and connection["ENABLED"]:
                        node.lins.append({"node":self.nodes[connection["IN"]],"connection":connection})
            #up to here --> but this seems more intuitive

            self.hidden_nodes = [ node for node in self.nodes if node.node_type == "HIDDEN"]
            self.output_nodes = [ node for node in self.nodes if node.node_type == "OUTPUT"]
            self.sensor_nodes = [ node for node in self.nodes if node.node_type == "SENSOR"]

  
        def activation (self):
            """
            The NN is defined as a set of nodes and connections.
            Each node has a set of previous nodes which are either hidden or input nodes.
            Nodes are class instances.
            
            The NEAT algorithm includes recurrent connections but ill try to leave them out for simplicity.
            This might be difficult bc. recurrent connections can occur through the random mutation.
            The recurrent cycles can be of any size so it might be difficult to prevent them.
            
            HiddenNode1 --> ... --> HiddenNodeN --> HiddenNode1
            ______
            Input:
            Nodes, Connections, Input Node Activations, 
            sigmoid function is expit(x) = 1/(1+exp(-x)) by default
            ______
            Ouput:
            activation of output nodes
            """
            
            #clearing the non-sensor nodes
            for node in self.output_nodes + self.hidden_nodes:
                node.activation = None
            
            #calculating activations
            return [node.node_activation() for node in self.output_nodes] 


        def list_input(self,index_start,list_argument):
            for idx,activation in enumerate(list_argument):
                self.sensor_nodes[index_start+idx].activation = activation


   
        class Node:
            def __init__(self,index,node_type,node_sigmoid_function):
                self.index  = index
                self.node_type  = node_type  
                self.activation = None
                self.sigmoid = node_sigmoid_function
                #LINs --> Local Input Nodes
                #first all nodes are constructed through the node_genome
                #then the lins are determined through the connection_genome
                self.lins   = []
                
            def node_activation(self):
                """
                Activation calculation is recursive in a way
                The current node calls up other node's activation functions until
                either the activation of the node is already known
                or until an input node is reached.
                
                This has the neat (no pun intended) effect that redundant nodes are never calculated.
                
                ________
                Input:
                Sigmoid function for the neural net
                ________
                Output:
                The nodes activation
                """
                if self.activation is None:
                    #local_input_node or lin is a list of dictionarys [{"node":node,"connection":connection},...]
                    self.activation = self.sigmoid(sum([lin["connection"]["WEIGHT"]*lin["node"].node_activation() for lin in self.lins]))
                return self.activation
        
        
