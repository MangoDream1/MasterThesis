from collections import deque
from itertools import combinations
import networkx as nx
import numpy as np


class NetworkUtils:
    def __init__(self, network, matrix):
        self.network = network
        self.matrix  = matrix

    def get_loop(self, size, found_length=10): #TODO: experiment with found_length
        network = self.network.to_undirected()        
        found = deque([], found_length)

        def recursion(node, start_node, loop):        
            if len(loop) < size:    
                for neighbor in network.neighbors(node):
                    if neighbor not in loop:
                        yield from recursion(neighbor, start_node, loop + [neighbor])
                    
            elif network.adj[node].get(start_node, None):
                sorted_loop = sorted(loop)

                if sorted_loop not in found:
                    found.append(sorted_loop)
                    yield sorted_loop      

        for node in network.nodes:
            yield from recursion(node, node, [node])

    def get_connected(self, max_length):
        network = self.network.to_undirected()
        for xnode, ynode in combinations(network.nodes, 2):
            for path in nx.all_simple_paths(network, xnode, ynode, max_length):
                yield path

    def get_cliques(self, max_size=10):
        network = self.network.to_undirected()
        for clique in nx.find_cliques(network):
            if len(clique) <= max_size:
                yield clique

    def get_crosses(self, min_size=5, max_size=50):
        indexes = np.arange(self.matrix.shape[0])

        for node in indexes:
            balance = self.matrix - self.matrix.T
            m = balance[node].toarray()[0]
            
            out_values = list(m[m<0])
            in_values  = list(m[m>0])
            
            out_indexes = list(indexes[m<0])
            in_indexes  = list(indexes[m>0])
            
            v = 0
            combination = [node]
            
            while len(out_values) != 0 and len(in_values) != 0:
                o = out_values.pop()
                oi = out_indexes.pop()
                
                v += o
                combination.append(oi)

                while len(in_values) != 0:
                    i = in_values.pop()
                    ii = in_indexes.pop()
                    
                    v += i
                    combination.append(ii)

                    if v > 0:
                        break

                if len(combination) > max_size:
                    break

                if len(combination) >= min_size:
                    yield combination
                    
                    combination = [node]
                    v = 0
    
    def all_combinations(self, size):
        network = self.network.to_undirected()        
        return combinations(network.nodes, size)