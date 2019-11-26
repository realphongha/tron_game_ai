package myBot;

public class Map2D {
	public static final int SPACE = 0;
	public static final int MY_TEAM = 1;
	public static final int ENEMY_TEAM = 2;
	public static final int WALL = 3;
	
	public int [][] map;
	public int mapSize;
	
	public Map2D(int map_size) {
		mapSize = map_size;
		map = new int[map_size][map_size];
	}
	
	public Map2D(int[][] _map, int map_size) {
		int i,j;
		mapSize = map_size;
		map = new int[map_size][map_size];
		for (i = 0; i < map_size; i++) {
			for (j = 0; j < map_size; j++) {
				map[i][j] = _map[i][j];
			}
		}
	}

	public Map2D(Map2D oldMap) {
		//int i,j;
		mapSize = oldMap.mapSize;
		map = new int[mapSize][mapSize];
		for (int i = 0; i < mapSize; i++) {
//			for (j = 0; j < mapSize; j++) {
//				map[i][j] = tmpMap[i][j];
//			}
			System.arraycopy(oldMap.map[i], 0, map[i], 0, mapSize);
		}
	}
}
