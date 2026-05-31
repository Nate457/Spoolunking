# Level 1: The Tangled Cavern
# Format: 0=floor, 5=solid, 6=string block, 1-4=torches (L,R,U,D)
# ("S",hp,atk,spd,sight,"color",size)  ("W",hp,atk,spd,sight)  ("C",hp,atk,spd,sight)

def _build():
    m = [[0]*65 for _ in range(35)]

    # --- Borders ---
    for c in range(65):
        m[0][c] = 5
        m[34][c] = 5
    for r in range(35):
        m[r][0] = 5
        m[r][64] = 5

    # ============================================================
    # ROOM 1 – Starting Chamber (rows 1-8, cols 1-15)
    # ============================================================
    # right wall of room 1
    for r in range(1, 9):
        m[r][15] = 5
    # bottom wall of room 1
    for c in range(1, 16):
        m[8][c] = 5
    # open corridor south from room 1 (cols 5-9, rows 9-10)
    m[8][5] = 0; m[8][6] = 0; m[8][7] = 0; m[8][8] = 0
    # open corridor east from room 1 (rows 3-5, col 15)
    m[3][15] = 0; m[4][15] = 0; m[5][15] = 0

    # torches in room 1
    m[1][14] = 2   # right torch
    m[7][1]  = 3   # top torch (faces up)

    # player spawn
    m[3][3] = "spawn"

    # enemies in room 1 (easy intro)
    m[6][10] = ("S", 6, 1, 3, 140, "Red", 1)
    m[5][12] = ("S", 6, 1, 3, 140, "Green", 1)

    # ============================================================
    # ROOM 2 – Cave Corridor (rows 1-8, cols 16-30)
    # ============================================================
    # right wall
    for r in range(1, 9):
        m[r][31] = 5
    # bottom wall
    for c in range(16, 32):
        m[8][c] = 5
    # open south from room 2 (cols 20-23)
    m[8][20] = 0; m[8][21] = 0; m[8][22] = 0

    # string block cover
    m[4][18] = 6; m[4][19] = 6
    m[5][22] = 6; m[5][23] = 6
    m[3][27] = 6; m[3][28] = 6

    # torches
    m[1][16] = 1  # left torch
    m[7][30] = 2  # right torch

    # enemies in room 2
    m[3][20] = ("S", 6, 1, 3, 150, "Red", 2)
    m[5][25] = ("C", 10, 2, 2, 150)
    m[2][28] = ("S", 6, 1, 2, 150, "White", 1)

    # ============================================================
    # ROOM 3 – The Deep Cave (rows 9-21, cols 1-44)
    # ============================================================
    # top wall already from room 1 bottom; extend it
    for c in range(32, 45):
        m[8][c] = 5
    # right wall
    for r in range(9, 22):
        m[r][44] = 5
    # bottom wall
    for c in range(1, 45):
        m[21][c] = 5
    # open south to boss (cols 18-23)
    m[21][18] = 0; m[21][19] = 0; m[21][20] = 0
    m[21][21] = 0; m[21][22] = 0; m[21][23] = 0

    # inner pillars / cover in room 3
    for c in range(6, 9):
        m[12][c] = 5
    for c in range(15, 18):
        m[15][c] = 5
    m[11][30] = 6; m[11][31] = 6; m[11][32] = 6
    m[17][35] = 6; m[17][36] = 6
    m[19][12] = 6; m[19][13] = 6
    m[13][38] = 6; m[13][39] = 6; m[13][40] = 6

    # torches in room 3
    m[9][1]  = 2  # left wall torch
    m[9][43] = 1  # right wall torch
    m[15][1] = 2
    m[20][43]= 1
    m[14][22]= 4  # center down-torch

    # enemies in room 3 (medium difficulty)
    m[11][5]  = ("C", 12, 2, 2, 155)
    m[13][25] = ("W", 12, 2, 2, 160)
    m[16][10] = ("S", 8, 1, 3, 150, "Green", 2)
    m[18][38] = ("C", 12, 2, 2, 155)
    m[10][40] = ("S", 8, 1, 3, 150, "Red", 2)
    m[20][20] = ("W", 12, 2, 2, 160)

    # ============================================================
    # ROOM 4 – Boss Chamber (rows 22-33, cols 5-59)
    # ============================================================
    # top wall
    for c in range(5, 60):
        m[22][c] = 5
    m[22][18] = 0; m[22][19] = 0; m[22][20] = 0
    m[22][21] = 0; m[22][22] = 0; m[22][23] = 0
    # left wall
    for r in range(22, 34):
        m[r][5] = 5
    # right wall
    for r in range(22, 34):
        m[r][59] = 5
    # bottom already border

    # dramatic cover pillars
    for c in range(10, 13):
        m[26][c] = 5
    for c in range(48, 51):
        m[26][c] = 5
    for c in range(10, 13):
        m[30][c] = 5
    for c in range(48, 51):
        m[30][c] = 5

    # string block walls
    m[24][20] = 6; m[24][21] = 6; m[24][22] = 6
    m[31][38] = 6; m[31][39] = 6; m[31][40] = 6

    # torches (dramatic boss atmosphere)
    m[23][6]  = 2
    m[23][58] = 1
    m[33][6]  = 3
    m[33][58] = 3
    m[28][6]  = 2
    m[28][58] = 1

    # BOSS: powerful wine wraith + elite guards
    m[28][32] = ("W", 30, 3, 2, 200)   # Boss: Elder Wine Wraith
    m[25][14] = ("C", 18, 3, 3, 160)   # Guard cat
    m[25][50] = ("C", 18, 3, 3, 160)   # Guard cat
    m[30][20] = ("W", 15, 2, 2, 160)   # Support wine wraith

    return m

map = _build()
