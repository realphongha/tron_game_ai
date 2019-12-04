# -*- coding: utf-8 -*-
"""
Bot Cuộc Chiến Lãnh Thổ.
Nhóm 24:
Hà Hải Phong - 20173299 
Hà Hữu Linh - 20173230 
Vũ Quang Đại - 20172993
Phạm Quang Huy - 20173181
"""
import socketio
import json
import traceback
import numpy as np
from collections import deque
from time import time

reverse = {'X': 'O', 'O': 'X', 1: 2, 2: 1}
turn_sym = {'X': 1, 'O': 2}

FILL_DEPTH = 4 # max depth for spacefill
START_DEPTH_MINIMAX = 3 # start depth for IDS minimax
START_DEPTH_FILL = 4 # start depth for IDS spacefill
MAX_DEPTH_MINIMAX = 100 # max depth for IDS minimax
MAX_DEPTH_FILL = 15 # max depth for IDS spacefill
TIME_LIMIT_MINIMAX = 0.8 # time limit for one turn
TIME_LIMIT_FILL = 0.8 # time limit for one turn
SIZE = 15
team = ''
while True:
    raw = raw_input("Choose your team (x/o): ")
    team = raw.upper()
    if team == 'O' or team == 'X':
        break
turn = turn_sym[team]
state = None # init state

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
        
    def move_back(self, dir):
        if dir == 1:
            self.matrix[self.opp_pos[0] * SIZE + self.opp_pos[1]] = 0
            self.turn = reverse[self.turn]
            self.opp_pos = (self.opp_pos[0] - 1, self.opp_pos[1])
            self.pos, self.opp_pos = self.opp_pos, self.pos
        elif dir == 2:
            self.matrix[self.opp_pos[0] * SIZE + self.opp_pos[1]] = 0
            self.turn = reverse[self.turn]
            self.opp_pos = (self.opp_pos[0] + 1, self.opp_pos[1])
            self.pos, self.opp_pos = self.opp_pos, self.pos
        elif dir == 3:
            self.matrix[self.opp_pos[0] * SIZE + self.opp_pos[1]] = 0
            self.turn = reverse[self.turn]
            self.opp_pos = (self.opp_pos[0], self.opp_pos[1] - 1)
            self.pos, self.opp_pos = self.opp_pos, self.pos
        elif dir == 4:
            self.matrix[self.opp_pos[0] * SIZE + self.opp_pos[1]] = 0
            self.turn = reverse[self.turn]
            self.opp_pos = (self.opp_pos[0], self.opp_pos[1] + 1)
            self.pos, self.opp_pos = self.opp_pos, self.pos

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
        is_ap = self.is_articulation_point_coor(pos)
        all_aps = set()
        for coor in self.avail_moves_coor(pos):
            visited = set()
            tin = {}
            low = {}
            articulation_points = set()
            dfs(coor)
            if not is_ap:
                return articulation_points
            all_aps |= articulation_points
        return all_aps

    def is_connected(self, pos1, pos2):
        # pos1 với pos2 có liên thông không? (pos1 == pos2 sẽ return False)
        # (pos2 là vật cản sẽ return False)
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

    def ultimate_flood_fill(self, pos, aps, added):
        """
        Bổ sung cho smart_flood_fill() ở dưới bằng cách xét giá trị pos truyền vào đầu tiên.
        """
        if self.is_articulation_point_coor(pos):
            return 1 + max(map(lambda x: self.smart_flood_fill(x, aps, added | {x}), self.avail_moves_coor(pos)))
        count = 0
        ap_adj = set()
        wasnt_popped = {pos}
        while wasnt_popped:
            cur_pos = wasnt_popped.pop()
            for next_pos in self.avail_moves_coor(cur_pos):
                if next_pos not in added:
                    if next_pos in aps:
                        ap_adj.add(next_pos)
                        # nếu có 3 cạnh vẫn có thể fill được
                        if self.avail_moves_count(next_pos) == 3: 
                            count += 1
                    else:
                        wasnt_popped.add(next_pos)
                        # điểm ngõ cụt sẽ không được tính (trừ điểm đầu) (điểm cuối không xét tới)
                        if self.avail_moves_count(next_pos) > 1 or \
                        (abs(pos[0] - next_pos[0]) + abs(pos[1] - next_pos[1]) == 1): 
                            count += 1
                    added.add(next_pos)
        max_val = count
        for ap in ap_adj:
            if self.avail_moves_count(ap) == 3:
                max_val = max(max_val, count + self.smart_flood_fill(ap, aps, added.copy())) 
            else:
                max_val = max(max_val, count + 1 + self.smart_flood_fill(ap, aps, added.copy())) 
        return max_val
        
    def smart_flood_fill(self, pos, aps, added):
        """
        Xét khoảng lớn nhất có thể fill với điều kiện khi qua điểm cắt bậc 2 
        thì không quay đầu được nữa.
        """
        count = 0
        ap_adj = set()
        wasnt_popped = {pos}
        while wasnt_popped:
            cur_pos = wasnt_popped.pop()
            for next_pos in self.avail_moves_coor(cur_pos):
                if next_pos not in added:
                    if next_pos in aps:
                        ap_adj.add(next_pos)
                        if self.avail_moves_count(next_pos) == 3: # nếu có 3 cạnh vẫn có thể fill được
                            count += 1
                    else:
                        wasnt_popped.add(next_pos)
                        if self.avail_moves_count(next_pos) > 1: 
                            count += 1
                    added.add(next_pos)
        max_val = count
        for ap in ap_adj:
            if self.avail_moves_count(ap) == 3:
                # cộng 1 cho ap rồi trừ 1 vì nếu có 3 cạnh mà trên đường lớn nhất thì không tính
                max_val = max(max_val, count + self.smart_flood_fill(ap, aps, added.copy())) 
            else:
                # cộng 1 cho cái ap
                max_val = max(max_val, count + 1 + self.smart_flood_fill(ap, aps, added.copy())) 
        return max_val # nếu không có ap nào kề với component đang xét thì chỉ trả về count

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

        return my_space * 0.999 - opp_space

    def separated_heuristic(self):
        # heuristic trạng thái đã phân tách
        my_space = self.ultimate_flood_fill(self.pos, self.find_articulation_points(self.pos), {self.pos})
        opp_space = self.ultimate_flood_fill(self.opp_pos, self.find_articulation_points(self.opp_pos), {self.opp_pos})
        return my_space * 0.999 - opp_space

class TimeOut(Exception):
    # exception khi sắp hết thời gian
    pass

def minimax_ids(state, start_depth, max_depth, alpha, beta, start_time):
    # duyệt minimax sâu dần, độ sâu khởi đầu là start_depth, trả về 
    # giá trị return_state hiện tại khi sắp hết thời gian
    new_state = Matrix(state.matrix, state.turn, state.pos, state.opp_pos)
    return_move = 1
    for depth in xrange(start_depth, max_depth + 1):
        try:
            return_move = minimax(new_state, depth, alpha, beta, start_time)
        except TimeOut:
            print("DEPTH", depth)
            return return_move
        except:
            traceback.print_exc()
    print("DEPTH", depth)
    return return_move

def minimax(state, depth, alpha, beta, start_time):
    if time() - start_time > TIME_LIMIT_MINIMAX: # sắp hết giờ!!!
        raise TimeOut()
    max_val = -1000
    return_move = 1
    for next_move in state.avail_moves():
        state.move(next_move)
        next_min = min_value(state, depth - 1, alpha, beta, start_time)
        if max_val < next_min:
            max_val = next_min
            return_move = next_move
        alpha = max(alpha, max_val)
        state.move_back(next_move)
    return return_move

def max_value(state, depth, alpha, beta, start_time):
    if time() - start_time > TIME_LIMIT_MINIMAX:
        raise TimeOut()
    if state.is_separated():
        return state.separated_heuristic()
    if depth <= 0:
        return state.not_separated_heuristic()
    max_val = -1000
    for next_move in state.avail_moves():
        state.move(next_move)
        max_val = max(max_val, min_value(state, depth - 1, alpha, beta, start_time))
        state.move_back(next_move)
        alpha = max(alpha, max_val)
        if alpha >= beta:
            return max_val
    if max_val == -1000:
        return -500 + depth
    return max_val


def min_value(state, depth, alpha, beta, start_time):
    if time() - start_time > TIME_LIMIT_MINIMAX:
        raise TimeOut()
    if state.is_separated():
        return -state.separated_heuristic()
    if depth <= 0:
        return -state.not_separated_heuristic()
    min_val = 1000
    for next_move in state.avail_moves():
        state.move(next_move)
        min_val = min(min_val, max_value(state, depth - 1, alpha, beta, start_time))
        state.move_back(next_move)
        beta = min(beta, min_val)
        if alpha >= beta:
            return min_val
    if min_val == 1000:
        return 500 - depth
    return min_val

def fill(state):
    max_val = -100000
    return_move = 1
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

def number_of_edges(state, start_time):
    if time() - start_time > TIME_LIMIT_FILL:
        raise TimeOut()
    added = {state.pos}
    temp = set()
    max_val = 0
    for pos in state.avail_moves_coor(state.pos):
        if pos not in temp:
            count = state.avail_moves_count(pos)
            added.add(pos)
            temp.add(pos)
            while added:
                cur_pos = added.pop()
                for next_pos in state.avail_moves_coor(cur_pos):
                    if next_pos not in temp:
                        count += state.avail_moves_count(next_pos)
                        added.add(next_pos)
                        temp.add(next_pos)
            max_val = max(max_val, count)
    return max_val

def search_path(state, depth, start_time):
    if time() - start_time > TIME_LIMIT_FILL:
        raise TimeOut()
    if depth: # depth > 0
        max_val = -999
        for move in state.avail_moves():
            state.move_1_player(move)
            temp = search_path(state, depth - 1, start_time)
            if max_val < temp:
                max_val = temp
            state.move_back_1_player(move)
        if max_val < -990:
            return -depth
        return max_val
    return number_of_edges(state, start_time) # depth == 0

def find_path(state, start_time, depth):
    if time() - start_time > TIME_LIMIT_FILL:
        raise TimeOut()
    return_move = 1
    max_val = -1000
    for move in state.avail_moves():
        state.move_1_player(move)
        temp = search_path(state, depth, start_time)
        if max_val < temp:
            max_val = temp
            return_move = move
        state.move_back_1_player(move)
    return return_move

def fill_v2(state, start_depth, max_depth, start_time):
    """
    hàm spacefill của thầy, nhưng dùng IDS
    """
    return_move = 1
    new_state = Matrix(state.matrix, state.turn, state.pos, state.opp_pos)
    for depth in xrange(start_depth, max_depth + 1):
        try:
            return_move = find_path(new_state, start_time, depth)
        except TimeOut:
            print("DEPTH", depth)
            return return_move
        except:
            traceback.print_exc()
    print("DEPTH", depth)
    return return_move

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
    global turn_sym
    global team
    global SIZE
    global reverse
    try:
        prepoint = data[team]
        rivalpoint = data[reverse[team]]
        # SIZE = data["ncol"]
        new_matrix = []
        for i in range(SIZE):
            for j in range(SIZE):
                new_matrix.append(data["map"][i][j])
        state = Matrix(new_matrix, turn_sym[team], (prepoint["x"], prepoint["y"]), (rivalpoint["x"], rivalpoint["y"]))
    except:
        traceback.print_exc()
@sio.on('time_Out')
def time_Out(data):
    print("Time out!")
@sio.on('change_Turn')
def change_Turn(data):
    begin = time()
    global state
    global turn_sym
    global team
    this_turn = data["turn"]
    result = data["result"]
    if result == "C":
        try:
            if this_turn == team:
                rivalpoint = data["point"]
                state.matrix[rivalpoint["x"]*SIZE + rivalpoint["y"]] = turn_sym[rivalpoint["type"]]
                state.opp_pos = (rivalpoint["x"], rivalpoint["y"])
                if state.is_separated():
                    # state.move_1_player(fill(state))
                    state.move_1_player(fill_v2(state, START_DEPTH_FILL, MAX_DEPTH_FILL, begin))
                else:
                    state.move_1_player(minimax_ids(state, START_DEPTH_MINIMAX, MAX_DEPTH_MINIMAX, -1000, 1000, begin))
                send_message(json.dumps({'x': state.pos[0], 'y': state.pos[1], 'type': team}))
        except:
            traceback.print_exc()
    elif result == team:
        print "You winnn!!!"
    else:
        print "You lose!!!"
    if this_turn == team:
        print("TIME: ",time() - begin)

sio.connect('http://localhost:3000', headers={'team': team})