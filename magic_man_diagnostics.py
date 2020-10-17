import os
import json
import sys
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import networkx as nx 
import magic_man_utils as utils

def score_estim(width,bot_name):
    """
    ______
    Input:
        bot name
        width, the width of the confidence band around the estimate to each side
    ______
    Output:
        Returns an estimate for the real mean score of the bot
        and an alpha value, the probability that the score estimate is off by more than width
        
    ______
        The real mean score is unknown since the game involves quite a bit of luck
        From personal experience and the games description I'd say that at least half of the
        outcome is determined by luck
        
        I assume the scores to be normally distributed around the mean.
        I can then estimate the probability of the real mean being within
        a set confidence band around the estimated mean
        
    """
    bot_score = utils.load_bot_score(bot_name)
    n=len(bot_score)
    mean,std = np.mean(bot_score),np.std(bot_score)
    
    
    #std deviation of the mean is the sample mean over the root of n
    #the confidence depends then depends on the width entered
    alpha = 1 - stats.norm.cdf((width)*np.sqrt(n)/std)
    
    if np.isnan(mean) or alpha==0 or n<5:
        mean,alpha = (-100,0.5)
        
    return mean,alpha
    
def conf_band_width(alpha,bot_name):
    """
    ______
    Input:
        bot name
        a significance value alpha
    ______
    Output:
        Returns the width of the confidence band to one side of the mean
    ______
        
    """  
    bot_score = utils.load_bot_score(bot_name)
    std = np.std(bot_score)
    
    down,up  = stats.norm.interval(alpha,loc=0,scale=std)
    
    return up

def score_converge(bot_name):
    """
    ______
    Input:
        Bot name
    ______
    Output:
        A plot of the bots average score over time.
    
    """
    bot_score = utils.load_bot_score(bot_name)
    plt.title(f"{bot_name} Score convergence")
    plt.xlabel("Games Played")
    plt.ylabel("Average Score")
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
    plt.title(label = f"{bot_name} Score histogram")
    plt.xlabel("Score")
    plt.hist(bot_score,bins=120,range=(-600,600))
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
    bot_names = utils.load_bot_names()
    score_tuples = [(score_estim(width,bot_name),bot_name) for bot_name in bot_names]
    
    return score_tuples
 

def gen_max_score(width,alpha):
    """
    one score tuple is ( score_estim or (mean,alpha) , bot name)
    
    Output:
        max bot score, bot name
    """
    score_tuples = bot_scores(width)
    assert not (insignificant_scores := ([tuple[1] for tuple in score_tuples if tuple[0][1] > alpha])), f"Not all bot scores are estimated to a significant level: {insignificant_scores}"

    score_tuples.sort(key = lambda score_tuple: score_tuple[0][0],reverse = True)
    return score_tuples[0][0][0],score_tuples[0][1] #this is garbage code and can be done better
    
def gen_avg_score(width,alpha):
    score_tuples = bot_scores(width)
    assert not (insignificant_scores := ([tuple[1] for tuple in score_tuples if tuple[0][1] > alpha])), f"Not all bot scores are estimated to a significant level: {insignificant_scores}"
    
    return sum([tuple[0][0] for tuple in score_tuples])/len(score_tuples)


def hidden_node_grade(self_node,in_edges_dict,grade_dict,hidden):
    #where to place the hidden node in the graph plot
    
    if not grade_dict[self_node] == None:
        return grade_dict[self_node]
    
    #is the input node is on the end of an edge from another hidden node?
    hidden_in_nodes=[node for node in [item[0] for item in in_edges_dict[self_node]] if node in list(hidden)]
    if hidden_in_nodes:
        highest_input_grade = max([hidden_node_grade(hidden_in_node,in_edges_dict,grade_dict,hidden) for hidden_in_node in hidden_in_nodes])
        self_grade=highest_input_grade+1
    else:
        self_grade = 0

    grade_dict[self_node]=self_grade
    return self_grade

def node_positions(Graph,net_type,scale=1,center=None,aspect_ratio=4 / 3):

    G, center = nx.drawing.layout._process_params(Graph, center=center, dim=2)
    nodes = set(Graph.nodes)
    height = 1
    width = aspect_ratio * height
    offset = (width / 2, height / 2)

    if net_type == 'play':
        left = list(range(utils.N_play_sensors))
        right = list(range(utils.N_play_sensors,utils.N_play_sensors+utils.N_play_outputs))        
    if net_type == 'bid':
        left = list(range(utils.N_bid_sensors))
        right = list(range(utils.N_bid_sensors,utils.N_bid_sensors+utils.N_bid_outputs))
    if net_type == 'stm':
        left = list(range(utils.N_stm_sensors))
        right = list(range(utils.N_stm_sensors,utils.N_stm_sensors+utils.N_stm_outputs))

    hidden = nodes - set(left) - set(right)

    if hidden:
        in_edges_dict={node:G.in_edges(node)for node in hidden}
        grade_dict={node:None for node in hidden}
        
        for node in hidden:
            hidden_node_grade(node,in_edges_dict,grade_dict,hidden)
        maximum_grade=max([grade for node,grade in grade_dict.items()])

        

    left_xs   = np.repeat(-width, len(left))    
    hidden_list=list(hidden)
    hidden_list.sort()
    hidden_xs = [-0.5*width + 1/(1+maximum_grade)*width*grade_dict[node] for node in hidden_list]

    right_xs  = np.repeat(width, len(right))

    left_ys   = np.linspace(0, height, len(left))
    hidden_ys = np.linspace(0, height, len(hidden))
    right_ys  = np.linspace(0, height, len(right))

    left_pos   = np.column_stack([left_xs, left_ys])
    hidden_pos = np.column_stack([hidden_xs, hidden_ys])
    right_pos  = np.column_stack([right_xs, right_ys])

    
    pos = np.concatenate([left_pos, right_pos, hidden_pos])
    pos = nx.drawing.layout.rescale_layout(pos, scale=scale) + center

    
    
    pos = dict(zip(nodes, pos))
    return pos

 
def graph(bot_name,net_type,added_only=True):
    """
    TODO
    https://www.geeksforgeeks.org/python-visualize-graphs-generated-in-networkx-using-matplotlib/
    https://networkx.github.io/documentation/stable/_modules/networkx/drawing/nx_pylab.html#draw
    """
    """
    ______
    Input:
        Bot Genome
        Neural Net Type
    ______
    Output:
        None
        Plots graph of each a neural net in the bot genome
    ______
        The layout can be customized with nx.draw(nn_graph,pos = dictionary)
    """
    
    bot_genome = utils.load_bot_genome(bot_name)
    connection_genome = bot_genome["{}_connection_genome".format(net_type)]
    node_genome = bot_genome["{}_node_genome".format(net_type)]
    init_innovation_number = utils.init_innovation_numbers[net_type]

    
    nn_graph = nx.DiGraph()#initializing the graph; adding the nodes and edges
    for node in node_genome:
        nn_graph.add_node(node["INDEX"],bias = node["BIAS"])    
    for gene in connection_genome:
        if gene["INNOVATION"] > init_innovation_number or added_only==False:
            nn_graph.add_edge(gene["IN"],gene["OUT"],weight = gene["WEIGHT"])


    try:#listing the weights and biases st. the graph can be colored
        edges,weights = zip(*nx.get_edge_attributes(nn_graph,'weight').items())
        nodes,biases = zip(*nx.get_node_attributes(nn_graph,'bias').items())
    except ValueError:
        print(f"No Connections in {bot_name}'s {net_type} net")
        return
    except Exception as exception:
        sys.exit(f"Graphing {bot_name}'s {net_type} net failed: {exception}")

    
    plt.title(f"{bot_name} Added Graph Structure in {net_type} net")#only works if called before nx.draw
    cmap = plt.cm.seismic
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin = min(weights+biases), vmax=max(weights+biases)))
    sm._A = []
    plt.colorbar(sm)#colorbar legend so the colors are identifiable


    nx.draw(nn_graph,arrows = True,alpha=0.5,pos = node_positions(nn_graph,net_type),edge_color=weights,node_color=biases,edge_cmap=cmap,cmap=cmap)
    nx.draw_networkx_labels(nn_graph,pos = node_positions(nn_graph,net_type))
    
    plt.show()
    

def species_over_time(pop_size):
    """
    ______
    Input:
       list of species_dict
    ______
    Output:
        Graph showing the species composition of the population
        over the generations
    """ 
    
    with open(utils.cwd + r'\Bots\species.json','r') as species_file: #best practice would be to have a utils function load the species_dict_list but yeah
        species_dict_list = json.load(species_file)
        species_file.close()
    
    gens=[int(gen_idx.split('_')[-1]) for gen_idx,species_dict in species_dict_list.items()]
    species_sizes=[[0 for _ in gens] for _ in range(pop_size+100)]
    
    for gen_idx,species_dict in species_dict_list.items():
        for species_idx,species in species_dict.items():
            species_sizes[int(species_idx)][int(gen_idx.split('_')[-1])] = len(species["MEMBERS"])

    lower=[0 for _ in gens]
    for series_idx,series in enumerate(species_sizes[:-1]):
        upper = [species_sizes[series_idx][idx] + lower[idx] for idx in gens]
        plt.plot(gens,upper,color='k',alpha=0.1)
        plt.fill_between(gens,lower,upper,alpha=0.1)
        lower=upper

    plt.xlabel("Generation")
    plt.ylabel("Population")   
    plt.show()



def population_progress():
    progress = utils.load_progress()
    max_score = [gen["MAX"] for gen in progress]
    conf = [gen["CONF"] for gen in progress]
    avg = [gen["AVG"] for gen in progress]
    idx_list = [gen["GEN"] for gen in progress]
    
    upperconf,lowerconf = [max_score[idx] + conf[idx] for idx in idx_list], [max_score[idx]-conf[idx] for idx in idx_list] 
    
    
    plt.title(label = "Score Progress")
    
    plt.plot(idx_list,upperconf,idx_list,lowerconf,color='b',alpha=0.3,linewidth=0)
    plt.fill_between(idx_list,upperconf,lowerconf,facecolor='b',alpha=0.1,label='Confidence Band')
    
    plt.xlabel("Generation")
    plt.ylabel("Score")
    
    plt.plot(idx_list,max_score,color='r',label = "Maximum Score",linewidth=0.5)
    plt.plot(idx_list,avg,color='k',label = "Average Score",linewidth=0.5)
    
    plt.legend()
    plt.show()

    











    
