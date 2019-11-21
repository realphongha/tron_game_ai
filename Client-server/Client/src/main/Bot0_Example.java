package main;

import java.util.ArrayList;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

// extends lớp AbstractClientPlayer, cần override lại 3 hàm: configTeamInfo(), newMapHandle(), myTurnHandle()
// để chạy bot, mở file clientGame.java, thêm hàm khởi tạo bot này vào phần tùy chọn lúc khởi động game (trong file clientGame.java có hướng dẫn thêm)
public class Bot0_Example extends AbstractClientPlayer{
	// teamSymbol : 'X' || 'O'
	// teamSymbol là thuộc tính của lớp abstract, được nhập vào ở giao diện console khi khởi động client
	
	private int map_size;
	private int[][] map;
	Vector2 myPos, enemyPos;
	// Vector 2 là 1 object có 2 thuộc tính: x và y, tương ứng với 2 tọa độ.
	// Hệ tọa độ của map: 	x - số thứ tự hàng (row)
	//						y - số thứ tự cột (column)
	// ví dụ: map[x][y]
	
	public Bot0_Example(String team) 
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
		members.add( new JSONObject("{name: Stupid Bot, mssv: 10010110}"));
			
		// Nhập tên team ở đây
		teamInfo.put("name", "Team bot vô địch");
		
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
		map_size = (int) data.get("ncol");
		JSONArray mapJSON = (JSONArray) data.get("map");
		// Gia tri 0 la o chua ai di qua, 1 team X da di qua, 2 team O da di qua, 3 la vat can
		map = new int[map_size][map_size];
		for (int i=0; i< mapJSON.length(); i++) {
			for (int j=0; j< mapJSON.getJSONArray(i).length(); j++) {
				map[i][j] = mapJSON.getJSONArray(i).getInt(j);
			}
		}
		// kết thúc xử lý
	}
	
	@Override
	public Vector2 myTurnHandle(Vector2 enemyMove){
		// Hàm để xử lý mỗi lượt đi. Trả về tọa độ mới mà mình đi.
		// * NOTE:	- Nếu tọa độ gửi đi là những ô không hợp lệ (tường, ô đã đi qua) => thua luôn
		// 			- Nếu tính toán quá thời gian => thua luôn
		// Mỗi lượt đi, server sẽ gửi tọa độ mới đi của team địch tới client
		
		// lưu tọa độ team địch vào map
		map[enemyMove.x][enemyMove.y] = ((teamSymbol=="X")?2:1);
		
		// viết code xử lý ở đây
		// ...
		// thay đổi tọa độ team mình sẽ đi vào biến myPos
		// VD: myPos.x = 6; myPos.y = 9;
		// ...
		
		// lưu vị trí mới của mình vào map
		map[myPos.x][myPos.y] = ((teamSymbol=="X")?1:2);
		return myPos;
	} 
}
