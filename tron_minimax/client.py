# -*- coding: utf-8 -*-
import socketio
import json
import traceback
import numpy as np
from collections import deque
from time import time

class Matrix:
    def __init__(self, matrix, turn, pos, opp_pos):
        self.matrix = np.array(matrix) # bàn cờ
        self.turn = turn # ký hiệu turn hiện tại
        self.pos = pos # vị trí người chơi hiện tại
        self.opp_pos = opp_pos # vị trí đối thủ

    def avail_moves(self):
        # trả về các nước đi có thể
        if self.pos[0] + 1 < SIZE:
            if self.matrix[(self.pos[0] + 1) * SIZE + self.pos[1]] == 0:
                yield 1 # down
        if self.pos[0] - 1 >= 0:
            if self.matrix[(self.pos[0] - 1) * SIZE + self.pos[1]] == 0:
                yield 2 # up
        if self.pos[1] + 1 < SIZE:
            if self.matrix[self.pos[0] * SIZE + self.pos[1] + 1] == 0:
                yield 3 # right
        if self.pos[1] - 1 >= 0:
            if self.matrix[self.pos[0] * SIZE + self.pos[1] - 1] == 0:
                yield 4 # left

    def avail_next_states(self):
        # trả về các state tiếp theo có thể
        if self.pos[0] + 1 < SIZE:
            if self.matrix[(self.pos[0] + 1) * SIZE + self.pos[1]] == 0:
                self.matrix[(self.pos[0] + 1) * SIZE + self.pos[1]] = self.turn
                yield Matrix(self.matrix, reverse[self.turn], self.opp_pos, (self.pos[0] + 1, self.pos[1]))
                self.matrix[(self.pos[0] + 1) * SIZE + self.pos[1]] = 0
        if self.pos[0] - 1 >= 0:
            if self.matrix[(self.pos[0] - 1) * SIZE + self.pos[1]] == 0 and self.pos[0] - 1 >= 0:
                self.matrix[(self.pos[0] - 1) * SIZE + self.pos[1]] = self.turn
                yield Matrix(self.matrix, reverse[self.turn], self.opp_pos, (self.pos[0] - 1, self.pos[1]))
                self.matrix[(self.pos[0] - 1) * SIZE + self.pos[1]] = 0
        if self.pos[1] + 1 < SIZE:
            if self.matrix[self.pos[0] * SIZE + self.pos[1] + 1] == 0 and self.pos[1] + 1 < SIZE:
                self.matrix[self.pos[0] * SIZE + self.pos[1] + 1] = self.turn
                yield Matrix(self.matrix, reverse[self.turn], self.opp_pos, (self.pos[0], self.pos[1] + 1))
                self.matrix[self.pos[0] * SIZE + self.pos[1] + 1] = 0
        if self.pos[1] - 1 >= 0:
            if self.matrix[self.pos[0] * SIZE + self.pos[1] - 1] == 0 and self.pos[1] - 1 >= 0:
                self.matrix[self.pos[0] * SIZE + self.pos[1] - 1] = self.turn
                yield Matrix(self.matrix, reverse[self.turn], self.opp_pos, (self.pos[0], self.pos[1] - 1))
                self.matrix[self.pos[0] * SIZE + self.pos[1] - 1] = 0

    def move_1_player(self, dir):
        # di chuyển nhưng không đổi turn (để fill)
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

    def move_back_1_player(self, dir):
        # quay ngược lại move_1_player()
        if dir == 1:
            self.matrix[self.pos[0] * SIZE + self.pos[1]] = 0
            self.pos = (self.pos[0] - 1, self.pos[1])
        elif dir == 2:
            self.matrix[self.pos[0] * SIZE + self.pos[1]] = 0
            self.pos = (self.pos[0] + 1, self.pos[1])
        elif dir == 3:
            self.matrix[self.pos[0] * SIZE + self.pos[1]] = 0
            self.pos = (self.pos[0], self.pos[1] - 1)
        elif dir == 4:
            self.matrix[self.pos[0] * SIZE + self.pos[1]] = 0
            self.pos = (self.pos[0], self.pos[1] + 1)
    def avail_moves_coor(self, pos):
        # trả về tọa độ các điểm có thể tới từ pos
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
        # trả về số các nước đi có thể từ pos (số bậc của pos)
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

    def flood_fill(self, cur_pos):
        # trả về danh sách các điểm liên thông với cur_pos
        added = {cur_pos}
        wasnt_popped = {cur_pos}
        while wasnt_popped:
            pos = wasnt_popped.pop()
            for next_pos in self.avail_moves_coor(pos):
                if next_pos not in added:
                    added.add(next_pos)
                    wasnt_popped.add(next_pos)
        return added

    def flood_fill_count(self, cur_pos):
        # trả về số điểm liên thông với cur_pos
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
        # trả về số điểm flood fill theo phương pháp checkerboard
        # nôm na là 1 điểm màu đỏ chỉ có thể nhảy sang 1 điểm màu đen
        # trả về 2 lần số điểm màu nào ít hơn.
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

    def find_articulation_points(self, pos):
        # trả về số điểm cắt trong khu vực liên thông với pos
        self.time = 0

        def dfs(node, p=-1):
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
                        articulation_points.add(node)
                    children += 1
            if p == -1 and children > 1:
                articulation_points.add(node)

        all_aps = set()
        for coor in self.avail_moves_coor(pos):
            visited = set()
            tin = {}
            low = {}
            articulation_points = set()
            dfs(coor)
            all_aps |= articulation_points
            if not self.is_articulation_point_coor(pos):
                break
        return all_aps

    def is_connected(self, pos1, pos2):
        # pos1 với pos2 có liên thông không? (pos1 == pos2 sẽ return False)
        added = {pos1}
        wasnt_popped = deque([pos1])
        while wasnt_popped:
            pos = wasnt_popped.pop()
            for next_pos in self.avail_moves_coor(pos):
                if next_pos == pos2:
                        return True
                if next_pos not in added:
                    added.add(next_pos)
                    wasnt_popped.append(next_pos)
        return False

    def is_articulation_point_coor(self, pos):
        # pos có là điểm cắt không?
        temp = self.matrix[pos[0]*SIZE+pos[1]]
        try:
            self.matrix[pos[0]*SIZE+pos[1]] = 1
            adj_coors = tuple(self.avail_moves_coor(pos))
            result = not self.is_connected(adj_coors[0], adj_coors[1])
            self.matrix[pos[0]*SIZE+pos[1]] = temp
            return result
        except:
            self.matrix[pos[0]*SIZE+pos[1]] = temp
            return False

    def is_separated(self):
        # trạng thái hiện tại đã phân tách chưa?
        added = set()
        wasnt_popped = deque([self.pos])
        while wasnt_popped:
            pos = wasnt_popped.popleft()
            for next_pos in self.avail_moves_coor(pos):
                if abs(next_pos[0] - self.opp_pos[0]) + abs(next_pos[1] - self.opp_pos[1]) == 1:
                    return False
                if next_pos not in added:
                    added.add(next_pos)
                    wasnt_popped.append(next_pos)
        return True

    def voronoi_domain(self, my_pos, opp_pos):
        # trả về lãnh thổ voronoi của my_pos và opp_pos bằng phương pháp
        # lần lượt mỗi bên đi 1 bước cho tới khi hết ô trống (my_pos đi trước). 
        my_domain = set()
        opp_domain = set()
        my_queue = {my_pos}
        opp_queue = {opp_pos}
        while not(not my_queue and not opp_queue): # ( ͡° ͜ʖ ͡°) 
            new_my_q = set()
            for pos in my_queue:
                for next_pos in self.avail_moves_coor(pos):
                    if next_pos not in my_domain and next_pos not in opp_domain:
                        my_domain.add(next_pos)
                        new_my_q.add(next_pos)
            my_queue = new_my_q

            new_opp_q = set()
            for pos in opp_queue:
                for next_pos in self.avail_moves_coor(pos):
                    if next_pos not in my_domain and next_pos not in opp_domain:
                        opp_domain.add(next_pos)
                        new_opp_q.add(next_pos)
            opp_queue = new_opp_q
        return my_domain, opp_domain

    def ultimate_flood_fill(self, pos, aps, added):
        # bổ sung cho hàm smart_flood_fill() dưới trường hợp pos là 1 điểm cắt.
        if self.is_articulation_point_coor(pos):
            return max(map(lambda x: self.smart_flood_fill(x, aps, added | {x}), self.avail_moves_coor(pos)))
        return self.smart_flood_fill(pos, aps, added)
        
    def smart_flood_fill(self, pos, aps, added):
        # số ô tối đa có thể fill được từ pos, khi từ 1 chamber đi qua 1 điểm cắt
        # thì không thể đi qua vùng ngoài của các điểm cắt khác trong chamber đó. 
        count = 0
        ap_adj = set()
        wasnt_popped = {pos}
        while wasnt_popped:
            cur_pos = wasnt_popped.pop()
            for next_pos in self.avail_moves_coor(cur_pos):
                if next_pos not in added:
                    if next_pos in aps:
                        ap_adj.add(next_pos)
                        if self.avail_moves_count(next_pos) == 3:
                            count += 1
                    else:
                        wasnt_popped.add(next_pos)
                        count += 1
                    added.add(next_pos)
        max_val = count
        for ap in ap_adj:
            if self.avail_moves_count(ap) == 3:
                max_val = max(max_val, count + self.smart_flood_fill(ap, aps, added.copy())) 
            else:
                max_val = max(max_val, count + 1 + self.smart_flood_fill(ap, aps, added.copy())) 
        return max_val

    def not_separated_heuristic(self):
        # heuristic trạng thái chưa phân tách
        me, opp = self.voronoi_domain(self.pos, self.opp_pos)
        # fill tạm hết lãnh thổ của đối phương để tính điểm của mình
        for pos in opp:
            self.matrix[pos[0] * SIZE + pos[1]] = 2
        my_space = self.ultimate_flood_fill(self.pos, self.find_articulation_points(self.pos), {self.pos})
        # rollback, bỏ fill đi:
        for pos in opp:
            self.matrix[pos[0] * SIZE + pos[1]] = 0
        # tương tự, fill hết lãnh thổ của mình
        for pos in me:
            self.matrix[pos[0] * SIZE + pos[1]] = 1
        opp_space = self.ultimate_flood_fill(self.opp_pos, self.find_articulation_points(self.opp_pos), {self.opp_pos})
        for pos in me:
            self.matrix[pos[0] * SIZE + pos[1]] = 0

        return my_space - opp_space

    def separated_heuristic(self):
        # heuristic trạng thái đã phân tách
        my_space = self.ultimate_flood_fill(self.pos, self.find_articulation_points(self.pos), {self.pos})
        opp_space = self.ultimate_flood_fill(self.opp_pos, self.find_articulation_points(self.opp_pos), {self.opp_pos})
        return my_space - opp_space

class TimeOut(Exception):
    # exception khi sắp hết thời gian
    pass

def minimax_ids(state, start_depth, alpha, beta, start_time):
    # duyệt minimax sâu dần, độ sâu khởi đầu là start_depth, trả về 
    # giá trị return_state hiện tại khi sắp hết thời gian
    return_state = None
    depth = start_depth
    while True:
        try:
            return_state = minimax(state, depth, alpha, beta, start_time)
            depth += 1
        except:
            break
    # print("DEPTH", depth)
    return return_state

def minimax(state, depth, alpha, beta, start_time):
    if time() - start_time > TIME_LIMIT: # sắp hết giờ!!!
        raise TimeOut()
    max_val = -100000
    return_state = None
    for next_state in state.avail_next_states():
        next_min = min_value(next_state, depth - 1, alpha, beta, start_time)
        if max_val < next_min:
            max_val = next_min
            return_state = next_state
        alpha = max(alpha, max_val)
    return return_state

def max_value(state, depth, alpha, beta, start_time):
    if time() - start_time > TIME_LIMIT:
        raise TimeOut()
    if state.is_separated():
        return state.separated_heuristic()
    if depth <= 0:
        return state.not_separated_heuristic()
    max_val = -100000
    for next_state in state.avail_next_states():
        max_val = max(max_val, min_value(next_state, depth - 1, alpha, beta, start_time))
        alpha = max(alpha, max_val)
        if alpha >= beta:
            return max_val
    if max_val == -100000:
        return -50000 + depth
    return max_val


def min_value(state, depth, alpha, beta, start_time):
    if time() - start_time > TIME_LIMIT:
        raise TimeOut()
    if state.is_separated():
        return -state.separated_heuristic()
    min_val = 100000
    for next_state in state.avail_next_states():
        min_val = min(min_val, max_value(next_state, depth - 1, alpha, beta, start_time))
        beta = min(beta, min_val)
        if alpha >= beta:
            return min_val
    if min_val == 100000:
        return 50000 - depth
    return min_val

def fill(state):
    max_val = -100000
    return_move = 0
    for next_move in state.avail_moves():
        state.move_1_player(next_move)
        point = filling_evaluate_with_depth(state, 1)
        state.move_back_1_player(next_move)
        if point > max_val:
            max_val = point
            return_move = next_move
    return return_move

def filling_evaluate(state):
    moves_count = state.avail_moves_count(state.pos)
    if moves_count == 0:
        return -10000
    aps = state.find_articulation_points(state.pos)
    return 11 * state.ultimate_flood_fill(state.pos, aps, {state.pos}) - 2 * moves_count - 4 * len(aps)

def filling_evaluate_with_depth(state, depth):
    moves_count = state.avail_moves_count(state.pos)
    if moves_count == 0:
        return -10000
    if depth == FILL_DEPTH:
        aps = state.find_articulation_points(state.pos)
        return 11 * state.ultimate_flood_fill(state.pos, aps, {state.pos}) - 2 * moves_count - 4 * len(aps)
    max_val = -10000
    for next_move in state.avail_moves():
        state.move_1_player(next_move)
        max_val = max(max_val, filling_evaluate_with_depth(state, depth + 1))
        state.move_back_1_player(next_move)
    return filling_evaluate(state) + max_val / (depth + 1)

reverse = {'X': 'O', 'O': 'X', 1: 2, 2: 1}
turn_sym = {'X': 1, 'O': 2}

FILL_DEPTH = 4 # max depth for spacefill
START_DEPTH = 2 # start depth for IDS minimax
TIME_LIMIT = 0.9 # time limit for one turn
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
state = None # init state

sio = socketio.Client()
@sio.event
def connect():
    print 'connection established'
    send_infor()
@sio.event
def send_infor():
    infor = json.dumps({"name": "Nhóm 24", "team": team, "members":[{"name": "Hà Hải Phong", "mssv": 20173299}, {"name": "Hà Hữu Linh", "mssv": 20173230}, {"name":"Vũ Quang Đại", "mssv":20172993}, {"name":"Phạm Quang Huy", "mssv":20173181}]})
    sio.emit('Infor', infor)
@sio.event
def send_message(point):
    sio.emit('moving', point) 

@sio.event
def disconnect():
    print 'disconnected from server'
@sio.on('new_Map')
def new_Map(data):
    global state
    try:
        prepoint = data[team]
        rivalpoint = data[reverse[team]]
        main_board = data["map"]
        SIZE = data["ncol"]
        SQ_SIZE = SIZE * SIZE
        new_matrix = []
        for i in range(SIZE):
            for j in range(SIZE):
                new_matrix.append(main_board[i][j])
        state = Matrix(new_matrix, turn_sym[team], (prepoint["x"], prepoint["y"]), (rivalpoint["x"], rivalpoint["y"]))
    except Exception:
        traceback.print_exc()
@sio.on('time_Out')
def time_Out(data):
    print("Time out!")
@sio.on('change_Turn')
def change_Turn(data):
    global state
    # begin = time()
    this_turn = data["turn"]
    result = data["result"]
    # print(result)
    if result == team:
        print "You winnn!!!"
    elif result == "C":
        try:
            if this_turn == team:
                rivalpoint = data["point"]
                state.matrix[rivalpoint["x"]*SIZE + rivalpoint["y"]] = turn_sym[rivalpoint["type"]]
                state.opp_pos = (rivalpoint["x"], rivalpoint["y"])
                if state.is_separated():
                    state.move_1_player(fill(state))
                    xo, yo = state.pos
                else:
                    state = minimax_ids(state, START_DEPTH, -100000, 100000, time())
                    state.turn = reverse[state.turn]
                    state.pos, state.opp_pos = state.opp_pos, state.pos
                    xo, yo = state.pos
                    print(xo, yo)

                point = json.dumps({'x': xo, 'y': yo, 'type': team})
                send_message(point)
                print point
        except Exception:
            traceback.print_exc()
    else:
        print "You lose!!!"
    # print("TIME: ",time() - begin)

sio.connect('http://localhost:3000', headers={'team': team})