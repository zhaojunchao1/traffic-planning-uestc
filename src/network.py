Network = dict

network = {
    "A": ["B", "C"],
    "B": ["C"],
    "C": [""],
}

def add_node(network, node):
    network[node] = []

def add_link(network, node1, node2):
    network[node1].append(node2)

network = {}

add_node(network, "A")
add_node(network, "B")
add_node(network, "C")
add_link(network, "A", "B")
add_link(network, "A", "C")
add_link(network, "B", "C")

print(network)

AttributeMap = dict

length_map = {
    ("A", "B"): 4,
    ("A", "C"): 3,
    ("B", "C"): 7,
}

speed_map = {
    ("A", "B"): 40,
    ("A", "C"): 40,
    ("B", "C"): 60,
}

Path = list

def dijkstra(network, attr_map, origin, destination) -> Path:
    pass

def assign(network, cost_function_map, od_pairs) -> AttributeMap:
    flow_map = {}
    for od_pair in od_pairs:
        new_flow_map = single_od_assign(network, cost_function_map, od_pair, flow_map)
        flow_map = flow_map_combine(flow_map, new_flow_map)

    return flow_map

def single_od_assign(network, cost_function_map, od_pair, base_flow_map) -> AttributeMap:
    origin, destination, flow = od_pair
    cost_map = update_cost(cost_function_map, base_flow_map)
    shortest_path = dijkstra(network, cost_map, origin, destination)
    flow_map = flow_loading(network, shortest_path, flow)

    for i in range(100):
        cost_map = update_cost(cost_function_map, flow_map_combine(base_flow_map, flow_map))
        shortest_path = dijkstra(network, cost_map, origin, destination)

        flow_map = flow_map_scale(flow_map, 0.9)
        new_flow_map = flow_loading(network, shortest_path, flow * 0.1)
        flow_map = flow_map_combine(flow_map, new_flow_map)

def flow_map_combine(map1, map2):
    map = {}
    for key in map1.keys():
        map[key] = map1[key] + map2[key]
    return map

def flow_map_scale(map1, scale):
    map = {}
    for key in map1.keys():
        map[key] = map1[key] * scale

    return map

def update_cost(cost_function_map, flow_map):
    map = {}
    for key in cost_function_map.keys[]:
        cost_function = cost_function_map[key]
        flow = flow_map[key]
        cost = cost_function(flow)
        map[key] = cost

    return map

def flow_loading(network, path, flow):
    map = {}
    links = set(zip(path[:-1], path[1:]))
    for link in network_links(network):
        if link in links:
            map[link] = flow
        else:
            map[link] = 0

    return map

def network_links(network):
    pass



    
