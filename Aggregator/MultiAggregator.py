from Aggregator.GenericAggregator import GenericAggregator

from multiprocessing import Process, Queue, Pool
import networkx as nx
import numpy as np
import scipy as sc

class MultiAggregator(GenericAggregator):
    def __init__(self, Aggregator, batch_size=4, *args, **kwargs):
        super().__init__(transaction_cost=1, balance_diff_multiplier=1)
        
        self.Aggregator = Aggregator
        self._args = args
        self._kwargs = kwargs

        self.batch_size = batch_size
        # self.pool_size = 4

    def iterate(self):
        cons, cost = self.cost(self.matrix)
        self.log_data.append(np.array([cost, cons, cons + cost]))

        subgraphs = nx.connected_component_subgraphs(self.network.to_undirected())
        processes = []
        output = Queue()
        # pool = Pool(self.pool_size)

        def handle_process(process):
            process.join()
            rnodes, rmatrix = output.get()
            self.matrix[np.ix_(rnodes, rnodes)] = rmatrix

            cons, cost = self.cost(self.matrix)

            print("-----------------")
            print("COST:",  cons, cost)
            print("-----------------")

            self.log_data.append(np.array([cost, cons, cons + cost]))

        for subgraph in subgraphs:
            process = Process(target=self._single_process, 
                args=(output, self.network, subgraph, self.Aggregator, *self._args), 
                kwargs=self._kwargs)

            processes.append(process)
            process.start()

            if len(processes) >= self.batch_size:
                handle_process(processes.pop())

        while len(processes) > 0:
            handle_process(processes.pop())
      

    @staticmethod
    def _single_process(output, graph, subgraph, Aggregator, *args, **kwargs):
        print("started")

        subgraph = graph.subgraph(subgraph.nodes)
        nodes = np.array(subgraph.nodes())

        # print(nodes) # FIXME: nodes always same order // proly sorted line 71
        # print("schijt", subgraph.nodes)

        matrix = nx.to_scipy_sparse_matrix(subgraph)

        agg = Aggregator(*args, **kwargs)
        agg.set_init_variables(matrix, subgraph)

        # agg.iterate(*args, **kwargs)
        agg.iterate(agg.get_loop, 3) # FIXME: make this modulair by making it a function

        # print(agg.matrix.toarray())

        # set result on correct place in master matrix

        # new_node_location = {x: i for i, x in enumerate(np.sort(nodes))}
        # fixed_matrix = sc.sparse.lil_matrix(agg.matrix.shape)

        # for i, x in enumerate(nodes):
        #     fixed_matrix[new_node_location[x]] = agg.matrix[i]

        # for i, x in enumerate(nodes):
        #     fixed_matrix[:,new_node_location[x]] = agg.matrix[:,i]

        # print("output", nodes)
        output.put((nodes, agg.matrix))