package playerControl;

import java.util.ArrayList;
import java.util.Scanner;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import main.AbstractClientPlayer;

public class HumanPlayer extends AbstractClientPlayer{
	private int map_size;
	private int[][] map;
	Vector2 myPos, enemyPos;
	private boolean upAvailable, downAvailable, leftAvailable, rightAvailable;
	
	public HumanPlayer(String team) 
			throws Exception {
		super(team);
	}
	
	@Override
	public JSONObject configTeamInfo() throws JSONException {
		ArrayList<JSONObject> members = new ArrayList<JSONObject>();
		//Thong tin cac thanh vien trong nhom
		members.add( new JSONObject("{name: Someone playing, mssv: 34567749}"));
		
		JSONObject teamInfo = new JSONObject();
		teamInfo.put("team", teamSymbol);
		teamInfo.put("name", "Tôi là ai?");
		teamInfo.put("members", members);
		
		return teamInfo;
	}
	
	@Override
	public void newMapHandle(JSONObject data) throws JSONException{
		JSONObject positionJSON = (JSONObject) data.get(teamSymbol);
		myPos = new Vector2(positionJSON.getInt("x"),positionJSON.getInt("y"));
		if (teamSymbol=="X")
			positionJSON = (JSONObject) data.get("O");
		else 
			positionJSON = (JSONObject) data.get("X");
		enemyPos = new Vector2(positionJSON.getInt("x"),positionJSON.getInt("y"));
		
		map_size = (int) data.get("ncol");
		JSONArray mapJSON = (JSONArray) data.get("map");
		// Gia tri 0 la o chua ai di qua, 1 team X da di qua, 2 team O da di qua, 3 la vat can
		map = new int[map_size][map_size];
		for (int i=0; i< mapJSON.length(); i++) {
			for (int j=0; j< mapJSON.getJSONArray(i).length(); j++) {
				map[i][j] = mapJSON.getJSONArray(i).getInt(j);
			}
		}
	}
	
	@Override
	public Vector2 myTurnHandle(Vector2 enemyMove){
//		for (int i=0; i<map_size;i++) {
//			for (int j=0;j<map_size;j++) {
//				char c;
//				switch (map[i][j]) {
//				case 0:
//					c = ' ';
//					break;
//				case 1:
//					c = 'x';
//					break;
//				case 2:
//					c = 'o';
//					break;
//				case 3:
//					c = 'H';
//					break;
//				default:
//					c = ' ';
//					break;
//				}
//				System.out.print(c);
//			}
//			System.out.print("\n");
//		}
		map[enemyMove.x][enemyMove.y] = ((teamSymbol=="X")?2:1);
		
		upAvailable = downAvailable = leftAvailable = rightAvailable = true;
		if (myPos.x == 0 || map[myPos.x-1][myPos.y] != 0) upAvailable = false;
		if (myPos.x == map_size-1 || map[myPos.x+1][myPos.y] != 0) downAvailable = false;
		if (myPos.y == 0 || map[myPos.x][myPos.y-1] != 0) leftAvailable = false;
		if (myPos.y == map_size-1 || map[myPos.x][myPos.y+1] != 0) rightAvailable = false;
		
		Scanner in = new Scanner(System.in); 	// vì in.close() sẽ xóa mất object System.in => không ipnut được nữa => không dùng in.close()
		System.out.print("Available moves: ");
		if (upAvailable) System.out.print("up (w) ");
		if (downAvailable) System.out.print("| down (s) ");
		if (leftAvailable) System.out.print("| left (a) ");
		if (rightAvailable) System.out.print("| right (d)");
		char c;
		boolean movable = false;
		do {
			System.out.print("Choose your move: ");
			c = in.next().charAt(0);
			if (c=='w' || c=='W') {
				if (upAvailable) {
					myPos.x--;
					movable = true;
				}
			}else if (c=='s' || c=='S') {
				if (downAvailable) {
					myPos.x++;
					movable = true;
				}
			}else if (c=='a' || c=='A') {
				if (leftAvailable) {
					myPos.y--;
					movable = true;
				}
			}else if (c=='d' || c=='D') {
				if (rightAvailable) {
					myPos.y++;
					movable = true;
				}
			}
		}while(!movable);
		//in.close();
				
		map[myPos.x][myPos.y] = ((teamSymbol=="X")?1:2);
		return myPos;
	} 
}
