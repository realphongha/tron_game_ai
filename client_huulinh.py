import socketio
import json
from collections import deque
import time
import heapq
import traceback
from copy import deepcopy
import sys
import math
def is_space(state, pos):
 
    if 0 <= pos[0] < SIZE and 0 <= pos[1] < SIZE:
        if state[pos[0]][pos[1]] == EMPTY:
            return True
        elif state[pos[0]][pos[1]] == TEMP:
            return True
    return False

def is_space_not_temp(state, pos):
    if 0 <= pos[0] < SIZE and 0 <= pos[1] < SIZE:
        if state[pos[0]][pos[1]] == EMPTY:
            return True
    return False

def count_spaces(state, pos):
    return len(avail_moves(state, pos))
def moves_not_temp(state, pos):
    moves_not_temp = []
    moves = [(pos[0]-1, pos[1]), (pos[0]+1, pos[1]), (pos[0], pos[1]-1), (pos[0], pos[1]+1)]

    for move in moves:
        if is_space_not_temp(state, move):
            moves_not_temp.append(move)

    return moves_not_temp

def avail_moves(state, pos):
    nextmoves = []
 
    moves = [(pos[0]-1, pos[1]), (pos[0]+1, pos[1]), (pos[0], pos[1]-1), (pos[0], pos[1]+1)]
 
    for move in moves:
        if is_space(state, move):
            nextmoves.append(move)
    return nextmoves

def flood_fill_count(state, pos):
    visited = {pos}
    queue = deque([pos])

    while queue:
        move = queue.popleft()

        for nextmove in avail_moves(state, move):
            if nextmove not in visited:
                visited.add(nextmove)
                queue.append(nextmove)

    return len(visited)

def flood_fill(state, pos):
    visited = {pos}
    queue = deque([pos])
 
    while queue:
        move = queue.popleft()
 
        for nextmove in avail_moves(state, move):
            if nextmove not in visited:
                visited.add(nextmove)
                queue.append(nextmove)
 
    return visited

def is_separated(state, pos, opp_pos):
	fill_pos = flood_fill(state, pos)
	nextmoves = avail_moves(state, opp_pos)
	for move in nextmoves:
		if move in fill_pos:
			return False
	return True

# find best path in phase separation
# A* algorithm
def find_path(state, pos):
	# estimated value
	depth = 0
	evalue = -10000
	nextmoves = avail_moves(state, pos); best_pos=nextmoves[0]
	if len(nextmoves)==0:
		return -1
	n2 = 0; visited = set()
	for next_pos in nextmoves:
		for move in avail_moves(state, next_pos):
			if move not in visited:
				visited.add(move)
				n2 += 1
	if n2 == 0:
		if best_pos[0] == pos[0]:
			if best_pos[1] == pos[1] - 1:
				return 1
			return 3
		else:
			if best_pos[0] == pos[0] - 1:
				return 0
			return 2
	for next_pos in nextmoves:
		state[next_pos[0]][next_pos[1]] = MYTURN
		nextmoves_v2 = avail_moves(state, next_pos)
		for next_pos2 in nextmoves_v2:
			state[next_pos2[0]][next_pos2[1]] = MYTURN
			cur_evalue = compute_eval(next_pos2, depth + 1, state)
			if cur_evalue > evalue:
				evalue = cur_evalue
				best_pos = next_pos
			state[next_pos2[0]][next_pos2[1]] = EMPTY
		state[next_pos[0]][next_pos[1]] = EMPTY

	if best_pos[0] == pos[0]:
		if best_pos[1] == pos[1] - 1:
			return 1
		return 3
	else:
		if best_pos[0] == pos[0] - 1:
			return 0
		return 2

# return estimated value of this matrix from pos
def compute_eval(pos, depth, state):
    nl = avail_moves(state, pos)
    if (depth == 10 or len(nl) == 0):
        max_dfs_depth = dfs_run(pos, state)
        return depth + max_dfs_depth
    """

    if (time.perf_counter() - start_time > max_time) or (len(nl) == 0):
        max_dfs_depth = dfs_run(pos, state)
        return depth + max_dfs_depth
    """

    ans = 0
    for next_pos in nl:
        state[next_pos[0]][next_pos[1]] = MYTURN
        ans = max(ans, compute_eval(next_pos, depth + 1, state))
        state[next_pos[0]][next_pos[1]] = EMPTY
    return ans


def dfs_run(pos, state):
    
    stack = [pos]
    dfs_depth = [1] 
    visit = [[False for _ in range(SIZE)] for __ in range(SIZE)]
    visit[pos[0]][pos[1]] = True
    max_dfs_depth = 1
    while len(stack):
        cur_pos = stack[-1]
        nl = avail_moves(state, pos)
        visit_all = True
        for next_pos in nl:
            if not visit[next_pos[0]][next_pos[1]]:
                visit_all = False
                visit[next_pos[0]][next_pos[1]] = True
                stack.append(next_pos)
                dfs_depth.append(dfs_depth[-1] + 1)
        if visit_all:
            stack.pop()
            max_dfs_depth = max(max_dfs_depth, dfs_depth[-1])
            dfs_depth.pop()
    return max_dfs_depth

def is_articulation_point(state, pos):
	nextmoves = avail_moves(state, pos)
 
	if len(nextmoves) == 0:
		return False
	move = nextmoves[0]
 
	f1 = flood_fill_count(state, pos)
	f2 = flood_fill_count(state, move)

	return f1 - 1 != f2

def flood_fill_count_checkerboard(state, cur_pos):
	visited = {cur_pos:True}
	stack = [cur_pos]; count_red = -1; count_black = 0

	while stack:
		pos = stack.pop()
		if visited[pos]:
			count_red += 1
		else:
			count_black += 1
		for next_pos in avail_moves(state, pos):
			if next_pos not in visited:
				visited[next_pos] = not visited[pos]
				stack.append(next_pos)
	return 2 * min(count_red, count_black)


def dfs(state, visited, low, num, pos, depth = 1):
 
	visited.append(pos)
	low[tuple(pos)] = depth
	num[tuple(pos)] = depth
 
	child_count = 0
	art_list = []; nextmoves = avail_moves(state, pos)
 
	for next_pos in nextmoves:
		if next_pos not in visited:
			child_count += 1
			art_list.extend(dfs(state, visited, low, num, next_pos, depth+1))
 
		#update low
		if num[tuple(next_pos)] < num[tuple(pos)]:
			low[tuple(pos)] = min(low[tuple(pos)], num[tuple(next_pos)])
 
		else:
			low[tuple(pos)] = min(low[tuple(pos)], low[tuple(next_pos)])
 
	if depth == 1 and child_count > 1:
		art_list.append(pos)
	elif depth > 1:
		for next_pos in nextmoves:
			if low[tuple(next_pos)] > num[tuple(pos)]:
				art_list.append(pos)
				break
	return art_list
 
def find_articulation_points(state, pos):
	visited = []
	low = {}; num = {}
 
	art_list = dfs(state, visited, low, num, pos)
	return art_list

def filling_evaluate(state, pos):
	count = count_spaces(state, pos)
	if count == 0:
		return -10000
	point = flood_fill_count(state, pos)+ flood_fill_count_checkerboard(state, pos) - 2 * count - 4 * len(find_articulation_points(state, pos))
	return point



def filling_evaluate_with_depth(state, pos, depth):
	count = count_spaces(state, pos)

	if count == 0:
		return -10000
	if depth == 6:
		point = flood_fill_count(state, pos) + flood_fill_count_checkerboard(state, pos) - 2 * count - 4 * len(find_articulation_points(state, pos))
		return point

	maxvalue = -10000
	for next_move in avail_moves(state, pos):
		state[next_move[0]][next_move[1]] = MYTURN
		maxvalue = max(maxvalue, filling_evaluate_with_depth(state, next_move, depth + 1))
		state[next_move[0]][next_move[1]] = EMPTY

	return filling_evaluate(state, pos) + maxvalue / (depth + 1)

def fill(state, pos):
	direction = -1

	nextmoves = avail_moves(state, pos)
	maxvalue = -10000; move = None
 
	if not is_articulation_point(state, pos):

		for next_move in avail_moves(state, pos):
			state[next_move[0]][next_move[1]] = MYTURN
			point = filling_evaluate_with_depth(state, next_move, 1)
			state[next_move[0]][next_move[1]] = EMPTY

			if point > maxvalue:
				maxvalue = point
				move = next_move

		print("IN ARTICULATIONSPOINT = " + str(maxvalue))
		if move == (pos[0]-1, pos[1]):
			direction = 0
		elif move == (pos[0], pos[1]-1):
			direction = 1
		elif move == (pos[0]+1, pos[1]):
			direction = 2
		elif move == (pos[0], pos[1]+1):
			direction = 3
	else:
		direction = find_path(state, pos)
	return direction


def myteam_go(myteam, state):
    myteam_tmp = deque([])

    sum_myteam = 0
    while len(myteam):
        pos = myteam.popleft()

        for next_pos in avail_moves(state, pos):
            sum_myteam += 1
            state[next_pos[0]][next_pos[1]] = MYTURN
            myteam_tmp.append(next_pos)
    for position in myteam_tmp:
        myteam.append(position)
    #return [sum_myteam, myteam]
    return sum_myteam

def oppteam_go(oppteam, state):
    oppteam_tmp = deque([])
    sum_oppteam = 0
    while len(oppteam):
        pos = oppteam.popleft()

        for next_pos in avail_moves(state, pos):
            sum_oppteam += 1
            state[next_pos[0]][next_pos[1]] = OPPTURN
            oppteam_tmp.append(next_pos)

    for position in oppteam_tmp:
        oppteam.append(position)

    #return [sum_oppteam, oppteam]
    return sum_oppteam

def count_edges(state, arp):
    count = 0
    tmp = deque([])

    while len(arp):
        pos = arp.popleft()

        for next_pos in moves_not_temp(state, pos):
            count += count_spaces(state, next_pos)
            tmp.append(next_pos)
            state[next_pos[0]][next_pos[1]] = TEMP

    for p in tmp:
        arp.append(p)
    return [count, arp]
    #return count


def luong_gia_canh(state, pos, opp_pos, ismyturn):
    mysum = 0; oppsum = 0
    my = deque([pos]); opp = deque([opp_pos])

    if ismyturn:
        my_compute = count_edges(state, my)
        mysum += my_compute[0]
        my = my_compute[1]
        #mysum += count_edges(state, my)

    while (len(my) or len(opp)):
        opp_compute = count_edges(state, opp)
        #oppsum += count_edges(state, opp)
        oppsum += opp_compute[0]
        opp = opp_compute[1]
        my_compute = count_edges(state, my)
        #mysum += count_edges(state, my)
        mysum += my_compute[0]
        my = my_compute[1]
    return mysum - oppsum

def luong_gia_outside(state, pos, opp_pos):
    mysum = 0; oppsum = 0
    tmp1 = 0; tmp2 = 0

    arp = deque([pos])
    tmp1turn = True
    while len(arp):
        #myteam_compute = myteam_go(arp, state)
        if tmp1turn:
            tmp1 += myteam_go(arp, state)
            #arp = myteam_compute[1]
            tmp1turn = False
        else:
            tmp2 += myteam_go(arp, state)
            #arp = myteam_compute[1]
            tmp1turn = True

    mysum = tmp1 + tmp2
    if tmp2 > tmp1:
        mysum -= (tmp2 - tmp1)

    elif tmp2 < tmp1 - 1:
        mysum -= (tmp1 - 1 - tmp2)

    tmp1 = 0; tmp2 = 0
    arp.append(opp_pos)
    tmp1turn = True
    while len(arp):
        #myteam_compute = myteam_go(arp, state)
        if tmp1turn:
            tmp1 += myteam_go(arp, state)
            #arp = myteam_compute[1]
            tmp1turn = False
        else:
            tmp2 += myteam_go(arp, state)
            #arp = myteam_compute[1]
            tmp1turn = True

    oppsum = tmp1 + tmp2
    if oppsum <= 0:
        if tmp2 > tmp1:
            oppsum -= (tmp2 - tmp1)
        elif tmp2 < (tmp1 - 1):
            oppsum -= (tmp1 - 1 - tmp2)

    return mysum - oppsum


def luong_gia(state, pos, opp_pos, ismyturn):
    myteam = deque([pos])
    oppteam = deque([opp_pos])
    sum_myteam = 0; sum_oppteam = 0

    if not is_separated(state, pos, opp_pos):
        if ismyturn:
            while (len(myteam) or len(oppteam)):
                #myteam_compute = myteam_go(myteam, state)
                sum_myteam += myteam_go(myteam, state)
                #myteam = myteam_compute[1]
                #oppteam_compute = oppteam_go(oppteam, state)
                sum_oppteam += oppteam_go(oppteam, state)
                #oppteam = oppteam_compute[1]

        else:
            while (len(myteam) or len(oppteam)):
                #oppteam_compute = oppteam_go(oppteam, state)
                sum_oppteam += oppteam_go(oppteam, state)
                oppteam = oppteam_compute[1]
                #myteam_compute = myteam_go(myteam, state)
                sum_myteam += myteam_go(myteam, state)
                #myteam = myteam_compute[1]
                
    else:
        while len(myteam):
            #myteam_compute = myteam_go(myteam, state)
            sum_myteam += myteam_go(myteam, state)
            #myteam = myteam_compute[1]

    return sum_myteam - sum_oppteam



def max_value(state, pos, opp_pos, depth, alpha, beta):
    global depth_minimax
    depth_minimax = depth 
    maxvalue = -80000
    nextmoves = avail_moves(state, pos); best_move = None

    if (not is_separated(state, pos, opp_pos)):
        if depth > 0:
            for next_move in nextmoves:
                state_tmp = deepcopy(state)
                state_tmp[next_move[0]][next_move[1]] = MYTURN
                tmp = min_value(state_tmp, next_move, opp_pos, depth_minimax - 1, alpha, beta)
                if tmp > maxvalue:
                    maxvalue = tmp
                if ALPHABETA:
                    if maxvalue >= beta:
                        return maxvalue
                    alpha = max(alpha, maxvalue)

        else:
            maxvalue = 31 * luong_gia(deepcopy(state), pos, opp_pos, True) + 11 * luong_gia_canh(deepcopy(state), pos, opp_pos, True);
        if maxvalue == -80000:
            maxvalue = -40000-depth
        return maxvalue

    t = 31 * luong_gia_outside(deepcopy(state), pos, opp_pos) + 11 * luong_gia_canh(deepcopy(state), pos, opp_pos, True)
    if t > 1 or t < -1:
        return t * 5
    return t 




def min_value(state, pos, opp_pos, depth, alpha, beta):
    global depth_minimax
    depth_minimax = depth
    minvalue = 80000
    nextmoves = avail_moves(state, opp_pos); best_move = None

    if (not is_separated(state, pos, opp_pos)):
        for next_move in nextmoves:
            state_tmp = deepcopy(state)
            state_tmp[next_move[0]][next_move[1]] = OPPTURN
            tmp = max_value(state_tmp, pos, next_move, depth_minimax - 1, alpha, beta)
            if tmp < minvalue:
                minvalue = tmp
            if ALPHABETA:
                if minvalue <= alpha:
                    return minvalue
                beta = min(beta, minvalue)

        if minvalue == 80000:
            minvalue = 40000 + depth
        return minvalue

    t = 31 * luong_gia_outside(deepcopy(state), pos, opp_pos) + 11 * luong_gia_canh(deepcopy(state), pos, opp_pos, False)
    if t > 1 or t < -1:
        return t * 5
    return t


def minimax(state, pos, opp_pos):
    global depth_minimax
    depth_minimax = 14
    direction = -1
    value = -80000; alpha = -80000; beta = 80000

    nextmoves = avail_moves(state, pos); best_move = None
    for next_move in nextmoves:
        state_tmp = deepcopy(state)
        state_tmp[next_move[0]][next_move[1]] = MYTURN
        tmp = min_value(state_tmp, next_move, opp_pos, depth_minimax - 1,  alpha, beta)
        if tmp > value:
            value = tmp
            best_move = next_move

    print('Value for minimax =  ' + str(value))
    if best_move[0] == pos[0]:
        if best_move[1] == pos[1] - 1:
            direction = 1
        else:
            direction = 3
    elif best_move[1] == pos[1]:
        if best_move[0] == pos[0] - 1:
            direction = 0
        else:
            direction = 2
    return direction

def next_move(state, pos, opp_pos):
    direction = -1
    if is_separated(state, pos, opp_pos):

        print("FILL MODE!!!!!!!!!!!!!!!!!!")
        start_time = time.time()
        direction = fill(state, pos)
        stop_time = time.time()
        print("TIME FOR FILL MODE =   " + str(stop_time-start_time))
        #end = time.perf_counter()
        #max_time = end - begin
        #print('maximum find_path time = ' + str(max_time))

    else:
        print("MINIMAX MODE!!!!!!!!!!!!!!!!")
        start_time = time.time()
        direction = minimax(state, pos, opp_pos)
        stop_time = time.time()
        print("TIME FOR MINIMAX MODE =   " + str(stop_time-start_time))


    return direction




REVERSE = {'X': 'O', 'O': 'X', 1: 2, 2: 1}
CONVERT_NOTATION = {'X': 1, 'O': 2}
ALPHABETA = True; depth_minimax = 14

#MINIMAX_DEPTH = 5 # minimax depth
SIZE = 15
team = None

while True:
    raw = raw_input("Choose your team (x/o): ")
    team = raw.upper()
    if team == 'O' or team == 'X':
        break
MYTURN = CONVERT_NOTATION[team]; OPPTURN = REVERSE[MYTURN]; TEMP = 4
#MINIMAX_DEPTH = 14
EMPTY = 0
state = []
main_board = []
prepoint = {}
my_pos = tuple()

sio = socketio.Client()
@sio.event
def connect():
    print 'connection established'
    send_infor()
@sio.event
def send_infor():
    infor = json.dumps({"name": "AlphaBK", "team": team, "members":[{"name": "Ha Huu Linh", "mssv": 20173230}, {"name": "Ha Hai Phong", "mssv": 20173299}, {"name":"Vu Quang Dai", "mssv":20172993}, {"name":"Pham Quang Huy", "mssv":20173181}]})
    sio.emit('Infor', infor)
@sio.event
def send_message(point): # point nuoc di tiep theo(x,y,type)
    sio.emit('moving', point) 

@sio.event
def disconnect():
    print 'disconnected from server'
@sio.on('new_Map')
def new_Map(data):
	global state
	global my_pos
	try:
		prepoint = data[team]
		rivalpoint = data[REVERSE[team]]
		main_board = data["map"]
		state = deepcopy(main_board)
		SIZE = data["ncol"]
		my_pos = (prepoint["x"], prepoint["y"])
		opp_pos = (rivalpoint["x"], rivalpoint["y"])
		state[my_pos[0]][my_pos[1]] = MYTURN
		state[opp_pos[0]][opp_pos[1]] = OPPTURN
	except Exception:
		traceback.print_exc()
@sio.on('time_Out')
def time_Out(data):
    print data
@sio.on('change_Turn')
def change_Turn(data):
	global my_pos
	this_turn = data["turn"]
	result = data["result"]
	print(result)
	if result == team:
		print "You winnn!!!"
	elif result == "C":
		try:
			if this_turn == team:
				rivalpoint = data["point"] # toa do diem doi thu vua di (x,y,type)
				opp_pos = (rivalpoint["x"], rivalpoint["y"])
				state[opp_pos[0]][opp_pos[1]] = OPPTURN #cap nhap board

				direction = next_move(state, my_pos, opp_pos)
				if direction == -1:
					my_pos = (0, 0)
					print 'Toi da thua!!!!!!!'

				elif direction == 0:
					my_pos = (my_pos[0]-1, my_pos[1])
				elif direction == 1:
					my_pos = (my_pos[0], my_pos[1]-1)
				elif direction == 2:
					my_pos = (my_pos[0]+1, my_pos[1])
				elif direction == 3:
					my_pos = (my_pos[0], my_pos[1]+1)

				state[my_pos[0]][my_pos[1]] = MYTURN
				xo, yo = my_pos
				######################################################################
				point = json.dumps({'x': xo, 'y': yo, 'type': team})
				send_message(point)
				print point
		except Exception:
			traceback.print_exc()
	else:
		print "You lose!!!"
sio.connect('http://localhost:3000', headers={'team': team})