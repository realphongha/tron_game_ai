package myTeamBot_v1;

public class Map {
	public static final int SPACE = 0;
	public static final int WALL = 3;
	public static final int TEAM_X = 1;
	public static final int TEAM_O = 2;
	public static final int TEMP = 4;
	public static final int MAP_SETTED = 10;
	
	public int [][] map;
	public int mapSize;
	
	public Map(int map_size) {
		mapSize = map_size;
		map = new int[map_size][map_size];
	}
	
	public Map(int[][] _map, int map_size) {
		int i,j;
		mapSize = map_size;
		map = new int[map_size][map_size];
		for (i = 0; i < map_size; i++) {
			for (j = 0; j < map_size; j++) {
				map[i][j] = _map[i][j];
			}
		}
	}

	public Map(Map oldMap) {
		int i,j;
		mapSize = oldMap.mapSize;
		map = new int[mapSize][mapSize];
		int[][] tmpMap = oldMap.map;
		for (i = 0; i < mapSize; i++) {
			for (j = 0; j < mapSize; j++) {
				map[i][j] = tmpMap[i][j];
			}
		}
//		mapSize = oldMap.mapSize;
//		map = new int[mapSize][mapSize];
//		for (int i = 0; i < mapSize; i++) {
//			System.arraycopy(oldMap.map[i], 0, map[i], 0, mapSize);
//		}
	}


	public boolean isSpace(int x, int y) {
		if ((x >= mapSize) || (y >= mapSize) || (x < 0) || (y < 0)) {
			return false;
		}
		if ((map[x][y] == SPACE) || (map[x][y] == TEMP)) {
			return true;
		}
		return false;
	}

	public int amountSpacesAround(int x, int y) {
		int count = 0;
		if (isSpace(x - 1, y)) {
			count++;
		}
		if (isSpace(x + 1, y)) {
			count++;
		}
		if (isSpace(x, y - 1)) {
			count++;
		}
		if (isSpace(x, y + 1)) {
			count++;
		}
		return count;
	}

	public boolean isSpaceAndNotTemp(int x, int y) {
		if ((x >= mapSize) || (y >= mapSize) || (x < 0) || (y < 0)) {
			return false;
		}
		return map[x][y] == 0;
	}

	public void setTemp(int x, int y) {
		map[x][y] = TEMP;
	}

	public void setTeamO(int x, int y) {
		map[x][y] = TEAM_O;
	}

	public void setTeamX(int x, int y) {
		map[x][y] = TEAM_X;
	}

	public void setMap(int x, int y) {
		map[x][y] = MAP_SETTED;
	}
	
	public void resetMap(int x, int y) {
		map[x][y] = SPACE;
	}

	public boolean isReachable(int x, int y) {
		if ((x >= mapSize) || (y >= mapSize) || (x < 0) || (y < 0)) {
			return false;
		}
		return map[x][y] == MAP_SETTED;
	}

	public void setSpace(int x, int y) {
		map[x][y] = SPACE;
	}
	
	public int countAvailableMove(int x, int y) {
		int count = 0;
		if (isSpace(x + 1, y)) {
			count++;
		}
		if (isSpace(x - 1, y)) {
			count++;
		}
		if (isSpace(x, y - 1)) {
			count++;
		}
		if (isSpace(x, y + 1)) {
			count++;
		}
		return count;
	}
	
	// debug
		public void drawMap(int myX, int myY, int enemyX, int enemyY, boolean isMyTeamX) {
			int i,j;
			String SPACE_SYMBOL = ".";
			String WALL_SYMBOL = "H";
			String TEAM_X_SYMBOL = "x";
			String TEAM_O_SYMBOL = "o";
			String TEMP_SYMBOL = "-";
			String MAP_SETTED_SYMBOL = "*";
			String mapDrawn = "";
			for (i=0;i<mapSize;i++) {
				for (j=0;j<mapSize;j++) {
					switch (map[i][j]) {
					case SPACE:
						mapDrawn += SPACE_SYMBOL;
						break;
					case WALL:
						mapDrawn += WALL_SYMBOL;
						break;
					case TEAM_O:
						if (isMyTeamX) {
							if (enemyX==i && enemyY==j) {
								mapDrawn += "O";
							}else {
								mapDrawn += TEAM_O_SYMBOL;
							}
						}else {
							if (myX==i && myY==j) {
								mapDrawn += "O";
							}else {
								mapDrawn += TEAM_O_SYMBOL;
							}
						}					
						break;
					case TEAM_X:
						if (isMyTeamX) {
							if (myX==i && myY==j) {
								mapDrawn += "X";
							}else {
								mapDrawn += TEAM_X_SYMBOL;
							}
						}else {
							if (enemyX==i && enemyY==j) {
								mapDrawn += "X";
							}else {
								mapDrawn += TEAM_X_SYMBOL;
							}
						}		
						break;
					case TEMP:
						mapDrawn += TEMP_SYMBOL;
						break;
					case MAP_SETTED:
						mapDrawn += MAP_SETTED_SYMBOL;
						break;
					default:
						break;
					}
				}
				mapDrawn+="\n";
			}
			System.out.println(mapDrawn);
		}
		
		public void drawMapWithoutMark() {
			int i,j;
			String SPACE_SYMBOL = ".";
			String WALL_SYMBOL = "H";
			String TEAM_X_SYMBOL = "x";
			String TEAM_O_SYMBOL = "o";
			String TEMP_SYMBOL = "-";
			String MAP_SETTED_SYMBOL = "*";
			String mapDrawn = "";
			for (i=0;i<mapSize;i++) {
				for (j=0;j<mapSize;j++) {
					switch (map[i][j]) {
					case SPACE:
						mapDrawn += SPACE_SYMBOL;
						break;
					case WALL:
						mapDrawn += WALL_SYMBOL;
						break;
					case TEAM_O:
						mapDrawn += TEAM_O_SYMBOL;
						break;
					case TEAM_X:
						mapDrawn += TEAM_X_SYMBOL;
						break;
					case TEMP:
						mapDrawn += TEMP_SYMBOL;
						break;
					case MAP_SETTED:
						mapDrawn += MAP_SETTED_SYMBOL;
						break;
					default:
						break;
					}
				}
				mapDrawn+="\n";
			}
			System.out.println(mapDrawn);
		}
}