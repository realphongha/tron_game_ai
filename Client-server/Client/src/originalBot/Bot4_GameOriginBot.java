package originalBot;

import java.util.ArrayList;
import java.util.LinkedList;
import java.util.Queue;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import main.AbstractClientPlayer;

public class Bot4_GameOriginBot extends AbstractClientPlayer{
	private static final int DEPTH_MINIMAX = 7;
	private static final int DEPTH_PATH = 12;
	private static final int MAXIMUM = 80000;
	private static final int MINIMUM = -80000;
	int[] priceofspace = new int[5];
	int amountnode;
	boolean crack = false;
	private boolean alphabeta = true;
	private static final int VAT = 5;
	private static final int VS = 1;
	private static final int KN = 31;
	private static final int KE = 11;
		
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
		
	public Bot4_GameOriginBot(String team) 
			throws Exception {
		super(team);
		
		// Thêm các khởi tạo cho lớp nếu cần
		// ...
		System.out.println("My team is: " + teamSymbol + "\n"); // debug
	}
	
	@Override
	public JSONObject configTeamInfo() throws JSONException {
		// Hàm để thiết lập thông tin về đội chơi
		ArrayList<JSONObject> members = new ArrayList<JSONObject>();
		JSONObject teamInfo = new JSONObject();
		teamInfo.put("team", teamSymbol);
		
		//Thêm thông tin thành viên trong nhóm theo mẫu dưới
		members.add( new JSONObject("{name: Original Bot, mssv: 10000000}"));
			
		// Nhập tên team ở đây
		teamInfo.put("name", "Bot của thầy");
		
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
		crack = false;
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
		enemyPos = enemyMove;
		
		//mapObj.drawMap(myPos.x, myPos.y, enemyPos.x, enemyPos.y, isTeamX); //debug
		// viết code xử lý ở đây
		direction = findDirection(mapObj, myPos.x, myPos.y, enemyPos.x, enemyPos.y);
		switch (direction) {
		case UP:
			//System.out.println("Result: UP\n"); // debug
			myPos.x--;
			break;
		case DOWN:
			//System.out.println("Result: DOWN\n"); // debug
			myPos.x++;
			break;
		case LEFT:
			//System.out.println("Result: LEFT\n"); // debug
			myPos.y--;
			break;
		case RIGHT:
			//System.out.println("Result: RIGHT\n"); // debug
			myPos.y++;
			break;
		default:
			//System.out.println("Result: NONE\n"); // debug
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
			//System.out.println("There s no space around\n"); // debug
			return Direction.NONE;
		}
		if (crack) { // đỡ phải check lại enemyInside(...)
			//System.out.println("Cracked phase\n"); // debug
			Direction tmp = findPathV1(map, x, y);
			//mapObj.drawMap(myPos.x, myPos.y, enemyPos.x, enemyPos.y, isTeamX);
			return tmp;
		}
		if (!enemyInside(new Map(map), xe, ye, x, y)) {
			crack = true;
			//System.out.println("Cracked phase\n"); // debug
			Direction tmp = findPathV1(map, x, y);
			//map.drawMap(myPos.x, myPos.y, enemyPos.x, enemyPos.y, isTeamX);
			return tmp;
		}
		//System.out.println("Divining phase\n"); // debug
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

	private Direction findPathV1(Map map, int x, int y) {
		int max = Integer.MIN_VALUE;
		Direction dir = Direction.NONE;
		if (map.isSpace(x - 1, y)) {
			Map m = new Map(map);
			setMyTeam(m, x - 1, y);
			int temp = searchPath(m, x - 1, y, DEPTH_PATH);
			if (temp > max) {
				max = temp;
				dir = Direction.UP;
			}
		}
		if (map.isSpace(x + 1, y)) {
			Map m = new Map(map);
			setMyTeam(m, x + 1, y);
			int temp = searchPath(m, x + 1, y, DEPTH_PATH);
			if (temp > max) {
				max = temp;
				dir = Direction.DOWN;
			}
		}
		if (map.isSpace(x, y - 1)) {
			Map m = new Map(map);
			setMyTeam(m, x, y - 1);
			int temp = searchPath(m, x, y - 1, DEPTH_PATH);
			if (temp > max) {
				max = temp;
				dir = Direction.LEFT;
			}
		}
		if (map.isSpace(x, y + 1)) {
			Map m = new Map(map);
			setMyTeam(m, x, y + 1);
			int temp = searchPath(m, x, y + 1, DEPTH_PATH);
			if (temp > max) {
				max = temp;
				dir = Direction.RIGHT;
			}
		}
		return dir;
	}

	private int searchPath(Map map, int x, int y, int depth) {
		int t = Integer.MIN_VALUE;
		int temp;
		//System.out.println("Run search path function at depth "+depth+"\n"); // debug
		
		if (depth <= 0) {
			//map.drawMap(myPos.x, myPos.y, enemyPos.x, enemyPos.y, isTeamX);
			int tmp = numberofegdes(map, x, y);
			//System.out.println("Number of edge = " + tmp + "\n"); // debug
			return tmp;
		}
		if (map.isSpace(x - 1, y)) {
			Map m = new Map(map);
			setMyTeam(m, x - 1, y);
			temp = searchPath(m, x - 1, y, depth - 1);
			t = temp > t ? temp : t;
		}
		if (map.isSpace(x + 1, y)) {
			Map m = new Map(map);
			setMyTeam(m, x + 1, y);
			temp = searchPath(m, x + 1, y, depth - 1);
			t = t > temp ? t : temp;
		}
		if (map.isSpace(x, y - 1)) {
			Map m = new Map(map);
			setMyTeam(m, x, y - 1);
			temp = searchPath(m, x, y - 1, depth - 1);
			t = t > temp ? t : temp;
		}
		if (map.isSpace(x, y + 1)) {
			Map m = new Map(map);
			setMyTeam(m, x, y + 1);
			temp = searchPath(m, x, y + 1, depth - 1);
			t = t > temp ? t : temp;
		}
		if (t == Integer.MIN_VALUE) {
			return -depth;
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

	private int numberofegdes(Map map, int x, int y) {
		int max = 0;
		ArrayList<Point> arp = new ArrayList<Point>();
		arp.add(new Point(x, y));

		int xs = x;
		int ys = y;
		if (map.isSpaceAndNotTemp(xs + 1, ys)) {
			int t = 0;
			t += map.amountSpacesAround(xs + 1, ys);
			map.setTemp(xs + 1, ys);
			arp.add(new Point(xs + 1, ys));
			while (!arp.isEmpty()) {
				Point p = (Point) arp.remove(0);
				xs = p.x;
				ys = p.y;
				if (map.isSpaceAndNotTemp(xs + 1, ys)) {
					t += map.amountSpacesAround(xs + 1, ys);
					map.setTemp(xs + 1, ys);
					arp.add(new Point(xs + 1, ys));
				}
				if (map.isSpaceAndNotTemp(xs - 1, ys)) {
					t += map.amountSpacesAround(xs - 1, ys);
					map.setTemp(xs - 1, ys);
					arp.add(new Point(xs - 1, ys));
				}
				if (map.isSpaceAndNotTemp(xs, ys + 1)) {
					t += map.amountSpacesAround(xs, ys + 1);
					map.setTemp(xs, ys + 1);
					arp.add(new Point(xs, ys + 1));
				}
				if (map.isSpaceAndNotTemp(xs, ys - 1)) {
					t += map.amountSpacesAround(xs, ys - 1);
					map.setTemp(xs, ys - 1);
					arp.add(new Point(xs, ys - 1));
				}
			}
			if (t > max) {
				max = t;
			}
		}
		if (map.isSpaceAndNotTemp(xs - 1, ys)) {
			int t = 0;
			t += map.amountSpacesAround(xs - 1, ys);
			map.setTemp(xs - 1, ys);
			arp.add(new Point(xs - 1, ys));
			while (!arp.isEmpty()) {
				Point p = (Point) arp.remove(0);
				xs = p.x;
				ys = p.y;
				if (map.isSpaceAndNotTemp(xs + 1, ys)) {
					t += map.amountSpacesAround(xs + 1, ys);
					map.setTemp(xs + 1, ys);
					arp.add(new Point(xs + 1, ys));
				}
				if (map.isSpaceAndNotTemp(xs - 1, ys)) {
					t += map.amountSpacesAround(xs - 1, ys);
					map.setTemp(xs - 1, ys);
					arp.add(new Point(xs - 1, ys));
				}
				if (map.isSpaceAndNotTemp(xs, ys + 1)) {
					t += map.amountSpacesAround(xs, ys + 1);
					map.setTemp(xs, ys + 1);
					arp.add(new Point(xs, ys + 1));
				}
				if (map.isSpaceAndNotTemp(xs, ys - 1)) {
					t += map.amountSpacesAround(xs, ys - 1);
					map.setTemp(xs, ys - 1);
					arp.add(new Point(xs, ys - 1));
				}
			}
			if (t > max) {
				max = t;
			}
		}
		if (map.isSpaceAndNotTemp(xs, ys + 1)) {
			int t = 0;
			t += map.amountSpacesAround(xs, ys + 1);
			map.setTemp(xs, ys + 1);
			arp.add(new Point(xs, ys + 1));
			while (!arp.isEmpty()) {
				Point p = (Point) arp.remove(0);
				xs = p.x;
				ys = p.y;
				if (map.isSpaceAndNotTemp(xs + 1, ys)) {
					t += map.amountSpacesAround(xs + 1, ys);
					map.setTemp(xs + 1, ys);
					arp.add(new Point(xs + 1, ys));
				}
				if (map.isSpaceAndNotTemp(xs - 1, ys)) {
					t += map.amountSpacesAround(xs - 1, ys);
					map.setTemp(xs - 1, ys);
					arp.add(new Point(xs - 1, ys));
				}
				if (map.isSpaceAndNotTemp(xs, ys + 1)) {
					t += map.amountSpacesAround(xs, ys + 1);
					map.setTemp(xs, ys + 1);
					arp.add(new Point(xs, ys + 1));
				}
				if (map.isSpaceAndNotTemp(xs, ys - 1)) {
					t += map.amountSpacesAround(xs, ys - 1);
					map.setTemp(xs, ys - 1);
					arp.add(new Point(xs, ys - 1));
				}
			}
			if (t > max) {
				max = t;
			}
		}
		if (map.isSpaceAndNotTemp(xs, ys - 1)) {
			int t = 0;
			t += map.amountSpacesAround(xs, ys - 1);
			map.setTemp(xs, ys - 1);
			arp.add(new Point(xs, ys - 1));
			while (!arp.isEmpty()) {
				Point p = (Point) arp.remove(0);
				xs = p.x;
				ys = p.y;
				if (map.isSpaceAndNotTemp(xs + 1, ys)) {
					t += map.amountSpacesAround(xs + 1, ys);
					map.setTemp(xs + 1, ys);
					arp.add(new Point(xs + 1, ys));
				}
				if (map.isSpaceAndNotTemp(xs - 1, ys)) {
					t += map.amountSpacesAround(xs - 1, ys);
					map.setTemp(xs - 1, ys);
					arp.add(new Point(xs - 1, ys));
				}
				if (map.isSpaceAndNotTemp(xs, ys + 1)) {
					t += map.amountSpacesAround(xs, ys + 1);
					map.setTemp(xs, ys + 1);
					arp.add(new Point(xs, ys + 1));
				}
				if (map.isSpaceAndNotTemp(xs, ys - 1)) {
					t += map.amountSpacesAround(xs, ys - 1);
					map.setTemp(xs, ys - 1);
					arp.add(new Point(xs, ys - 1));
				}
			}
			if (t > max) {
				max = t;
			}
		}
		return max;
	}

	public Direction minimax(Map map, int x, int y, int xe, int ye) {
		int depth = DEPTH_MINIMAX;
		Direction direction = Direction.NONE;

		int value = MINIMUM;
		int alpha = MINIMUM;
		int beta = MAXIMUM;
		amountnode = 0;
		//map.drawMap(x, y, xe, ye, isTeamX); // debug
		if (map.isSpace(x, y + 1)) {
			Map maptemp = new Map(map);
			setMyTeam(maptemp, x, y + 1);
			int temp = minValue(maptemp, x, y + 1, xe, ye, depth - 1, alpha, beta);
			//System.out.println("Evaluate right: "+temp); // debug
			if (temp > value) {
				value = temp;
				direction = Direction.RIGHT;
			}
		}
		if (map.isSpace(x, y - 1)) {
			Map maptemp = new Map(map);
			setMyTeam(maptemp, x, y - 1);
			int temp = minValue(maptemp, x, y - 1, xe, ye, depth - 1, alpha, beta);
			//System.out.println("Evaluate left: "+temp); // debug
			if (temp > value) {
				value = temp;
				direction = Direction.LEFT;
			}
		}
		if (map.isSpace(x + 1, y)) {
			Map maptemp = new Map(map);
			setMyTeam(maptemp, x + 1, y);
			int temp = minValue(maptemp, x + 1, y, xe, ye, depth - 1, alpha, beta);
			//System.out.println("Evaluate down: "+temp); // debug
			if (temp > value) {
				value = temp;
				direction = Direction.DOWN;
			}
		}
		if (map.isSpace(x - 1, y)) {
			Map maptemp = new Map(map);
			setMyTeam(maptemp, x - 1, y);
			int temp = minValue(maptemp, x - 1, y, xe, ye, depth - 1, alpha, beta);
			//System.out.println("Evaluate up: "+temp); // debug
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
		if ((!crack) && (!enemyInside(map, xe, ye, x, y))) {
			int t = KN * luonggiaOutside(new Map(map), x, y, xe, ye)
					+ KE * luonggiacanh(new Map(map), x, y, xe, ye, true);
			if ((t > VS) || (t < -VS)) {
				return t * VAT;
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
			max = KN * luonggia(new Map(map), x, y, xe, ye, true)
					+ KE * luonggiacanh(new Map(map), x, y, xe, ye, true);
		}
		if (max == MINIMUM) {
			max = MINIMUM/2 - depth;
		}
		return max;
	}

	private int minValue(Map map, int x, int y, int xe, int ye, int depth, int alpha, int beta) {
		amountnode += 1;
		int min = MAXIMUM;
		if ((!crack) && (!enemyInside(map, xe, ye, x, y))) {
			int t = KN * luonggiaOutside(new Map(map), x, y, xe, ye)
					+ KE * luonggiacanh(new Map(map), x, y, xe, ye, false);
			if ((t > VS) || (t < -VS)) {
				return t * VAT;
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
		if (min == MAXIMUM) {
			min = MAXIMUM/2 + depth;
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
		if (!crack) {
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

	private boolean enemyInside(Map m, int xg, int yg, int xr, int yr) {
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

}