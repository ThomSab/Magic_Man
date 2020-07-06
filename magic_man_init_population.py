import os
import json
import magic_man_utils as utils


def initial_genome(name,N_bid_sensors  =  89,N_bid_outputs  =  1,
                     N_play_sensors = 160,N_play_outputs = 60,
                     N_stm_sensors  = 160,N_stm_outputs  = 10):
    """
    Creates a genome for the minimal structure as described in the paper
    All Sensors are connected to all output nodes
    No hidden Nodes
    """


    bid_sensors = [{"INDEX":1+idx              ,"TYPE":"SENSOR"} for idx in range(N_bid_sensors)]
    bid_outputs = [{"INDEX":1+N_bid_sensors+idx,"TYPE":"OUTPUT"} for idx in range(N_bid_outputs)]

   
    play_sensors= [{"INDEX":1+idx               ,"TYPE":"SENSOR"} for idx in range(N_play_sensors)]
    play_outputs= [{"INDEX":1+N_play_sensors+idx,"TYPE":"OUTPUT"} for idx in range(N_play_outputs)]


    stm_sensors= [{"INDEX":1+idx              ,"TYPE":"SENSOR"} for idx in range(N_stm_sensors)]
    stm_outputs= [{"INDEX":1+N_stm_sensors+idx,"TYPE":"OUTPUT"} for idx in range(N_stm_outputs)]

    #these are oneliners
    #python i love u
    bid_connections = [{"IN": sensor_idx, "OUT": output_idx,"WEIGHT": 0, "ENABLED": 1, "INNOVATION": N_bid_outputs*sensor_idx+output_idx+1}
                        for sensor_idx in range(N_bid_sensors) for output_idx in range(N_bid_outputs)]

    play_connections = [{"IN": sensor_idx, "OUT": output_idx,"WEIGHT": 0, "ENABLED": 1, "INNOVATION": N_play_outputs*sensor_idx+output_idx+1}
                        for sensor_idx in range(N_play_sensors) for output_idx in range(N_play_outputs)]

    stm_connections = [{"IN": sensor_idx, "OUT": output_idx,"WEIGHT": 0, "ENABLED": 1, "INNOVATION": N_stm_outputs*sensor_idx+output_idx+1}
                        for sensor_idx in range(N_stm_sensors) for output_idx in range(N_stm_outputs)]

    return [{
        "bid_node_genome"       :bid_sensors+bid_outputs,
        "bid_connection_genome" :bid_connections,
        "play_node_genome"      :play_sensors+play_outputs,
        "play_connection_genome":play_connections,
        "stm_node_genome"       :stm_sensors+stm_outputs,
        "stm_connection_genome" :stm_connections
        }]
        
    
if __name__ == "__main__":
    print(initial_genome('josh'))
    utils.save('josh',genome = initial_genome('josh'),generate=True)