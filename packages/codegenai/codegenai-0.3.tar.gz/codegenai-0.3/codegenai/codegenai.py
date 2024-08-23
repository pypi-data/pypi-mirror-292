code = """
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
def main():
    graph = {"A" : {"B":9,"C":4,"D":7},
            "B" : {"A":9,"E":11},
            "C" : {"A":4,"E":17,"F":12},
            "D" : {"A":7,"F":14},
            "E" : {"B":11,"G":5,"C":17},
            "F" : {"D":14,"C":12,"G":9},
            "G" : {"E":5,"F":9}}
    heuristic = {"A":21,"B":14,"C":18,"D":18,"E":5,"F":8,"G":0}
    BFS(graph, "A", "F")
    DFS(graph, "A", "F")
    UCS(graph, "A", "G")
    DLS(graph, "A", "G", 3)
    IDS(graph, "A", "G")
    AStar(graph, "A", "G", heuristic)
    IDAStar(graph, "A", "G", heuristic)

if __name__ == '__main__':
    main()
"""
def display():
    print(code)