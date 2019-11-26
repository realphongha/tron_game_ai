package main;
import org.json.JSONObject;
import org.json.JSONArray;
import org.json.JSONException;

import io.socket.client.IO;
import io.socket.client.Socket;
import io.socket.emitter.Emitter;
import myTeamBot_v1.Bot5_OriginalMinimax_Spacefill;
import originalBot.Bot4_GameOriginBot;
import playerControl.HumanPlayer;
import playerControl.HumanPlayerGUI;
import simpleTestingBot.Bot1_RandomWalk;

import java.util.ArrayList;
import java.util.Scanner;

public class clientGame {
	private Socket socket;
	private int width_board;
	private int[][] main_board;
	private JSONObject prepoint;
	
	//Team co 2 gia tri X hoac O
	private static final String team="X";
	private static final String hostAddress = "http://localhost:3000";
	
	public static void main(String[] args) {
		try {
			ArrayList<JSONObject> members = new ArrayList<JSONObject>();
			
			//Thong tin cac thanh vien trong nhom
			members.add( new JSONObject("{name: Hà Hữu Linh, mssv: 2019000}"));
			members.add( new JSONObject("{name: Hà Hải Phong, mssv: 2019000}"));
			members.add( new JSONObject("{name: Vũ Quang Đại, mssv: 2019000}"));
			members.add( new JSONObject("{name: Phạm Huy, mssv: 2019000}"));
			
			JSONObject teamInfo = new JSONObject();
			teamInfo.put("team",team);
			teamInfo.put("name", "Tên của team này là 0w0");
			teamInfo.put("members", members);
			
			//
			// start: đoạn này để test các con bot
				// tùy chọn loại bot sẽ chơi
			Scanner in = new Scanner(System.in);
			System.out.print("Choose bot used: \n"
					+ "0. Main bot \n"
					+ "1. Human Player\n"
					+ "2. Human player GUI\n"
					+ "3. Random walk\n"
					+ "4. Original game's bot\n"
					+ "5. My Team s Bot: Combine original minimax + space fill by articulation point\n"
					+ "Input the bot you choose: ");
			int botNumber = in.nextInt();
				
				// tùy chọn team. 1 trận cần có 2 team, 1 team 'X' và 1 team 'O'
			char c;
			boolean teamChoosen = false;
			do {
				System.out.print("Choose your team (x/o): ");
				c = in.next().charAt(0);
				if (c=='x' || c=='X') {
					c = 'X';
					teamChoosen = true;
				}else if (c=='o' || c=='O') {
					c = 'O';
					teamChoosen = true;
				}
			} while (!teamChoosen);
			String team_symbol = c+"";
				
				// tạo client. Các bot client cần truyền vào team_symbol ("X" hoặc "O")
				// VD: new botExample(teamSymbol);
			switch (botNumber) {
			case 1:
				System.out.print("You joined the game. Have fun! ^^\n");
				new HumanPlayer(team_symbol); 	// tự mình điều khiển bằng giao diện dòng lệnh
				break;
			case 2:
				new HumanPlayerGUI(team_symbol); // tự mình điều khiển, sử dụng giao diện đồ họa, có phím bấm các hướng đi
				break;
			case 3:
				System.out.print("Use stupid random walk bot :|\n");
				new Bot1_RandomWalk(team_symbol); 	// Random walk bot
				break;
			case 4:
				System.out.print("Use original game's bot ;]\n");
				new Bot4_GameOriginBot(team_symbol); 	// Bot trong game của thầy
				break;
			case 5:
				System.out.print("Use my team's bot ;]\n");
				new Bot5_OriginalMinimax_Spacefill(team_symbol); 	// Bot trong game của thầy
				break;
			default:
				System.out.print("Use no bot, no player !\n");
				//new clientGame(teamInfo);
				break;
			}
			//in.close();
			// end: đoạn này để test các con bot
			//
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	
	// Khi nào xong thuật toán sẽ viết lại đống dưới này sau
	/*
	public clientGame(final JSONObject teamInfo) 
			throws Exception {

		IO.Options opts = new IO.Options();
		opts.query = "team=".concat(team);
		socket = IO.socket(hostAddress, opts);
		socket.connect();
		
		socket.emit("Infor", teamInfo);
		
		socket.on("new_Map", new Emitter.Listener() {
			public void call(Object... args) {
				// TODO Auto-generated method stub
				JSONObject data = (JSONObject) args[0];
				try {
					// Lay thong tin vi tri hien tai gom 3 thanh phan (x,y,type)
					prepoint = (JSONObject) data.get(team);
					System.out.println(prepoint);
					width_board = (int) data.get("ncol");
					JSONArray map = (JSONArray) data.get("map");
					// Gia tri 0 la o chua ai di qua, 1 team X da di qua, 2 team O da di qua, 3 la vat can
					main_board = new int[width_board][width_board];
					for (int i=0; i<map.length(); i++) {
						for (int j=0; j<map.getJSONArray(i).length(); j++) {
							main_board[i][j] = map.getJSONArray(i).getInt(j);
						}
					}
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
					
					if (result.compareTo(team)==0) {
						System.out.println("You winnnn!");
					} else if (result.compareTo("C")==0) {
						
					}else {
						System.out.println("You lose!");
					}
					
					//Den luot ban tim nuoc di 
					if (turn.compareTo(team)==0) {
						//code thuat toan trong day de tim nuoc di moi toa do x,y;
						
						
						
						//CODE o day
						
						
						//gui toa do nuoc di
						send_message(0,0,team);
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
					if (team_losed.equals(team)) {
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
	*/
}
