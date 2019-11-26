package simpleTestingBot;
import java.util.ArrayList;
import java.util.Random;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import main.AbstractClientPlayer;

public class Bot1_RandomWalk extends AbstractClientPlayer{
	// teamSymbol : 'X' || 'O'
	private int map_size;
	private int[][] map;
	Vector2 myPos, enemyPos;
	Random rand;
	
	public Bot1_RandomWalk(String team) 
			throws Exception {
		super(team);
		rand = new Random(); 
	}
	
	@Override
	public JSONObject configTeamInfo() throws JSONException {
		ArrayList<JSONObject> members = new ArrayList<JSONObject>();
		//Thong tin cac thanh vien trong nhom
		members.add( new JSONObject("{name: Stupid Bot, mssv: 10010110}"));
		
		JSONObject teamInfo = new JSONObject();
		teamInfo.put("team", teamSymbol);
		teamInfo.put("name", "Team bot vô địch");
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
		map[enemyMove.x][enemyMove.y] = ((teamSymbol=="X")?2:1);
		
		int maxAvailDirection = 4;
		boolean[] moveAvailable = new boolean[4];
		moveAvailable[0] = moveAvailable[1] = moveAvailable[2] = moveAvailable[3] = true;
		if (myPos.x == 0 || map[myPos.x-1][myPos.y] != 0) {
			moveAvailable[0] = false;
			maxAvailDirection--;
		}
		if (myPos.x == map_size-1 || map[myPos.x+1][myPos.y] != 0) {
			moveAvailable[1] = false;
			maxAvailDirection--;
		}
		if (myPos.y == 0 || map[myPos.x][myPos.y-1] != 0) {
			moveAvailable[2] = false;
			maxAvailDirection--;
		}
		if (myPos.y == map_size-1 || map[myPos.x][myPos.y+1] != 0) {
			moveAvailable[3] = false;
			maxAvailDirection--;
		}
		
		if (maxAvailDirection > 0) {
			int counter = rand.nextInt(maxAvailDirection);
			int index = 0;
			while (counter >= 0) {
				if (moveAvailable[index]) {
					counter--;
				}
				index++;
			}
			index--;
			
			switch (index) {
			case 0:
				myPos.x--;
				break;
			case 1:
				myPos.x++;
				break;
			case 2:
				myPos.y--;
				break;
			case 3:
				myPos.y++;
				break;
			}
		}
				
		//in.close();
		map[myPos.x][myPos.y] = ((teamSymbol=="X")?1:2);
		return myPos;
	} 
}
