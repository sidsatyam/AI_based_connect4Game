import numpy as np
import random
import pygame
import sys
import math
from functools import lru_cache
from collections import defaultdict

BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)

ROW_COUNT = 6
COLUMN_COUNT = 7

PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

WINDOW_LENGTH = 4

# Difficulty depths
DIFFICULTY_DEPTHS = {
    "Easy": 2,
    "Medium": 4,
    "Hard": 6,
}

# --------------------------- Board functions ---------------------------

def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT), dtype=int)


def drop_piece(board, row, col, piece):
    board[row][col] = piece


def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0


def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r


def print_board(board):
    print(np.flip(board, 0))


# Modified: return coordinates of win (list of (r,c)) or None
def winning_move(board, piece):
    # horizontal
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if all(board[r, c + i] == piece for i in range(4)):
                return [(r, c + i) for i in range(4)]

    # vertical
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if all(board[r + i, c] == piece for i in range(4)):
                return [(r + i, c) for i in range(4)]

    # positively sloped
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if all(board[r + i, c + i] == piece for i in range(4)):
                return [(r + i, c + i) for i in range(4)]

    # negatively sloped
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if all(board[r - i, c + i] == piece for i in range(4)):
                return [(r - i, c + i) for i in range(4)]

    return None


# --------------------------- Scoring / Heuristics ---------------------------

def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE

    count_piece = window.count(piece)
    count_opp = window.count(opp_piece)
    count_empty = window.count(EMPTY)

    if count_piece == 4:
        score += 1000
    elif count_piece == 3 and count_empty == 1:
        score += 50
    elif count_piece == 2 and count_empty == 2:
        score += 10

    if count_opp == 3 and count_empty == 1:
        score -= 80  # larger penalty to block opponent

    return score


def score_position(board, piece):
    score = 0

    # center control heavier
    center_array = list(board[:, COLUMN_COUNT // 2])
    center_count = center_array.count(piece)
    score += center_count * 6

    # horizontal
    for r in range(ROW_COUNT):
        row_array = list(board[r, :])
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # vertical
    for c in range(COLUMN_COUNT):
        col_array = list(board[:, c])
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # positive diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + i, c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    # negative diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + 3 - i, c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score


def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) is not None or winning_move(board, AI_PIECE) is not None or len(get_valid_locations(board)) == 0


# --------------------------- Minimax with Alpha-Beta and Transposition Table ---------------------------
# We'll use a simple transposition table keyed by (board_tuple, depth, maximizing)

transposition_table = {}


def board_to_tuple(board):
    return tuple(board.reshape(ROW_COUNT * COLUMN_COUNT).tolist())


def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)

    board_key = (board_to_tuple(board), depth, maximizingPlayer)
    if board_key in transposition_table:
        return transposition_table[board_key]

    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, float('inf'))
            elif winning_move(board, PLAYER_PIECE):
                return (None, -float('inf'))
            else:
                return (None, 0)
        else:
            return (None, score_position(board, AI_PIECE))

    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        transposition_table[board_key] = (column, value)
        return column, value

    else:
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        transposition_table[board_key] = (column, value)
        return column, value


# --------------------------- Utility / Move selection ---------------------------

def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations


def pick_best_move(board, piece):
    valid_locations = get_valid_locations(board)
    best_score = -float('inf')
    best_col = random.choice(valid_locations)
    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, piece)
        score = score_position(temp_board, piece)
        if score > best_score:
            best_score = score
            best_col = col
    return best_col


# --------------------------- Pygame UI ---------------------------

pygame.init()
pygame.mixer.init()

SQUARESIZE = 100
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT + 1) * SQUARESIZE
size = (width, height)
RADIUS = int(SQUARESIZE / 2 - 5)

screen = pygame.display.set_mode(size)
pygame.display.set_caption("Connect Four - Enhanced")

myfont = pygame.font.SysFont("monospace", 60)
smallfont = pygame.font.SysFont("monospace", 30)

# load sounds if present
try:
    drop_sound = pygame.mixer.Sound("drop.wav")
except Exception:
    drop_sound = None
try:
    win_sound = pygame.mixer.Sound("win.wav")
except Exception:
    win_sound = None


def draw_board(board, highlight_positions=None):
    # draw board
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)

    # pieces
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(screen, RED, (int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(screen, YELLOW, (int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)

    # highlight winning positions
    if highlight_positions:
        for (r, c) in highlight_positions:
            # convert board coords to screen center
            center_x = int(c * SQUARESIZE + SQUARESIZE / 2)
            center_y = int(height - (r * SQUARESIZE + SQUARESIZE / 2))
            pygame.draw.circle(screen, GREEN, (center_x, center_y), RADIUS - 6, 6)

    pygame.display.update()


# animate the drop of a piece in a column to target row
def animate_drop(col, target_row, piece_color):
    x = int(col * SQUARESIZE + SQUARESIZE / 2)
    for r in range(ROW_COUNT - 1, target_row - 1, -1):
        draw_board(board)
        y = int(height - (r * SQUARESIZE + SQUARESIZE / 2))
        pygame.draw.circle(screen, piece_color, (x, y), RADIUS)
        pygame.display.update()
        pygame.time.wait(40)


# Draw menu for difficulty selection

def show_difficulty_menu():
    screen.fill(BLACK)
    title = myfont.render("Select Difficulty", True, WHITE)
    screen.blit(title, (width // 2 - title.get_width() // 2, 50))

    buttons = []
    gap = 20
    w = 220
    h = 70
    start_y = 200
    for idx, (name, depth) in enumerate(DIFFICULTY_DEPTHS.items()):
        rect = pygame.Rect(width // 2 - w // 2, start_y + idx * (h + gap), w, h)
        buttons.append((rect, name))
        pygame.draw.rect(screen, DARK_GREEN, rect)
        label = smallfont.render(f"{name} (depth {depth})", True, WHITE)
        screen.blit(label, (rect.x + 20, rect.y + 20))

    pygame.display.update()

    picking = True
    while picking:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for rect, name in buttons:
                    if rect.collidepoint(event.pos):
                        return DIFFICULTY_DEPTHS[name]


# play a sound safely

def try_play(sound):
    try:
        if sound:
            sound.play()
    except Exception:
        pass


# Restart / Exit buttons after game over

def show_game_over_menu(winner_text):
    # overlay
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    label = myfont.render(winner_text, True, WHITE)
    screen.blit(label, (width // 2 - label.get_width() // 2, 50))

    # buttons
    w = 220
    h = 60
    play_rect = pygame.Rect(width // 2 - w - 20, height // 2 - h // 2, w, h)
    exit_rect = pygame.Rect(width // 2 + 20, height // 2 - h // 2, w, h)

    pygame.draw.rect(screen, GREEN, play_rect)
    pygame.draw.rect(screen, (200, 0, 0), exit_rect)

    play_label = smallfont.render("Play Again", True, WHITE)
    exit_label = smallfont.render("Exit", True, WHITE)

    screen.blit(play_label, (play_rect.x + 40, play_rect.y + 18))
    screen.blit(exit_label, (exit_rect.x + 85, exit_rect.y + 18))

    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_rect.collidepoint(event.pos):
                    return "play"
                if exit_rect.collidepoint(event.pos):
                    return "exit"


# --------------------------- Main Loop ---------------------------

board = create_board()
print_board(board)

game_over = False

# pick difficulty
search_depth = show_difficulty_menu()

turn = random.randint(PLAYER, AI)

# draw initial board
screen.fill(BLACK)
draw_board(board)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
            posx = event.pos[0]
            # highlight hover column
            col_hover = int(math.floor(posx / SQUARESIZE))
            if 0 <= col_hover < COLUMN_COUNT:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                if turn == PLAYER and not game_over:
                    pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)
            pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
            if game_over:
                continue

            # Player move
            if turn == PLAYER:
                posx = event.pos[0]
                col = int(math.floor(posx / SQUARESIZE))

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    # animate
                    try_play(drop_sound)
                    animate_drop(col, row, RED)
                    drop_piece(board, row, col, PLAYER_PIECE)

                    win_coords = winning_move(board, PLAYER_PIECE)
                    if win_coords:
                        try_play(win_sound)
                        draw_board(board, highlight_positions=win_coords)
                        label = myfont.render("Player wins!", True, RED)
                        screen.blit(label, (40, 10))
                        pygame.display.update()
                        game_over = True

                    turn = (turn + 1) % 2
                    print_board(board)
                    draw_board(board)

        # AI turn
    if turn == AI and not game_over:
        # compute best move
        pygame.time.wait(300)  # small delay to feel natural
        transposition_table.clear()  # clear table each AI move to limit growth (simple policy)
        col, minimax_score = minimax(board, search_depth, -math.inf, math.inf, True)

        if col is None:
            col = random.choice(get_valid_locations(board))

        if is_valid_location(board, col):
            row = get_next_open_row(board, col)
            try_play(drop_sound)
            animate_drop(col, row, YELLOW)
            drop_piece(board, row, col, AI_PIECE)

            win_coords = winning_move(board, AI_PIECE)
            if win_coords:
                try_play(win_sound)
                draw_board(board, highlight_positions=win_coords)
                label = myfont.render("AI wins!", True, YELLOW)
                screen.blit(label, (40, 10))
                pygame.display.update()
                game_over = True

            print_board(board)
            draw_board(board)

            turn = (turn + 1) % 2

    if game_over:
        # show menu
        result = "Draw"
        if winning_move(board, PLAYER_PIECE):
            result = "Player wins!"
        elif winning_move(board, AI_PIECE):
            result = "AI wins!"

        action = show_game_over_menu(result)
        if action == "play":
            board = create_board()
            game_over = False
            transposition_table.clear()
            screen.fill(BLACK)
            draw_board(board)
            turn = random.randint(PLAYER, AI)
            # choose difficulty again
            search_depth = show_difficulty_menu()
            continue
        else:
            pygame.quit()
            sys.exit()

    pygame.display.update()

