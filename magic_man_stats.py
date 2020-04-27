import numpy as np
import matplotlib.pyplot as plt
import math

def mov_avg(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0)) 
    raw = (cumsum[N:] - cumsum[:-N]) / float(N)
    for i in range(math.floor(int(N/2))):
        raw = np.insert(raw,i,x[i])
    for i in range(math.floor(int(N/2)-1),0,-1):
        raw = np.append(raw,x[-i])
    return raw
    
