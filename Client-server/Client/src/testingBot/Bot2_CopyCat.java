package testingBot;

import java.util.ArrayList;
import java.util.Random;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import main.AbstractClientPlayer;

public class Bot2_CopyCat extends AbstractClientPlayer{
	// teamSymbol : 'X' || 'O'
		private int map_size;
		private int[][] map;
		Vector2 myPos, enemyPos;
		Random rand;
		
		public Bot2_CopyCat(String team) 
				throws Exception {
			super(team);
			rand = new Random(); 
		}
		
		@Override
		public JSONObject configTeamInfo() throws JSONException {
			ArrayList<JSONObject> members = new ArrayList<JSONObject>();
			//Thong tin cac thanh vien trong nhom
			members.add( new JSONObject("{name: Copier1, mssv: 13577531}"));
			members.add( new JSONObject("{name: CatCat, mssv: 24688642}"));
			
			JSONObject teamInfo = new JSONObject();
			teamInfo.put("team", teamSymbol);
			teamInfo.put("name", "You are me, and I am you");
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
			
					
			//in.close();
			map[myPos.x][myPos.y] = ((teamSymbol=="X")?1:2);
			return myPos;
		} 
}
