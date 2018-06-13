from Aggregator.GenericAggregator import GenericAggregator
from utils.progress_bar import progress_bar

from multiprocessing import Process, Queue, Pool
import networkx as nx
import numpy as np
import scipy as sc

class MultiAggregator(GenericAggregator):
    def __init__(self, Aggregator, *args, result={}, pool_size=10, pool=None, progress=True, func=lambda agg: agg.iterate(), **kwargs):
        super().__init__(transaction_cost=1, balance_diff_multiplier=1)
        
        self.Aggregator = Aggregator
        self._args = args
        self._kwargs = kwargs

        self.result = result

        self.func = func

        self.progress = progress

        self.pool_size = pool_size
        self.pool = pool

        self._correction = False

        # self.final_stretch = Queue()

        if not pool:
            self.pool = Pool(self.pool_size)

    def iterate(self):
        cons, cost = self.cost(self.matrix)
        self.log_data.append(np.array([cost, cons, cons + cost]))

        subgraphs = nx.connected_component_subgraphs(self.network.to_undirected())

        queue = Queue()
        started = Queue()

        def handle_process(*args):
            rnodes, rmatrix = args[0]

            self.matrix[np.ix_(rnodes, rnodes)] = rmatrix

            cons, cost = self.cost(self.matrix)
            self.log_data.append(np.array([cost, cons, cons + cost]))
            
            started.get()
            queue.put(1)

        def error_process(*args):
            print("\n\n---ERROR---")
            print(args)
            print("---ERROR---\n")            

            started.get()            
            queue.put(1)

        i = 0
        for subgraph in subgraphs:
            started.put(1) 
            i += 1

            self.pool.apply_async(self._single_process, 
                (self.func, self.network, subgraph, self.Aggregator, *self._args,), 
                self._kwargs, handle_process, error_process)
        
        if self.progress:
            update_progress = progress_bar(0, i)
            _max = i

        while i != 0:
            if self.progress:
                update_progress(_max - i)
            
            queue.get()
            i -= 1

            # if i < self.pool_size:
            #     self.final_stretch.put(1)

        super().iterate()      

    @staticmethod
    def _single_process(func, graph, subgraph, Aggregator, *args, **kwargs):         
        subgraph = graph.subgraph(subgraph.nodes)
        nodes = np.array(subgraph.nodes())

        matrix = nx.to_scipy_sparse_matrix(subgraph)

        agg = Aggregator(*args, **kwargs)
        agg.set_init_variables(matrix, subgraph)

        func(agg)

        return nodes, agg.matrix