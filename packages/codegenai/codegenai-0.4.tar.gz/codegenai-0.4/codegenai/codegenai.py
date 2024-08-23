code = """
import networkx as nx
import matplotlib.pyplot as plt

def pretty_print(graph, title = "Graph Visualization",weighted = False, directed = False, heuristic = None):
    g = nx.DiGraph() if directed else nx.Graph()
    for u in graph:
        label = u
        if heuristic:
            label += "("+str(heuristic[u])+")"
        g.add_node(u, label = label)
        for v in graph[u]:
            g.add_edge(u, v, weight = graph[u][v])
    pos = nx.circular_layout(g)
    nx.draw(g, pos, 
            node_size = 1100, node_color = 'lightgreen',
            font_size = 11, font_family = 'cursive',
            width = 1.5, edge_color = 'red',
            edgecolors = 'black', linewidths = 1.5,
            margins = 0.25, clip_on = False)
    nx.draw_networkx_labels(g, pos, labels = nx.get_node_attributes(g, 'label'))
    if weighted:
        nx.draw_networkx_edge_labels(g, pos, 
                                     edge_labels = nx.get_edge_attributes(g, 'weight'),
                                     font_size = 8, font_family = 'cursive')
    plt.suptitle(title)
    plt.axis('off')
    plt.show()
    plt.clf()
def display(graph):
    g = nx.DiGraph()
    for u in graph:
        g.add_node(u)
        for v in graph[u]:
            g.add_edge(u, v, weight = graph[u][v])
    pos = nx.circular_layout(g)
    nx.draw(g, pos, with_labels = True)
    nx.draw_networkx_edge_labels(g, pos, edge_labels = nx.get_edge_attributes(g, 'weight'))
    plt.show()
    plt.clf()
def get_input(heuristic = False, weighted = False, bound = False, directed = False):
    rtn = []
    graph = {}
    rtn.append(graph)
    if heuristic:
        h = {}
        for _ in range(int(input("Enter no of nodes: "))):
            x, hval = input("Enter node and heuristic value: ").split()
            h[x] = int(hval)
        rtn.append(h)
    for _ in range(int(input("Enter no of edges: "))):
        if weighted:
            u, v, w = input("Enter (node, adj, weight): ").split()
        else:
            u, v = input("Enter (node, adj): ").split()
            w = 0
        graph[u] = graph.get(u,{})
        graph[u][v] = int(w)
        if not directed:
            graph[v] = graph.get(v,{})
            graph[v][u] = int(w)
    source, goal = input("Enter source and goal: ").split()
    if bound:
        b = int(input("Enter memory bound: "))
        rtn.append(b)
    rtn.extend([source, goal])
    return rtn
def print_path(node, parent):
    if node != None:
        return print_path(parent[node], parent) + [node]
    return []
def BFS(graph, start, goal):
    queue = [start]
    visited = []
    parent = {start : None}
    while queue:
        node = queue.pop(0)#First element
        visited.append(node)
        if node == goal:
            print("Result(BFS):",print_path(node, parent))
            return True
        for adj in graph[node]:
            if adj not in visited and adj not in queue:
                queue.append(adj)
                parent[adj] = node
    return False
def DFS(graph, start, goal):
    stack = [start]
    visited = []
    parent = {start : None}
    while stack:
        node = stack.pop()#last element
        visited.append(node)
        if node == goal:
            print("Result(DFS):",print_path(node, parent))
            return True
        for adj in graph[node]:
            if adj not in visited and adj not in stack:
                stack.append(adj)
                parent[adj] = node
    return False
def UCS(graph, start, goal):
    queue = [start]
    visited = []
    parent = {start : None}
    cost = {start : 0}
    while queue:
        queue.sort(key = lambda x : cost[x])
        node = queue.pop(0)
        visited.append(node)
        if node == goal:
            print("Result(UCS):",print_path(node, parent),"Path cost =",cost[node])
            return True
        for adj in graph[node]:
            if adj not in visited:
                new_cost = cost[node] + graph[node][adj]
                if adj not in queue:
                    queue.append(adj)
                elif new_cost > cost[adj]:
                    continue
                cost[adj] = new_cost
                parent[adj] = node
    return False
def DLS(graph, start, goal, limit):
    result = recursive_dls(graph, start, goal, limit, [start])
    print("Result(DLS):",result)
def recursive_dls(graph, node, goal, limit, visited):
    if node == goal:
        return [node]
    elif limit == 0:
        return 'cutoff'
    else:
        status = 'failure'
        for adj in graph[node]:
            if adj not in visited:
                visited.append(adj)
                result = recursive_dls(graph, adj, goal, limit - 1, visited)
                if result == 'cutoff':
                    status = 'cutoff'
                    visited.remove(adj)
                elif result != 'failure':
                    return [node] + result
        return status
def IDS(graph, start, goal):
    depth = 0
    while True:
        result = recursive_dls(graph, start, goal, depth, [start])
        print("Result(IDS/IDDFS):",result,"at depth limit =",depth)
        if result != 'cutoff':
            return
        depth += 1
def AStar(graph, start, goal, h):
    queue = [start]
    visited = []
    parent = {start : None}
    g = {start : 0}
    f = {start : h[start]}
    while queue:
        queue.sort(key = lambda x : f[x])
        node = queue.pop(0)
        visited.append(node)
        if node == goal:
            print("Result(A*):",print_path(node, parent),"Path cost =",g[node])
            return True
        for adj in graph[node]:
            if adj not in visited:
                gcost = g[node] + graph[node][adj]
                fcost = gcost + h[adj]
                if adj not in queue:
                    queue.append(adj)
                elif fcost > f[adj]:
                    continue
                g[adj] = gcost
                f[adj] = fcost
                parent[adj] = node
    return False
def IDAStar(graph, start, goal, h):
    def dfs(graph, parent, node, goal, g, h, th):
        f = g + h[node]
        if f > th:
            return None, f
        if node == goal:
            return node, f
        min_th = inf
        for adj in graph[node]:
            result, temp_th = dfs(graph, parent, adj, goal, g + graph[node][adj], h, th)
            if result is not None:
                parent[adj] = node
                return result, temp_th
            elif temp_th < min_th:
                min_th = temp_th
        return None, min_th
    
    inf = 9999999
    parent = {start : None}    
    th = h[start]
    while True:
        result, new_th = dfs(graph, parent, start, goal, 0, h, th)
        if result is not None:
            result = print_path(result, parent)
            cost = sum([graph[n1][n2] for n1, n2 in zip(result,result[1:])])
            print("Result(IDA*):",result,"Path cost =",cost)
            return
        elif new_th == inf:
            print("Result(IDA*): failure")
            return
        th = new_th
def SMAStar(graph, start, goal, h, bound):
    queue = [start]
    visited = []
    parent = {start : None}
    g = {start : 0}
    f = {start : h[start]}
    backup = {}
    while queue:
        queue.sort(key = lambda x : f[x])
        node = queue.pop(0)
        visited.append(node)
        if node == goal:
            print("Result(SMA*):",print_path(node, parent),"Path cost =",g[node])
            return True
        successors = []
        for adj in graph[node]:
            if adj in visited:
                continue
            gcost = g[node] + graph[node][adj]
            fcost = gcost + h[adj]
            if adj in queue:
                if fcost >= f[adj]:
                    continue
            elif len(queue) < bound:
                    queue.append(adj)
            else:
                worst = max(queue, key = lambda x : f[x])
                if fcost < f[worst]:
                    backup[worst] = f[worst]
                    queue.remove(worst)
                    queue.append(adj)
                else:
                    continue
            g[adj] = gcost
            f[adj] = fcost
            parent[adj] = node
            successors.append(adj)
        if not successors and node in backup:
            f[node] = backup[node]
        elif not successors:
            f[node] = float('inf')
    return False
from random import randint as rint
def genetic(gen, pop):
    def mutate(b1, b2):
        b1, b2 = list(b1), list(b2)
        x, y = rint(0,7), rint(0,7)
        b1[x], b2[x] = b2[x], b1[x]
        b1[y] = str(int(y) + 1)
        return (''.join(b1),''.join(b2))
    def crossover(b1, b2):
        b1, b2 = list(b1), list(b2)
        x = rint(1,7)
        b1[0:x], b2[0:x] = b2[0:x], b1[0:x]
        return (''.join(b1), ''.join(b2))
    def fitness(b):
        b = list(b)
        attacks = 0
        for i in range(8):
            for j in range(i+1, 8):
                if b[i] == b[j] or abs(int(b[i]) - int(b[j])) == j - i:
                    attacks += 1
        return attacks
    i = 0
    pq = []
    pq.append((fitness(pop[0]),pop[0]))
    pq.append((fitness(pop[1]),pop[1]))
    for i in range(gen+1):
        f1, b1 = pq.pop(0)
        f2, b2 = pq.pop(0)
        pq.clear()
        if f1 == 0:
            print("Goal State:",b1,"Generation:",i+1)
            return
        elif f2 == 0:
            print("Goal State:",b2,"Generation:",i+1)
            return
        x1, x2 = crossover(b1, b2)
        x3, x4 = crossover(b2, b1)
        new_pop = [(x1, x2), (x3, x4), mutate(x1, x2), mutate(x2, x1)]
        for child in new_pop:
            pq.append((fitness(child[0]), child[0]))
            pq.append((fitness(child[1]), child[1]))
        pq.append((f1, b1))
        pq.append((f2, b2))
        pq.sort(key = lambda x : x[0])
    print("Most Evolved State:",pq[0][1],"Generation:",i,"Attacks:",pq[0][0])
def main():
    graph = {"A" : {"B":9,"C":4,"D":7},
             "B" : {"A":9,"E":11},
             "C" : {"A":4,"E":17,"F":12},
             "D" : {"A":7,"F":14},
             "E" : {"B":11,"G":5,"C":17},
             "F" : {"D":14,"C":12,"G":9},
             "G" : {"E":5,"F":9}}
    heuristic = {"A":21,"B":14,"C":18,"D":18,"E":5,"F":8,"G":0}
    #pretty_print(graph, title = "Graph", weighted = True, directed = True, heuristic = heuristic)
    display(graph)
    BFS(graph, "A", "F")
    DFS(graph, "A", "F")
    UCS(graph, "A", "G")
    DLS(graph, "A", "G", 3)
    IDS(graph, "A", "G")
    AStar(graph, "A", "G", heuristic)
    IDAStar(graph, "A", "G", heuristic)
    #graph, heuristic, bound, source, goal = get_input(heuristic = True,weighted = True,bound = True)
    SMAStar(graph, "A", "G", heuristic, bound = 3)
    print("Genetic Algorithm Example 1 ", end="")
    genetic(1000, ["32152911","24748552"])
    print("Genetic Algorithm Example 2 ", end="")
    genetic(1000, ["57142860","56782463"])
main()
"""
bfs = """
import networkx as nx
import matplotlib.pyplot as plt
def display(graph):
    g = nx.Graph(graph)
    nx.draw(g, with_labels = True)
    plt.show()
    plt.clf()
def print_path(node, parent):
    if node != None:
        return print_path(parent[node], parent) + [node]
    return []
def BFS(graph, start, goal):
    queue = [start]
    visited = []
    parent = {start : None}
    while queue:
        node = queue.pop(0)#First element
        visited.append(node)
        if node == goal:
            print("Result(BFS):",print_path(node, parent))
            return True
        for adj in graph[node]:
            if adj not in visited and adj not in queue:
                queue.append(adj)
                parent[adj] = node
    return False
def test():
    graph = {"A" : {"B":0,"C":0,"D":0},
             "B" : {"A":0,"E":0},
             "C" : {"A":0,"E":0,"F":0},
             "D" : {"A":0,"F":0},
             "E" : {"B":0,"G":0,"C":0},
             "F" : {"D":0,"C":0,"G":0},
             "G" : {"E":0,"F":0}}
    display(graph)
    BFS(graph, "A", "F")
def main():
    #test()
    graph = {}
    for _ in range(int(input("Enter no of edges: "))):
        u, v = input("Enter edge(u, v): ").split()
        graph[u] = graph.get(u,{})
        graph[v] = graph.get(v,{})
        graph[u][v] = 0
        graph[v][u] = 0
    source, goal = input("Enter source and goal: ").split()
    display(graph)
    BFS(graph, source, goal)
    '''
    Sample Input/Output
    Enter no of edges:  9
    Enter edge(u, v):  A B
    Enter edge(u, v):  A C
    Enter edge(u, v):  A D
    Enter edge(u, v):  B E
    Enter edge(u, v):  C E
    Enter edge(u, v):  C F
    Enter edge(u, v):  D F
    Enter edge(u, v):  E G
    Enter edge(u, v):  F G
    Enter source and goal:  A F
    Result(BFS): ['A', 'C', 'F']
    '''
main()
"""
dfs = """
import networkx as nx
import matplotlib.pyplot as plt
def display(graph):
    g = nx.Graph(graph)
    nx.draw(g, with_labels = True)
    plt.show()
    plt.clf()
def print_path(node, parent):
    if node != None:
        return print_path(parent[node], parent) + [node]
    return []
def DFS(graph, start, goal):
    stack = [start]
    visited = []
    parent = {start : None}
    while stack:
        node = stack.pop()#last element
        visited.append(node)
        if node == goal:
            print("Result(DFS):",print_path(node, parent))
            return True
        for adj in graph[node]:
            if adj not in visited and adj not in stack:
                stack.append(adj)
                parent[adj] = node
    return False
def test():
    graph = {"A" : {"B":0,"C":0,"D":0},
             "B" : {"A":0,"E":0},
             "C" : {"A":0,"E":0,"F":0},
             "D" : {"A":0,"F":0},
             "E" : {"B":0,"G":0,"C":0},
             "F" : {"D":0,"C":0,"G":0},
             "G" : {"E":0,"F":0}}
    display(graph)
    DFS(graph, "A", "F")
def main():
    #test()
    graph = {}
    for _ in range(int(input("Enter no of edges: "))):
        u, v = input("Enter edge(u, v): ").split()
        graph[u] = graph.get(u,{})
        graph[v] = graph.get(v,{})
        graph[u][v] = 0
        graph[v][u] = 0
    source, goal = input("Enter source and goal: ").split()
    display(graph)
    DFS(graph, source, goal)
    '''
    Sample Input/Output
    Enter no of edges:  9
    Enter edge(u, v):  A B
    Enter edge(u, v):  A C
    Enter edge(u, v):  A D
    Enter edge(u, v):  B E
    Enter edge(u, v):  C E
    Enter edge(u, v):  C F
    Enter edge(u, v):  D F
    Enter edge(u, v):  E G
    Enter edge(u, v):  F G
    Enter source and goal:  A F
    Result(DFS): ['A', 'D', 'F']
    '''
main()
"""
ucs = """
import networkx as nx
import matplotlib.pyplot as plt
def display(graph):
    g = nx.DiGraph()
    for u in graph:
        g.add_node(u)
        for v in graph[u]:
            g.add_edge(u, v, weight = graph[u][v])
    pos = nx.circular_layout(g)
    nx.draw(g, pos, with_labels = True)
    nx.draw_networkx_edge_labels(g, pos, edge_labels = nx.get_edge_attributes(g, 'weight'))
    plt.show()
    plt.clf()
def print_path(node, parent):
    if node != None:
        return print_path(parent[node], parent) + [node]
    return []
def UCS(graph, start, goal):
    queue = [start]
    visited = []
    parent = {start : None}
    cost = {start : 0}
    while queue:
        queue.sort(key = lambda x : cost[x])
        node = queue.pop(0)
        visited.append(node)
        if node == goal:
            print("Result(UCS):",print_path(node, parent),"Path cost =",cost[node])
            return True
        for adj in graph[node]:
            if adj not in visited:
                new_cost = cost[node] + graph[node][adj]
                if adj not in queue:
                    queue.append(adj)
                elif new_cost > cost[adj]:
                    continue
                cost[adj] = new_cost
                parent[adj] = node
    return False
def test():
    graph = {"A" : {"B":9,"C":4,"D":7},
             "B" : {"A":9,"E":11},
             "C" : {"A":4,"E":17,"F":12},
             "D" : {"A":7,"F":14},
             "E" : {"B":11,"G":5,"C":17},
             "F" : {"D":14,"C":12,"G":9},
             "G" : {"E":5,"F":9}}
    display(graph)
    UCS(graph, "A", "G")
def main():
    #test()
    graph = {}
    for _ in range(int(input("Enter no of edges: "))):
        u, v, w = input("Enter edge(u, v, weight): ").split()
        graph[u] = graph.get(u,{})
        graph[v] = graph.get(v,{})
        graph[u][v] = int(w)
        graph[v][u] = int(w)
    source, goal = input("Enter source and goal: ").split()
    display(graph)
    UCS(graph, source, goal)
    '''
    Sample Input/Output
    Enter no of edges:  9
    Enter edge(u, v, weight):  A B 9
    Enter edge(u, v, weight):  A C 4
    Enter edge(u, v, weight):  A D 7
    Enter edge(u, v, weight):  B E 11
    Enter edge(u, v, weight):  C E 17
    Enter edge(u, v, weight):  C F 12
    Enter edge(u, v, weight):  D F 14
    Enter edge(u, v, weight):  E G 5
    Enter edge(u, v, weight):  F G 9
    Enter source and goal:  A G
    Result(UCS): ['A', 'B', 'E', 'G'] Path cost = 25
    '''
main()
"""
dls = """
import networkx as nx
import matplotlib.pyplot as plt
def display(graph):
    g = nx.Graph(graph)
    nx.draw(g, with_labels = True)
    plt.show()
    plt.clf()
def print_path(node, parent):
    if node != None:
        return print_path(parent[node], parent) + [node]
    return []
def DLS(graph, start, goal, limit):
    result = recursive_dls(graph, start, goal, limit, [start])
    print("Result(DLS):",result)
def recursive_dls(graph, node, goal, limit, visited):
    if node == goal:
        return [node]
    elif limit == 0:
        return 'cutoff'
    else:
        status = 'failure'
        for adj in graph[node]:
            if adj not in visited:
                visited.append(adj)
                result = recursive_dls(graph, adj, goal, limit - 1, visited)
                if result == 'cutoff':
                    status = 'cutoff'
                    visited.remove(adj)
                elif result != 'failure':
                    return [node] + result
        return status
def test():
    graph = {"A" : {"B":0,"C":0,"D":0},
             "B" : {"A":0,"E":0},
             "C" : {"A":0,"E":0,"F":0},
             "D" : {"A":0,"F":0},
             "E" : {"B":0,"G":0,"C":0},
             "F" : {"D":0,"C":0,"G":0},
             "G" : {"E":0,"F":0}}
    display(graph)
    DLS(graph, "A", "G", 3)
def main():
    #test()
    graph = {}
    for _ in range(int(input("Enter no of edges: "))):
        u, v = input("Enter edge(u, v): ").split()
        graph[u] = graph.get(u,{})
        graph[v] = graph.get(v,{})
        graph[u][v] = 0
        graph[v][u] = 0
    source, goal, limit = input("Enter source and goal and limit: ").split()    
    display(graph)
    DLS(graph, source, goal, int(limit))
    '''
    Sample Input/Output
    Enter no of edges:  9
    Enter edge(u, v):  A B
    Enter edge(u, v):  A C
    Enter edge(u, v):  A D
    Enter edge(u, v):  B E
    Enter edge(u, v):  C E
    Enter edge(u, v):  C F
    Enter edge(u, v):  D F
    Enter edge(u, v):  E G
    Enter edge(u, v):  F G
    Enter source and goal and limit:  A G 3
    Result(DLS): ['A', 'B', 'E', 'G']
    '''
main()
"""
ids = """
import networkx as nx
import matplotlib.pyplot as plt
def display(graph):
    g = nx.Graph(graph)
    nx.draw(g, with_labels = True)
    plt.show()
    plt.clf()
def print_path(node, parent):
    if node != None:
        return print_path(parent[node], parent) + [node]
    return []
def recursive_dls(graph, node, goal, limit, visited):
    if node == goal:
        return [node]
    elif limit == 0:
        return 'cutoff'
    else:
        status = 'failure'
        for adj in graph[node]:
            if adj not in visited:
                visited.append(adj)
                result = recursive_dls(graph, adj, goal, limit - 1, visited)
                if result == 'cutoff':
                    status = 'cutoff'
                    visited.remove(adj)
                elif result != 'failure':
                    return [node] + result
        return status
def IDS(graph, start, goal):
    depth = 0
    while True:
        result = recursive_dls(graph, start, goal, depth, [start])
        print("Result(IDS/IDDFS):",result,"at depth limit =",depth)
        if result != 'cutoff':
            return
        depth += 1
def test():
    graph = {"A" : {"B":0,"C":0,"D":0},
             "B" : {"A":0,"E":0},
             "C" : {"A":0,"E":0,"F":0},
             "D" : {"A":0,"F":0},
             "E" : {"B":0,"G":0,"C":0},
             "F" : {"D":0,"C":0,"G":0},
             "G" : {"E":0,"F":0}}
    display(graph)
    IDS(graph, "A", "G")
def main():
    #test()
    graph = {}
    for _ in range(int(input("Enter no of edges: "))):
        u, v = input("Enter edge(u, v): ").split()
        graph[u] = graph.get(u,{})
        graph[v] = graph.get(v,{})
        graph[u][v] = 0
        graph[v][u] = 0
    source, goal= input("Enter source and goal: ").split()    
    display(graph)
    IDS(graph, source, goal)
    '''
    Sample Input/Output
    Enter no of edges:  9
    Enter edge(u, v):  A B
    Enter edge(u, v):  A C
    Enter edge(u, v):  A D
    Enter edge(u, v):  B E
    Enter edge(u, v):  C E
    Enter edge(u, v):  C F
    Enter edge(u, v):  D F
    Enter edge(u, v):  E G
    Enter edge(u, v):  F G
    Enter source and goal:  A G
    Result(IDS/IDDFS): cutoff at depth limit = 0
    Result(IDS/IDDFS): cutoff at depth limit = 1
    Result(IDS/IDDFS): cutoff at depth limit = 2
    Result(IDS/IDDFS): ['A', 'B', 'E', 'G'] at depth limit = 3
    '''
main()
"""
astar = """
import networkx as nx
import matplotlib.pyplot as plt
def display(graph):
    g = nx.DiGraph()
    for u in graph:
        g.add_node(u)
        for v in graph[u]:
            g.add_edge(u, v, weight = graph[u][v])
    pos = nx.circular_layout(g)
    nx.draw(g, pos, with_labels = True)
    nx.draw_networkx_edge_labels(g, pos, edge_labels = nx.get_edge_attributes(g, 'weight'))
    plt.show()
    plt.clf()
def print_path(node, parent):
    if node != None:
        return print_path(parent[node], parent) + [node]
    return []
def AStar(graph, start, goal, h):
    queue = [start]
    visited = []
    parent = {start : None}
    g = {start : 0}
    f = {start : h[start]}
    while queue:
        queue.sort(key = lambda x : f[x])
        node = queue.pop(0)
        visited.append(node)
        if node == goal:
            print("Result(A*):",print_path(node, parent),"Path cost =",g[node])
            return True
        for adj in graph[node]:
            if adj not in visited:
                gcost = g[node] + graph[node][adj]
                fcost = gcost + h[adj]
                if adj not in queue:
                    queue.append(adj)
                elif fcost > f[adj]:
                    continue
                g[adj] = gcost
                f[adj] = fcost
                parent[adj] = node
    return False
def test():
    graph = {"A" : {"B":9,"C":4,"D":7},
             "B" : {"A":9,"E":11},
             "C" : {"A":4,"E":17,"F":12},
             "D" : {"A":7,"F":14},
             "E" : {"B":11,"G":5,"C":17},
             "F" : {"D":14,"C":12,"G":9},
             "G" : {"E":5,"F":9}}
    heuristic = {"A":21,"B":14,"C":18,"D":18,"E":5,"F":8,"G":0}
    print("Heuristic: ",heuristic)
    display(graph)
    AStar(graph, "A", "G", heuristic)
def main():
    #test()
    graph = {}
    h = {}
    for _ in range(int(input("Enter no of nodes: "))):
        x, hval = input("Enter node and heuristic value: ").split()
        h[x] = int(hval)
    for _ in range(int(input("Enter no of edges: "))):
        u, v, w = input("Enter edge(u, v, weight): ").split()
        graph[u] = graph.get(u,{})
        graph[v] = graph.get(v,{})
        graph[u][v] = int(w)
        graph[v][u] = int(w)
    source, goal = input("Enter source and goal: ").split()
    display(graph)
    AStar(graph, source, goal, h)
    '''
    Sample Input/Output
    Enter no of nodes:  7
    Enter node and heuristic value:  A 21
    Enter node and heuristic value:  B 14
    Enter node and heuristic value:  C 18
    Enter node and heuristic value:  D 18
    Enter node and heuristic value:  E 5
    Enter node and heuristic value:  F 8
    Enter node and heuristic value:  G 0
    Enter no of edges:  9
    Enter edge(u, v, weight):  A B 9
    Enter edge(u, v, weight):  A C 4
    Enter edge(u, v, weight):  A D 7
    Enter edge(u, v, weight):  B E 11
    Enter edge(u, v, weight):  C E 17
    Enter edge(u, v, weight):  C F 12
    Enter edge(u, v, weight):  D F 14
    Enter edge(u, v, weight):  E G 5
    Enter edge(u, v, weight):  F G 9
    Enter source and goal:  A G
    Result(A*): ['A', 'B', 'E', 'G'] Path cost = 25
    '''
main()
"""
idastar = """
import networkx as nx
import matplotlib.pyplot as plt
def display(graph):
    g = nx.DiGraph()
    for u in graph:
        g.add_node(u)
        for v in graph[u]:
            g.add_edge(u, v, weight = graph[u][v])
    pos = nx.circular_layout(g)
    nx.draw(g, pos, with_labels = True)
    nx.draw_networkx_edge_labels(g, pos, edge_labels = nx.get_edge_attributes(g, 'weight'))
    plt.show()
    plt.clf()
def print_path(node, parent):
    if node != None:
        return print_path(parent[node], parent) + [node]
    return []
def IDAStar(graph, start, goal, h):
    def dfs(graph, parent, node, goal, g, h, th):
        f = g + h[node]
        if f > th:
            return None, f
        if node == goal:
            return node, f
        min_th = inf
        for adj in graph[node]:
            result, temp_th = dfs(graph, parent, adj, goal, g + graph[node][adj], h, th)
            if result is not None:
                parent[adj] = node
                return result, temp_th
            elif temp_th < min_th:
                min_th = temp_th
        return None, min_th
    
    inf = 9999999
    parent = {start : None}    
    th = h[start]
    while True:
        result, new_th = dfs(graph, parent, start, goal, 0, h, th)
        if result is not None:
            result = print_path(result, parent)
            cost = sum([graph[n1][n2] for n1, n2 in zip(result,result[1:])])
            print("Result(IDA*):",result,"Path cost =",cost)
            return
        elif new_th == inf:
            print("Result(IDA*): failure")
            return
        th = new_th
def test():
    graph = {"A" : {"B":9,"C":4,"D":7},
             "B" : {"A":9,"E":11},
             "C" : {"A":4,"E":17,"F":12},
             "D" : {"A":7,"F":14},
             "E" : {"B":11,"G":5,"C":17},
             "F" : {"D":14,"C":12,"G":9},
             "G" : {"E":5,"F":9}}
    heuristic = {"A":21,"B":14,"C":18,"D":18,"E":5,"F":8,"G":0}
    print("Heuristic: ",heuristic)
    display(graph)
    IDAStar(graph, "A", "G", heuristic)
def main():
    #test()
    graph = {}
    h = {}
    for _ in range(int(input("Enter no of nodes: "))):
        x, hval = input("Enter node and heuristic value: ").split()
        h[x] = int(hval)
    for _ in range(int(input("Enter no of edges: "))):
        u, v, w = input("Enter edge(u, v, weight): ").split()
        graph[u] = graph.get(u,{})
        graph[v] = graph.get(v,{})
        graph[u][v] = int(w)
        graph[v][u] = int(w)
    source, goal = input("Enter source and goal: ").split()
    display(graph)
    IDAStar(graph, source, goal, h)
    '''
    Sample Input/Output
    Enter no of nodes:  7
    Enter node and heuristic value:  A 21
    Enter node and heuristic value:  B 14
    Enter node and heuristic value:  C 18
    Enter node and heuristic value:  D 18
    Enter node and heuristic value:  E 5
    Enter node and heuristic value:  F 8
    Enter node and heuristic value:  G 0
    Enter no of edges:  9
    Enter edge(u, v, weight):  A B 9
    Enter edge(u, v, weight):  A C 4
    Enter edge(u, v, weight):  A D 7
    Enter edge(u, v, weight):  B E 11
    Enter edge(u, v, weight):  C E 17
    Enter edge(u, v, weight):  C F 12
    Enter edge(u, v, weight):  D F 14
    Enter edge(u, v, weight):  E G 5
    Enter edge(u, v, weight):  F G 9
    Enter source and goal:  A G
    Result(IDA*): ['A', 'B', 'E', 'G'] Path cost = 25
    '''
main()
"""
smastar = """
import networkx as nx
import matplotlib.pyplot as plt
def display(graph):
    g = nx.DiGraph()
    for u in graph:
        g.add_node(u)
        for v in graph[u]:
            g.add_edge(u, v, weight = graph[u][v])
    pos = nx.circular_layout(g)
    nx.draw(g, pos, with_labels = True)
    nx.draw_networkx_edge_labels(g, pos, edge_labels = nx.get_edge_attributes(g, 'weight'))
    plt.show()
    plt.clf()
def print_path(node, parent):
    if node != None:
        return print_path(parent[node], parent) + [node]
    return []
def SMAStar(graph, start, goal, h, bound):
    queue = [start]
    visited = []
    parent = {start : None}
    g = {start : 0}
    f = {start : h[start]}
    backup = {}
    while queue:
        queue.sort(key = lambda x : f[x])
        node = queue.pop(0)
        visited.append(node)
        if node == goal:
            print("Result(SMA*):",print_path(node, parent),"Path cost =",g[node])
            return True
        successors = []
        for adj in graph[node]:
            if adj in visited:
                continue
            gcost = g[node] + graph[node][adj]
            fcost = gcost + h[adj]
            if adj in queue:
                if fcost >= f[adj]:
                    continue
            elif len(queue) < bound:
                    queue.append(adj)
            else:
                worst = max(queue, key = lambda x : f[x])
                if fcost < f[worst]:
                    backup[worst] = f[worst]
                    queue.remove(worst)
                    queue.append(adj)
                else:
                    continue
            g[adj] = gcost
            f[adj] = fcost
            parent[adj] = node
            successors.append(adj)
        if not successors and node in backup:
            f[node] = backup[node]
        elif not successors:
            f[node] = float('inf')
    return False
def test():
    graph = {"A" : {"B":9,"C":4,"D":7},
             "B" : {"A":9,"E":11},
             "C" : {"A":4,"E":17,"F":12},
             "D" : {"A":7,"F":14},
             "E" : {"B":11,"G":5,"C":17},
             "F" : {"D":14,"C":12,"G":9},
             "G" : {"E":5,"F":9}}
    heuristic = {"A":21,"B":14,"C":18,"D":18,"E":5,"F":8,"G":0}
    print("Heuristic: ",heuristic)
    display(graph)
    SMAStar(graph, "A", "G", heuristic, 4)
def main():
    #test()
    graph = {}
    h = {}
    for _ in range(int(input("Enter no of nodes: "))):
        x, hval = input("Enter node and heuristic value: ").split()
        h[x] = int(hval)
    for _ in range(int(input("Enter no of edges: "))):
        u, v, w = input("Enter edge(u, v, weight): ").split()
        graph[u] = graph.get(u,{})
        graph[v] = graph.get(v,{})
        graph[u][v] = int(w)
        graph[v][u] = int(w)
    source, goal, bound = input("Enter source and goal and bound: ").split()
    display(graph)
    SMAStar(graph, source, goal, h, int(bound))
    '''
    Sample Input/Output
    Enter no of nodes:  7
    Enter node and heuristic value:  A 21
    Enter node and heuristic value:  B 14
    Enter node and heuristic value:  C 18
    Enter node and heuristic value:  D 18
    Enter node and heuristic value:  E 5
    Enter node and heuristic value:  F 8
    Enter node and heuristic value:  G 0
    Enter no of edges:  9
    Enter edge(u, v, weight):  A B 9
    Enter edge(u, v, weight):  A C 4
    Enter edge(u, v, weight):  A D 7
    Enter edge(u, v, weight):  B E 11
    Enter edge(u, v, weight):  C E 17
    Enter edge(u, v, weight):  C F 12
    Enter edge(u, v, weight):  D F 14
    Enter edge(u, v, weight):  E G 5
    Enter edge(u, v, weight):  F G 9
    Enter source and goal and bound:  A G 4
    Result(SMA*): ['A', 'C', 'F', 'G'] Path cost = 25
    '''
main()
"""
genetic = """
from random import randint as rint
def genetic(gen, pop):
    def mutate(b1, b2):
        b1, b2 = list(b1), list(b2)
        x, y = rint(0,7), rint(0,7)
        b1[x], b2[x] = b2[x], b1[x]
        b1[y] = str(int(y) + 1)
        return (''.join(b1),''.join(b2))
    def crossover(b1, b2):
        b1, b2 = list(b1), list(b2)
        x = rint(1,7)
        b1[0:x], b2[0:x] = b2[0:x], b1[0:x]
        return (''.join(b1), ''.join(b2))
    def fitness(b):
        b = list(b)
        attacks = 0
        for i in range(8):
            for j in range(i+1, 8):
                if b[i] == b[j] or abs(int(b[i]) - int(b[j])) == j - i:
                    attacks += 1
        return attacks
    i = 0
    pq = []
    pq.append((fitness(pop[0]),pop[0]))
    pq.append((fitness(pop[1]),pop[1]))
    for i in range(gen+1):
        f1, b1 = pq.pop(0)
        f2, b2 = pq.pop(0)
        pq.clear()
        if f1 == 0:
            print("Goal State:",b1,"Generation:",i+1)
            return
        elif f2 == 0:
            print("Goal State:",b2,"Generation:",i+1)
            return
        x1, x2 = crossover(b1, b2)
        x3, x4 = crossover(b2, b1)
        new_pop = [(x1, x2), (x3, x4), mutate(x1, x2), mutate(x2, x1)]
        for child in new_pop:
            pq.append((fitness(child[0]), child[0]))
            pq.append((fitness(child[1]), child[1]))
        pq.append((f1, b1))
        pq.append((f2, b2))
        pq.sort(key = lambda x : x[0])
    print("Most Evolved State:",pq[0][1],"Generation:",i,"Attacks:",pq[0][0])
def main():
    print("Genetic Algorithm Example 1 ", end="")
    genetic(1000, ["32152911","24748552"])
    print("Genetic Algorithm Example 2 ", end="")
    genetic(1000, ["57142860","56782463"])
    '''
    Sample input/output (can change randomly)
    Genetic Algorithm Example 1 Most Evolved State: 24742951 Generation: 1000 Attacks: 2
    Genetic Algorithm Example 2 Goal State: 57142863 Generation: 2
    '''
main()
"""

def display(name = ""):
    try:
        match name.lower():
            case "bfs":     print(bfs)
            case "dfs":     print(dfs)
            case "ucs":     print(ucs)
            case "dls":     print(dls)
            case "ids":     print(ids)
            case "astar":   print(astar)
            case "idastar": print(idastar)
            case "smastar": print(smastar)
            case "genetic": print(genetic)
            case _:         print(code)
    except:
        print(code)