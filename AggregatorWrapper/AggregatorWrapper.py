from collections import defaultdict

import networkx as nx


class AggregatorWrapper:
    def __init__(self, aggregator, transactions, time_block, *args, **kwargs):
        self.transactions = transactions

        self.aggregators = defaultdict(lambda: aggregator(*args, **kwargs))

        self.split_into_blocks(time_block)

    def split_into_blocks(self, time_block):
        """
        Splits self.transactions into time blocks. If time_blocks not specified (either 0 or None), then all
        transactions put into the same block.
        :param time_block: size of each time block
        :return:
        """

        self.transactions = sorted(self.transactions, key=lambda tx: tx.timestamp)
        tx_block = defaultdict(list)

        if time_block == 0 or not time_block:
            tx_block[0] = self.transactions
        else:
            min_time, max_time = self.transactions[0].timestamp, self.transactions[-1].timestamp
            time = max_time - min_time
            amount = int(time / time_block)

            transactions = []

            for i in range(amount):
                limit = min_time + (i+1) * time_block

                while True:
                    if self.transactions[0].timestamp < limit:
                        popped = self.transactions.pop(0)
                        tx_block[i].append(popped)
                        transactions.append(popped)
                        continue

                    break

            self.transactions = transactions

        self._create_networks(tx_block)

    def _create_networks(self, tx_block):
        """
        Creates networks for each block and saves in self.network with same key as tx_block
        :param tx_block: nested list with all transactions per block
        :return:
        """

        for k, v in tx_block.items():
            directed_graph = nx.DiGraph()
            edges = [tx.get_graph_edge() for tx in v]

            # joins edges from and to same location
            joined = defaultdict(int)
            for to, fr, amount in edges:
                joined[(to, fr)] += amount

            edges = [(to, fr, amount) for (to, fr), amount in joined.items()]
            directed_graph.add_weighted_edges_from(edges)

            self.aggregators[k].set_init_variables(
                nx.to_scipy_sparse_matrix(directed_graph), directed_graph)

    
#
    # TODO separate from Aggregator class
    # def simple_hill_climber(self, block_number):
    #     matrix = self.matrices[block_number]
    #     goal_balance = self.goal_balance[block_number]
    #     abs_max = self.abs_max[block_number]

    #     print("Pre-cost", self.block_cost(matrix, goal_balance))

    #     # Random matrix for init
    #     matrix = sc.sparse.random(*matrix.shape).asformat(MATRIX_FORMAT)

    #     diff_cost, tx_cost = self.block_cost(matrix, goal_balance)
    #     cost = diff_cost + tx_cost

    #     non_improvement = 0
    #     i = 0

    #     print("Init cost %s" % cost, diff_cost, tx_cost )

    #     while non_improvement <= 1000 and cost != 0:
    #         old_matrix = matrix.copy()
    #         matrix = self._add_random_transaction(matrix, abs_max)

    #         n_diff_cost, n_tx_cost = self.block_cost(matrix, goal_balance)
    #         n_cost = n_diff_cost + n_tx_cost

    #         if n_cost >= cost:
    #             non_improvement += 1
    #             matrix = old_matrix
    #         else:
    #             i += 1
    #             non_improvement = 0
    #             diff_cost = n_diff_cost
    #             tx_cost = n_tx_cost
    #             cost = n_cost

    #         # print("Iteration: %s Cost: %s Edges: %s" % (i, cost, self.networks[block_number].number_of_edges()))

    #     self.matrices[block_number] = matrix
    #     self.networks[block_number] = nx.from_scipy_sparse_matrix(matrix, create_using=nx.DiGraph())

    #     print("Last cost %s" % cost, diff_cost, tx_cost)

    # @staticmethod
    # def _add_random_transaction(matrix, abs_max, mutation_rate=0.1, deviations_divider=3):
    #     selection = sc.sparse.rand(*matrix.shape, mutation_rate) > 0  # look if always 10% then problem
    #     amounts = np.random.normal(0, abs_max / deviations_divider, len(selection.data))

    #     matrix[selection] += amounts
    #     matrix[matrix < 0] = 0

    #     return matrix
