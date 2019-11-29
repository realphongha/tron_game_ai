import socketio
import json
import heapq
import traceback
from collections import deque

class Matrix:
    def __init__(self, matrix, turn, pos, opp_pos):
        self.matrix = list(matrix) # the board
        self.turn = turn # current turn
        self.pos = pos # player position
        self.opp_pos = opp_pos # opponent position

    def avail_moves(self):
        if self.pos[0] + 1 < SIZE:
            if self.matrix[(self.pos[0] + 1) * SIZE + self.pos[1]] == 0:
                yield 1
        if self.pos[0] - 1 >= 0:
            if self.matrix[(self.pos[0] - 1) * SIZE + self.pos[1]] == 0:
                yield 2
        if self.pos[1] + 1 < SIZE:
            if self.matrix[self.pos[0] * SIZE + self.pos[1] + 1] == 0:
                yield 3
        if self.pos[1] - 1 >= 0:
            if self.matrix[self.pos[0] * SIZE + self.pos[1] - 1] == 0:
                yield 4

    def avail_moves_1_player(self):
        if self.pos[0] + 1 < SIZE:
            if self.matrix[(self.pos[0] + 1) * SIZE + self.pos[1]] == 0:
                yield 1
        if self.pos[0] - 1 >= 0:
            if self.matrix[(self.pos[0] - 1) * SIZE + self.pos[1]] == 0:
                yield 2
        if self.pos[1] + 1 < SIZE:
            if self.matrix[self.pos[0] * SIZE + self.pos[1] + 1] == 0:
                yield 3
        if self.pos[1] - 1 >= 0:
            if self.matrix[self.pos[0] * SIZE + self.pos[1] - 1] == 0:
                yield 4

    def move(self, dir):
        # dir = direction
        if dir == 1:
            self.matrix[(self.pos[0] + 1) * SIZE + self.pos[1]] = self.turn
            self.turn = reverse[self.turn]
            self.pos = (self.pos[0] + 1, self.pos[1])
            self.pos, self.opp_pos = self.opp_pos, self.pos
        elif dir == 2:
            self.matrix[(self.pos[0] - 1) * SIZE + self.pos[1]] = self.turn
            self.turn = reverse[self.turn]
            self.pos = (self.pos[0] - 1, self.pos[1])
            self.pos, self.opp_pos = self.opp_pos, self.pos
        elif dir == 3:
            self.matrix[self.pos[0] * SIZE + self.pos[1] + 1] = self.turn
            self.turn = reverse[self.turn]
            self.pos = (self.pos[0], self.pos[1] + 1)
            self.pos, self.opp_pos = self.opp_pos, self.pos
        elif dir == 4:
            self.matrix[self.pos[0] * SIZE + self.pos[1] - 1] = self.turn
            self.turn = reverse[self.turn]
            self.pos = (self.pos[0], self.pos[1] - 1)
            self.pos, self.opp_pos = self.opp_pos, self.pos
        elif dir == -1:
            self.matrix[self.opp_pos[0] * SIZE + self.opp_pos[1]] = 0
            self.turn = reverse[self.turn]
            self.opp_pos = (self.opp_pos[0] - 1, self.opp_pos[1])
            self.pos, self.opp_pos = self.opp_pos, self.pos
        elif dir == -2:
            self.matrix[self.opp_pos[0] * SIZE + self.opp_pos[1]] = 0
            self.turn = reverse[self.turn]
            self.opp_pos = (self.opp_pos[0] + 1, self.opp_pos[1])
            self.pos, self.opp_pos = self.opp_pos, self.pos
        elif dir == -3:
            self.matrix[self.opp_pos[0] * SIZE + self.opp_pos[1]] = 0
            self.turn = reverse[self.turn]
            self.opp_pos = (self.opp_pos[0], self.opp_pos[1] - 1)
            self.pos, self.opp_pos = self.opp_pos, self.pos
        elif dir == -4:
            self.matrix[self.opp_pos[0] * SIZE + self.opp_pos[1]] = 0
            self.turn = reverse[self.turn]
            self.opp_pos = (self.opp_pos[0], self.opp_pos[1] + 1)
            self.pos, self.opp_pos = self.opp_pos, self.pos

    def move_1_player(self, dir):
        # dir = direction
        if dir == 1:
            self.matrix[(self.pos[0] + 1) * SIZE + self.pos[1]] = self.turn
            self.pos = (self.pos[0] + 1, self.pos[1])
        elif dir == 2:
            self.matrix[(self.pos[0] - 1) * SIZE + self.pos[1]] = self.turn
            self.pos = (self.pos[0] - 1, self.pos[1])
        elif dir == 3:
            self.matrix[self.pos[0] * SIZE + self.pos[1] + 1] = self.turn
            self.pos = (self.pos[0], self.pos[1] + 1)
        elif dir == 4:
            self.matrix[self.pos[0] * SIZE + self.pos[1] - 1] = self.turn
            self.pos = (self.pos[0], self.pos[1] - 1)
        elif dir == -1:
            self.matrix[self.pos[0] * SIZE + self.pos[1]] = 0
            self.pos = (self.pos[0] - 1, self.pos[1])
        elif dir == -2:
            self.matrix[self.pos[0] * SIZE + self.pos[1]] = 0
            self.pos = (self.pos[0] + 1, self.pos[1])
        elif dir == -3:
            self.matrix[self.pos[0] * SIZE + self.pos[1]] = 0
            self.pos = (self.pos[0], self.pos[1] - 1)
        elif dir == -4:
            self.matrix[self.pos[0] * SIZE + self.pos[1]] = 0
            self.pos = (self.pos[0], self.pos[1] + 1)

    def avail_moves_coor(self, pos):
        if pos[0] + 1 < SIZE:
            if self.matrix[(pos[0] + 1) * SIZE + pos[1]] == 0:
                yield (pos[0] + 1, pos[1])
        if pos[0] - 1 >= 0:
            if self.matrix[(pos[0] - 1) * SIZE + pos[1]] == 0:
                yield (pos[0] - 1, pos[1])
        if pos[1] + 1 < SIZE:
            if self.matrix[pos[0] * SIZE + pos[1] + 1] == 0:
                yield (pos[0], pos[1] + 1)
        if pos[1] - 1 >= 0:
            if self.matrix[pos[0] * SIZE + pos[1] - 1] == 0:
                yield (pos[0], pos[1] - 1)

    def avail_moves_count(self, pos):
        count = 0
        if pos[0] + 1 < SIZE:
            if self.matrix[(pos[0] + 1) * SIZE + pos[1]] == 0:
                count += 1
        if pos[0] - 1 >= 0:
            if self.matrix[(pos[0] - 1) * SIZE + pos[1]] == 0:
                count += 1
        if pos[1] + 1 < SIZE:
            if self.matrix[pos[0] * SIZE + pos[1] + 1] == 0:
                count += 1
        if pos[1] - 1 >= 0:
            if self.matrix[pos[0] * SIZE + pos[1] - 1] == 0:
                count += 1
        return count

    def flood_fill_count(self, cur_pos):
        added = {cur_pos}
        wasnt_popped = {cur_pos}
        while wasnt_popped:
            pos = wasnt_popped.pop()
            for next_pos in self.avail_moves_coor(pos):
                if next_pos not in added:
                    added.add(next_pos)
                    wasnt_popped.add(next_pos)
        return len(added)

    def flood_fill_count_checkerboard(self, cur_pos):
        visited = {cur_pos: True} 
        stack = [cur_pos]
        count_red = -1
        count_black = 0
        while stack:
            pos = stack.pop()
            if visited[pos]:
                count_red += 1
            else:
                count_black += 1
            for next_pos in self.avail_moves_coor(pos): 
                if next_pos not in visited: 
                    visited[next_pos] = not visited[pos] 
                    stack.append(next_pos)
        return 2 * min(count_red, count_black)

    def flood_fill(self, cur_pos):
        added = {cur_pos}
        wasnt_popped = {cur_pos}
        while wasnt_popped:
            pos = wasnt_popped.pop()
            for next_pos in self.avail_moves_coor(pos):
                if next_pos not in added:
                    added.add(next_pos)
                    wasnt_popped.add(next_pos)
        return added

    def find_articulation_points(self):
        self.time = 0

        def dfs(node, p=-1):
            aps = 0
            visited.add(node)
            tin[node] = low[node] = self.time
            self.time += 1
            children = 0
            for next_node in self.avail_moves_coor(node):
                if next_node == p:
                    continue
                if next_node in visited:
                    low[node] = min(low[node], tin.get(next_node, -1))
                else:
                    dfs(next_node, node)
                    low[node] = min(low[node], low.get(next_node, -1))
                    if low.get(next_node, -1) >= tin[node] and p != -1:
                        aps += 1
                    children += 1
            if p == -1 and children > 1:
                aps += 1
            return aps

        visited = set()
        tin = {}
        low = {}
        avail = tuple(self.avail_moves_coor(self.pos))
        if avail:
            start = avail[0]
            return dfs(start)
        return 0

    def is_articulation_point(self):
        try:
            next_move = tuple(self.avail_moves_1_player())[0]
            cur_flood_fill = self.flood_fill_count(self.pos)
            self.move_1_player(next_move)
            next_flood_fill = self.flood_fill_count(self.pos)
            self.move_1_player(-next_move)
            return cur_flood_fill - 1 != next_flood_fill
        except:
            return False

    def is_separated(self):
        return len(self.flood_fill(self.pos) & self.flood_fill(self.opp_pos)) == 0

    def min_dist_bfs_obstacle(self, pos1, pos2):
        temp = self.matrix[pos2[0]*SIZE+pos2[1]]
        self.matrix[pos2[0]*SIZE+pos2[1]] = 0  

        visited = {pos1: 0} 
        queue = deque([pos1])
        while queue:
            pos = queue.popleft()
            if pos == pos2:
                self.matrix[pos2[0]*SIZE+pos2[1]] = temp
                return visited[pos]
            for next_pos in self.avail_moves_coor(pos): 
                if next_pos not in visited: 
                    visited[next_pos] = visited[pos] + 1 
                    queue.append(next_pos) 
        self.matrix[pos2[0]*SIZE+pos2[1]] = temp
        return 1000

    def min_dist_dijktra(self, pos):
        V = self.flood_fill(pos)
        d = {}
        for v in V:
            d[v] = 1000
        d[pos] = 0
        for v in self.avail_moves_coor(pos):
            d[v] = 1
        V.remove(pos)
        V = sorted(list(V), key = lambda x: -d[x])
        while V:
            u = V.pop()
            for v in self.avail_moves_coor(u):
                if d[v] > d[u] + 1:
                    d[v] = d[u] + 1
                    # V = sorted(V, key = lambda x: -d[x])
                    try:
                        V.remove(v)
                        for i in range(len(V)):
                            if d[V[i]] <= d[v]:
                                V.insert(i, v)
                                break
                    except:
                        pass
        return d

    def voronoi_point(self):
        point = 0
        me = self.min_dist_dijktra(self.pos)
        opp = self.min_dist_dijktra(self.opp_pos)
        for i in range(SIZE):
            for j in range(SIZE):
                if self.matrix[i * SIZE + j] == 0:
                    my_dist = me.get((i, j), 1000)
                    opp_dist = opp.get((i, j), 1000)
                    if my_dist > opp_dist:
                        point -= 1
                    elif my_dist == opp_dist == 1000:
                        pass
                    else:
                        point += 1
        return point

    def voronoi_edges(self):
        point = 0
        me = self.min_dist_dijktra(self.pos)
        opp = self.min_dist_dijktra(self.opp_pos)
        for i in range(SIZE):
            for j in range(SIZE):
                moves = self.avail_moves_count((i, j))
                if self.matrix[i * SIZE + j] == 0:
                    my_dist = me.get((i, j), 1000)
                    opp_dist = opp.get((i, j), 1000)
                    if my_dist > opp_dist:
                        point -= moves
                    elif my_dist == opp_dist == 1000:
                        pass
                    else:
                        point += moves
        return point

    def space_heuristic(self):
        return self.flood_fill_count_checkerboard(self.pos) - \
                    self.flood_fill_count_checkerboard(self.opp_pos)

    def activate_minimax(self):
        return self.min_dist_bfs_obstacle(self.pos, self.opp_pos) <= MINIMAX_DEPTH * 2

def minimax(state, depth, alpha, beta):
    max_val = -100000
    return_move = 0
    for next_move in state.avail_moves():
        state.move(next_move)
        next_min = min_value(state, depth + 1, alpha, beta)
        if max_val < next_min:
            max_val = next_min
            return_move = next_move
        alpha = max(alpha, max_val)
        state.move(-next_move)
    return return_move


def max_value(state, depth, alpha, beta):
    global turn
    if state.is_separated():
            point = 31 * state.space_heuristic() + 11 * state.voronoi_edges()
            # point = state.space_heuristic()
            if point > 1:
                return point * 1000
    if depth == MINIMAX_DEPTH:
        point = 31 * state.voronoi_point() + 11 * state.voronoi_edges()
        return point if state.turn == turn else -point
    max_val = -100000
    for next_move in state.avail_moves():
        state.move(next_move)
        max_val = max(max_val, min_value(state, depth + 1, alpha, beta))
        state.move(-next_move)
        alpha = max(alpha, max_val)
        if alpha >= beta:
            return max_val
    if max_val == -100000:
        return -100000 + depth
    return max_val


def min_value(state, depth, alpha, beta):
    global turn
    if depth == MINIMAX_DEPTH:
        point = 31 * state.voronoi_point() + 11 * state.voronoi_edges()
        return point if state.turn == turn else -point
    min_val = 100000
    for next_move in state.avail_moves():
        state.move(next_move)
        min_val = min(min_val, max_value(state, depth + 1, alpha, beta))
        state.move(-next_move)
        beta = min(beta, min_val)
        if alpha >= beta:
            return min_val
    if min_val == 100000:
        return 100000 - depth
    return min_val

def fill(state):
    max_val = -100000
    return_move = 0
    for next_move in state.avail_moves_1_player():
        state.move_1_player(next_move)
        point = filling_evaluate_with_depth(state, 1)
        state.move_1_player(-next_move)
        if point > max_val:
            max_val = point
            return_move = next_move
    return return_move

def filling_evaluate(state):
    moves_count = state.avail_moves_count(state.pos)
    if moves_count == 0:
        return -10000
    point = state.flood_fill_count(state.pos) + state.flood_fill_count_checkerboard(state.pos) - 2 * moves_count - 4 * state.find_articulation_points()
    if state.is_articulation_point():
        point -= 500
    return point

def filling_evaluate_with_depth(state, depth):
    moves_count = state.avail_moves_count(state.pos)
    if moves_count == 0:
        return -10000
    if depth == FILL_DEPTH:
        point = state.flood_fill_count(state.pos) + state.flood_fill_count_checkerboard(state.pos) - 2 * moves_count - 4 * state.find_articulation_points()
        if state.is_articulation_point():
            point -= 500
        return point
    max_val = -10000
    for next_move in state.avail_moves_1_player():
        state.move_1_player(next_move)
        max_val = max(max_val, filling_evaluate_with_depth(state, depth + 1))
        state.move_1_player(-next_move)
    return filling_evaluate(state) + max_val / (depth + 1)


reverse = {'X': 'O', 'O': 'X', 1: 2, 2: 1}
turn_sym = {'X': 1, 'O': 2}

FILL_DEPTH = 6 # space fill depth
MINIMAX_DEPTH = 5 # minimax depth
SIZE = 15
SQ_SIZE = SIZE * SIZE
while True:
    raw = raw_input("Choose your team (x/o): ")
    team = raw.upper()
    if team == 'O' or team == 'X':
        break
turn = turn_sym[team]
main_board = []
prepoint = {}
state = Matrix([], turn_sym[team], None, None) # init state

sio = socketio.Client()
@sio.event
def connect():
    print 'connection established'
    send_infor()
@sio.event
def send_infor():
    infor = json.dumps({"name": "Team O", "team": team, "members":[{"name": "Phong", "mssv": 20173299}]})
    sio.emit('Infor', infor)
@sio.event
def send_message(point): # point nuoc di tiep theo(x,y,type)
    sio.emit('moving', point) 

@sio.event
def disconnect():
    print 'disconnected from server'
@sio.on('new_Map')
def new_Map(data):
    try:
        prepoint = data[team]
        rivalpoint = data[reverse[team]]
        main_board = data["map"]
        SIZE = data["ncol"]
        SQ_SIZE = SIZE * SIZE
        state.matrix = []
        for i in range(SIZE):
            for j in range(SIZE):
                state.matrix.append(main_board[i][j])
        state.pos = (prepoint["x"], prepoint["y"])
        state.opp_pos = (rivalpoint["x"], rivalpoint["y"])
        # print(state.matrix, state.pos, state.opp_pos)
    except Exception:
        traceback.print_exc()
@sio.on('time_Out')
def time_Out(data):
    print("Time out!")
@sio.on('change_Turn')
def change_Turn(data):
    this_turn = data["turn"]
    result = data["result"]
    print(result)
    if result == team:
        print "You winnn!!!"
    elif result == "C":
        try:
            if this_turn == team:
                rivalpoint = data["point"] # toa do diem doi thu vua di (x,y,type)
                state.matrix[rivalpoint["x"]*SIZE + rivalpoint["y"]] = turn_sym[rivalpoint["type"]]
                state.opp_pos = (rivalpoint["x"], rivalpoint["y"])
                if state.is_separated():
                    state.move_1_player(fill(state))
                    xo, yo = state.pos
                else:
                    print(state.matrix, state.pos, state.opp_pos, state.turn)
                    state.move_1_player(minimax(state, 1, -100000, 100000))
                    xo, yo = state.pos
                    print(xo, yo)

                point = json.dumps({'x': xo, 'y': yo, 'type': team})
                send_message(point)
                print point
        except Exception:
            traceback.print_exc()
    else:
        print "You lose!!!"
sio.connect('http://localhost:3000', headers={'team': team})