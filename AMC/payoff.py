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


# 参数设置
L = 50
r = 3
k = 0.6  # 监管费用
alpha = 1.6  # 惩罚成本
beta = 0.3  # 背叛者将这一轮中额外获得的beta收益给裁判
K = 0.1
iterations = 5000

G_refer = init_graph(L)
G_game = init_graph(L)

cooperator_rates = []
refer_rates = []

game_strategies = nx.get_node_attributes(G_game, 'strategy')
refer_strategies = nx.get_node_attributes(G_refer, 'strategy')

average_gamedict = {}
average_referdict = {}

# 存储上一轮中节点的策略
gamelast_strategies = game_strategies.copy()
referlast_strategies = refer_strategies.copy()

for iteration in range(iterations + 1):

    # 获得节点收益
    gamepayoff_dict = get_gamepayoff(G_game)
    average_gamepayoff = sum(gamepayoff_dict.values()) / len(gamepayoff_dict)
    average_gamedict[iteration] = average_gamepayoff

    referpayoff_dict = get_referpayoff(G_game, G_refer)
    average_referpayoff = sum(referpayoff_dict.values()) / len(referpayoff_dict)
    average_referdict[iteration] = average_referpayoff

    # 计算合作频率
    cooperator_rate = calculate_cooperator_rate(G_game, game_strategies)
    cooperator_rates.append(cooperator_rate)

    # 公平裁判比例
    refer_rate = calculate_cooperator_rate(G_refer, refer_strategies)
    refer_rates.append(refer_rate)

    # 博弈层节点的策略更新，使用费米函数
    for node_i in G_game.nodes:
        payoff_i = gamepayoff_dict[node_i]

        # 随机选择一个邻居
        neighbors = list(G_game.neighbors(node_i))
        random_neighbor = random.choice(neighbors)
        random_neighbor_payoff = gamepayoff_dict[random_neighbor]

        probability1 = Fermi_function(payoff_i, random_neighbor_payoff)

        # 策略更新
        if random.random() < probability1:
            game_strategies[node_i] = gamelast_strategies[random_neighbor]

    # 存储节点策略
    gamelast_strategies = game_strategies.copy()

    nx.set_node_attributes(G_game, game_strategies, 'strategy')

    # 裁判层节点的策略更新，使用费米函数
    for node_j in G_refer.nodes:
        payoff_j = referpayoff_dict[node_j]
        neighbors = list(G_refer.neighbors(node_j))

        # 随机选择一个邻居进行策略更新
        select_neighbor = random.choice(neighbors)
        select_neighbor_payoff = referpayoff_dict[select_neighbor]

        probability2 = Fermi_function(payoff_j, select_neighbor_payoff)

        # 策略更新
        if random.random() < probability2:
            refer_strategies[node_j] = referlast_strategies[select_neighbor]

    # 存储策略
    referlast_strategies = refer_strategies.copy()

    nx.set_node_attributes(G_refer, refer_strategies, 'strategy')

    print(
        "\r t: {:d}/{:d}, fc: {:.4f}, rc: {:.4f}, gamepayoff: {:.4f}, referpayoff: {:.4f}".format(iteration, iterations,
                                                                                                  cooperator_rate,
                                                                                                  refer_rate,
                                                                                                  average_gamepayoff,
                                                                                                  average_referpayoff),
        end="     ")