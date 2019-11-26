package myBot;

import java.util.ArrayList;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import main.AbstractClientPlayer;

public class Bot3_Minimax_2_Areas extends AbstractClientPlayer{
	// teamSymbol : 'X' || 'O'
	// teamSymbol là thuộc tính của lớp abstract, được nhập vào ở giao diện console khi khởi động client
	
	private Vector2 myPos, enemyPos;
	private Map2D currentMap;
	
	public Bot3_Minimax_2_Areas(String team) 
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
		members.add( new JSONObject("{name: Black, mssv: 11111111}"));
		members.add( new JSONObject("{name: White, mssv: 00000000}"));
			
		// Nhập tên team ở đây
		teamInfo.put("name", "Alice on Wonderland");
		
		teamInfo.put("members", members);		
		return teamInfo;
	}
	
	@Override
	public void newMapHandle(JSONObject data) throws JSONException{
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
		map_size = (int) data.get("ncol");
		currentMap = new Map2D(map_size);
		
		JSONArray mapJSON = (JSONArray) data.get("map");
		int[][] initMap = currentMap.map;		
		for (int i=0; i < map_size; i++) {
			for (int j=0; j < map_size; j++) {
				switch ( mapJSON.getJSONArray(i).getInt(j) ) {
				case 0:
					initMap[i][j] = Map2D.SPACE;
					break;
				case 1: // vị trí bắt đầu của team X
					initMap[i][j] = (isTeamX ? Map2D.MY_TEAM : Map2D.ENEMY_TEAM);
					break;
				case 2: // vị trí bắt đầu của team O
					initMap[i][j] = (isTeamX ? Map2D.ENEMY_TEAM : Map2D.MY_TEAM);
					break;
				case 3:
					initMap[i][j] = Map2D.WALL;
					break;
				default:
					break;
				}	
			}
		}
		
		initMap[myPos.x][myPos.y] = Map2D.MY_TEAM;
		initMap[enemyPos.x][enemyPos.y] = Map2D.ENEMY_TEAM;
	}
	
	@Override
	public Vector2 myTurnHandle(Vector2 enemyMove){
		enemyPos = enemyMove;
		currentMap.map[enemyPos.x][enemyPos.y] = Map2D.ENEMY_TEAM;
		
		// có 2 giai đoạn (phase): 
		// conflict phase - giai đoạn tranh chấp lãnh thổ
		// separated phase - giai đoạn 2 bên đã tách nhau, chỉ cần tìm đường để đi hết phần của mình
		
		Direction resultDirection = Direction.NONE;
		if (inSeparatedPhase()) 
		{
			resultDirection = findDirectionToFillArea();
		}
		else 
		{
			resultDirection = findDirectionToWin();
		}
		
		switch (resultDirection) {
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
			break;
		}
		
		// lưu vị trí mới của mình vào map
		return myPos;
	} 
	
	private Direction findDirectionToWin() {
		// TODO Auto-generated method stub
		return null;
	}

	private Direction findDirectionToFillArea() {
		// TODO Auto-generated method stub
		return null;
	}

	private enum Direction {NONE, UP, DOWN, LEFT, RIGHT}
	
	private boolean separated = false;
	private boolean inSeparatedPhase(){
		if (separated) return true;
		
		// check
		// ...
		// .
		
		return false;
	}
	
	private Vector2 minimaxSearch(int depth) {
		Vector2 optMove = new Vector2();
		Vector2 tmpPos;
		float tmpEval, optEval = Float.NEGATIVE_INFINITY;
		int[][] tmpMap;
		
		
		return optMove;
	}
	
	private float minValue() {
		return 0;
	}
	
	private float maxValue() {
		return 0;
	}
	
	private boolean chooseArea() {
		return true;
	}
	
	private class MinimaxNode{
		int accessA, potentialA, accessB, potentialB;
		int[][] map;
	}
}
