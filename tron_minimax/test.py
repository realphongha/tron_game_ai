"""
Game Tron đơn giản trên command line.
Mục đích chính để debug.

Nhập vào trạng thái ban đầu để tạo ván chơi mới.

Input mẫu:
11
g
10 10 0 0
g----------
-----------
------#----
---#-------
-----------
-----------
-----------
-------#---
----#------
-----------
----------r
>>> kích thước bảng là 11, g sẽ đi trước, vị trí của g là (0, 0) và vị trí của r 
là (10, 10)

Chọn mode 1 để chơi với máy (AI vs Player), mode 2 để máy tự chơi (AI vs AI).

Lưu ý khi chơi AI vs Player, g sẽ là bot, r là player, nếu muốn player đi trước 
thì thay g bằng r ở dòng đầu).
"""

from math import inf
from time import sleep, time
from collections import deque
import heapq

reverse = {'r': 'g', 'g': 'r'}
# constants:
SIZE = 0 # kích thước bảng
SQ_SIZE = 0 # SIZE * SIZE
FILL_DEPTH = 6 # độ sâu chế độ space fill
MINIMAX_DEPTH = 7 # độ sâu minimax

# handles input:
SIZE = int(input())
SQ_SIZE = SIZE * SIZE
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
                # self.matrix[(self.pos[0] + 1) * SIZE + self.pos[1]] = self.turn
                # yield Matrix(self.matrix, reverse[self.turn], self.opp_pos, (self.pos[0] + 1, self.pos[1]))
                # self.matrix[(self.pos[0] + 1) * SIZE + self.pos[1]] = '-'
                yield 1
        if self.pos[0] - 1 >= 0:
            if self.matrix[(self.pos[0] - 1) * SIZE + self.pos[1]] == '-' and self.pos[0] - 1 >= 0:
                # self.matrix[(self.pos[0] - 1) * SIZE + self.pos[1]] = self.turn
                # yield Matrix(self.matrix, reverse[self.turn], self.opp_pos, (self.pos[0] - 1, self.pos[1]))
                # self.matrix[(self.pos[0] - 1) * SIZE + self.pos[1]] = '-'
                yield 2
        if self.pos[1] + 1 < SIZE:
            if self.matrix[self.pos[0] * SIZE + self.pos[1] + 1] == '-' and self.pos[1] + 1 < SIZE:
                # self.matrix[self.pos[0] * SIZE + self.pos[1] + 1] = self.turn
                # yield Matrix(self.matrix, reverse[self.turn], self.opp_pos, (self.pos[0], self.pos[1] + 1))
                # self.matrix[self.pos[0] * SIZE + self.pos[1] + 1] = '-'
                yield 3
        if self.pos[1] - 1 >= 0:
            if self.matrix[self.pos[0] * SIZE + self.pos[1] - 1] == '-' and self.pos[1] - 1 >= 0:
                # self.matrix[self.pos[0] * SIZE + self.pos[1] - 1] = self.turn
                # yield Matrix(self.matrix, reverse[self.turn], self.opp_pos, (self.pos[0], self.pos[1] - 1))
                # self.matrix[self.pos[0] * SIZE + self.pos[1] - 1] = '-'
                yield 4

    def avail_moves_1_player(self):
        """
        debug chế độ fill 1 người chơi, trả về state mới có turn, pos, opp_pos giống state cũ
        """
        if self.pos[0] + 1 < SIZE:
            if self.matrix[(self.pos[0] + 1) * SIZE + self.pos[1]] == '-' and self.pos[0] + 1 < SIZE:
                # self.matrix[(self.pos[0] + 1) * SIZE + self.pos[1]] = self.turn
                # yield Matrix(self.matrix, self.turn, (self.pos[0] + 1, self.pos[1]), self.opp_pos)
                # self.matrix[(self.pos[0] + 1) * SIZE + self.pos[1]] = '-'
                yield 1
        if self.pos[0] - 1 >= 0:
            if self.matrix[(self.pos[0] - 1) * SIZE + self.pos[1]] == '-' and self.pos[0] - 1 >= 0:
                # self.matrix[(self.pos[0] - 1) * SIZE + self.pos[1]] = self.turn
                # yield Matrix(self.matrix, self.turn, (self.pos[0] - 1, self.pos[1]), self.opp_pos)
                # self.matrix[(self.pos[0] - 1) * SIZE + self.pos[1]] = '-'
                yield 2
        if self.pos[1] + 1 < SIZE:
            if self.matrix[self.pos[0] * SIZE + self.pos[1] + 1] == '-' and self.pos[1] + 1 < SIZE:
                # self.matrix[self.pos[0] * SIZE + self.pos[1] + 1] = self.turn
                # yield Matrix(self.matrix, self.turn, (self.pos[0], self.pos[1] + 1), self.opp_pos)
                # self.matrix[self.pos[0] * SIZE + self.pos[1] + 1] = '-'
                yield 3
        if self.pos[1] - 1 >= 0:
            if self.matrix[self.pos[0] * SIZE + self.pos[1] - 1] == '-' and self.pos[1] - 1 >= 0:
                # self.matrix[self.pos[0] * SIZE + self.pos[1] - 1] = self.turn
                # yield Matrix(self.matrix, self.turn, (self.pos[0], self.pos[1] - 1), self.opp_pos)
                # self.matrix[self.pos[0] * SIZE + self.pos[1] - 1] = '-'
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
            self.matrix[self.opp_pos[0] * SIZE + self.opp_pos[1]] = '-'
            self.turn = reverse[self.turn]
            self.opp_pos = (self.opp_pos[0] - 1, self.opp_pos[1])
            self.pos, self.opp_pos = self.opp_pos, self.pos
        elif dir == -2:
            self.matrix[self.opp_pos[0] * SIZE + self.opp_pos[1]] = '-'
            self.turn = reverse[self.turn]
            self.opp_pos = (self.opp_pos[0] + 1, self.opp_pos[1])
            self.pos, self.opp_pos = self.opp_pos, self.pos
        elif dir == -3:
            self.matrix[self.opp_pos[0] * SIZE + self.opp_pos[1]] = '-'
            self.turn = reverse[self.turn]
            self.opp_pos = (self.opp_pos[0], self.opp_pos[1] - 1)
            self.pos, self.opp_pos = self.opp_pos, self.pos
        elif dir == -4:
            self.matrix[self.opp_pos[0] * SIZE + self.opp_pos[1]] = '-'
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
            self.matrix[self.pos[0] * SIZE + self.pos[1]] = '-'
            self.pos = (self.pos[0] - 1, self.pos[1])
        elif dir == -2:
            self.matrix[self.pos[0] * SIZE + self.pos[1]] = '-'
            self.pos = (self.pos[0] + 1, self.pos[1])
        elif dir == -3:
            self.matrix[self.pos[0] * SIZE + self.pos[1]] = '-'
            self.pos = (self.pos[0], self.pos[1] - 1)
        elif dir == -4:
            self.matrix[self.pos[0] * SIZE + self.pos[1]] = '-'
            self.pos = (self.pos[0], self.pos[1] + 1)

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
            cur_flood_fill = self.flood_fill_count(self.pos)
            self.move_1_player(next_move)
            next_flood_fill = self.flood_fill_count(self.pos)
            self.move_1_player(-next_move)
            # return self.flood_fill_count(self.pos) - 1 != next_move.flood_fill_count(next_move.pos)
            return cur_flood_fill - 1 != next_flood_fill
        except:
            return False  # khi không có nút kề

    def is_separated(self):
        """
        2 người chơi đã ở trạng thái phân tách.
        """
        return len(self.flood_fill(self.pos) & self.flood_fill(self.opp_pos)) == 0

    def manhattan_dist(self, pos1, pos2):
        """
        Khoảng cách manhattan (không dùng nữa).
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def min_dist_bfs(self, pos1, pos2):
        """ 
        Khoảng cách nhỏ nhất dùng BFS (không dùng nữa).
        """
        visited = {pos1: 0} 
        queue = deque([pos1])
        while queue:
            pos = queue.popleft()
            if pos == pos2:
                return visited[pos]
            for next_pos in self.avail_moves_coor(pos): 
                if next_pos not in visited: 
                    visited[next_pos] = visited[pos] + 1 
                    queue.append(next_pos) 
        return inf # nếu pos1 và pos2 không cùng thành phần liên thông 
                   # thì trả về inf.

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

    def voronoi_heuristic_evaluate(self):
        """
        Đánh giá heuristic cho 1 trạng thái trước khi separated, dùng cho minimax.
        Công thức: tổng bậc của các ô gần vị trí người chơi - tổng bậc các ô gần vị trí đối thủ
        (tính theo khoảng cách ngắn nhất - dùng dijktra) 

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
                moves = self.avail_moves_count((i, j))
                if self.matrix[i * SIZE + j] == '-':
                    my_dist = me.get((i, j), inf)
                    opp_dist = opp.get((i, j), inf)
                    if my_dist > opp_dist:
                        point -= (31 + 11 * moves)
                    elif my_dist == opp_dist == inf:
                        pass # không ai tới được (i, j) thì thôi không xét
                    else:
                        point += (31 + 11 * moves) # khoảng cách bằng nhau, bot của người chơi sẽ tới trước (do là game turn-based)
        return point

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
def minimax2(state, depth):
    """
    Cái này giống cái dưới nhưng chậm hơn, giữ lại một thời gian backup cho an toàn
    Ý tưởng: 
    .có thể dùng iterative deepening search với độ sâu tăng dần, tính thời gian
        sau mỗi vòng lặp để giới hạn mỗi nước đi < 1s
    .trong trường hợp đi sau, phần minimax k thắng được >> có thể cầm hòa.
    (vd phần space sau khi phân tách kém 1 ô >> return point = 0 chứ không phải
    -10000 * 1 như trước)
    """
    return max(state.avail_moves(), key=lambda x: min_value(x, depth + 1, -inf, inf))

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
    return_move = 0
    for next_move in state.avail_moves():
        state.move(next_move)
        next_min = min_value(state, depth + 1, alpha, beta)
        if max_val < next_min:
            max_val = next_min
            return_move = next_move
        alpha = max(alpha, max_val)
        state.move(-next_move)
    print(max_val)
    # chắc không cần nữa:
    # if max_val == -inf:
    #     return tuple(state.avail_moves())[0]
    return return_move


def max_value(state, depth, alpha, beta):
    # if state.avail_moves_count(state.pos) == 0:
    #     return -inf if state.turn == turn else inf
    # >> khi vào deadend, trả về -inf nếu là turn người chơi và ngược lại
    # viết ra đây cho rõ chứ trong trường hợp đấy hàm cũng tự trả về 
    # max_val = -inf như dưới rồi.
    global turn
    # if state.is_separated():
    #         # state.pos, state.opp_pos = state.opp_pos, state.pos
    #         # opp_point = filling_evaluate_minimax(state)
    #         # state.pos, state.opp_pos = state.opp_pos, state.pos
    #         # point = filling_evaluate_minimax(state) - opp_point - 0.5
    #         # return point if state.turn == turn else -point
    #         point = 31 * state.space_heuristic() + 11 * state.voronoi_edges()
    #         if point > 1 or point < -1:
    #             return point * 5 if state.turn == turn else -point * 5
    if depth == MINIMAX_DEPTH:
        point = 31 * state.voronoi_point() + 11 * state.voronoi_edges()
        return point if state.turn == turn else -point
    max_val = -inf
    for next_move in state.avail_moves():
        state.move(next_move)
        max_val = max(max_val, min_value(state, depth + 1, alpha, beta))
        state.move(-next_move)
        alpha = max(alpha, max_val)
        if alpha >= beta:
            return max_val
    if max_val == -inf:
        return -100000 + depth
    return max_val


def min_value(state, depth, alpha, beta):
    global turn
    # if state.is_separated():
    #     point = 31 * state.space_heuristic() + 11 * state.voronoi_edges()
    #     if point > 1 or point < -1:
    #         return point * 5 if state.turn == turn else -point * 5
    if depth == MINIMAX_DEPTH:
        point = 31 * state.voronoi_point() + 11 * state.voronoi_edges()
        return point if state.turn == turn else -point
    min_val = inf
    for next_move in state.avail_moves():
        state.move(next_move)
        min_val = min(min_val, max_value(state, depth + 1, alpha, beta))
        state.move(-next_move)
        beta = min(beta, min_val)
        if alpha >= beta:
            return min_val
    if min_val == inf:
        return 100000 - depth
    return min_val
# }}

# Space fill algorithm: {{
def fill(state):
    """
    Chế độ fill khoảng trống khi 2 player đã tách khỏi nhau
    :param state: trạng thái hiện tại
    :return: trạng thái di chuyển có lợi nhất tiếp theo
    Ý tưởng: 
    .dùng ids giống minimax đã nêu.
    .red and black checkerboard? (của a1k0n)
    """
    # if state.is_articulation_point():  # chọn thành phần liên thông size lớn nhất nếu hiện tại đang ở articulation point
    #     next_state = max(state.avail_moves_1_player(), key=lambda x: x.flood_fill_count(x.pos))
    # else:  # nếu không ở articulation point, dùng hàm đánh giá trạng thái để xác định nước tiếp theo:
    #     next_state = max(state.avail_moves_1_player(), key=lambda x: filling_evaluate_with_depth(x, 1))
    max_val = -100000
    for next_move in state.avail_moves_1_player():
        state.move_1_player(next_move)
        point = filling_evaluate_with_depth(state, 1)
        state.move_1_player(-next_move)
        if point > max_val:
            max_val = point
            return_move = next_move
    return return_move


def filling_evaluate(state):
    """
    Đánh giá heuristic cho trạng thái đã separated, dùng để fill khoảng trống.
    """
    moves_count = state.avail_moves_count(state.pos)
    if moves_count == 0:
        return -10000  # nếu đi vào ngõ cụt, trả về giá trị tệ nhất
    # if state.is_articulation_point(): # nếu ở AP thì xét điểm lớn nhất của các trạng thái con
    #     return max(map(lambda x: filling_evaluate(x), state.avail_moves_1_player())) + 2
    # công thức: số ô có thể tới - 2 * bậc của ô - 4 * số điểm cắt trong các ô có thể tới
    point = state.flood_fill_count(state.pos) + state.flood_fill_count_checkerboard(state.pos) - 2 * moves_count - 4 * len(state.find_articulation_points())
    if state.is_articulation_point():  # trừ điểm khi bot đang ở articulation point
        point -= 500
    return point

def filling_evaluate_minimax(state):
    """
    Đánh giá heuristic cho trạng thái đã separated, dùng trong cuối phần minimax.
    .xét tới articulation point?
    """
    if state.is_articulation_point():  # nếu bot ở articular point, tính dựa trên trạng thái con lớn nhất
        #return filling_evaluate_minimax(max(state.avail_moves_1_player(), key = lambda x: filling_evaluate_minimax(x))) + 1
        return max(map(lambda x: filling_evaluate_minimax(x), state.avail_moves_1_player())) + 1
    point = state.flood_fill_count(state.pos)
    return point


def filling_evaluate_with_depth(state, depth):
    """
    Hàm đơn giản để áp dụng hàm filling_evaluate() bên trên với chiều sâu FILL_DEPTH.
    """
    moves_count = state.avail_moves_count(state.pos)
    if moves_count == 0:
        return -10000
    if depth == FILL_DEPTH:
        point = state.flood_fill_count(state.pos) + state.flood_fill_count_checkerboard(state.pos) - 2 * moves_count - 4 * len(state.find_articulation_points())
        if state.is_articulation_point():  # trừ điểm khi bot đang ở articulation point
            point -= 500
        return point
    max_val = -inf
    for next_move in state.avail_moves_1_player():
        state.move_1_player(next_move)
        max_val = max(max_val, filling_evaluate_with_depth(state, depth + 1))
        state.move_1_player(-next_move)
    return filling_evaluate(state) + max_val / (depth + 1)
# }}


# chạy thôi:
cur = Matrix(matrix, turn, cur_pos, opp_pos)
cur.display(0)

mode = input("\nChoose play mode (1 - AI vs Player, 2 - AI vs AI): ")
if mode == '1': # AI vs Player
    turn = 'g' # máy luôn là 'g'
    while True:
        if cur.avail_moves_count(cur.opp_pos) == 0:
            print("\nEnd game!")
            break
        if cur.turn == 'r':
            player_move = tuple(map(int, input("\nYou are 'r'.\nEnter your move\n(For example: '0 2' means position (0, 2)): ").rstrip().split()))
            cur.matrix[player_move[0] * SIZE + player_move[1]] = 'r'
            cur.pos = player_move
            cur.turn = reverse[cur.turn]
            cur.pos, cur.opp_pos = cur.opp_pos, cur.pos
            cur.display(0)
        if cur.avail_moves_count(cur.opp_pos) == 0:
            print("\nEnd game!")
            break
        if cur.turn == 'g':
            print("\nAI move:")
            start = time()

            ### AI thinking...
            if cur.is_separated():
                print("FILL MODE!")
                next_move = fill(cur)
                cur.move_1_player(next_move)
                cur.turn = reverse[cur.turn]
                cur.pos, cur.opp_pos = cur.opp_pos, cur.pos
            else:
                # dùng minimax luôn từ đầu:

                print("MINIMAX MODE!")
                next_move = minimax(cur, 1, -inf, inf)
                cur.move(next_move)

                # hai bot gần nhau mới dùng:

                # if cur.activate_minimax():
                #     print("MINIMAX MODE!") 
                #     cur = minimax(cur, 1, -inf, inf)
                # else:
                #     print("PRE MINIMAX MODE!")
                #     cur = max(cur.avail_moves_1_player(), key=lambda x: x.voronoi_heuristic_evaluate())
                #     cur.turn = reverse[cur.turn]
                #     cur.pos, cur.opp_pos = cur.opp_pos, cur.pos
            ###

            print("Time:", time()-start, "(s)")
            cur.display(0)
elif mode == '2': # AI vs AI
    while True:
        if cur.avail_moves_count(cur.pos) == 0:
            print("\nEnd game!")
            break
        else:
            print("\nAI move:")
            start = time()

            ### AI thinking...
            if cur.is_separated():
                print("FILL MODE!")
                next_move = fill(cur)
                cur.move_1_player(next_move)
                cur.turn = reverse[cur.turn]
                cur.pos, cur.opp_pos = cur.opp_pos, cur.pos
            else:
                # dùng minimax luôn từ đầu:

                print("MINIMAX MODE!")
                next_move = minimax(cur, 1, -inf, inf)
                cur.move(next_move)

                # hai bot gần nhau mới dùng:

                # if cur.activate_minimax(): 
                #     print("MINIMAX MODE!") 
                #     cur = minimax(cur, 1, -inf, inf)
                # else:
                #     print("PRE MINIMAX MODE!")
                #     print(cur.min_dist_bfs(cur.pos, cur.opp_pos))
                #     cur = max(cur.avail_moves_1_player(), key=lambda x: x.voronoi_heuristic_evaluate())
                #     cur.turn = reverse[cur.turn]
                #     cur.pos, cur.opp_pos = cur.opp_pos, cur.pos
            ###

            print("Time:", time()-start, "(s)")
            turn = reverse[turn]
            cur.display(0.3)