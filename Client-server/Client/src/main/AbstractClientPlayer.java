package main;
import org.json.JSONException;
import org.json.JSONObject;

import io.socket.client.IO;
import io.socket.client.Socket;
import io.socket.emitter.Emitter;

public abstract class AbstractClientPlayer {
	private Socket socket;
	protected String teamSymbol;
	
	public class Vector2{
		public int x;
		public int y;
		public Vector2(int _x, int _y) {
			x = _x;
			y = _y;
		}
		public Vector2() {
			x = 0;
			y = 0;
		}
	}
	
	//Team co 2 gia tri X hoac O
	private static final String hostAddress = "http://localhost:3000";
	
	public AbstractClientPlayer(String _team) 
			throws Exception {
		teamSymbol = _team;
		
		JSONObject teamInfo = configTeamInfo();
		
		IO.Options opts = new IO.Options();
		opts.query = "team=".concat(teamSymbol);
		socket = IO.socket(hostAddress, opts);
		socket.connect();
		
		socket.emit("Infor", teamInfo);
		
		socket.on("new_Map", new Emitter.Listener() {
			public void call(Object... args) {
				try {
					// TODO Auto-generated method stub
					JSONObject data = (JSONObject) args[0];
					newMapHandle(data);
				} catch (JSONException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}
		});
		
		socket.on("connect", new Emitter.Listener() {
			public void call(Object... args) {
				System.out.println("Connection established successfully");
			}
		});
		
		socket.on("change_Turn", new Emitter.Listener() {
			public void call(Object... args) {
				JSONObject data = (JSONObject) args[0];
				try {
					// rivalpoint la toa do diem doi thu vua di gom  3 thanh phan (x,y, type)
					JSONObject rivalpoint = (JSONObject) data.get("point");
					String turn = (String) data.get("turn");
					String result = (String) data.get("result");
					
					if (result.compareTo(teamSymbol)==0) {
						System.out.println("You winnnn!");
					} else if (result.compareTo("C")==0) {
						
					}else {
						System.out.println("You lose!");
					}
					
					//Den luot ban tim nuoc di 
					if (turn.compareTo(teamSymbol)==0) {
						Vector2 enemyMove = new Vector2();
						enemyMove.x = rivalpoint.getInt("x");
						enemyMove.y = rivalpoint.getInt("y");
						
						Vector2 myMove = myTurnHandle(enemyMove);		
						
						//gui toa do nuoc di
						send_message(myMove.x, myMove.y, teamSymbol);
					}
				} catch (JSONException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}
		});
		
		socket.on("time_Out", new Emitter.Listener() {
			public void call(Object... args) {
				JSONObject data = (JSONObject) args[0];
				try {
					String team_losed = (String) data.get("team");
					if (team_losed.equals(teamSymbol)) {
						System.out.println("You lose!");
					} else {
						System.out.println("You winnnnn!");
					}
					//socket.close();
				} catch (JSONException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}
		});
	}

	public void send_message(int row, int col, String team) throws JSONException {
		JSONObject message = new JSONObject();
		message.put("x", row);
		message.put("y", col);
		message.put("type", team);
		this.socket.emit("moving", message);
	}
	
	public abstract JSONObject configTeamInfo() throws JSONException;
	public abstract void newMapHandle(JSONObject data) throws JSONException;
	public abstract Vector2 myTurnHandle(Vector2 enemyMove);
}
