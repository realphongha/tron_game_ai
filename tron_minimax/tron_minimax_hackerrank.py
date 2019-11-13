from math import inf

reverse = {'r': 'g', 'g': 'r'}
# constant:
SIZE = 15
SQ_SIZE = SIZE * SIZE
FILL_DEPTH = 5
MINIMAX_DEPTH = 4

# handles input (from hackerrank):
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
        self.matrix = matrix.copy()
        self.turn = turn
        self.pos = pos
        self.opp_pos = opp_pos

    def display(self, time):
        # for debugging
        for i in range(SQ_SIZE):
            if i % SIZE == 0:
                print()
            print(self.matrix[i], end=' ')
        if time:
            sleep(time)

    def avail_moves(self):
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

    def flood_fill_count(self):
        """
        :return: số node liên thông với node của bot hiện tại (không tính node hiện tại)
        """
        added = {self.pos}
        wasnt_popped = {self.pos}
        count = 0
        while wasnt_popped:
            pos = wasnt_popped.pop()
            for next_pos in self.avail_moves_coor(pos):
                if next_pos not in added:
                    added.add(next_pos)
                    wasnt_popped.add(next_pos)
                    count += 1
        return count

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
            trong khoảng không gian bot có thể tới.
        Không rõ nó hoạt động như nào nhưng vẫn chạy đúng.
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
            return self.flood_fill_count() - 1 != tuple(self.avail_moves_1_player())[0].flood_fill_count()
        except:
            return False  # khi không có nút kề

    def is_separated(self):
        return len(self.flood_fill(self.pos) & self.flood_fill(self.opp_pos)) == 0

    def manhattan_dist(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def voronoi_heuristic_evaluate(self):
        """
        Đánh giá heuristic cho 1 trạng thái trước khi separated, dùng cho minimax
        :return: giá trị trạng thái đang xét
        """
        global turn
        point = 0
        for i in range(SIZE):
            for j in range(SIZE):
                if self.matrix[i * SIZE + j] == '-':
                    my_pos_flood_fill = self.flood_fill(self.pos)
                    opp_pos_flood_fill = self.flood_fill(self.opp_pos)
                    if (i, j) in my_pos_flood_fill and (i, j) not in opp_pos_flood_fill:
                        point += 1
                    elif (i, j) not in my_pos_flood_fill and (i, j) in opp_pos_flood_fill:
                        point -= 1
                    elif (i, j) not in my_pos_flood_fill and (i, j) not in opp_pos_flood_fill:
                        pass
                    else:
                        moves_count = self.avail_moves_count((i, j))
                        if self.manhattan_dist(self.pos, (i, j)) < self.manhattan_dist(self.opp_pos, (i, j)):
                            point += 1
                        elif self.manhattan_dist(self.pos, (i, j)) > self.manhattan_dist(self.opp_pos, (i, j)):
                            point -= 1
                        else:
                            pass
        if self.turn == turn:
            return point
        return -point

    def activate_minimax(self):
        return self.manhattan_dist(self.pos, self.opp_pos) <= MINIMAX_DEPTH + 1


def minimax(state, depth):
    return max(state.avail_moves(), key=lambda x: min_value(x, depth + 1, -inf, inf))


def max_value(state, depth, alpha, beta):
    if depth == MINIMAX_DEPTH:
        if state.is_separated():
            point = 10000 * (state.flood_fill_count() - len(state.flood_fill(state.opp_pos)))
            return point if state.turn == turn else -point
        return state.voronoi_heuristic_evaluate()
    max_val = -inf
    for next_state in state.avail_moves():
        max_val = max(max_val, min_value(next_state, depth + 1, alpha, beta))
        if max_val >= beta:
            return max_val
        alpha = max(alpha, max_val)
    return max_val


def min_value(state, depth, alpha, beta):
    if depth == MINIMAX_DEPTH:
        if state.is_separated():
            point = 10000 * (state.flood_fill_count() - len(state.flood_fill(state.opp_pos)))
            return point if state.turn == turn else -point
        return state.voronoi_heuristic_evaluate()
    min_val = inf
    for next_state in state.avail_moves():
        min_val = min(min_val, max_value(next_state, depth + 1, alpha, beta))
        if min_val <= alpha:
            return min_val
        beta = min(beta, min_val)
    return min_val


def fill(state):
    """
    Chế độ fill khoảng trống khi 2 player đã tách khỏi nhau
    :param state: trạng thái hiện tại
    :return: trạng thái di chuyển có lợi nhất tiếp theo
    """
    if state.is_articulation_point():  # chọn thành phần liên thông size lớn nhất nếu hiện tại đang ở articulation point
        next_state = max(state.avail_moves_1_player(), key=lambda x: x.flood_fill_count())
    else:  # nếu không ở articulation point, dùng hàm đánh giá trạng thái để xác định nước tiếp theo:
        next_state = max(state.avail_moves_1_player(), key=lambda x: filling_evaluate_with_depth(x, 0))
    return next_state


def filling_evaluate(state):
    moves_count = state.avail_moves_count(state.pos)
    if moves_count == 0:
        return -10000  # nếu đi vào ngõ cụt, trả về giá trị tệ nhất
    point = state.flood_fill_count() - 2 * moves_count - 4 * len(state.find_articulation_points())
    if state.is_articulation_point():  # trừ điểm khi bot đang ở articulation point
        point -= 500
    return point


def filling_evaluate_with_depth(state, depth):
    """
    Đánh giá heuristic cho trạng thái đã separated, dùng để fill khoảng trống
    :param state: trạng thái hiện tại
    :param depth: độ sâu sẽ xét
    :return: đánh giá trạng thái hiện tại
    """
    moves_count = state.avail_moves_count(state.pos)
    if moves_count == 0:
        return -10000
    if depth == FILL_DEPTH:
        point = state.flood_fill_count() - 2 * moves_count - 4 * len(state.find_articulation_points())
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


mat = Matrix(matrix, turn, cur_pos, opp_pos)

if mat.is_separated():
    new_pos = fill(mat).pos
else:
    if mat.activate_minimax():
        new_pos = minimax(mat, 0).opp_pos
    else:
        new_pos = max(mat.avail_moves_1_player(), key=lambda x: x.voronoi_heuristic_evaluate()).pos

print(return_move(new_pos, cur_pos))