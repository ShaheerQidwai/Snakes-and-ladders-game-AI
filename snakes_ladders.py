import pygame
import sys
import random
import math

pygame.init()

# Constants
TOP_PANEL_HEIGHT = 100
CELL_SIZE = 40
MAIN_COLS = 10
PATH_COLS = 5
WIDTH = CELL_SIZE * (MAIN_COLS + PATH_COLS * 2 + 2)
HEIGHT = CELL_SIZE * 12 + TOP_PANEL_HEIGHT
FPS = 60

# colors
COLORS = {
    'background': (255, 255, 255),
    'main_path': (173, 216, 230),
    'safe_path': (200, 230, 200),
    'risky_path': (255, 200, 200),
    'snake': (255, 50, 50),
    'ladder': (50, 200, 50),
    'powerup': (255, 215, 0),
    'text': (0, 0, 0),
    'border': (100, 100, 100),
    'safe_text': (0, 100, 0),
    'risky_text': (150, 0, 0),
    'human': (0, 0, 255),
    'ai': (255, 0, 0),
}
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PURPLE = (138, 43, 226)
DARK_GRAY = (128, 128, 128)

# fonts
FONT = pygame.font.SysFont('Arial', 14, bold=True)
SMALL_FONT = pygame.font.SysFont('Arial', 10)
LARGE_FONT = pygame.font.SysFont('Arial', 24, bold=True)

# screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Strategic Snakes & Ladders")
clock = pygame.time.Clock()
place_trap_button = pygame.Rect(WIDTH // 2 - 60, 60, 120, 30)

def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    surface.blit(text_obj, (x, y))

def draw_dice(surface, value, x, y):
    pygame.draw.rect(surface, BLACK, (x, y, 30, 30), border_radius=4)
    pygame.draw.rect(surface, WHITE, (x + 2, y + 2, 26, 26), border_radius=4)

    cx, cy = x+15, y+15
    offset= 7
    dots ={
        1: [(cx, cy)],
        2: [(cx - offset, cy - offset), (cx + offset, cy + offset)],
        3: [(cx - offset, cy - offset), (cx, cy), (cx + offset, cy + offset)],
        4: [(cx - offset, cy - offset), (cx + offset, cy - offset),
            (cx - offset, cy + offset), (cx + offset, cy + offset)],
        5: [(cx - offset, cy - offset), (cx + offset, cy - offset),
            (cx, cy),
            (cx - offset, cy + offset), (cx + offset, cy + offset)],
        6: [(cx - offset, cy - offset), (cx + offset, cy - offset),
            (cx - offset, cy), (cx + offset, cy),
            (cx - offset, cy + offset), (cx + offset, cy + offset)],
    }

    for dot in dots.get(value, []):
        pygame.draw.circle(surface, BLACK, dot, 3)

class Board:
    def __init__(self):
        self.tiles = {}
        self.snakes = {}
        self.ladders = {}
        self.powerups = []
        self.initialize_board()

    def initialize_board(self):
        for pos in range(1, 21):
            self.tiles[pos] = {'type': 'main', 'rect': None, 'connections': [pos + 1] if pos < 20 else []}

        for pos in range(21, 51):
            self.tiles[pos] = {'type': 'safe', 'rect': None, 'connections': [pos + 1] if pos < 50 else [51], 'display_num': f"{pos}A"}

        risky_path_bases = list(range(21, 50, 5))
        risky_path_tiles = list(range(101, 101 + len(risky_path_bases)))
        for i, pos in enumerate(risky_path_tiles):
            self.tiles[pos] = {'type': 'risky', 'rect': None, 'connections': [risky_path_tiles[i + 1]] if i < len(risky_path_tiles) - 1 else [51], 'display_num': f"{risky_path_bases[i]}B"}

        self.tiles[20]['connections'] = [21, 101]

        for pos in range(51, 101):
            self.tiles[pos] = {'type': 'main', 'rect': None, 'connections': [pos + 1] if pos < 100 else [], 'display_num': str(pos)}

        self.snakes = {16: 5, 47: 43, 88: 65, 35: 22, 45: 32, 101: 10, 103: 11, 104:30 , 106: 3, 98: 50}
        self.ladders = {6: 18, 23: 41, 79: 91, 21: 33, 30: 45, 40: 60, 25: 40, 58: 70, 66: 78}
        self.powerups = [7, 17, 29, 36, 44, 57, 66, 77, 84, 95]

    def draw(self):
        screen.fill(COLORS['background'])
        for pos, tile in self.tiles.items():
            color = COLORS[f"{tile['type']}_path"]
            row, col = self.calculate_position(pos)
            x = col * CELL_SIZE
            y = row * CELL_SIZE + TOP_PANEL_HEIGHT
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            tile['rect'] = rect
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, COLORS['border'], rect, 1)
            text_color = COLORS['text']
            if tile['type'] == 'safe': text_color = COLORS['safe_text']
            elif tile['type'] == 'risky': text_color = COLORS['risky_text']
            text = FONT.render(tile.get('display_num', str(pos)), True, text_color)
            screen.blit(text, text.get_rect(center=rect.center))
        self.draw_connections()
        self.draw_powerups()

    def draw_connections(self):
        for start, end in self.snakes.items():
            if start in self.tiles and end in self.tiles:
                self.draw_line_arrow(self.tiles[start]['rect'].center, self.tiles[end]['rect'].center, COLORS['snake'])
        for start, end in self.ladders.items():
            if start in self.tiles and end in self.tiles:
                self.draw_line_arrow(self.tiles[start]['rect'].center, self.tiles[end]['rect'].center, COLORS['ladder'])

    def draw_line_arrow(self, start, end, color):
        pygame.draw.line(screen, color, start, end, 4)
        self.draw_arrow(end, start, color)

    def draw_arrow(self, end, start, color):
        dx= end[0] - start[0]
        dy =end[1] - start[1]
        angle= math.atan2(-dy, dx)
        size = 8
        points =[
            end,
            (end[0] + size * math.cos(angle + math.pi / 6), end[1] - size * math.sin(angle + math.pi / 6)),
            (end[0] + size * math.cos(angle - math.pi / 6), end[1] - size * math.sin(angle - math.pi / 6))
        ]
        pygame.draw.polygon(screen, color, points)
    
    def draw_powerups(self):
        for pos in self.powerups:
            if pos in self.tiles:
                rect = self.tiles[pos]['rect']
                if rect:
                    pygame.draw.circle(screen, COLORS['powerup'], rect.center, CELL_SIZE // 4)
                    text = SMALL_FONT.render("P", True, COLORS['text'])
                    screen.blit(text, text.get_rect(center=rect.center))

        # Draw placed traps for each player
        for pos in ai.traps_placed:
            if pos in self.tiles:
                rect = self.tiles[pos]['rect']
                if rect:
                    pygame.draw.rect(screen, COLORS['ai'], rect)
                    text = SMALL_FONT.render("T", True, COLORS['text'])
                    screen.blit(text, text.get_rect(center=rect.center))
        for pos in human.traps_placed :
            if pos in self.tiles:
                rect = self.tiles[pos]['rect']
                if rect:
                    pygame.draw.rect(screen, COLORS['human'], rect)
                    text = SMALL_FONT.render("T", True, COLORS['text'])
                    screen.blit(text, text.get_rect(center=rect.center))

    def calculate_position(self, pos):
        if pos <= 20:
            row = 11 - ((pos - 1) // MAIN_COLS)
            col = (pos - 1) % MAIN_COLS
            if ((pos - 1) // MAIN_COLS) % 2 == 1:
                col = MAIN_COLS - 1 - col
            return row, col + PATH_COLS + 1
        elif 21 <= pos <= 50:
            row= 10 - (pos - 21) // 5
            col =((pos - 21) % 5)
            return row, col + 1
        elif pos >=101:
            index =pos - 101
            row = 10 -index
            col = MAIN_COLS+ PATH_COLS + 2
            return row,col
        else:
            offset = pos - 51
            row = 5 - (offset // MAIN_COLS)
            col = offset % MAIN_COLS
            if (offset // MAIN_COLS) % 2 == 1:
                col = MAIN_COLS - 1 - col
            return row, col + PATH_COLS + 1

    def draw_top_panel(self, human, ai, dice_value=None, rolling=False):
        pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, TOP_PANEL_HEIGHT))
        pygame.draw.line(screen, BLACK, (0, TOP_PANEL_HEIGHT), (WIDTH, TOP_PANEL_HEIGHT), 2)

        # human info left
        draw_text("HUMAN", FONT, COLORS['human'], screen, 20, 10)
        draw_text(f"Traps left: {human.traps_left}", FONT, BLACK, screen, 20, 40)
        if human_last_roll:
            draw_dice(screen, human_last_roll, 100, 10)

        # ai info right
        draw_text("AI", FONT, COLORS['ai'], screen, WIDTH - 100, 10)
        draw_text(f"Traps left: {ai.traps_left}", FONT, BLACK, screen, WIDTH - 130, 40)
        if ai_last_roll:
            draw_dice(screen, ai_last_roll, WIDTH - 140, 10)

        # rolling status
        if rolling:
            draw_text("Rolling...", FONT, BLACK, screen, WIDTH // 2 - 40, 35)

        # trap button
        pygame.draw.rect(screen, PURPLE if trap_mode else DARK_GRAY, place_trap_button)
        draw_text("Place Trap", FONT, WHITE, screen, place_trap_button.x + 10, place_trap_button.y + 10)


class Player:
    def __init__(self, name, color, is_ai=False):
        self.name =name
        self.color=color
        self.extra_roll = False
        self.is_ai = is_ai
        self.position= 1
        self.traps_left =2
        self.traps_placed = [] 
        self.snake_bites= 0

    def move(self, steps, board):
        if self.position <=100 and self.position+steps>=100:
            self.position=self.position+steps
            return True
        for _ in range(steps):
            if self.position in board.tiles:
                next_tiles = board.tiles[self.position]['connections']
                if self.position == 20:
                    if self.is_ai:
                        # Heuristic decision
                        safe_risk_score = self.evaluate_risk_vs_safe()
                        self.position = next_tiles[0] if safe_risk_score >= 0 else next_tiles[1]  
                    else:
                        choice = prompt_path_choice()
                        self.position = next_tiles[0] if choice == 'safe' else next_tiles[1]
                else:
                    self.position = next_tiles[0] if next_tiles else self.position
        
        if self.position in board.snakes:
            self.snake_bites=self.snake_bites+1
            self.position = board.snakes[self.position]
        elif self.position in board.ladders:
            self.position = board.ladders[self.position]

    def evaluate_risk_vs_safe(self):
        if self.is_ai and self.position < human.position - 5 and human.traps_placed not in range(101,107) and self.snake_bites < 5:
            return -1  # risky
        return 1  # safe


    def place_trap(self, position, board):
        if self.traps_left > 0 and position not in self.traps_placed and position != self.position:
            self.traps_placed.append(position)
            self.traps_left -= 1
            return True  # trap successful
        return False

    def draw_token(self, board):
        if self.position in board.tiles:
            center = board.tiles[self.position]['rect'].center
            pygame.draw.circle(screen, self.color, center, CELL_SIZE // 4)

def prompt_path_choice():
    popup = pygame.Surface((200, 100))
    popup.fill((240, 240, 240))
    pygame.draw.rect(popup, COLORS['border'], popup.get_rect(), 2)
    label = FONT.render("Choose Path:", True, COLORS['text'])
    safe_btn = pygame.Rect(30, 40, 60, 30)
    risky_btn = pygame.Rect(110, 40, 60, 30)
    popup.blit(label, (60, 10))
    pygame.draw.rect(popup, COLORS['safe_path'], safe_btn)
    pygame.draw.rect(popup, COLORS['risky_path'], risky_btn)
    popup.blit(FONT.render("Safe", True, COLORS['safe_text']), (safe_btn.x + 8, safe_btn.y + 5))
    popup.blit(FONT.render("Risky", True, COLORS['risky_text']), (risky_btn.x + 5, risky_btn.y + 5))
    screen.blit(popup, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if pygame.Rect(WIDTH // 2 - 70, HEIGHT // 2 - 10, 60, 30).collidepoint(mouse_pos): return 'safe'
                elif pygame.Rect(WIDTH // 2 + 10, HEIGHT // 2 - 10, 60, 30).collidepoint(mouse_pos): return 'risky'


def prompt_powerup_choice():
    popup = pygame.Surface((240, 120))
    popup.fill((240, 240, 240))
    pygame.draw.rect(popup, COLORS['border'], popup.get_rect(), 2)

    label = FONT.render("Choose Powerup:", True, COLORS['text'])
    erase_btn = pygame.Rect(30, 50, 80, 30)
    roll_btn = pygame.Rect(130, 50, 80, 30)

    popup.blit(label, (60, 10))
    pygame.draw.rect(popup, COLORS['safe_path'], erase_btn)
    pygame.draw.rect(popup, COLORS['risky_path'], roll_btn)

    popup.blit(FONT.render("Disarm", True, BLACK), (erase_btn.x + 10, erase_btn.y + 5))
    popup.blit(FONT.render("Extra Roll", True, BLACK), (roll_btn.x + 5, roll_btn.y + 5))

    screen.blit(popup, (WIDTH // 2 - 120, HEIGHT // 2 - 60))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                abs_erase = pygame.Rect(WIDTH//2 - 120 + erase_btn.x, HEIGHT//2 - 60 + erase_btn.y, erase_btn.width, erase_btn.height)
                abs_roll = pygame.Rect(WIDTH//2 - 120 + roll_btn.x, HEIGHT//2 - 60 + roll_btn.y, roll_btn.width, roll_btn.height)
                if abs_erase.collidepoint(mouse_pos):
                    return "erase"
                elif abs_roll.collidepoint(mouse_pos):
                    return "extra"


def handle_trap_placement(current_player):
    mouse_pos = pygame.mouse.get_pos()
    for pos, tile in board.tiles.items():
        rect = tile['rect']
        if rect.collidepoint(mouse_pos):
            if current_player.place_trap(pos, board):
                return True
    return False

def should_place_trap(ai, human, board):
    if ai.traps_left ==0:
        return False

    human_distance = human.position - ai.position

    if human.position <20:
        return False

    if human_distance< 3 or human_distance > 20:
        return False

    if human.position >= 95:
        return False

    for snake_head in board.snakes:
        if human.position < snake_head <= human.position + 6:
            return False
    return True


# game loop
board = Board()
human = Player("Human", COLORS['human'])
ai = Player("AI", COLORS['ai'], is_ai=True)
players = [human, ai]
current_index = 0
dice_value = None
human_last_roll = None
ai_last_roll = None
rolling = False
game_over = False
trap_mode = False
ai_skip_turn = False
human_skip_turn = False

while True:
    screen.fill(WHITE)
    board.draw()
    board.draw_top_panel(human, ai, dice_value, rolling)
    for p in players:
        p.draw_token(board)

    if pygame.mouse.get_pressed()[0] and not rolling and not game_over:
        mouse_pos = pygame.mouse.get_pos()

        # Toggle trap mode
        if place_trap_button.collidepoint(mouse_pos) and current_index == 0:
            if players[current_index].traps_left==0:
                print('No traps left')
            else:    
                trap_mode = not trap_mode

        elif trap_mode and current_index == 0:
            if handle_trap_placement(human):
                trap_mode = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN and not rolling and not game_over:
            if current_index == 0:
                if human_skip_turn:
                    print("Human's turn is skipped due to trap!")
                    human_skip_turn = False
                    current_index = 1
                else:
                    dice_value = random.randint(1, 6)
                    rolling = True
                    human_last_roll = dice_value
                    pygame.time.delay(500)
                    game_over= human.move(dice_value, board)
                    rolling = False
                    pygame.display.update()


                    if human.position in ai.traps_placed:
                        ai.traps_placed.remove(human.position) 
                        human_skip_turn = True
                        print("Human stepped on AI's trap!")

                    if players[current_index].position in board.powerups:
                        choice = prompt_powerup_choice()
                        if choice == "erase":
                            players[1].traps_placed.clear()
                            print(' Ai Traps cleared')
                        elif choice == "extra":
                            human.extra_roll = True
                            print('Extra roll for human')

                    if human.extra_roll:
                        human.extra_roll = False
                        continue
                    else:
                        current_index = 1


    if current_index == 1 and not rolling and not game_over:
        if ai_skip_turn:
            print("AI's turn is skipped due to trap!")
            ai_skip_turn = False
            current_index = 0
        else:
            dice_value = random.randint(1, 6)
            ai_last_roll = dice_value
            rolling = True
            pygame.time.delay(500)
            game_over = ai.move(dice_value, board)
            rolling = False

            # check if ai landed on human trap
            if ai.position in human.traps_placed:
                human.traps_placed.remove(ai.position)
                ai_skip_turn = True
                print("AI stepped on Human's trap!")

            # placing trap by ai
            if should_place_trap(ai, human, board):
                for offset in range(3, 7):  # check tiles 3 to 6 ahead of human
                    trap_pos = human.position + offset
                    if trap_pos in board.tiles and trap_pos not in ai.traps_placed:
                        if trap_pos not in board.snakes and trap_pos not in board.powerups:
                            ai.place_trap(trap_pos, board)
                            print(f"AI placed trap at tile {trap_pos}")
                            break


            if players[current_index].position in board.powerups:
                #disarm if >1 traps ahead
                if any(t > ai.position for t in human.traps_placed):
                    human.traps_placed.clear()
                    print("AI removed your traps!")
                else:
                    ai.extra_roll = True
                    print("AI gained an extra roll!")
            
            if ai.extra_roll:
                ai.extra_roll=False
                continue
            else:
                current_index = 0


    if game_over:
        win_text = LARGE_FONT.render(
            "Human Wins!" if human.position >= 100 else "AI Wins!",
            True,
            COLORS['human'] if human.position >= 100 else COLORS['ai']
        )
        screen.blit(win_text, (WIDTH // 2 - 80, 10))
        pygame.display.flip()
        pygame.time.delay(3000)
        break

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
sys.exit()
