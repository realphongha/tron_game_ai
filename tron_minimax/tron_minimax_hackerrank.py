from math import inf
from collections import deque
import heapq

reverse = {'r': 'g', 'g': 'r'}
# constants:
FILL_DEPTH = 6 # độ sâu chế độ space fill
MINIMAX_DEPTH = 10 # độ sâu minimax
SIZE = 15
SQ_SIZE = SIZE * SIZE
# handles input:
turn = input().rstrip()
line2 = tuple(map(int, input().rstrip().split()))
cur_pos = (line2[0], line2[1])
opp_pos = (line2[2], line2[3])
if turn == 'g':
    cur_pos, opp_pos = opp_pos, cur_pos
matrix = []
for i in range(SIZE):
    matrix += list(input().rstrip())


class Matrix:
    def __init__(self, matrix, turn, pos, opp_pos):
        self.matrix = matrix.copy() # bảng trạng thái game, mảng 1 chiều
        self.turn = turn # lượt hiện tại ('r' hoặc 'g')
        self.pos = pos # vị trí người chơi
        self.opp_pos = opp_pos # vị trí đối thủ

    def display(self, time):
        # for debugging
        for i in range(SQ_SIZE):
            if i % SIZE == 0:
                print()
            print(self.matrix[i], end=' ')
        if time:
            sleep(time)

    def avail_moves(self):
        """
        trả về các obj trạng thái ma trận mới có thể đi được từ vị trí hiện tại, 
        đảo ngược turn, vị trí 2 người chơi
        """
        if self.pos[0] + 1 < SIZE:
            if self.matrix[(self.pos[0] + 1) * SIZE + self.pos[1]] == '-':
                self.matrix[(self.pos[0] + 1) * SIZE + self.pos[1]] = self.turn
                yield Matrix(self.matrix, reverse[self.turn], self.opp_pos, (self.pos[0] + 1, self.pos[1]))
                self.matrix[(self.pos[0] + 1) * SIZE + self.pos[1]] = '-'
        if self.pos[0] - 1 >= 0:
            if self.matrix[(self.pos[0] - 1) * SIZE + self.pos[1]] == '-' and self.pos[0] - 1 >= 0:
                self.matrix[(self.pos[0] - 1) * SIZE + self.pos[1]] = self.turn
                yield Matrix(self.matrix, reverse[self.turn], self.opp_pos, (self.pos[0] - 1, self.pos[1]))
                self.matrix[(self.pos[0] - 1) * SIZE + self.pos[1]] = '-'
        if self.pos[1] + 1 < SIZE:
            if self.matrix[self.pos[0] * SIZE + self.pos[1] + 1] == '-' and self.pos[1] + 1 < SIZE:
                self.matrix[self.pos[0] * SIZE + self.pos[1] + 1] = self.turn
                yield Matrix(self.matrix, reverse[self.turn], self.opp_pos, (self.pos[0], self.pos[1] + 1))
                self.matrix[self.pos[0] * SIZE + self.pos[1] + 1] = '-'
        if self.pos[1] - 1 >= 0:
            if self.matrix[self.pos[0] * SIZE + self.pos[1] - 1] == '-' and self.pos[1] - 1 >= 0:
                self.matrix[self.pos[0] * SIZE + self.pos[1] - 1] = self.turn
                yield Matrix(self.matrix, reverse[self.turn], self.opp_pos, (self.pos[0], self.pos[1] - 1))
                self.matrix[self.pos[0] * SIZE + self.pos[1] - 1] = '-'

    def avail_moves_1_player(self):
        """
        debug chế độ fill 1 người chơi, trả về state mới có turn, pos, opp_pos giống state cũ
        """
        if self.pos[0] + 1 < SIZE:
            if self.matrix[(self.pos[0] + 1) * SIZE + self.pos[1]] == '-' and self.pos[0] + 1 < SIZE:
                self.matrix[(self.pos[0] + 1) * SIZE + self.pos[1]] = self.turn
                yield Matrix(self.matrix, self.turn, (self.pos[0] + 1, self.pos[1]), self.opp_pos)
                self.matrix[(self.pos[0] + 1) * SIZE + self.pos[1]] = '-'
        if self.pos[0] - 1 >= 0:
            if self.matrix[(self.pos[0] - 1) * SIZE + self.pos[1]] == '-' and self.pos[0] - 1 >= 0:
                self.matrix[(self.pos[0] - 1) * SIZE + self.pos[1]] = self.turn
                yield Matrix(self.matrix, self.turn, (self.pos[0] - 1, self.pos[1]), self.opp_pos)
                self.matrix[(self.pos[0] - 1) * SIZE + self.pos[1]] = '-'
        if self.pos[1] + 1 < SIZE:
            if self.matrix[self.pos[0] * SIZE + self.pos[1] + 1] == '-' and self.pos[1] + 1 < SIZE:
                self.matrix[self.pos[0] * SIZE + self.pos[1] + 1] = self.turn
                yield Matrix(self.matrix, self.turn, (self.pos[0], self.pos[1] + 1), self.opp_pos)
                self.matrix[self.pos[0] * SIZE + self.pos[1] + 1] = '-'
        if self.pos[1] - 1 >= 0:
            if self.matrix[self.pos[0] * SIZE + self.pos[1] - 1] == '-' and self.pos[1] - 1 >= 0:
                self.matrix[self.pos[0] * SIZE + self.pos[1] - 1] = self.turn
                yield Matrix(self.matrix, self.turn, (self.pos[0], self.pos[1] - 1), self.opp_pos)
                self.matrix[self.pos[0] * SIZE + self.pos[1] - 1] = '-'

    def avail_moves_coor(self, pos):
        """
        Trả về tọa độ các điểm có thể đi được từ vị trí pos.
        """
        if pos[0] + 1 < SIZE:
            if self.matrix[(pos[0] + 1) * SIZE + pos[1]] == '-':
                yield (pos[0] + 1, pos[1])
        if pos[0] - 1 >= 0:
            if self.matrix[(pos[0] - 1) * SIZE + pos[1]] == '-':
                yield (pos[0] - 1, pos[1])
        if pos[1] + 1 < SIZE:
            if self.matrix[pos[0] * SIZE + pos[1] + 1] == '-':
                yield (pos[0], pos[1] + 1)
        if pos[1] - 1 >= 0:
            if self.matrix[pos[0] * SIZE + pos[1] - 1] == '-':
                yield (pos[0], pos[1] - 1)

    def avail_moves_count(self, pos):
        """
        Đếm số điểm có thể đi được từ vị trí pos.
        """
        count = 0
        if pos[0] + 1 < SIZE:
            if self.matrix[(pos[0] + 1) * SIZE + pos[1]] == '-':
                count += 1
        if pos[0] - 1 >= 0:
            if self.matrix[(pos[0] - 1) * SIZE + pos[1]] == '-':
                count += 1
        if pos[1] + 1 < SIZE:
            if self.matrix[pos[0] * SIZE + pos[1] + 1] == '-':
                count += 1
        if pos[1] - 1 >= 0:
            if self.matrix[pos[0] * SIZE + pos[1] - 1] == '-':
                count += 1
        return count

    def flood_fill_count(self, cur_pos):
        """
        :return: số node liên thông với node hiện tại (không tính node hiện tại)
        """
        added = {cur_pos}
        wasnt_popped = {cur_pos}
        count = 0
        while wasnt_popped:
            pos = wasnt_popped.pop()
            for next_pos in self.avail_moves_coor(pos):
                if next_pos not in added:
                    added.add(next_pos)
                    wasnt_popped.add(next_pos)
                    count += 1
        return count

    def flood_fill_count_checkerboard(self, cur_pos):
        # đếm space bằng phương pháp "red-and-black squares"
        visited = {cur_pos: True} 
        stack = [cur_pos]
        count_red = -1 # trừ đi cái cur_pos ban đầu
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
        """
        :return: 1 set các node liên thông với node hiện tại (tính cả node hiện tại)
        """
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
        """
        :return: 1 set chứa tất cả articulation points (điểm chia cắt 1 thành phần liên thông thành nhiều thành phần)
            trong khoảng không gian bot có thể tới (dùng trong heuristic space fill). 
        Không rõ nó hoạt động như nào nhưng vẫn chạy đúng.
        Thuật toán lấy ở đây: https://cp-algorithms.com/graph/cutpoints.html
        """
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

        visited = set()
        tin = {}
        low = {}
        articulation_points = set()
        avail = tuple(self.avail_moves_coor(self.pos))
        if avail:
            start = avail[0]
            dfs(start)
            # dfs(self.avail_moves_coor(self.pos).__next__())
            return articulation_points
        return set()  # board đã full nên không có articulation points

    def is_articulation_point(self):
        """
        :return: True nếu bot đang đứng trên articulation point và ngược lại
        """
        try:
            next_move = tuple(self.avail_moves_1_player())[0]
            return self.flood_fill_count(self.pos) - 1 != next_move.flood_fill_count(next_move.pos)
        except:
            return False  # khi không có nút kề

    def is_separated(self):
        """
        2 người chơi đã ở trạng thái phân tách.
        """
        return len(self.flood_fill(self.pos) & self.flood_fill(self.opp_pos)) == 0

    def min_dist_bfs_obstacle(self, pos1, pos2):
        """ 
        Cũng tính min distance dựa vào BFS nhưng xét cả cho vị trí pos2 là 
        vật cản.
        """
        # chuyển vị trí pos2 thành ô trống trước, nếu không sẽ éo tìm được.
        temp = self.matrix[pos2[0]*SIZE+pos2[1]]
        self.matrix[pos2[0]*SIZE+pos2[1]] = '-'  

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
        return inf # nếu pos1 và pos2 không cùng thành phần liên thông 
                   # thì trả về inf.

    def min_dist_dijktra(self, pos):
        """
        Trả về một danh sách khoảng cách ngắn nhất từ tập điểm liên thông với 
        pos tới pos.
        """
        V = self.flood_fill(pos)
        d = {}
        for v in V:
            d[v] = inf
        d[pos] = 0
        for v in self.avail_moves_coor(pos):
            d[v] = 1
        V.remove(pos)
        V = [(d[v], v) for v in V]
        heapq.heapify(V)
        while V:
            u = heapq.heappop(V)[1]
            for v in self.avail_moves_coor(u):
                if d[v] > d[u] + 1:
                    d[v] = d[u] + 1
                    for i in range(len(V)):
                        if V[i][1] == v:
                            V[i] = (d[v], v)
                            heapq.heapify(V)
                            break
        return d

    def voronoi_point(self):
        """
        lãnh thổ voronoi tính bằng số ô

        Ý tưởng: 
        .trừ điểm cho mỗi articular point trong lãnh thổ của mình 
        .nghiên cứu thêm về chambers tree (https://www.a1k0n.net/2010/03/04/google-ai-postmortem.html)
        .hàm utility của a1k0n 55 (n1-n2) + 194 (e1-e2)?
        """
        point = 0
        me = self.min_dist_dijktra(self.pos)
        opp = self.min_dist_dijktra(self.opp_pos)
        for i in range(SIZE):
            for j in range(SIZE):
                if self.matrix[i * SIZE + j] == '-':
                    my_dist = me.get((i, j), inf)
                    opp_dist = opp.get((i, j), inf)
                    if my_dist > opp_dist:
                        point -= 1
                    elif my_dist == opp_dist == inf:
                        pass # không ai tới được (i, j) thì thôi không xét
                    else:
                        point += 1 # khoảng cách bằng nhau, bot của người chơi sẽ tới trước (do là game turn-based)
        return point

    def voronoi_edges(self):
        """
        lãnh thổ voronoi, tính theo cạnh
        """
        point = 0
        me = self.min_dist_dijktra(self.pos)
        opp = self.min_dist_dijktra(self.opp_pos)
        for i in range(SIZE):
            for j in range(SIZE):
                moves = self.avail_moves_count((i, j))
                if self.matrix[i * SIZE + j] == '-':
                    my_dist = me.get((i, j), inf)
                    opp_dist = opp.get((i, j), inf)
                    if my_dist > opp_dist:
                        point -= moves
                    elif my_dist == opp_dist == inf:
                        pass # không ai tới được (i, j) thì thôi không xét
                    else:
                        point += moves # khoảng cách bằng nhau, bot của người chơi sẽ tới trước (do là game turn-based)
        return point

    def space_heuristic(self):
        """
        Dùng đánh giá khoảng trống còn lại.
        """
        return self.flood_fill_count_checkerboard(self.pos) - \
                    self.flood_fill_count_checkerboard(self.opp_pos)

    def activate_minimax(self):
        """
        Chỉ sử dụng minimax khi đủ gần.
        """
        return self.min_dist_bfs_obstacle(self.pos, self.opp_pos) <= MINIMAX_DEPTH * 2


# Minimax algorithm: {{

def minimax(state, depth, alpha, beta):
    """
    Ý tưởng: 
    .có thể dùng iterative deepening search với độ sâu tăng dần, tính thời gian
        sau mỗi vòng lặp để giới hạn mỗi nước đi < 1s
    .trong trường hợp đi sau, phần minimax k thắng được >> có thể cầm hòa.
    (vd phần space sau khi phân tách kém 1 ô >> return point = 0 chứ không phải
    -10000 * 1 như trước)
    """
    max_val = -inf
    for next_state in state.avail_moves():
        next_min = min_value(next_state, depth + 1, alpha, beta)
        if max_val < next_min:
            max_val = next_min
            return_state = next_state
        alpha = max(alpha, max_val)
    return return_state


def max_value(state, depth, alpha, beta):
    global turn
    if depth == MINIMAX_DEPTH:
        point = 31 * state.voronoi_point() + 11 * state.voronoi_edges()
        return point if state.turn == turn else -point
    max_val = -inf
    for next_state in state.avail_moves():
        max_val = max(max_val, min_value(next_state, depth + 1, alpha, beta))
        alpha = max(alpha, max_val)
        if alpha >= beta:
            return max_val
    if max_val == -inf:
        return -100000 + depth
    return max_val


def min_value(state, depth, alpha, beta):
    global turn
    if depth == MINIMAX_DEPTH:
        point = 31 * state.voronoi_point() + 11 * state.voronoi_edges()
        return point if state.turn == turn else -point
    min_val = inf
    for next_state in state.avail_moves():
        min_val = min(min_val, max_value(next_state, depth + 1, alpha, beta))
        beta = min(beta, min_val)
        if alpha >= beta:
            return min_val
    if min_val == inf:
        return 100000 - depth
    return min_val
# }}

# Space fill algorithm: {{
def fill(state):
    next_state = max(state.avail_moves_1_player(), key=lambda x: filling_evaluate_with_depth(x, 1))
    return next_state

def filling_evaluate(state):
    """
    Đánh giá heuristic cho trạng thái đã separated, dùng để fill khoảng trống.
    """
    moves_count = state.avail_moves_count(state.pos)
    if moves_count == 0:
        return -10000
    point = state.flood_fill_count(state.pos) + state.flood_fill_count_checkerboard(state.pos) - 2 * moves_count - 4 * len(state.find_articulation_points())
    if state.is_articulation_point():
        point -= 500
    return point

def filling_evaluate_with_depth(state, depth):
    moves_count = state.avail_moves_count(state.pos)
    if moves_count == 0:
        return -10000
    if depth == FILL_DEPTH:
        point = state.flood_fill_count(state.pos) + state.flood_fill_count_checkerboard(state.pos) - 2 * moves_count - 4 * len(state.find_articulation_points())
        if state.is_articulation_point():  # trừ điểm khi bot đang ở articulation point
            point -= 500
        return point
    max_val = -inf
    for next_state in state.avail_moves_1_player():
        max_val = max(max_val, filling_evaluate_with_depth(next_state, depth + 1))
    return filling_evaluate(state) + max_val / (depth + 1)

def return_move(new, old):
    if new[0] == old[0] + 1 and new[1] == old[1]:
        return "DOWN"
    if new[0] == old[0] - 1 and new[1] == old[1]:
        return "UP"
    if new[0] == old[0] and new[1] == old[1] + 1:
        return "RIGHT"
    if new[0] == old[0] and new[1] == old[1] - 1:
        return "LEFT"
# }}


mat = Matrix(matrix, turn, cur_pos, opp_pos)

if mat.is_separated():
    new_pos = fill(mat).pos
else:
    if mat.activate_minimax(): 
        new_pos = minimax(mat, 1, -inf, inf).opp_pos
    else:
        new_pos = max(mat.avail_moves_1_player(), key=lambda x: 31 * x.voronoi_point() + 11 * x.voronoi_edges()).pos

print(return_move(new_pos, cur_pos))