# import pygame and initialize
import pygame
import sys

# Game settings
BOARD_WIDTH = 26
BOARD_HEIGHT = 30
CELL_SIZE = 20
WINDOW_WIDTH = BOARD_WIDTH * CELL_SIZE
WINDOW_HEIGHT = BOARD_HEIGHT * CELL_SIZE
FPS = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
PLAYER1_COLOR = (0, 120, 255)
PLAYER2_COLOR = (255, 80, 80)

def draw_grid(screen):
	for x in range(0, WINDOW_WIDTH, CELL_SIZE):
		pygame.draw.line(screen, GRAY, (x, 0), (x, WINDOW_HEIGHT))
	for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
		pygame.draw.line(screen, GRAY, (0, y), (WINDOW_WIDTH, y))
	# Divider in the middle
	midx = (BOARD_WIDTH // 2) * CELL_SIZE
	pygame.draw.line(screen, (80, 80, 80), (midx, 0), (midx, WINDOW_HEIGHT), width=3)

def draw_board(screen, board):
	for y in range(BOARD_HEIGHT):
		for x in range(BOARD_WIDTH):
			if board[y][x] == 1:
				pygame.draw.rect(screen, PLAYER1_COLOR, (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))
			elif board[y][x] == 2:
				pygame.draw.rect(screen, PLAYER2_COLOR, (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))

def rotate_pattern(pattern, rotation):
	# rotation: 0=0deg, 1=90deg, 2=180deg, 3=270deg
	if rotation == 0:
		return pattern
	rotated = pattern
	for _ in range(rotation):
		rotated = [(-dy, dx) for dx, dy in rotated]
	min_x = min(dx for dx, dy in rotated)
	min_y = min(dy for dx, dy in rotated)
	# Shift so top-left is (0,0)
	rotated = [(dx - min_x, dy - min_y) for dx, dy in rotated]
	return rotated

def draw_deleted_ghost(screen, deleted_blocks):
	ghost_color = (120, 120, 120, 100)  # Gray, transparent
	s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
	s.fill(ghost_color)
	for x, y in deleted_blocks:
		s_rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
		screen.blit(s, s_rect)

def draw_ghost(screen, player, selected_pattern, placements_left, pattern_rotation):
	mx, my = pygame.mouse.get_pos()
	x, y = mx // CELL_SIZE, my // CELL_SIZE
	ghost_color = PLAYER1_COLOR if player == 1 else PLAYER2_COLOR
	ghost_color = (*ghost_color[:3], 100)  # Add alpha for transparency
	s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
	s.fill(ghost_color)
	if selected_pattern:
		pattern = rotate_pattern(PATTERNS[selected_pattern], pattern_rotation)
		if placements_left >= len(pattern):
			for dx, dy in pattern:
				px, py = x + dx, y + dy
				if 0 <= px < BOARD_WIDTH and 0 <= py < BOARD_HEIGHT:
					s_rect = pygame.Rect(px*CELL_SIZE, py*CELL_SIZE, CELL_SIZE, CELL_SIZE)
					screen.blit(s, s_rect)
	else:
		if 0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT and placements_left > 0:
			s_rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
			screen.blit(s, s_rect)

def count_neighbors(board, x, y):
	counts = {0: 0, 1: 0, 2: 0}
	for dy in [-1, 0, 1]:
		for dx in [-1, 0, 1]:
			if dx == 0 and dy == 0:
				continue
			nx, ny = x + dx, y + dy
			if 0 <= nx < BOARD_WIDTH and 0 <= ny < BOARD_HEIGHT:
				counts[board[ny][nx]] += 1
	return counts

def evolve(board):
	new_board = [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
	for y in range(BOARD_HEIGHT):
		for x in range(BOARD_WIDTH):
			cell = board[y][x]
			neighbors = count_neighbors(board, x, y)
			total_live = neighbors[1] + neighbors[2]
			if cell == 0:
				# Birth: 3 neighbors total, assign to majority color
				if total_live == 3:
					if neighbors[1] > neighbors[2]:
						new_board[y][x] = 1
					elif neighbors[2] > neighbors[1]:
						new_board[y][x] = 2
					# If tie, stays dead (0)
			else:
				# Survival: 2 or 3 neighbors (any player)
				if total_live == 2 or total_live == 3:
					new_board[y][x] = cell
				# Otherwise, cell dies
	return new_board

def check_win(board):
	# Player 1 wins if any of their cells reach the last column
	for y in range(BOARD_HEIGHT):
		if board[y][BOARD_WIDTH-1] == 1:
			return 1
	# Player 2 wins if any of their cells reach the first column
	for y in range(BOARD_HEIGHT):
		if board[y][0] == 2:
			return 2
	return 0



# Default setups (patterns)
PATTERNS = {
	'glider': [
		(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)
	],
	'block': [
		(0, 0), (0, 1), (1, 0), (1, 1)
	],
	'blinker': [
		(0, 1), (1, 1), (2, 1)
	]
}
PATTERN_KEYS = ['glider', 'block', 'blinker']

def can_place_pattern(board, pattern, x, y, player):
	for dx, dy in pattern:
		px, py = x + dx, y + dy
		if not (0 <= px < BOARD_WIDTH and 0 <= py < BOARD_HEIGHT):
			return False
		if board[py][px] != 0:
			return False
		if player == 1 and px >= BOARD_WIDTH // 2:
			return False
		if player == 2 and px < BOARD_WIDTH // 2:
			return False
	return True

def place_pattern(board, pattern, x, y, player):
	for dx, dy in pattern:
		px, py = x + dx, y + dy
		board[py][px] = player

def boards_equal(b1, b2):
	for y in range(BOARD_HEIGHT):
		for x in range(BOARD_WIDTH):
			if b1[y][x] != b2[y][x]:
				return False
	return True

def board_hash(board):
	return tuple(tuple(row) for row in board)

def main():
	pygame.init()
	screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
	pygame.display.set_caption("Conway's Game of Life: Duel")
	clock = pygame.time.Clock()

	board = [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
	initial_board = [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
	round_placements = []  # List of dicts: {1: set(), 2: set()} for each round
	round_number = 1
	player = 1
	first_player = 1
	placement_player = first_player
	placements_left = 5
	max_placements = 5
	font = pygame.font.SysFont(None, 32)
	phase = "placement"  # or "evolution"
	evolution_steps = 500
	evolution_counter = 0
	winner = 0
	selected_pattern = None
	pattern_rotation = 0
	points = {1: 0, 2: 0}

	running = True
	prev_board = None
	seen_states = {}
	deleted_blocks_ghost = set()
	current_round_placements = {1: set(), 2: set()}
	placement_done = {1: False, 2: False}
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif phase == "placement" and event.type == pygame.KEYDOWN:
				# 1,2,3 to select pattern
				if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
					idx = event.key - pygame.K_1
					if 0 <= idx < len(PATTERN_KEYS):
						selected_pattern = PATTERN_KEYS[idx]
						pattern_rotation = 0
				# R to rotate pattern
				elif event.key == pygame.K_r and selected_pattern:
					pattern_rotation = (pattern_rotation + 1) % 4
				# Deselect pattern
				elif event.key == pygame.K_ESCAPE:
					selected_pattern = None
					pattern_rotation = 0
				# No manual start; evolution begins only after both players place
			elif phase == "placement" and event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 3):
				mx, my = pygame.mouse.get_pos()
				x, y = mx // CELL_SIZE, my // CELL_SIZE
				if event.button == 1:
					if selected_pattern:
						pattern = rotate_pattern(PATTERNS[selected_pattern], pattern_rotation)
						# Only allow if enough placements left
						if can_place_pattern(board, pattern, x, y, placement_player) and placements_left >= len(pattern):
							place_pattern(board, pattern, x, y, placement_player)
							for dx, dy in pattern:
								current_round_placements[placement_player].add((x + dx, y + dy))
							placements_left -= len(pattern)
							selected_pattern = None
							pattern_rotation = 0
					else:
						if placements_left > 0 and board[y][x] == 0:
							if placement_player == 1 and x < BOARD_WIDTH // 2:
								board[y][x] = 1
								current_round_placements[1].add((x, y))
								placements_left -= 1
							elif placement_player == 2 and x >= BOARD_WIDTH // 2:
								board[y][x] = 2
								current_round_placements[2].add((x, y))
								placements_left -= 1
				elif event.button == 3:
					# Delete only your own block: if placed this round, refund a placement; otherwise costs 1 placement
					if 0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT and board[y][x] == placement_player:
						placed_this_round = (x, y) in current_round_placements[placement_player]
						if placed_this_round:
							current_round_placements[placement_player].discard((x, y))
							board[y][x] = 0
							placements_left = min(max_placements, placements_left + 1)
						elif placements_left > 0:
							board[y][x] = 0
							placements_left -= 1
				if placements_left == 0:
					placement_done[placement_player] = True
					if placement_done[1] and placement_done[2]:
						# Both players placed; start evolution
						for y2 in range(BOARD_HEIGHT):
							for x2 in range(BOARD_WIDTH):
								initial_board[y2][x2] = board[y2][x2]
						round_placements.append({1: current_round_placements[1].copy(), 2: current_round_placements[2].copy()})
						current_round_placements = {1: set(), 2: set()}
						placement_done = {1: False, 2: False}
						phase = "evolution"
						evolution_counter = 0
					else:
						# Switch to the other player and reset their placements_left
						placement_player = 2 if placement_player == 1 else 1
						placements_left = max_placements

		if phase == "evolution":
			if evolution_counter < evolution_steps and winner == 0:
				next_board = evolve(board)
				winner = check_win(next_board)
				evolution_counter += 1
				is_stale = prev_board is not None and boards_equal(board, next_board)
				board_hash_val = board_hash(next_board)
				seen_states[board_hash_val] = seen_states.get(board_hash_val, 0) + 1
				cycle_detected = seen_states[board_hash_val] >= 3
				prev_board = [row[:] for row in board]
				board = next_board
				if winner:
					points[winner] += 1
				if (is_stale or cycle_detected) and not winner:
					# End round if board is stale or cycle detected and no winner
					phase = "placement"
					# Delete up to 5 blocks from each player placed 5 rounds ago
					if len(round_placements) >= 5:
						for p in [1, 2]:
							for i, (x, y) in enumerate(round_placements[round_number - 5][p]):
								if i < 5:
									initial_board[y][x] = 0
					board = [row[:] for row in initial_board]
					first_player = 2 if first_player == 1 else 1
					player = first_player
					placement_player = first_player
					placements_left = max_placements
					current_round_placements = {1: set(), 2: set()}
					placement_done = {1: False, 2: False}
					winner = 0
					prev_board = None
					seen_states = {}
					round_number += 1
			else:
				phase = "placement"
				# Delete up to 5 blocks from each player placed 5 rounds ago
				if len(round_placements) >= 6:
					for p in [1, 2]:
						for i, (x, y) in enumerate(round_placements[round_number - 5][p]):
							if i < 5:
								initial_board[y][x] = 0
				board = [row[:] for row in initial_board]
				# Alternate first player each round
				first_player = 2 if first_player == 1 else 1
				player = first_player
				placement_player = first_player
				placements_left = max_placements
				current_round_placements = {1: set(), 2: set()}
				placement_done = {1: False, 2: False}
				winner = 0
				prev_board = None
				seen_states = {}
				round_number += 1

		screen.fill(WHITE)
		draw_board(screen, board)
		draw_grid(screen)

		deleted_blocks = set()
		# Show ghost of deleted blocks for the current placement player if blocks are deleted this round
		if deleted_blocks_ghost:
			deleted_blocks = deleted_blocks_ghost
		elif len(round_placements) >= 5 and round_number > 5:
			# Only show deleted blocks for the current placement player
			deleted_blocks = round_placements[round_number - 5][placement_player] if placement_player in round_placements[round_number - 5] else set()
		if phase == "placement":
			prev_board = None
			seen_states = {}
			draw_ghost(screen, placement_player, selected_pattern, placements_left, pattern_rotation)
			if deleted_blocks:
				draw_deleted_ghost(screen, deleted_blocks)
			info = f"Player {placement_player}'s turn | Placements left: {placements_left}"
			text = font.render(info, True, BLACK)
			screen.blit(text, (10, 10))
			#tip = font.render("L-click place / R-click delete (free if placed this round)", True, BLACK)
			#screen.blit(tip, (10, 40))
			patinfo = font.render("1:Glider 2:Block 3:Blinker | ESC: Deselect", True, BLACK)
			screen.blit(patinfo, (10, 70))
			score = font.render(f"Score - Player 1: {points[1]} | Player 2: {points[2]}", True, (80, 0, 80))
			screen.blit(score, (10, 130))
			if selected_pattern:
				sel = font.render(f"Selected: {selected_pattern.title()} (R: rotate, click to place)", True, (0, 120, 0))
				screen.blit(sel, (10, 100))
		elif phase == "evolution":
			if winner:
				win_text = font.render(f"Player {winner} wins!", True, (0,200,0))
				screen.blit(win_text, (10, 10))
			else:
				evo_text = font.render(f"Evolution step {evolution_counter}/{evolution_steps}", True, BLACK)
				screen.blit(evo_text, (10, 10))
			score = font.render(f"Score - Player 1: {points[1]} | Player 2: {points[2]}", True, (80, 0, 80))
			screen.blit(score, (10, 130))

		pygame.display.flip()
		clock.tick(FPS)


	pygame.quit()
	sys.exit()

if __name__ == "__main__":
	main()
