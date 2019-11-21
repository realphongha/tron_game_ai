package playerControl;

import java.awt.BorderLayout;
import java.awt.GridLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import java.util.ArrayList;
import java.util.concurrent.Semaphore;

import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import main.AbstractClientPlayer;

public class HumanPlayerGUI extends AbstractClientPlayer{
	// config
	static final int BUTTON_SIZE = 50; // unit: px
	static final int BUTTON_SPACING = 5; // unit: px
	static final int MESSAGE_AREA_HEIGHT = 50; // unit: px
	static final int SLEEP_TIME = 10;
	JButton upButton, downButton, leftButton, rightButton, surrenderButton;
	JLabel message;
	boolean moved;
	
	Semaphore semaphore; 
	
	//
	private int map_size;
	private int[][] map;
	Vector2 myPos, enemyPos;
	private boolean upAvailable, downAvailable, leftAvailable, rightAvailable;
	
	public HumanPlayerGUI(String team) 
			throws Exception {
		super(team);
		createGUI();
		
		moved = false;
		semaphore = new Semaphore(1);
	}
	
	@Override
	public JSONObject configTeamInfo() throws JSONException {
		ArrayList<JSONObject> members = new ArrayList<JSONObject>();
		//Thong tin cac thanh vien trong nhom
		members.add( new JSONObject("{name: Normie, mssv: 12345678}"));
		members.add( new JSONObject("{name: Foo, mssv: 23456789}"));
		
		JSONObject teamInfo = new JSONObject();
		teamInfo.put("team", teamSymbol);
		teamInfo.put("name", "Team công nghệ cao");
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
		
		message.setText("Your turn");
		
		upAvailable = downAvailable = leftAvailable = rightAvailable = false;
		
		if (myPos.x > 0 && map[myPos.x-1][myPos.y] == 0) {
			upButton.setEnabled(true);
			upAvailable = true;
		}
		if (myPos.x < map_size-1 && map[myPos.x+1][myPos.y] == 0) {
			downButton.setEnabled(true);
			downAvailable = true;
		}
		if (myPos.y > 0 && map[myPos.x][myPos.y-1] == 0) {
			leftAvailable = true;
			leftButton.setEnabled(true);
		}
		if (myPos.y < map_size-1 && map[myPos.x][myPos.y+1] == 0) {
			rightAvailable = true;
			rightButton.setEnabled(true);
		}

		while (!moved) {
			try {
				Thread.sleep(SLEEP_TIME);
			} catch (InterruptedException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
		
		moved = false;
		message.setText("Enemy's turn");
		
		map[myPos.x][myPos.y] = ((teamSymbol=="X")?1:2);
		return myPos;
	} 
	
	private void createGUI() {
		JFrame controller = new JFrame();
		controller.setTitle("Controller - Cuộc chiến lãnh thổ");
		controller.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		controller.setResizable(true);
		controller.setSize(BUTTON_SIZE * 3 + BUTTON_SPACING * 2, BUTTON_SIZE * 2 + BUTTON_SPACING * 1 + MESSAGE_AREA_HEIGHT);
		
		controller.addKeyListener(new KeyControlListener());
		
		message = new JLabel();
		message.setText("Game hasn't started");
		controller.add(message, BorderLayout.NORTH);
		
		JPanel controlPanel = new JPanel();
		controller.add(controlPanel, BorderLayout.SOUTH);
		
		controlPanel.setLayout(new GridLayout(2, 3, BUTTON_SPACING, BUTTON_SPACING));
//		String[] buttonMap = {
//				" ","↑"," ",
//				"←","↓","→"
//		};
		
		// add nothingness
		surrenderButton = new JButton("=(");
		surrenderButton.addActionListener(new ActionListener() {
		    @Override
		    public void actionPerformed(ActionEvent e) {
		    	moveByPlayer(0);
		    }
		});
		controlPanel.add(surrenderButton);
		
		// add up button
		upButton = new JButton("↑");
		upButton.addActionListener(new ActionListener() {
		    @Override
		    public void actionPerformed(ActionEvent e) {
		    	moveByPlayer(1);
		    }
		});
		controlPanel.add(upButton);
		
		// add nothingness
		controlPanel.add(new JLabel(""));
		
		// add left button
		leftButton = new JButton("←");
		leftButton.addActionListener(new ActionListener() {
			@Override
				public void actionPerformed(ActionEvent e) {
					moveByPlayer(2);
				}
			});
		controlPanel.add(leftButton);
		
		// add down button
		downButton = new JButton("↓");
		downButton.addActionListener(new ActionListener() {
			@Override
				public void actionPerformed(ActionEvent e) {
					moveByPlayer(3);
				}
			});
		controlPanel.add(downButton);
		
		// add right button
		rightButton = new JButton("→");
		rightButton.addActionListener(new ActionListener() {
			@Override
				public void actionPerformed(ActionEvent e) {
					moveByPlayer(4);
				}
			});
		controlPanel.add(rightButton);
		upButton.setEnabled(false);
		downButton.setEnabled(false);
		leftButton.setEnabled(false);
		rightButton.setEnabled(false);
						
		controller.setVisible(true);
	}
	
	private void moveByPlayer(int direction) {
		// "↑" : 1
		// "←" : 2
		// "↓" : 3
		// "→" : 4
		try {
			semaphore.acquire();
			switch (direction) {
			case 0: // surrender
				lockAllButton();
				moved = true;
				break;
			case 1:
				if (upAvailable) {
					myPos.x--;
					lockAllButton();
					moved = true;
				}
				break;
			case 2:
				if (leftAvailable) {
					myPos.y--;
					lockAllButton();
					moved = true;
				}
				break;
			case 3:
				if (downAvailable) {
					myPos.x++;
					lockAllButton();
					moved = true;
				}
				break;
			case 4:
				if (rightAvailable) {
					myPos.y++;
					lockAllButton();
					moved = true;
				}
				break;
			default:
				break;
			}
			semaphore.release();
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	private void lockAllButton() {
		// lock button
		upButton.setEnabled(false);
		downButton.setEnabled(false);
		leftButton.setEnabled(false);
		rightButton.setEnabled(false);
		upAvailable = downAvailable = leftAvailable = rightAvailable = false;
	}
	
	private class KeyControlListener extends KeyAdapter {
	    @Override
	    public void keyPressed(KeyEvent event) {
	    	char ch = event.getKeyChar();
	    	if 		(ch == 'w' || ch == 'W' || ch == KeyEvent.VK_UP) 	{ moveByPlayer(1); }
	    	else if (ch == 'a' || ch == 'A' || ch == KeyEvent.VK_LEFT) 	{ moveByPlayer(2); }
	    	else if (ch == 's' || ch == 'S' || ch == KeyEvent.VK_DOWN) 	{ moveByPlayer(3); }
	    	else if (ch == 'd' || ch == 'D' || ch == KeyEvent.VK_RIGHT) { moveByPlayer(4); }
	    	else if (ch == 'p' || ch == 'P') 							{ moveByPlayer(0); }
	    }
	}
}