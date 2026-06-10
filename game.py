import pygame

from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from game_context import GameContext
from states.main_menu import MainMenu
from utils.assets_manager import AssetsManager

from utils.cursor_manager import CursorManager


class Game:
    screen: pygame.surface.Surface
    clock: pygame.time.Clock
    fps: int    # Nombre de frames par seconde
    running: bool
    dt: float   # Delta time, représente le temps qui s'écoule entre 2 frames (n'a pas été utilisé, mais pourrait l'être pour ajouter des animations visuelles)

    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("Miaouno")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.fps = 240
        self.running = False

        # Load fonts
        AssetsManager.load_font("lilita_one_s", 12,"LilitaOne-Regular.ttf")
        AssetsManager.load_font("lilita_one_m", 25, "LilitaOne-Regular.ttf")
        AssetsManager.load_font("lilita_one_l", 50, "LilitaOne-Regular.ttf")
        AssetsManager.load_font("lilita_one_xl", 65, "LilitaOne-Regular.ttf")

        # Load icons
        AssetsManager.load_image("arrow_back", "icons/arrow_back.svg", 0.1)

        # Load card symbol
        AssetsManager.load_image("0", "0.png", 0.25)
        AssetsManager.load_image("1", "1.png", 0.25)
        AssetsManager.load_image("2", "2.png", 0.25)
        AssetsManager.load_image("3", "3.png", 0.25)
        AssetsManager.load_image("4", "4.png", 0.25)
        AssetsManager.load_image("5", "5.png", 0.25)
        AssetsManager.load_image("6", "6.png", 0.25)
        AssetsManager.load_image("7", "7.png", 0.25)
        AssetsManager.load_image("8", "8.png", 0.25)
        AssetsManager.load_image("9", "9.png", 0.25)
        AssetsManager.load_image("skip", "skip.png", 0.25)
        AssetsManager.load_image("reverse", "reverse.png", 0.25)
        AssetsManager.load_image("+2", "+2.png", 0.25)
        AssetsManager.load_image("wild", "wild.png", 0.25)
        AssetsManager.load_image("+4", "+4.png", 0.25)
        AssetsManager.load_image("verso", "verso.png", 0.25)

        # Load game symbol
        AssetsManager.load_image("uno", "uno.png", 0.25)
        AssetsManager.load_image("contre_uno", "contre_uno.png", 0.25)
        AssetsManager.load_image("clockwise", "clockwise.png", 0.2)
        AssetsManager.load_image("anticlockwise", "anticlockwise.png", 0.2)

        # Init custom cursors
        AssetsManager.load_image("cursor_paw_normal", "cursors/cursor_paw_normal.png", 0.3)
        AssetsManager.load_image("cursor_paw_pointer", "cursors/cursor_paw_pointer.png", 0.3)
        AssetsManager.load_image("forbiden_cursor_paw_pointer", "cursors/forbiden_cursor_paw_pointer.png", 0.3)
        pygame.mouse.set_visible(False)

        # Load logo
        AssetsManager.load_image("logo", "verso.png", 0.9)

        # Load victory / defeat
        AssetsManager.load_image("victory", "victory.png", 0.9)
        AssetsManager.load_image("defeat", "defeat.png", 0.9)

        self.game_context = GameContext()
        self.game_context.state_manager.push(MainMenu(self.game_context))

    def run(self):
        self.running = True
        while self.running:
            self.dt = self.clock.tick(self.fps) / 1000

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    self.game_context.stop_session()

            if self.game_context.state_manager.is_empty():
                self.running = False

            if not self.running:
                break

            CursorManager.reset()

            current_game_state = self.game_context.state_manager.current_state()
            current_game_state.update(events, self.dt)
            current_game_state.render(self.screen)

            # Affichage du curseur custom
            cursor = AssetsManager.get_image(CursorManager.state.value)
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.screen.blit(cursor, (mouse_x - cursor.get_width() / 4, mouse_y - cursor.get_height() / 4))

            pygame.display.flip()

