package myTeamBot_v1;

import java.util.ArrayList;
import java.util.LinkedList;
import java.util.Queue;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import main.AbstractClientPlayer;
import main.AbstractClientPlayer.Vector2;

public class Bot5_Debug extends AbstractClientPlayer{
	private static final int DEPTH_MINIMAX = 13;
	private static final int MAXIMUM = 80000;
	private static final int MINIMUM = -80000;
	int[] priceofspace = new int[5];
	int amountnode;
	boolean separated = false;
	private boolean alphabeta = true;
	
	private static final int FILLING_EVALUATE_DEPTH = 15;
		
	private enum Direction {NONE, UP, DOWN, LEFT, RIGHT}
	
	private class Point {
		int x;
		int y;

		public Point(int x, int y) {
			this.x = x;
			this.y = y;
		}
	}
	
	private Map mapObj;
	Vector2 myPos, enemyPos;
	Direction direction;
		
	public Bot5_Debug(String team) 
			throws Exception {
		super(team);
		
		// Thêm các khởi tạo cho lớp nếu cần
		// ...
	}
	
	@Override
	public JSONObject configTeamInfo() throws JSONException {
		// Hàm để thiết lập thông tin về đội chơi
		ArrayList<JSONObject> members = new ArrayList<JSONObject>();
		JSONObject teamInfo = new JSONObject();
		teamInfo.put("team", teamSymbol);
		
		//Thêm thông tin thành viên trong nhóm theo mẫu dưới
		members.add( new JSONObject("{name: Hà Hữu Linh, mssv: 20190000}"));
		members.add( new JSONObject("{name: Hà Hải Phong, mssv: 20190000}"));
		members.add( new JSONObject("{name: Vũ Quang Đại, mssv: 20190000}"));
		members.add( new JSONObject("{name: Phạm Huy, mssv: 20190000}"));
			
		// Nhập tên team ở đây
		teamInfo.put("name", "My Team");
		
		teamInfo.put("members", members);		
		return teamInfo;
	}
	
	@Override
	public void newMapHandle(JSONObject data) throws JSONException{
		// Hàm xử lý khi bắt đầu vào trận. Server sẽ gửi thông tin map đến client
		
		// Ví dụ: xử lý để tạo ra bản đồ lưu trong map[][]
			// lấy vị trí hiện tại của team mình
		JSONObject positionJSON = (JSONObject) data.get(teamSymbol);
		myPos = new Vector2(positionJSON.getInt("x"),positionJSON.getInt("y")); 
		
			// lấy vị trí hiện tại của địch
		if (teamSymbol=="X")
			positionJSON = (JSONObject) data.get("O");
		else 
			positionJSON = (JSONObject) data.get("X");
		enemyPos = new Vector2(positionJSON.getInt("x"),positionJSON.getInt("y")); 
		
			// lưu thông tin bản đồ
		int map_size;
		int[][] initMap;
		map_size = (int) data.get("ncol");
		JSONArray mapJSON = (JSONArray) data.get("map");
		initMap = new int[map_size][map_size];
		for (int i=0; i< mapJSON.length(); i++) {
			for (int j=0; j< mapJSON.getJSONArray(i).length(); j++) {
				initMap[i][j]= mapJSON.getJSONArray(i).getInt(j);
			}
		}
		mapObj = new Map(initMap,map_size);
		setEnemyTeam(mapObj, enemyPos.x, enemyPos.y);
		setMyTeam(mapObj, myPos.x, myPos.y);
		
		separated = false;
		// kết thúc xử lý
	}
	
	@Override
	public Vector2 myTurnHandle(Vector2 enemyMove){
		// Hàm để xử lý mỗi lượt đi. Trả về tọa độ mới mà mình đi.
		// * NOTE:	- Nếu tọa độ gửi đi là những ô không hợp lệ (tường, ô đã đi qua) => thua luôn
		// 			- Nếu tính toán quá thời gian => thua luôn
		// Mỗi lượt đi, server sẽ gửi tọa độ mới đi của team địch tới client
		
		// lưu tọa độ team địch vào map
		setEnemyTeam(mapObj, enemyMove.x, enemyMove.y);
		
		// viết code xử lý ở đây
		direction = findDirection(mapObj, myPos.x, myPos.y, enemyMove.x, enemyMove.y);
		switch (direction) {
		case UP:
			myPos.x--;
			break;
		case DOWN:
			myPos.x++;
			break;
		case LEFT:
			myPos.y--;
			break;
		case RIGHT:
			myPos.y++;
			break;
		default:
			myPos.x = myPos.y = 0;
			break;
		}
		
		// lưu vị trí mới của mình vào map
		setMyTeam(mapObj, myPos.x, myPos.y);
		
		return myPos;
	} 
	
	private void setMyTeam(Map map, int x, int y) {
		if (isTeamX) {
			map.setTeamX(x, y);
		}else {
			map.setTeamO(x, y);
		}
	}
	
	private void setEnemyTeam(Map map, int x, int y) {
		if (isTeamX) {
			map.setTeamO(x, y);
		}else {
			map.setTeamX(x, y);
		}
	}
	
	private Direction findDirection(Map map, int x, int y, int xe, int ye) {
		if ((!map.isSpace(x - 1, y)) && (!map.isSpace(x + 1, y)) && (!map.isSpace(x, y + 1))
				&& (!map.isSpace(x, y - 1))) {
			return Direction.NONE;
		}
		if (separated) { // đỡ phải check lại enemyInside(...)
			return fill(map, myPos);
		}
		if (!isSeparated(map, x, y, xe, ye)) {
			separated = true;
			return fill(map, myPos);
		}
		
		Direction t = minimax(map, x, y, xe, ye);
		if (t == Direction.NONE) {
			if (map.isSpace(x - 1, y)) {
				return Direction.UP;
			}
			if (map.isSpace(x + 1, y)) {
				return Direction.DOWN;
			}
			if (map.isSpace(x, y - 1)) {
				return Direction.LEFT;
			}
			if (map.isSpace(x, y + 1)) {
				return Direction.RIGHT;
			}
		}
		return t;
	}

	private int countEdgesAStep(Map map, ArrayList<Point> arp) {
		int count = 0;
		ArrayList<Point> temp = new ArrayList<Point>();
		while (!arp.isEmpty()) {
			Point p = (Point) arp.remove(0);
			int x = p.x;
			int y = p.y;
			if (map.isSpaceAndNotTemp(x + 1, y)) {
				count += map.amountSpacesAround(x + 1, y);
				temp.add(new Point(x + 1, y));
				map.setTemp(x + 1, y);
			}
			if (map.isSpaceAndNotTemp(x - 1, y)) {
				count += map.amountSpacesAround(x - 1, y);
				temp.add(new Point(x - 1, y));
				map.setTemp(x - 1, y);
			}
			if (map.isSpaceAndNotTemp(x, y + 1)) {
				count += map.amountSpacesAround(x, y + 1);
				temp.add(new Point(x, y + 1));
				map.setTemp(x, y + 1);
			}
			if (map.isSpaceAndNotTemp(x, y - 1)) {
				count += map.amountSpacesAround(x, y - 1);
				temp.add(new Point(x, y - 1));
				map.setTemp(x, y - 1);
			}
		}
		arp.addAll(temp);
		return count;
	}

	private int luonggiacanh(Map map, int x, int y, int xe, int ye, boolean myturn) {
		int mysum = 0;
		int hissum = 0;
		ArrayList<Point> me = new ArrayList<Point>();
		ArrayList<Point> him = new ArrayList<Point>();
		me.add(new Point(x, y));
		him.add(new Point(xe, ye));
		if (myturn) {
			mysum += countEdgesAStep(map, me);
		}
		while ((!me.isEmpty()) || (!him.isEmpty())) {
			hissum += countEdgesAStep(map, him);
			mysum += countEdgesAStep(map, me);
		}
		return mysum - hissum;
	}

	public Direction minimax(Map map, int x, int y, int xe, int ye) {
		int depth = DEPTH_MINIMAX;
		Direction direction = Direction.NONE;

		int value = MINIMUM;
		int alpha = MINIMUM;
		int beta = MAXIMUM;
		amountnode = 0;
		if (map.isSpace(x, y + 1)) {
			Map maptemp = new Map(map);
			setMyTeam(maptemp, x, y + 1);
			int temp = minValue(maptemp, x, y + 1, xe, ye, depth - 1, alpha, beta);
			if (temp > value) {
				value = temp;
				direction = Direction.RIGHT;
			}
		}
		if (map.isSpace(x, y - 1)) {
			Map maptemp = new Map(map);
			setMyTeam(maptemp, x, y - 1);
			int temp = minValue(maptemp, x, y - 1, xe, ye, depth - 1, alpha, beta);
			if (temp > value) {
				value = temp;
				direction = Direction.LEFT;
			}
		}
		if (map.isSpace(x + 1, y)) {
			Map maptemp = new Map(map);
			setMyTeam(maptemp, x + 1, y);
			int temp = minValue(maptemp, x + 1, y, xe, ye, depth - 1, alpha, beta);
			if (temp > value) {
				value = temp;
				direction = Direction.DOWN;
			}
		}
		if (map.isSpace(x - 1, y)) {
			Map maptemp = new Map(map);
			setMyTeam(maptemp, x - 1, y);
			int temp = minValue(maptemp, x - 1, y, xe, ye, depth - 1, alpha, beta);
			if (temp > value) {
				value = temp;
				direction = Direction.UP;
			}
		}
		//System.out.println("V12: " + value);

		return direction;
	}

	private int maxValue(Map map, int x, int y, int xe, int ye, int depth, int alpha, int beta) {
		amountnode += 1;
		int max = MINIMUM;
		if ((!separated) && (!isSeparated(map, xe, ye, x, y))) {
			int t = 31 * luonggiaOutside(new Map(map), x, y, xe, ye)
					+ 11 * luonggiacanh(new Map(map), x, y, xe, ye, true);
			if ((t > 1) || (t < -1)) {
				return t * 5;
			}
			return t;
		}
		if (depth > 0) {
			if (map.isSpace(x + 1, y)) {
				Map maptemp = new Map(map);
				setMyTeam(maptemp, x + 1, y);
				int temp = minValue(maptemp, x + 1, y, xe, ye, depth - 1, alpha, beta);
				if (temp > max) {
					max = temp;
				}
				if (alphabeta) {
					if (max >= beta) {
						return max;
					}
					if (alpha < max) {
						alpha = max;
					}
				}
			}
			if (map.isSpace(x - 1, y)) {
				Map maptemp = new Map(map);
				setMyTeam(maptemp, x - 1, y);
				int temp = minValue(maptemp, x - 1, y, xe, ye, depth - 1, alpha, beta);
				if (temp > max) {
					max = temp;
				}
				if (alphabeta) {
					if (max >= beta) {
						return max;
					}
					if (alpha < max) {
						alpha = max;
					}
				}
			}
			if (map.isSpace(x, y + 1)) {
				Map maptemp = new Map(map);
				setMyTeam(maptemp, x, y + 1);
				int temp = minValue(maptemp, x, y + 1, xe, ye, depth - 1, alpha, beta);
				if (temp > max) {
					max = temp;
				}
				if (alphabeta) {
					if (max >= beta) {
						return max;
					}
					if (alpha < max) {
						alpha = max;
					}
				}
			}
			if (map.isSpace(x, y - 1)) {
				Map maptemp = new Map(map);
				setMyTeam(maptemp, x, y - 1);
				int temp = minValue(maptemp, x, y - 1, xe, ye, depth - 1, alpha, beta);
				if (temp > max) {
					max = temp;
				}
				if (alphabeta) {
					if (max >= beta) {
						return max;
					}
					if (alpha < max) {
						alpha = max;
					}
				}
			}
		} else {
			max = 31 * luonggia(new Map(map), x, y, xe, ye, true)
					+ 11 * luonggiacanh(new Map(map), x, y, xe, ye, true);
		}
		if (max == -80000) {
			max = -40000 - depth;
		}
		return max;
	}

	private int minValue(Map map, int x, int y, int xe, int ye, int depth, int alpha, int beta) {
		amountnode += 1;
		int min = MAXIMUM;
		if ((!separated) && (!isSeparated(map, xe, ye, x, y))) {
			int t = 31 * luonggiaOutside(new Map(map), x, y, xe, ye)
					+ 11 * luonggiacanh(new Map(map), x, y, xe, ye, false);
			if ((t > 1) || (t < -1)) {
				return t * 5;
			}
			return t;
		}
		if (map.isSpace(xe + 1, ye)) {
			Map maptemp = new Map(map);
			setEnemyTeam(maptemp, xe + 1, ye);
			int temp = maxValue(maptemp, x, y, xe + 1, ye, depth - 1, alpha, beta);
			if (temp < min) {
				min = temp;
			}
			if (alphabeta) {
				if (min <= alpha) {
					return min;
				}
				beta = beta < min ? beta : min;
			}
		}
		if (map.isSpace(xe - 1, ye)) {
			Map maptemp = new Map(map);
			setEnemyTeam(maptemp, xe - 1, ye);
			int temp = maxValue(maptemp, x, y, xe - 1, ye, depth - 1, alpha, beta);
			if (temp < min) {
				min = temp;
			}
			if (alphabeta) {
				if (min <= alpha) {
					return min;
				}
				beta = beta < min ? beta : min;
			}
		}
		if (map.isSpace(xe, ye + 1)) {
			Map maptemp = new Map(map);
			setEnemyTeam(maptemp, xe, ye + 1);
			int temp = maxValue(maptemp, x, y, xe, ye + 1, depth - 1, alpha, beta);
			if (temp < min) {
				min = temp;
			}
			if (alphabeta) {
				if (min <= alpha) {
					return min;
				}
				beta = beta < min ? beta : min;
			}
		}
		if (map.isSpace(xe, ye - 1)) {
			Map maptemp = new Map(map);
			setEnemyTeam(maptemp, xe, ye - 1);
			int temp = maxValue(maptemp, x, y, xe, ye - 1, depth - 1, alpha, beta);
			if (temp < min) {
				min = temp;
			}
			if (alphabeta) {
				if (min <= alpha) {
					return min;
				}
				beta = beta < min ? beta : min;
			}
		}
		if (min == 80000) {
			min = 40000 + depth;
		}
		return min;
	}

	private int luonggiaOutside(Map m, int x, int y, int xe, int ye) {
		int mysum = 0;
		int hissum = 0;
		int black = 0;
		int white = 0;
		ArrayList<Point> arp = new ArrayList<Point>();
		arp.add(new Point(x, y));
		boolean blackturn = true;
		while (!arp.isEmpty()) {
			if (blackturn) {
				black += redGo(arp, m);
				blackturn = false;
			} else {
				white += redGo(arp, m);
				blackturn = true;
			}
		}
		mysum = white + black;
		if (white > black) {
			mysum -= white - black;
		} else if (white < black - 1) {
			mysum -= black - 1 - white;
		}
		black = white = 0;
		arp.add(new Point(xe, ye));
		blackturn = true;
		while (!arp.isEmpty()) {
			if (blackturn) {
				black += redGo(arp, m);
				blackturn = false;
			} else {
				white += redGo(arp, m);
				blackturn = true;
			}
		}
		hissum = white + black;
		if (hissum <= 0) {
			if (white > black) {
				hissum -= white - black;
			} else if (white < black - 1) {
				hissum -= black - 1 - white;
			}
		}
		return mysum - hissum;
	}

	public int luonggia(Map map, int x, int y, int xe, int ye, boolean ismyturn) {
		ArrayList<Point> red = new ArrayList<Point>();
		ArrayList<Point> green = new ArrayList<Point>();
		red.add(new Point(x, y));
		green.add(new Point(xe, ye));
		int sumred = 0;
		int sumgreen = 0;
		if (!separated) {
			if (ismyturn) {
				while ((!red.isEmpty()) || (!green.isEmpty())) {
					sumred += redGo(red, map);
					sumgreen += greenGo(green, map);
				}
			} else {
				while ((!red.isEmpty()) || (!green.isEmpty())) {
					sumgreen += greenGo(green, map);
					sumred += redGo(red, map);
				}
			}
		} else {
			while (!red.isEmpty()) {
				sumred += redGo(red, map);
			}
		}
		return sumred - sumgreen;
	}

	private int redGo(ArrayList<Point> red, Map map) {
		ArrayList<Point> redtemp = new ArrayList<Point>();

		int sumred = 0;
		while (!red.isEmpty()) {
			Point point = (Point) red.get(0);
			int x = point.x;
			int y = point.y;
			if (map.isSpace(x + 1, y)) {
				sumred++;
				setMyTeam(map, x + 1, y);
				redtemp.add(new Point(x + 1, y));
			}
			if (map.isSpace(x - 1, y)) {
				sumred++;
				setMyTeam(map, x - 1, y);
				redtemp.add(new Point(x - 1, y));
			}
			if (map.isSpace(x, y + 1)) {
				sumred++;
				setMyTeam(map, x, y + 1);
				redtemp.add(new Point(x, y + 1));
			}
			if (map.isSpace(x, y - 1)) {
				sumred++;
				setMyTeam(map, x, y - 1);
				redtemp.add(new Point(x, y - 1));
			}
			red.remove(0);
		}
		for (int i = 0; i < redtemp.size(); i++) {
			red.add((Point) redtemp.get(i));
		}
		return sumred;
	}

	private int greenGo(ArrayList<Point> green, Map map) {
		ArrayList<Point> greentemp = new ArrayList<Point>();

		int sumgreen = 0;
		while (!green.isEmpty()) {
			Point point = (Point) green.get(0);
			int x = point.x;
			int y = point.y;
			if (map.isSpace(x + 1, y)) {
				sumgreen++;
				setEnemyTeam(map, x + 1, y);
				greentemp.add(new Point(x + 1, y));
			}
			if (map.isSpace(x - 1, y)) {
				sumgreen++;
				setEnemyTeam(map, x - 1, y);
				greentemp.add(new Point(x - 1, y));
			}
			if (map.isSpace(x, y + 1)) {
				sumgreen++;
				setEnemyTeam(map, x, y + 1);
				greentemp.add(new Point(x, y + 1));
			}
			if (map.isSpace(x, y - 1)) {
				sumgreen++;
				setEnemyTeam(map, x, y - 1);
				greentemp.add(new Point(x, y - 1));
			}
			green.remove(0);
		}
		for (int i = 0; i < greentemp.size(); i++) {
			green.add((Point) greentemp.get(i));
		}
		return sumgreen;
	}

	private boolean isSeparated(Map m, int xg, int yg, int xr, int yr) {
		Map map = new Map(m);
		Queue<Point> queue = new LinkedList<Point>();
		queue.add(new Point(xr, yr));
		while (!queue.isEmpty()) {
			Point element = queue.remove();
			int x = element.x;
			int y = element.y;
			if (map.isSpace(x + 1, y)) {
				map.setMap(x + 1, y);
				queue.add(new Point(x + 1, y));
			}
			if (map.isSpace(x - 1, y)) {
				map.setMap(x - 1, y);
				queue.add(new Point(x - 1, y));
			}
			if (map.isSpace(x, y - 1)) {
				map.setMap(x, y - 1);
				queue.add(new Point(x, y - 1));
			}
			if (map.isSpace(x, y + 1)) {
				map.setMap(x, y + 1);
				queue.add(new Point(x, y + 1));
			}
		}
		if ((map.isReachable(xg + 1, yg)) || (map.isReachable(xg - 1, yg)) || (map.isReachable(xg, yg + 1))
				|| (map.isReachable(xg, yg - 1))) {
			return true;
		}
		return false;
	}

	private Direction fill(Map map, Vector2 pos) {
		int maxSize = Integer.MIN_VALUE;
		int x = pos.x,
			y = pos.y;
		int tmp;
		Direction dir = Direction.NONE;
		Vector2 tmpPos = new Vector2();
		tmpPos.x = x; tmpPos.y = y;
		if (isArticulationPoint(map, pos)) {
			if (map.isSpace(x-1, y)) { // kiểm tra ô phía trên
				tmpPos.x = x-1;
				tmp = countFloodFill(map, tmpPos);
				if (tmp > maxSize) {
					maxSize = tmp;
					dir = Direction.UP;
				}
			}
			if (map.isSpace(x+1, y)) { // kiểm tra ô phía dưới
				tmpPos.x = x+1;
				tmp = countFloodFill(map, tmpPos);
				if (tmp > maxSize) {
					maxSize = tmp;
					dir = Direction.DOWN;
				}
			}
			tmpPos.x = x; tmpPos.y = y;
			if (map.isSpace(x,y-1)) { // kiểm tra ô bên trái
				tmpPos.y = y-1;
				tmp = countFloodFill(map, tmpPos);
				if (tmp > maxSize) {
					maxSize = tmp;
					dir = Direction.LEFT;
				}
			}
			if (map.isSpace(x,y+1)) { // kiểm tra ô bên phải
				tmpPos.y = y+1;
				tmp = countFloodFill(map, tmpPos);
				if (tmp > maxSize) {
					maxSize = tmp;
					dir = Direction.RIGHT;
				}
			}
		}else {
			tmpPos.x = x; tmpPos.y = y;
			if (map.isSpace(x-1, y)) { // kiểm tra ô phía trên
				tmpPos.x = x-1;
				tmp = filling_evaluate_with_depth(map, tmpPos, 1);
				if (tmp > maxSize) {
					maxSize = tmp;
					dir = Direction.UP;
				}
			}
			if (map.isSpace(x+1, y)) { // kiểm tra ô phía dưới
				tmpPos.x = x+1;
				tmp = filling_evaluate_with_depth(map, tmpPos, 1);
				if (tmp > maxSize) {
					maxSize = tmp;
					dir = Direction.DOWN;
				}
			}
			tmpPos.x = x; tmpPos.y = y;
			if (map.isSpace(x,y-1)) { // kiểm tra ô bên trái
				tmpPos.y = y-1;
				tmp = filling_evaluate_with_depth(map, tmpPos, 1);
				if (tmp > maxSize) {
					maxSize = tmp;
					dir = Direction.LEFT;
				}
			}
			if (map.isSpace(x,y+1)) { // kiểm tra ô bên phải
				tmpPos.y = y+1;
				tmp = filling_evaluate_with_depth(map, tmpPos, 1);
				if (tmp > maxSize) {
					maxSize = tmp;
					dir = Direction.RIGHT;
				}
			}
		}
		return dir;
	}

	private int filling_evaluate_with_depth(Map map, Vector2 pos, int depth) {
		
		int x = pos.x,
			y = pos.y;
		
		int countAvailMove = map.countAvailableMove(x,y);
		
		if (countAvailMove == 0)
			return -10000;
		
		if (depth == FILLING_EVALUATE_DEPTH) {
			int point = countFloodFill(map, pos) - 2*countAvailMove - 4*countArticulationPoints(map, pos);
			if (isArticulationPoint(map, pos)) 
				point -= 500;
			return point;
		}
		
		int max = Integer.MIN_VALUE;
		int value;
		Vector2 tmpPos = new Vector2();
		tmpPos.x = x; tmpPos.y = y;
		if (map.isSpace(x + 1, y)) {
			tmpPos.x = x+1;
			map.setMap(x + 1, y);			
			value = filling_evaluate_with_depth(map, tmpPos, depth+1);
			map.resetMap(x + 1, y);
			if (value > max) max = value;
		}
		if (map.isSpace(x - 1, y)) {
			tmpPos.x = x-1;
			map.setMap(x - 1, y);			
			value = filling_evaluate_with_depth(map, tmpPos, depth+1);
			map.resetMap(x - 1, y);
			if (value > max) max = value;
		}
		tmpPos.x = x; tmpPos.y = y;
		if (map.isSpace(x, y - 1)) {
			tmpPos.y = y-1;
			map.setMap(x, y - 1);			
			value = filling_evaluate_with_depth(map, tmpPos, depth+1);
			map.resetMap(x, y - 1);
			if (value > max) max = value;
		}
		if (map.isSpace(x, y + 1)) {
			tmpPos.y = y+1;
			map.setMap(x, y + 1);			
			value = filling_evaluate_with_depth(map, tmpPos, depth+1);
			map.resetMap(x, y + 1);
			if (value > max) max = value;
		}
		return filling_evaluate(map, pos) + max / (depth+1);
	}

	private int filling_evaluate(Map map, Vector2 pos) {
		int x = pos.x,
			y = pos.y;
			
		int countAvailMove = map.countAvailableMove(x,y);
			
		if (countAvailMove == 0)
			return -10000;
		
		map.drawMap(myPos.x, myPos.y, enemyPos.x, enemyPos.y, isTeamX);
		System.out.print(countArticulationPoints(map, pos));
			
		int point = countFloodFill(map, pos) - 2*countAvailMove - 4*countArticulationPoints(map, pos);
		if (isArticulationPoint(map, pos)) 
			point -= 500;
		return point;
	}

	private int countArticulationPoints(Map map, Vector2 pos) {
		int[][] num = new int[map.mapSize][map.mapSize];
		int[][] low = new int[map.mapSize][map.mapSize];
		boolean[][] visited = new boolean[map.mapSize][map.mapSize];
		return DFSCountAPs(map, visited, low, num, pos, 1);
	}
	
	private int DFSCountAPs(Map map, boolean[][] visited, int[][] low, int[][] num, Vector2 pos, int depth) {
		int APCount = 0;
		int childCount = 0;
		int x = pos.x,
			y = pos.y;
		visited[x][y] = true;
		low[x][y] = num[x][y] = depth;
		
		Vector2 tmpPos = new Vector2();
		tmpPos.x = x; tmpPos.y = y;
		if (map.isSpace(x + 1, y)) {
			tmpPos.x = x+1;
			if (!visited[tmpPos.x][tmpPos.y]) {
				childCount++;
				APCount += DFSCountAPs(map, visited, low, num, tmpPos, depth+1);
				if (num[tmpPos.x][tmpPos.y] < num[x][y])
					low[x][y] = ((low[x][y] > num[tmpPos.x][tmpPos.y]) ? num[tmpPos.x][tmpPos.y] : low[x][y]);
				else
					low[x][y] = ((low[x][y] > low[tmpPos.x][tmpPos.y]) ? low[tmpPos.x][tmpPos.y] : low[x][y]);
			}
		}
		if (map.isSpace(x - 1, y)) {
			tmpPos.x = x-1;
			if (!visited[tmpPos.x][tmpPos.y]) {
				childCount++;
				APCount += DFSCountAPs(map, visited, low, num, tmpPos, depth+1);
				if (num[tmpPos.x][tmpPos.y] < num[x][y])
					low[x][y] = ((low[x][y] > num[tmpPos.x][tmpPos.y]) ? num[tmpPos.x][tmpPos.y] : low[x][y]);
				else
					low[x][y] = ((low[x][y] > low[tmpPos.x][tmpPos.y]) ? low[tmpPos.x][tmpPos.y] : low[x][y]);
			}
		}
		tmpPos.x = x; tmpPos.y = y;
		if (map.isSpace(x, y - 1)) {
			tmpPos.y = y-1;
			if (!visited[tmpPos.x][tmpPos.y]) {
				childCount++;
				APCount += DFSCountAPs(map, visited, low, num, tmpPos, depth+1);
				if (num[tmpPos.x][tmpPos.y] < num[x][y])
					low[x][y] = ((low[x][y] > num[tmpPos.x][tmpPos.y]) ? num[tmpPos.x][tmpPos.y] : low[x][y]);
				else
					low[x][y] = ((low[x][y] > low[tmpPos.x][tmpPos.y]) ? low[tmpPos.x][tmpPos.y] : low[x][y]);
			}
		}
		if (map.isSpace(x, y + 1)) {
			tmpPos.y = y+1;
			if (!visited[tmpPos.x][tmpPos.y]) {
				childCount++;
				APCount += DFSCountAPs(map, visited, low, num, tmpPos, depth+1);
				if (num[tmpPos.x][tmpPos.y] < num[x][y])
					low[x][y] = ((low[x][y] > num[tmpPos.x][tmpPos.y]) ? num[tmpPos.x][tmpPos.y] : low[x][y]);
				else
					low[x][y] = ((low[x][y] > low[tmpPos.x][tmpPos.y]) ? low[tmpPos.x][tmpPos.y] : low[x][y]);
			}
		}
		
		if (depth == 1) {
			if (childCount > 1) APCount++;
		}else {
			tmpPos.x = x; tmpPos.y = y;
			if (map.isSpace(x + 1, y)) {
				tmpPos.x = x+1;
				if (low[tmpPos.x][tmpPos.y] > num[x][y]) APCount++;
			}
			if (map.isSpace(x - 1, y)) {
				tmpPos.x = x-1;
				if (low[tmpPos.x][tmpPos.y] > num[x][y]) APCount++;
			}
			tmpPos.x = x; tmpPos.y = y;
			if (map.isSpace(x, y - 1)) {
				tmpPos.y = y-1;
				if (low[tmpPos.x][tmpPos.y] > num[x][y]) APCount++;
			}
			if (map.isSpace(x, y + 1)) {
				tmpPos.y = y+1;
				if (low[tmpPos.x][tmpPos.y] > num[x][y]) APCount++;
			}
		}
		return APCount;
	}

	private int countFloodFill(Map map, Vector2 pos) {
		Map tmpMap = new Map(map);
		int count = 0;
		Queue<Vector2> queue = new LinkedList<Vector2>();
		queue.add(pos);
		while (!queue.isEmpty()) {
			Vector2 tmpPos = queue.remove();
			count++;
			int x = tmpPos.x;
			int y = tmpPos.y;
			if (tmpMap.isSpace(x + 1, y)) {
				tmpMap.setMap(x + 1, y);
				queue.add(new Vector2(x + 1, y));
			}
			if (tmpMap.isSpace(x - 1, y)) {
				tmpMap.setMap(x - 1, y);
				queue.add(new Vector2(x - 1, y));
			}
			if (tmpMap.isSpace(x, y - 1)) {
				tmpMap.setMap(x, y - 1);
				queue.add(new Vector2(x, y - 1));
			}
			if (tmpMap.isSpace(x, y + 1)) {
				tmpMap.setMap(x, y + 1);
				queue.add(new Vector2(x, y + 1));
			}
		}
		return count;
	}

	private boolean isArticulationPoint(Map map, Vector2 pos) {
		int x = pos.x,
			y = pos.y;
		Vector2 tmpPos = new Vector2();
		tmpPos.x = x; tmpPos.y = y;
		if (map.isSpace(x-1, y)) { // kiểm tra ô phía trên
			tmpPos.x = x-1;
		}
		else if (map.isSpace(x+1, y)) { // kiểm tra ô phía dưới
			tmpPos.x = x+1;
		}
		else if (map.isSpace(x,y-1)) { // kiểm tra ô bên trái
			tmpPos.y = y-1;
		}
		else if (map.isSpace(x,y+1)) { // kiểm tra ô bên phải
			tmpPos.y = y+1;
		}
		else {
			return false;
		}
		int f1 = countFloodFill(map, pos);
		int f2 = countFloodFill(map, tmpPos);
		return (f1-1 != f2);
		//return (countFloodFill(map, pos) - 1 != countFloodFill(map, tmpPos));
	}
}
