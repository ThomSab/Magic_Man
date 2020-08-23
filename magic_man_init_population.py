import os
import json
import magic_man_utils as utils
from magic_train import species_represent,speciation,mutation_step
from magic_man_player import Player

N_bid_sensors,N_bid_outputs,N_play_sensors,N_play_outputs,N_stm_sensors,N_stm_outputs = utils.init_list

def initial_genome(N_bid_sensors,N_bid_outputs,
                   N_play_sensors,N_play_outputs,
                   N_stm_sensors,N_stm_outputs):
    """
    Creates a genome for the minimal structure as described in the paper
    All Sensors are connected to all output nodes
    No hidden Nodes
    """


    bid_sensors = [{"INDEX":idx              ,"TYPE":"SENSOR"} for idx in range(N_bid_sensors)]
    bid_outputs = [{"INDEX":N_bid_sensors+idx,"TYPE":"OUTPUT"} for idx in range(N_bid_outputs)]

   
    play_sensors= [{"INDEX":idx               ,"TYPE":"SENSOR"} for idx in range(N_play_sensors)]
    play_outputs= [{"INDEX":N_play_sensors+idx,"TYPE":"OUTPUT"} for idx in range(N_play_outputs)]


    stm_sensors= [{"INDEX":idx              ,"TYPE":"SENSOR"} for idx in range(N_stm_sensors)]
    stm_outputs= [{"INDEX":N_stm_sensors+idx,"TYPE":"OUTPUT"} for idx in range(N_stm_outputs)]

    #these are oneliners
    #python i love u
    bid_connections = [{"IN": sensor_idx, "OUT": output_idx,"WEIGHT": 0, "ENABLED": 1, "INNOVATION": N_bid_outputs*sensor_idx+(output_idx-N_bid_sensors)+1}
                        for sensor_idx in range(N_bid_sensors) for output_idx in range(N_bid_sensors,(N_bid_sensors+N_bid_outputs))]

    play_connections = [{"IN": sensor_idx, "OUT": output_idx,"WEIGHT": 0, "ENABLED": 1, "INNOVATION": N_play_outputs*sensor_idx+output_idx-N_play_sensors+1}
                        for sensor_idx in range(N_play_sensors) for output_idx in range(N_play_sensors,(N_play_sensors+N_play_outputs))]

    stm_connections = [{"IN": sensor_idx, "OUT": output_idx,"WEIGHT": 0, "ENABLED": 1, "INNOVATION": N_stm_outputs*sensor_idx+output_idx-N_stm_sensors+1}
                        for sensor_idx in range(N_stm_sensors) for output_idx in range(N_stm_sensors,(N_stm_sensors+N_stm_outputs))]

    return {
        "bid_node_genome"       :bid_sensors+bid_outputs,
        "bid_connection_genome" :bid_connections,
        "play_node_genome"      :play_sensors+play_outputs,
        "play_connection_genome":play_connections,
        "stm_node_genome"       :stm_sensors+stm_outputs,
        "stm_connection_genome" :stm_connections
        }


"""
Innitial Innovation Number for each net
the IIN depends on how many sensor nodes and output nodes a net has
It is constant over all initial bots since they all start out minimal
"""    
bid_iin  = [ ((N_bid_outputs) *N_bid_sensors)  ]
play_iin = [ ((N_play_outputs)*N_play_sensors) ]
stm_iin  = [ ((N_stm_outputs) *N_stm_sensors)  ]



if __name__ == "__main__":
    for player in utils.load_empty_bot_names(0):
        utils.save_init_genome(player,
            init_genome = initial_genome(N_bid_sensors,N_bid_outputs,N_play_sensors,N_play_outputs,N_stm_sensors,N_stm_outputs))
        utils.save_init_score(player,0)
    for net_type,net_iin in [('bid',bid_iin),('play',play_iin),('stm',stm_iin)]:
        utils.save_init_innovation(net_type,net_iin)
    utils.save_init_progress()
    bots = [Player(bot_name) for bot_name in utils.load_bot_names()]
    
    for bot in bots:
        mutation_step(bot.name)
    # init mutation step st. the first generation isnt pointless
        
    utils.save_generation_species(0,speciation(bots,species_dict=species_represent()))





    
