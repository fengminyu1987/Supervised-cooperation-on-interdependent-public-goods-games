import networkx as nx
import random
import numpy as np
import json

def init_graph(L):
    # 生成规模为 L*L 的方格网络
    G = nx.grid_2d_graph(L, L, periodic=True)

    # 将节点重新映射为整数
    new_mapping = {}
    for i in G.nodes:
        new_mapping[i] = i[0] * L + i[1]
    graph = nx.relabel_nodes(G, new_mapping)

    # 为每个节点随机分配一个策略
    for node in graph.nodes:
        graph.nodes[node]["strategy"] = 1 if random.random() < 0.5 else 0  # 0: 背叛, 1: 合作
    return graph

# 得到每一轮中以node为中心的平均收益
def get_payoffcenter(G_game, strategies):
    payoffcenter = {}
    for node in G_game.nodes():
        neighbors = list(G_game.neighbors(node))
        Nc = strategies[node]
        for neighbor in neighbors:
            Nc += strategies[neighbor]
        result = (Nc * r) / 5
        payoffcenter[node] = result
    return payoffcenter

# 得到博弈层的节点收益
def get_gamepayoff(G_game, game_strategies, refer_strategies, payoffcenter):
    gamepayoff_dictionary = {}

    for node in G_game.nodes():
        payoff = 0

        if refer_strategies[node] == 1:  # 公平裁判
            payoff = payoffcenter[node] - game_strategies[node] - alpha * (1 - game_strategies[node])

        elif refer_strategies[node] == 0:  # 腐败裁判
            payoff = payoffcenter[node] - game_strategies[node] - beta * (payoffcenter[node]) * (1 - game_strategies[node])

        # 遍历node的邻居，计算总收益
        neighbors = list(G_game.neighbors(node))
        for neighbor in neighbors:
            if refer_strategies[neighbor] == 1:
                payoff += payoffcenter[neighbor] - game_strategies[node] - alpha * (1 - game_strategies[node])
            elif refer_strategies[neighbor] == 0:
                payoff += payoffcenter[neighbor] - game_strategies[node] - beta * (payoffcenter[neighbor]) * (1 - game_strategies[node])

        # 将收益储存到字典中
        gamepayoff_dictionary[node] = payoff
    return gamepayoff_dictionary

# 得到裁判层的收益
def get_referpayoff(G_refer, game_strategies, payoffcenter):
    referpayoff_dictionary = {}

    for node in G_refer.nodes():
        payoff = 0
        Nc = 1 - game_strategies[node]
        neighbors = list(G_refer.neighbors(node))
        for neighbor in neighbors:
            Nc += (1 - game_strategies[neighbor])

        if refer_strategies[node] == 1:
            payoff = k  # 公平裁判获得监管费k
        elif refer_strategies[node] == 0:
            payoff = beta * Nc * payoffcenter[node]  # 腐败裁判获取贿赂

        # 将裁判node收益存储到字典中
        referpayoff_dictionary[node] = payoff
    return referpayoff_dictionary

# 费米函数
def Fermi_function(x, y):
    return 1 / (1 + np.exp((x - y) / K))

# 计算合作者频率(公平裁判比例)
def calculate_cooperator_rate(G, strategies):
    c = sum(1 for value in strategies.values() if value == 1)
    return c / len(G.nodes)

L = 50
r = 1.2
k = 0.2   # 监管费用
Alpha = np.arange(0, 0.2, 0.2)
Beta = np.arange(0, 0.2, 0.2)  # 背叛者将这一轮中额外获得的beta收益给裁判
K = 0.1
iterations = 20
simulations = 3

fc_Result = {}
rc_Result = {}

for alpha in Alpha:
    Fc = []
    Rc = []
    for beta in Beta:
        total_cooperator_rates = np.zeros(simulations)
        total_refer_rates = np.zeros(simulations)

        for simulation in range(simulations):
            G_refer = init_graph(L)
            G_game = init_graph(L)

            game_strategies = nx.get_node_attributes(G_game, 'strategy')
            refer_strategies = nx.get_node_attributes(G_refer, 'strategy')

            # 存储上一轮中节点的策略
            gamelast_strategies = game_strategies.copy()
            referlast_strategies = refer_strategies.copy()

            Y1 = [calculate_cooperator_rate(G_game, game_strategies)]
            Y2 = [calculate_cooperator_rate(G_refer, refer_strategies)]

            for iteration in range(iterations):
                payoffcenter = get_payoffcenter(G_game, game_strategies)

                gamepayoff_dict = get_gamepayoff(G_game, game_strategies, refer_strategies, payoffcenter)
                referpayoff_dict = get_referpayoff(G_refer, game_strategies, payoffcenter)

                # 博弈层节点的策略更新
                for node_i in G_game.nodes:
                    payoff_i = gamepayoff_dict[node_i]
                    neighbors = list(G_game.neighbors(node_i))
                    if neighbors:  # 确保邻居不为空
                        random_neighbor = random.choice(neighbors)
                        random_neighbor_payoff = gamepayoff_dict[random_neighbor]
                        probability1 = Fermi_function(payoff_i, random_neighbor_payoff)

                        if random.random() < probability1:
                            game_strategies[node_i] = gamelast_strategies[random_neighbor]

                gamelast_strategies = game_strategies.copy()

                # 裁判层节点的策略更新
                for node_j in G_refer.nodes:
                    payoff_j = referpayoff_dict[node_j]
                    neighbors = list(G_refer.neighbors(node_j))
                    if neighbors:  # 确保邻居不为空
                        select_neighbor = random.choice(neighbors)
                        select_neighbor_payoff = referpayoff_dict[select_neighbor]
                        probability2 = Fermi_function(payoff_j, select_neighbor_payoff)

                        if random.random() < probability2:
                            refer_strategies[node_j] = referlast_strategies[select_neighbor]

                referlast_strategies = refer_strategies.copy()

                cooperator_rate = calculate_cooperator_rate(G_game, game_strategies)
                refer_rate = calculate_cooperator_rate(G_refer, refer_strategies)

                Y1.append(cooperator_rate)
                Y2.append(refer_rate)

                print("\r {}: {:.2f}, {}: {:.2f}, simulation: {:d}/{:d}, t: {:d}/{:d}, fc: {:.4f}, rc: {:.4f}".format(
                    "α", alpha, "β", beta, simulation, simulations, iteration, iterations, cooperator_rate, refer_rate), end="     ")

            total_cooperator_rates[simulation] = np.mean(Y1[iterations - 5:])
            total_refer_rates[simulation] = np.mean(Y2[iterations - 5:])

        average_cooperator_rates = total_cooperator_rates.mean()
        average_refer_rates = total_refer_rates.mean()

        Fc.append(average_cooperator_rates)
        Rc.append(average_refer_rates)

    fc_Result["{:.2f}".format(alpha)] = Fc
    rc_Result["{:.2f}".format(alpha)] = Rc

json_str1 = json.dumps(fc_Result)
json_str2 = json.dumps(rc_Result)

with open('alpha_beta/alpha_betaFc.json', 'w') as json_file:
    json_file.write(json_str1)
with open('alpha_beta/alpha_betaRc.json', 'w') as json_file:
    json_file.write(json_str2)