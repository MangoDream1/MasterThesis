from collections import deque, defaultdict
from itertools import combinations
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

class NetworkComponentMethods:
    def __init__(self):
        self.component_data = defaultdict(int)
        self.network = np.array([])
        self.matrix = np.array([])

        self.found_length = 1000 #TODO: experiment with found_length

    def get_loop(self, size): 
        network = self.network.to_undirected()        
        found = deque([], self.found_length)

        def recursion(node, start_node, loop):        
            if len(loop) < size:    
                for neighbor in network.neighbors(node):
                    if neighbor not in loop:
                        yield from recursion(neighbor, start_node, loop + [neighbor])
                    
            elif network.adj[node].get(start_node, None):
                sorted_loop = sorted(loop)

                if sorted_loop not in found:
                    found.append(sorted_loop)
                    self.component_data[name] += 1
                    yield sorted_loop      

        name = "Loop %s" % size
        for node in network.nodes:
            yield from recursion(node, node, [node])

    def get_connected(self, max_length):
        network = self.network.to_undirected()
        for xnode, ynode in combinations(network.nodes, 2):
            for path in nx.all_simple_paths(network, xnode, ynode, max_length):
                self.component_data["Connected"] += 1
                yield path

    def get_cliques(self, max_size=10):
        network = self.network.to_undirected()
        for clique in nx.find_cliques(network):
            if len(clique) <= max_size:
                self.component_data["Clique"] += 1
                yield clique

    def get_crosses(self, min_size=5, max_size=50):
        actors = np.arange(self.matrix.shape[0])
        found = deque([], self.found_length)        

        for node in actors:
            m = (self.matrix[node] - self.matrix.T[node]).toarray()[0]

            selection = m!=0
            m = m[selection]
            indexes = actors[selection]

            out_values = list(m[m<0])
            in_values  = list(m[m>0])
            
            out_indexes = list(indexes[m<0])
            in_indexes  = list(indexes[m>0])
            
            v = 0
            combination = [node]
            
            while len(out_values) != 0 and len(in_values) != 0:
                v += out_values.pop()
                oi = out_indexes.pop()
                
                combination.append(oi)

                while len(in_values) != 0 and v < 0:
                    v += in_values.pop()
                    ii = in_indexes.pop()
                    
                    combination.append(ii)

                if len(combination) > max_size:
                    break

                if len(combination) >= min_size and v > 0:
                    sorted_combi = sorted(combination)

                    if sorted_combi not in found:
                        found.append(sorted_combi)
                        yield sorted_combi  
                        self.component_data["Cross%s" % min_size] += 1

                    combination = [node]
                    v = 0
    
    def all_combinations(self, size):
        network = self.network.to_undirected()
        self.component_data["All"] += 1  
        return combinations(network.nodes, size)

    def plot_bar_component_count(self):
        names, data = zip(*sorted(list(self.component_data.items())))
        x_pos = list(range(len(names)))

        plt.bar(x_pos, data)
        plt.xlabel("Component count")
        plt.ylabel("Amount")
        plt.title("Amount of components solved")

        plt.xticks(x_pos, names)

        plt.show()

