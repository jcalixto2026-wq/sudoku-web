import asyncio
import copy
import random
import time
import pygame

WIDTH = 540
HEIGHT = 960
FPS = 60

BOARD_X = 18
BOARD_Y = 128
BOARD_SIZE = 504
CELL_SIZE = BOARD_SIZE // 9

# Colores
BG_TOP = (14, 21, 43)
BG_BOTTOM = (38, 31, 72)
PANEL = (25, 34, 65)
PANEL_2 = (35, 46, 82)
WHITE = (246, 248, 255)
TEXT_SOFT = (197, 208, 235)
BLUE = (82, 154, 255)
BLUE_DARK = (42, 95, 180)
CYAN = (87, 218, 226)
GREEN = (103, 222, 150)
YELLOW = (255, 213, 91)
RED = (244, 91, 111)
GRID_LIGHT = (109, 126, 167)
GRID_DARK = (218, 226, 247)
CELL_FIXED = (31, 43, 79)
CELL_SELECTED = (66, 111, 180)
CELL_RELATED = (42, 57, 94)
CELL_SAME = (49, 85, 124)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku")
clock = pygame.time.Clock()

FONT_SMALL = pygame.font.Font(None, 28)
FONT_BODY = pygame.font.Font(None, 34)
FONT_MEDIUM = pygame.font.Font(None, 42)
FONT_NUMBER = pygame.font.Font(None, 45)
FONT_BIG = pygame.font.Font(None, 72)
FONT_TITLE = pygame.font.Font(None, 98)

PUZZLES = {
    "Facil": [
        (
            "530070000"
            "600195000"
            "098000060"
            "800060003"
            "400803001"
            "700020006"
            "060000280"
            "000419005"
            "000080079"
        ),
        (
            "200080300"
            "060070084"
            "030500209"
            "000105408"
            "000000000"
            "402706000"
            "301007040"
            "720040060"
            "004010003"
        ),
    ],
    "Medio": [
        (
            "000260701"
            "680070090"
            "190004500"
            "820100040"
            "004602900"
            "050003028"
            "009300074"
            "040050036"
            "703018000"
        ),
        (
            "000000000"
            "000003085"
            "001020000"
            "000507000"
            "004000100"
            "090000000"
            "500000073"
            "002010000"
            "000040009"
        ),
    ],
    "Dificil": [
        (
            "000000907"
            "000420180"
            "000705026"
            "100904000"
            "050000040"
            "000507009"
            "920108000"
            "034059000"
            "507000000"
        ),
        (
            "005300000"
            "800000020"
            "070010500"
            "400005300"
            "010070006"
            "003200080"
            "060500009"
            "004000030"
            "000009700"
        ),
    ],
}


def draw_gradient(surface, top_color, bottom_color):
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        color = tuple(
            int(top_color[i] * (1 - ratio) + bottom_color[i] * ratio)
            for i in range(3)
        )
        pygame.draw.line(surface, color, (0, y), (WIDTH, y))


def draw_text_center(surface, text, font, color, center):
    image = font.render(text, True, color)
    rect = image.get_rect(center=center)
    surface.blit(image, rect)


def format_time(seconds):
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{minutes:02d}:{secs:02d}"


def string_to_board(puzzle):
    return [
        [int(puzzle[row * 9 + col]) for col in range(9)]
        for row in range(9)
    ]


def find_empty(board):
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                return row, col
    return None


def is_valid(board, row, col, number):
    if number in board[row]:
        return False

    for test_row in range(9):
        if board[test_row][col] == number:
            return False

    box_row = (row // 3) * 3
    box_col = (col // 3) * 3
    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            if board[r][c] == number:
                return False

    return True


def solve_board(board):
    empty = find_empty(board)
    if empty is None:
        return True

    row, col = empty
    for number in range(1, 10):
        if is_valid(board, row, col, number):
            board[row][col] = number
            if solve_board(board):
                return True
            board[row][col] = 0

    return False


class Button:
    def __init__(self, rect, text, font=FONT_MEDIUM):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font

    def draw(self, surface, fill=BLUE, border=WHITE, text_color=WHITE):
        shadow = self.rect.move(0, 5)
        pygame.draw.rect(surface, (8, 12, 28), shadow, border_radius=18)
        pygame.draw.rect(surface, fill, self.rect, border_radius=18)
        pygame.draw.rect(surface, border, self.rect, 3, border_radius=18)
        draw_text_center(surface, self.text, self.font, text_color, self.rect.center)

    def contains(self, pos):
        return self.rect.collidepoint(pos)


class SudokuGame:
    def __init__(self):
        self.state = "menu"
        self.difficulty = "Facil"
        self.original = [[0] * 9 for _ in range(9)]
        self.board = [[0] * 9 for _ in range(9)]
        self.solution = [[0] * 9 for _ in range(9)]
        self.selected = None
        self.mistakes = 0
        self.max_mistakes = 3
        self.start_time = 0.0
        self.end_time = None
        self.message = ""
        self.message_color = WHITE
        self.message_until = 0.0

        self.difficulty_buttons = [
            Button((92, 430, 356, 82), "FACIL"),
            Button((92, 535, 356, 82), "MEDIO"),
            Button((92, 640, 356, 82), "DIFICIL"),
        ]

        self.number_buttons = []
        button_size = 68
        gap = 12
        start_x = (WIDTH - (button_size * 3 + gap * 2)) // 2
        start_y = 696

        number = 1
        for row in range(3):
            for col in range(3):
                x = start_x + col * (button_size + gap)
                y = start_y + row * (button_size + gap)
                self.number_buttons.append(
                    (number, Button((x, y, button_size, button_size), str(number), FONT_NUMBER))
                )
                number += 1

        self.erase_button = Button((24, 882, 150, 54), "BORRAR", FONT_BODY)
        self.new_button = Button((190, 882, 156, 54), "NUEVO", FONT_BODY)
        self.menu_button = Button((362, 882, 154, 54), "MENU", FONT_BODY)

    def start_game(self, difficulty):
        self.difficulty = difficulty
        puzzle_text = random.choice(PUZZLES[difficulty])
        self.original = string_to_board(puzzle_text)
        self.board = copy.deepcopy(self.original)
        self.solution = copy.deepcopy(self.original)

        if not solve_board(self.solution):
            self.show_message("No se pudo preparar el tablero", RED, 3.0)
            self.state = "menu"
            return

        self.selected = self.find_first_empty()
        self.mistakes = 0
        self.start_time = time.monotonic()
        self.end_time = None
        self.message = ""
        self.state = "playing"

    def find_first_empty(self):
        for row in range(9):
            for col in range(9):
                if self.original[row][col] == 0:
                    return row, col
        return None

    def elapsed_time(self):
        if self.start_time == 0:
            return 0
        if self.end_time is not None:
            return self.end_time - self.start_time
        return time.monotonic() - self.start_time

    def show_message(self, text, color, seconds=1.0):
        self.message = text
        self.message_color = color
        self.message_until = time.monotonic() + seconds

    def is_complete(self):
        return all(self.board[row][col] != 0 for row in range(9) for col in range(9))

    def select_cell(self, pos):
        x, y = pos
        if not (
            BOARD_X <= x < BOARD_X + BOARD_SIZE
            and BOARD_Y <= y < BOARD_Y + BOARD_SIZE
        ):
            return False

        col = int((x - BOARD_X) // CELL_SIZE)
        row = int((y - BOARD_Y) // CELL_SIZE)
        self.selected = (row, col)
        return True

    def enter_number(self, number):
        if self.state != "playing" or self.selected is None:
            return

        row, col = self.selected
        if self.original[row][col] != 0:
            self.show_message("Esta casilla no se puede cambiar", TEXT_SOFT, 0.8)
            return

        if number == self.solution[row][col]:
            self.board[row][col] = number
            self.show_message("Correcto", GREEN, 0.55)

            if self.is_complete():
                self.end_time = time.monotonic()
                self.state = "won"
            else:
                self.move_to_next_empty()
        else:
            self.mistakes += 1
            self.show_message("Numero incorrecto", RED, 0.9)
            if self.mistakes >= self.max_mistakes:
                self.end_time = time.monotonic()
                self.state = "lost"

    def erase_selected(self):
        if self.state != "playing" or self.selected is None:
            return

        row, col = self.selected
        if self.original[row][col] == 0:
            self.board[row][col] = 0

    def move_to_next_empty(self):
        if self.selected is None:
            self.selected = self.find_first_empty()
            return

        start_index = self.selected[0] * 9 + self.selected[1]
        for offset in range(1, 82):
            index = (start_index + offset) % 81
            row = index // 9
            col = index % 9
            if self.original[row][col] == 0 and self.board[row][col] == 0:
                self.selected = (row, col)
                return

    def move_selection(self, row_delta, col_delta):
        if self.selected is None:
            self.selected = (0, 0)
            return

        row, col = self.selected
        self.selected = (
            max(0, min(8, row + row_delta)),
            max(0, min(8, col + col_delta)),
        )

    def handle_press(self, pos):
        if self.state == "menu":
            for index, button in enumerate(self.difficulty_buttons):
                if button.contains(pos):
                    self.start_game(("Facil", "Medio", "Dificil")[index])
                    return

        elif self.state == "playing":
            if self.select_cell(pos):
                return

            for number, button in self.number_buttons:
                if button.contains(pos):
                    self.enter_number(number)
                    return

            if self.erase_button.contains(pos):
                self.erase_selected()
            elif self.new_button.contains(pos):
                self.start_game(self.difficulty)
            elif self.menu_button.contains(pos):
                self.state = "menu"

        elif self.state in ("won", "lost"):
            if self.new_button.contains(pos):
                self.start_game(self.difficulty)
            elif self.menu_button.contains(pos):
                self.state = "menu"

    def handle_key(self, event):
        if event.key == pygame.K_ESCAPE:
            self.state = "menu"
            return

        if self.state == "menu":
            if event.key == pygame.K_1:
                self.start_game("Facil")
            elif event.key == pygame.K_2:
                self.start_game("Medio")
            elif event.key == pygame.K_3:
                self.start_game("Dificil")
            return

        if self.state != "playing":
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.start_game(self.difficulty)
            return

        if pygame.K_1 <= event.key <= pygame.K_9:
            self.enter_number(event.key - pygame.K_0)
        elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE, pygame.K_0):
            self.erase_selected()
        elif event.key == pygame.K_LEFT:
            self.move_selection(0, -1)
        elif event.key == pygame.K_RIGHT:
            self.move_selection(0, 1)
        elif event.key == pygame.K_UP:
            self.move_selection(-1, 0)
        elif event.key == pygame.K_DOWN:
            self.move_selection(1, 0)
        elif event.key == pygame.K_n:
            self.start_game(self.difficulty)

    def draw_header(self, surface):
        title = FONT_BIG.render("SUDOKU", True, WHITE)
        surface.blit(title, (22, 18))

        diff = FONT_BODY.render(self.difficulty.upper(), True, CYAN)
        surface.blit(diff, (25, 88))

        time_image = FONT_BODY.render(format_time(self.elapsed_time()), True, WHITE)
        time_rect = time_image.get_rect(topright=(WIDTH - 24, 26))
        surface.blit(time_image, time_rect)

        errors = FONT_SMALL.render(
            f"Errores: {self.mistakes}/{self.max_mistakes}",
            True,
            RED if self.mistakes else TEXT_SOFT,
        )
        errors_rect = errors.get_rect(topright=(WIDTH - 24, 73))
        surface.blit(errors, errors_rect)

    def draw_board(self, surface):
        selected_number = None
        if self.selected is not None:
            selected_number = self.board[self.selected[0]][self.selected[1]]

        for row in range(9):
            for col in range(9):
                rect = pygame.Rect(
                    BOARD_X + col * CELL_SIZE,
                    BOARD_Y + row * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE,
                )

                fill = PANEL
                if self.original[row][col] != 0:
                    fill = CELL_FIXED

                if self.selected is not None:
                    selected_row, selected_col = self.selected
                    same_box = (
                        row // 3 == selected_row // 3
                        and col // 3 == selected_col // 3
                    )
                    if row == selected_row or col == selected_col or same_box:
                        fill = CELL_RELATED

                    if (
                        selected_number not in (None, 0)
                        and self.board[row][col] == selected_number
                    ):
                        fill = CELL_SAME

                    if (row, col) == self.selected:
                        fill = CELL_SELECTED

                pygame.draw.rect(surface, fill, rect)

                number = self.board[row][col]
                if number != 0:
                    color = WHITE if self.original[row][col] != 0 else CYAN
                    image = FONT_NUMBER.render(str(number), True, color)
                    image_rect = image.get_rect(center=rect.center)
                    surface.blit(image, image_rect)

        for index in range(10):
            width = 4 if index % 3 == 0 else 1
            color = GRID_DARK if index % 3 == 0 else GRID_LIGHT
            x = BOARD_X + index * CELL_SIZE
            y = BOARD_Y + index * CELL_SIZE

            pygame.draw.line(
                surface,
                color,
                (x, BOARD_Y),
                (x, BOARD_Y + BOARD_SIZE),
                width,
            )
            pygame.draw.line(
                surface,
                color,
                (BOARD_X, y),
                (BOARD_X + BOARD_SIZE, y),
                width,
            )

    def draw_message(self, surface):
        if self.message and time.monotonic() < self.message_until:
            draw_text_center(
                surface,
                self.message,
                FONT_SMALL,
                self.message_color,
                (WIDTH // 2, 660),
            )

    def draw_number_pad(self, surface):
        for number, button in self.number_buttons:
            fill = BLUE_DARK

            completed_count = sum(
                1
                for row in range(9)
                for col in range(9)
                if self.board[row][col] == number
            )
            if completed_count >= 9:
                fill = PANEL_2

            button.draw(surface, fill=fill, border=GRID_LIGHT)

        self.erase_button.draw(surface, fill=PANEL_2, border=GRID_LIGHT)
        self.new_button.draw(surface, fill=BLUE_DARK, border=GRID_LIGHT)
        self.menu_button.draw(surface, fill=PANEL_2, border=GRID_LIGHT)

    def draw_menu(self, surface):
        draw_text_center(surface, "SUDOKU", FONT_TITLE, WHITE, (WIDTH // 2, 210))
        draw_text_center(
            surface,
            "Elige una dificultad",
            FONT_MEDIUM,
            TEXT_SOFT,
            (WIDTH // 2, 330),
        )

        colors = (GREEN, BLUE, RED)
        for button, color in zip(self.difficulty_buttons, colors):
            button.draw(surface, fill=color, border=WHITE)

        draw_text_center(
            surface,
            "Toca una casilla y luego un numero",
            FONT_SMALL,
            TEXT_SOFT,
            (WIDTH // 2, 815),
        )
        draw_text_center(
            surface,
            "Tambien funciona con teclado",
            FONT_SMALL,
            TEXT_SOFT,
            (WIDTH // 2, 855),
        )

    def draw_overlay(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((7, 11, 28, 222))
        surface.blit(overlay, (0, 0))

        if self.state == "won":
            title = "GANASTE"
            color = GREEN
            subtitle = "Sudoku completado"
        else:
            title = "FIN DEL JUEGO"
            color = RED
            subtitle = "Llegaste a 3 errores"

        draw_text_center(surface, title, FONT_BIG, color, (WIDTH // 2, 315))
        draw_text_center(
            surface,
            subtitle,
            FONT_MEDIUM,
            WHITE,
            (WIDTH // 2, 400),
        )
        draw_text_center(
            surface,
            f"Tiempo: {format_time(self.elapsed_time())}",
            FONT_MEDIUM,
            YELLOW,
            (WIDTH // 2, 470),
        )

        new_centered = Button((104, 575, 332, 78), "JUGAR OTRA VEZ")
        menu_centered = Button((104, 680, 332, 78), "VOLVER AL MENU")
        new_centered.draw(surface, fill=BLUE)
        menu_centered.draw(surface, fill=PANEL_2)

        self.overlay_new_button = new_centered
        self.overlay_menu_button = menu_centered

    def draw(self, surface):
        draw_gradient(surface, BG_TOP, BG_BOTTOM)

        for index in range(18):
            x = (index * 113 + 29) % WIDTH
            y = (index * 173 + 70) % HEIGHT
            pygame.draw.circle(surface, (82, 91, 139), (x, y), 2)

        if self.state == "menu":
            self.draw_menu(surface)
            return

        self.draw_header(surface)
        self.draw_board(surface)

        if self.state == "playing":
            self.draw_message(surface)
            self.draw_number_pad(surface)
        else:
            self.draw_overlay(surface)

    def process_event(self, event):
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:
            self.handle_key(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.state in ("won", "lost"):
                if hasattr(self, "overlay_new_button") and self.overlay_new_button.contains(event.pos):
                    self.start_game(self.difficulty)
                elif hasattr(self, "overlay_menu_button") and self.overlay_menu_button.contains(event.pos):
                    self.state = "menu"
            else:
                self.handle_press(event.pos)

        if event.type == pygame.FINGERDOWN:
            pos = (event.x * WIDTH, event.y * HEIGHT)
            if self.state in ("won", "lost"):
                if hasattr(self, "overlay_new_button") and self.overlay_new_button.contains(pos):
                    self.start_game(self.difficulty)
                elif hasattr(self, "overlay_menu_button") and self.overlay_menu_button.contains(pos):
                    self.state = "menu"
            else:
                self.handle_press(pos)

        return True


async def main():
    game = SudokuGame()
    running = True

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            running = game.process_event(event)
            if not running:
                break

        game.draw(screen)
        pygame.display.update()

        # Necesario para que Pygbag funcione dentro del navegador.
        await asyncio.sleep(0)

    pygame.quit()


asyncio.run(main())
