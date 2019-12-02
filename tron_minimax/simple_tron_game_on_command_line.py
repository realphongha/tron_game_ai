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
import timeit
from collections import deque
import heapq

reverse = {'r': 'g', 'g': 'r'}
# constants:
SIZE = 0 # kích thước bảng
SQ_SIZE = 0 # SIZE * SIZE
FILL_DEPTH = 4 # độ sâu chế độ space fill
MINIMAX_DEPTH = 4 # độ sâu minimax

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
            self.matrix[self.pos[0] * SIZE + self.pos[1]] = '-'
            self.turn = reverse[self.turn]
            self.opp_pos = (self.opp_pos[0] - 1, self.opp_pos[1])
            self.pos, self.opp_pos = self.opp_pos, self.pos
        elif dir == -2:
            self.matrix[self.pos[0] * SIZE + self.pos[1]] = '-'
            self.turn = reverse[self.turn]
            self.opp_pos = (self.opp_pos[0] + 1, self.opp_pos[1])
            self.pos, self.opp_pos = self.opp_pos, self.pos
        elif dir == -3:
            self.matrix[self.pos[0] * SIZE + self.pos[1]] = '-'
            self.turn = reverse[self.turn]
            self.opp_pos = (self.opp_pos[0], self.opp_pos[1] - 1)
            self.pos, self.opp_pos = self.opp_pos, self.pos
        elif dir == -4:
            self.matrix[self.pos[0] * SIZE + self.pos[1]] = '-'
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

    def flood_fill_count_no_aps(self, cur_pos):
        aps = self.find_articulation_points()
        added = {cur_pos}
        wasnt_popped = {cur_pos}
        count = 0
        while wasnt_popped:
            pos = wasnt_popped.pop()
            for next_pos in self.avail_moves_coor(pos):
                if next_pos not in added and next_pos not in aps:
                    added.add(next_pos)
                    wasnt_popped.add(next_pos)
                    count += self.avail_moves_count(next_pos)
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

    def flood_fill_voronoi(self, my_pos, opp_pos):
        added = {}
        my_queue = {my_pos}
        opp_queue = {opp_pos}
        while not(not my_queue and not opp_queue):
            new_my_q = set()
            for pos in my_queue:
                for next_pos in self.avail_moves_coor(pos):
                    if next_pos not in added:
                        added[next_pos] = 0
                        new_my_q.add(next_pos)
            my_queue = new_my_q

            new_opp_q = set()
            for pos in opp_queue:
                for next_pos in self.avail_moves_coor(pos):
                    if next_pos not in added:
                        added[next_pos] = 1
                        new_opp_q.add(next_pos)
            opp_queue = new_opp_q
        return added


    def ultimate_flood_fill(self, pos, aps, added):
        if self.is_articulation_point_2(pos):
            return max(map(lambda x: self.smart_flood_fill(x, aps, added | {x}), self.avail_moves_coor(pos)))
        return self.smart_flood_fill(pos, aps, added)

    def smart_flood_fill(self, pos, aps, added):
        """
        Xét khoảng lớn nhất có thể fill với điều kiện khi qua điểm cắt 2 cạnh 
        thì không quay đầu được nữa.
        usage: smart_flood_fill(pos, aps, {pos})
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

        all_aps = set()
        for coor in self.avail_moves_coor(self.pos):
            visited = set()
            tin = {}
            low = {}
            articulation_points = set()
            dfs(coor)
            all_aps |= articulation_points
            if not self.is_articulation_point():
                break
        return all_aps

    def is_articulation_point(self):
        """
        :return: True nếu bot đang đứng trên articulation point và ngược lại
        """
        try:
            next_move = tuple(self.avail_moves_1_player())[0]
            return self.flood_fill_count(self.pos) - 1 != next_move.flood_fill_count(next_move.pos)
        except:
            return False

    def is_connected(self, pos1, pos2):
        """
        pos1 != pos
        """
        added = {pos1}
        wasnt_popped = {pos1}
        while wasnt_popped:
            pos = wasnt_popped.pop()
            for next_pos in self.avail_moves_coor(pos):
                if next_pos == pos2:
                    return True
                if next_pos not in added:
                    added.add(next_pos)
                    wasnt_popped.add(next_pos)
        return False

    def is_articulation_point_coor(self, pos):
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

    def is_articulation_point_2(self, pos):
        """
        :return: True nếu bot đang đứng trên articulation point và ngược lại
        """
        try:
            temp = 'g'
            temp, self.matrix[pos[0]*SIZE+pos[1]] = self.matrix[pos[0]*SIZE+pos[1]], temp
            next_move = tuple(self.avail_moves_coor(pos))[0]
            self.matrix[next_move[0]*SIZE + next_move[1]] = 'g'
            next_move_fill = self.flood_fill_count(next_move)
            self.matrix[next_move[0]*SIZE + next_move[1]] = '-'
            result = self.flood_fill_count(pos) - 1 != next_move_fill
            self.matrix[pos[0]*SIZE+pos[1]] = temp
            return result
        except:
            return False

    def is_separated(self):
        """
        2 người chơi đã ở trạng thái phân tách.
        """
        return len(self.flood_fill(self.pos) & self.flood_fill(self.opp_pos)) == 0

    def is_separated_2(self):
        added = set()
        wasnt_popped = {self.pos}
        while wasnt_popped:
            pos = wasnt_popped.pop()
            for next_pos in self.avail_moves_coor(pos):
                if abs(next_pos[0] - self.opp_pos[0]) + abs(next_pos[1] - self.opp_pos[1]) == 1:
                    return False
                if next_pos not in added:
                    added.add(next_pos)
                    wasnt_popped.add(next_pos)
        return True

    def is_separated_3(self):
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

    def voronoi_point2(self):
        point = 0
        me = self.min_dist_dijktra(self.pos)
        opp = self.min_dist_dijktra(self.opp_pos)
        while True:
            try:
                pos = me.popitem()
                my_dist = pos[1]
                opp_dist = opp.pop(pos[0], 1000)
            except:
                try:
                    pos = opp.popitem()
                    opp_dist = pos[1]
                    my_dist = me.pop(pos[0], 1000)
                except:
                    return point
            if my_dist > opp_dist:
                point -= 1
            else:
                point += 1

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

    def voronoi_domain(self, my_pos, opp_pos):
        my_domain = set()
        opp_domain = set()
        my_queue = {my_pos}
        opp_queue = {opp_pos}
        utility_edges = 0
        while not(not my_queue and not opp_queue):
            new_my_q = set()
            for pos in my_queue:
                for next_pos in self.avail_moves_coor(pos):
                    if next_pos not in my_domain and next_pos not in opp_domain:
                        my_domain.add(next_pos)
                        new_my_q.add(next_pos)
                        utility_edges += self.avail_moves_count(next_pos)
            my_queue = new_my_q

            new_opp_q = set()
            for pos in opp_queue:
                for next_pos in self.avail_moves_coor(pos):
                    if next_pos not in my_domain and next_pos not in opp_domain:
                        opp_domain.add(next_pos)
                        new_opp_q.add(next_pos)
                        utility_edges -= self.avail_moves_count(next_pos)
            opp_queue = new_opp_q
        return my_domain, opp_domain, utility_edges


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
    for next_state in state.avail_moves():
        next_min = min_value(next_state, depth + 1, alpha, beta)
        if max_val < next_min:
            max_val = next_min
            return_state = next_state
        alpha = max(alpha, max_val)
    print(max_val)
    # chắc không cần nữa:
    # if max_val == -inf:
    #     return tuple(state.avail_moves())[0]
    return return_state


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
    # if state.is_separated():
    #     point = 31 * state.space_heuristic() + 11 * state.voronoi_edges()
    #     if point > 1 or point < -1:
    #         return point * 5 if state.turn == turn else -point * 5
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
    next_state = max(state.avail_moves_1_player(), key=lambda x: filling_evaluate_with_depth_v6(x, 1))
    return next_state

def fill_greedy(state):
    """
    Fill dùng greedy heuristic. 
    Kỳ vọng sẽ thay cho hàm fill() bên trên nhưng tới giờ vẫn chạy như cc.
    Đọc hàm greedy_filling_evaluate() ở dưới để biết thêm.
    """
    remaining = 0
    next_states = [] # lưu đường đi lấy được vào đây
    if state.is_articulation_point():  # chọn thành phần liên thông size lớn nhất nếu hiện tại đang ở articulation point
        next_state = max(state.avail_moves_1_player(), key=lambda x: x.flood_fill_count(x.pos))
        remaining = 0
    elif remaining == 0:
        next_states = greedy_filling_evaluate(state, 1)[1][:-1]
        remaining = len(next_states) - 1
        next_state = next_states.pop()
    else:
        remaining -= 1
        next_state = next_states.pop()
    return next_state

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
        # min_val = min(map(lambda x: x.flood_fill_count(x.pos), state.avail_moves_1_player()))
        # if min_val <= 2:
        #     point -= 2 * min_val
        # else:
        #     point -= 20 * min_val
        point -= 20 * min(map(lambda x: x.flood_fill_count(x.pos), state.avail_moves_1_player()))
    return point

def filling_evaluate_v2(state):
    """
    Đánh giá heuristic cho trạng thái đã separated, dùng để fill khoảng trống.
    """
    moves_count = state.avail_moves_count(state.pos)
    if moves_count == 0:
        return -10000  # nếu đi vào ngõ cụt, trả về giá trị tệ nhất
    # if state.is_articulation_point(): # nếu ở AP thì xét điểm lớn nhất của các trạng thái con
    #     return max(map(lambda x: filling_evaluate(x), state.avail_moves_1_player())) + 2
    # công thức: số ô có thể tới - 2 * bậc của ô - 4 * số điểm cắt trong các ô có thể tới
    point = filling_evaluate_v3(state) + state.flood_fill_count_checkerboard(state.pos) - 2 * moves_count - 4 * len(state.find_articulation_points())
    if state.is_articulation_point():  # trừ điểm khi bot đang ở articulation point
        point -= 500
    return point


def filling_evaluate_v3(state):
    if state.is_articulation_point():  
        return max(map(lambda x: filling_evaluate_v3(x), state.avail_moves_1_player())) + state.avail_moves_count(state.pos) + 1
    return state.flood_fill_count_no_aps(state.pos) + state.flood_fill_count_checkerboard(state.pos) - 2 * state.avail_moves_count(state.pos) - 4 * len(state.find_articulation_points())

def filling_evaluate_v4(state):
    if state.is_articulation_point():  
        return max(map(lambda x: filling_evaluate_v3(x), state.avail_moves_1_player())) + 1.5
    return state.flood_fill_count(state.pos) + state.flood_fill_count_checkerboard(state.pos) - 2 * state.avail_moves_count(state.pos) - 4 * len(state.find_articulation_points())

def filling_evaluate_v5(state):
    moves_count = state.avail_moves_count(state.pos)
    if moves_count == 0:
        return -10000
    aps = state.find_articulation_points()
    return 10 * state.ultimate_flood_fill(state.pos, aps, {state.pos}) + state.flood_fill_count_checkerboard(state.pos) - 2 * moves_count - 4 * len(aps)

def filling_evaluate_with_depth_v5(state, depth):
    moves_count = state.avail_moves_count(state.pos)
    if moves_count == 0:
        return -10000
    if depth == FILL_DEPTH:
        aps = state.find_articulation_points()
        return 10 * state.ultimate_flood_fill(state.pos, aps, {state.pos}) + state.flood_fill_count_checkerboard(state.pos) - 2 * moves_count - 4 * len(aps)
    max_val = -inf
    for next_state in state.avail_moves_1_player():
        max_val = max(max_val, filling_evaluate_with_depth_v5(next_state, depth + 1))
    return filling_evaluate_v5(state) + max_val / (depth + 1)

def filling_evaluate_v6(state):
    moves_count = state.avail_moves_count(state.pos)
    if moves_count == 0:
        return -10000
    aps = state.find_articulation_points()
    return 11 * state.ultimate_flood_fill(state.pos, aps, {state.pos}) - 2 * moves_count - 4 * len(aps)

def filling_evaluate_with_depth_v6(state, depth):
    moves_count = state.avail_moves_count(state.pos)
    if moves_count == 0:
        return -10000
    if depth == FILL_DEPTH:
        aps = state.find_articulation_points()
        return 11 * state.ultimate_flood_fill(state.pos, aps, {state.pos}) - 2 * moves_count - 4 * len(aps)
    max_val = -inf
    for next_state in state.avail_moves_1_player():
        max_val = max(max_val, filling_evaluate_with_depth_v5(next_state, depth + 1))
    return filling_evaluate_v5(state) + max_val / (depth + 1)

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
            # min_val = min(map(lambda x: x.flood_fill_count(x.pos), state.avail_moves_1_player()))
            # if min_val <= 2:
            #     point -= 2 * min_val
            # else:
            #     point -= 20 * min_val
            point -= 20 * min(map(lambda x: x.flood_fill_count(x.pos), state.avail_moves_1_player()))
        return point
    max_val = -inf
    for next_state in state.avail_moves_1_player():
        max_val = max(max_val, filling_evaluate_with_depth(next_state, depth + 1))
    return filling_evaluate(state) + max_val / (depth + 1)

def flood_fill_v2(state):
    if state.is_articulation_point():
        return max(map(lambda x: flood_fill_v2(x), state.avail_moves_1_player())) + state.avail_moves_count(state.pos)
    return state.flood_fill_count_no_aps(state.pos)

def filling_evaluate_with_depth_v2(state, depth):
    """
    Hàm đơn giản để áp dụng hàm filling_evaluate() bên trên với chiều sâu FILL_DEPTH.
    """
    spaces_left = state.flood_fill_count_checkerboard(state.pos)
    if depth == 10:
        # point = flood_fill_v2(state) + spaces_left - 2 * state.avail_moves_count(state.pos) - 4 * len(state.find_articulation_points())
        # return point
        return filling_evaluate_v2(state)
    max_val = 0
    for next_state in state.avail_moves_1_player():
        new_val = 1 + filling_evaluate_with_depth_v2(next_state, depth + 1)
        if new_val > max_val:
            max_val = new_val
        if new_val == spaces_left:
            break
    return max_val

def filling_evaluate_with_depth_v3(state, depth):
    """
    Hàm đơn giản để áp dụng hàm filling_evaluate() bên trên với chiều sâu FILL_DEPTH.
    """ 
    if depth == 6:
        return filling_evaluate_v3(state)
    max_val = -10000
    for next_state in state.avail_moves_1_player():
        max_val = max(max_val, filling_evaluate_with_depth_v3(next_state, depth + 1))
    return max_val

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

def greedy_filling_evaluate(state, depth):
    """
    Trả về trạng thái con ở cuối cây với giá trị lớn nhất và đường đi từ trạng thái hiện tại tới đó.
    """
    if state.avail_moves_count(state.pos) == 0 or depth == 7:
        return (filling_evaluate_v3(state), [state])
    max_val = (-inf, None)
    for next_state in state.avail_moves_1_player():
        max_val = max(max_val, greedy_filling_evaluate(next_state, depth + 1), key = lambda x: x[0])
    max_val[1].append(state)
    return max_val

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




def dfs_run(state, start_time, max_time):
    stack = [state.pos]
    dfs_depth = [1] 
    visit = [[False for _ in range(SIZE)] for __ in range(SIZE)]
    visit[state.pos[0]][state.pos[1]] = True
    max_dfs_depth = 1
    while stack:
        #neu qua thoi gian cho phep, tra luon ve do sau lon nhat da duyet toi
        if time()-start_time > max_time:
            return max(max_dfs_depth, dfs_depth[-1])

        cur_pos = stack[-1]
        nl = state.avail_moves_coor(cur_pos)
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


def fill2(state):
    MAX_TIME = 1 / state.avail_moves_count(state.pos)
    if state.is_articulation_point():
        # next_state = max(map(lambda x: dfs_run(x, time(), MAX_TIME) + state.flood_fill_count(state.pos) - \
        #                                4 * len(state.find_articulation_points()), state.avail_moves()))
        next_state = max(state.avail_moves_1_player(), key = lambda x: dfs_run(x, time(), MAX_TIME) + state.flood_fill_count(state.pos) - \
                                       4 * len(state.find_articulation_points()))
    else:
        # next_state = max(map(lambda x: dfs_run(x, time(), MAX_TIME), state.avail_moves()))
        next_state = max(state.avail_moves_1_player(), key=lambda x: dfs_run(x, time(), MAX_TIME))
    return next_state


# chạy thôi:
cur = Matrix(matrix, turn, cur_pos, opp_pos)
cur.display(0)

# start = time()
# for i in range(1000):
#     cur.is_articulation_point()
# print(time()-start)
# start = time()
# for i in range(1000):
#     cur.is_articulation_point_2(cur.pos)
# print(time()-start)
# start = time()
# for i in range(1000):
#     cur.is_articulation_point_coor(cur.pos)
# print(time()-start)

# start = time()
# for i in range(5000):
#     cur.is_separated_3()
# print(time()-start)
# start = time()
# for i in range(5000):
#     cur.is_separated_2()
# print(time()-start)

print (cur.is_separated_3())

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
                cur = fill(cur)
                cur.turn = reverse[cur.turn]
                cur.pos, cur.opp_pos = cur.opp_pos, cur.pos
            else:
                # dùng minimax luôn từ đầu:

                print("MINIMAX MODE!")
                cur = minimax(cur, 1, -inf, inf)

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
                cur = fill(cur)
                cur.turn = reverse[cur.turn]
                cur.pos, cur.opp_pos = cur.opp_pos, cur.pos
            else:
                # dùng minimax luôn từ đầu:

                print("MINIMAX MODE!")
                cur = minimax(cur, 1, -inf, inf)

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
            cur.display(0)