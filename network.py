import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()

G.add_node(1, pos=(80, 90))
G.add_node(2, pos=(80, 70))
G.add_node(3, pos=(90, 50))
G.add_node(4, pos=(90, 20))
G.add_node(5, pos=(90, 10))
G.add_node(6, pos=(70, 50))
G.add_node(7, pos=(60, 70))
G.add_node(8, pos=(60, 50))
G.add_node(9, pos=(60, 10))
G.add_node(10, pos=(10, 50))

G.add_edge(1, 2, length=30, speed=40)
G.add_edge(1, 7, length=50, speed=60)
G.add_edge(2, 7, length=40, speed=60)
G.add_edge(2, 3, length=40, speed=60)
G.add_edge(2, 6, length=40, speed=60)
G.add_edge(3, 4, length=50, speed=60)
G.add_edge(3, 6, length=40, speed=40)
G.add_edge(4, 5, length=10, speed=40)
G.add_edge(4, 6, length=70, speed=60)
G.add_edge(5, 9, length=90, speed=60)
G.add_edge(6, 8, length=10, speed=40)
G.add_edge(7, 8, length=30, speed=40)
G.add_edge(7, 10, length=130, speed=80)
G.add_edge(8, 9, length=60, speed=60)
G.add_edge(8, 10, length=120, speed=80)
G.add_edge(9, 10, length=150, speed=80)

# 定义函数，用于寻找图中每对OD（起点-终点）之间的最短路径
def find_shortest_paths(G, od_pairs):
    shortest_paths = {}
    def time_weight(u, v, d):
        return d['time']
    # 遍历所有的OD对
    for od_pair in od_pairs:
        # 解构OD对，获取起点、终点和流量（这里流量未使用）
        origin, destination, _ = od_pair
        path = nx.shortest_path(G, source=origin, target=destination, weight=time_weight)
        shortest_paths[od_pair[:2]] = path  
    return shortest_paths

def update_time(t0, flow, capacity):
    flow_ratio = flow / capacity
    time_multiplier = (1 + (flow_ratio ** 2))
    t = t0 * time_multiplier
    return t

# 定义函数，用于更新所有最短路径上的边的时间
def update_path_times(G, shortest_time_paths, capacity):
    # 遍历所有的OD对和对应的最短路径
    for od_pair, path in shortest_time_paths.items():
        # 遍历路径上的每一条边
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            # 如果边存在，则更新其时间
            if G.has_edge(u, v):
                edge_data = G[u][v]
                new_time = update_time(edge_data['time'], edge_data['flow'], capacity)
                edge_data['time'] = new_time

#将流量分配到最短路径上的每一条边
def assign_flows_to_links(G, shortest_time_paths, od_flows):
    link_flows = {}

    for od_pair, path in shortest_time_paths.items():
        total_flow = od_flows[od_pair]

        for i in range(len(path) - 1):
            link = (path[i], path[i + 1])
            if link not in link_flows:
                link_flows[link] = 0
            link_flows[link] += total_flow

            if G.has_edge(link[0], link[1]):
                G[link[0]][link[1]]['flow'] = link_flows[link]

    return link_flows

#调整流量，使得部分流量转向新的最短路径
def adjust_flow(G, link_flows, shortest_paths, od_pairs):
    shortest_path_flows = {}
    cumulative_flow_on_shortest_path = {}
    for od_pair in od_pairs:
        origin, destination, flow = od_pair
        path = shortest_paths[origin, destination]
        for i in range(len(path) - 1):
            link = (path[i], path[i + 1])
            # 累加最短路径上的流量
            if link not in shortest_path_flows:
                shortest_path_flows[link] = 0
            shortest_path_flows[link] += flow
            
            # 累加该最短路径上的flow，而不是覆盖
            if link not in cumulative_flow_on_shortest_path:
                cumulative_flow_on_shortest_path[link] = 0
            cumulative_flow_on_shortest_path[link] += flow

    # 更新所有路段的流量
    for u, v, data in G.edges(data=True):
        link = (u, v)
        old_flow = data['flow']
        
        # 使用累加的流量来进行更新
        if link in cumulative_flow_on_shortest_path:
            new_flow = old_flow * 0.9 + cumulative_flow_on_shortest_path[link] * 0.1
        else:
            new_flow = old_flow * 0.9
        
        data['flow'] = new_flow

    return {link: G[link[0]][link[1]]['flow'] for link in link_flows}

capacity = 1800
od_pairs = [(1, 9, 2000), (2, 5, 1000)]
#将流量信息从三元组列表中分离出来，存储为字典
od_flows = {od_pair[:2]: od_pair[2] for od_pair in od_pairs}

# 初始化图中每条边的流量和时间
for edge in G.edges(data=True):
    edge_data = edge[2]
    edge_data['flow'] = 0  
    edge_data['time'] = edge_data['length'] / edge_data['speed']  

# 寻找初始的最短路径，并分配流量到边
shortest_paths = find_shortest_paths(G, od_pairs)
link_flows = assign_flows_to_links(G, shortest_paths, od_flows)

update_path_times(G, shortest_paths, capacity)
shortest_paths = find_shortest_paths(G, od_pairs)
adjusted_link_flows = adjust_flow(G, link_flows, shortest_paths, od_pairs)# 进行100次迭代，每次迭代更新路径时间、寻找新的最短路径并调整流量
for i in range(100):
    update_path_times(G, shortest_paths, capacity)
    shortest_paths = find_shortest_paths(G, od_pairs)
    adjusted_link_flows = adjust_flow(G, adjusted_link_flows, shortest_paths, od_pairs)

# 打印最终的最短路径和路径上每条边的流量和时间
for od_pair, path in shortest_paths.items():
    origin, destination = od_pair
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        if G.has_edge(u, v):
            data = G[u][v]
            if 'flow' in data:
                print(f"  Edge ({u}, {v})  flow: {round(data['flow'], 2)}")
            else:
                print(f"  Edge ({u}, {v})  does not have a flow attribute.")
    print(f"Shortest path from {origin} to {destination}: {path}")

pos = nx.get_node_attributes(G, 'pos')
nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=300, font_size=8, font_weight='bold')
nx.draw_networkx_edge_labels(G, pos, edge_labels={(u, v): round(G[u][v]["flow"], 2)  for u, v in G.edges()})

for od_pair, path in shortest_paths.items():
    origin, destination = od_pair
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        edge = (u, v) 
        if G.has_edge(u, v):
            data = G[u][v]
            if 'flow' in data:
                flow = data['flow']
                nx.draw_networkx_edges(G, pos, edgelist=[edge], width=flow/50)
plt.show()