import random
import math

from kivy.app import App
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import ScreenManager, Screen

Window.clearcolor = (0.035, 0.035, 0.045, 1)


class MayorXO(App):

    def build(self):
        self.player_score = 0
        self.cpu_score = 0
        self.draws = 0
        self.difficulty = "Medium"

        self.manager = ScreenManager()
        self.create_home()
        self.create_game()

        return self.manager

    def create_home(self):
        screen = Screen(name="home")

        layout = BoxLayout(
            orientation="vertical",
            padding=25,
            spacing=20
        )

        layout.add_widget(WidgetSpacer())

        title = Label(
            text="[b]MAYOR[/b] [color=ff3030]XO[/color]",
            markup=True,
            font_size=42,
            size_hint_y=0.25
        )

        subtitle = Label(
            text="THE ULTIMATE XO CHALLENGE",
            font_size=14,
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=0.12
        )

        layout.add_widget(title)
        layout.add_widget(subtitle)

        start = Button(
            text="PLAY GAME",
            font_size=22,
            bold=True,
            size_hint_y=0.17,
            background_normal="",
            background_color=(0.8, 0.04, 0.08, 1)
        )

        start.bind(on_release=self.start_game)
        layout.add_widget(start)

        info = Label(
            text="CHALLENGE THE COMPUTER\n"
                 "3 DIFFICULTY LEVELS",
            font_size=14,
            halign="center",
            size_hint_y=0.17
        )

        layout.add_widget(info)
        layout.add_widget(WidgetSpacer())

        screen.add_widget(layout)
        self.manager.add_widget(screen)

    def create_game(self):
        screen = Screen(name="game")

        root = BoxLayout(
            orientation="vertical",
            padding=14,
            spacing=9
        )

        header = BoxLayout(
            size_hint_y=0.12
        )

        back = Button(
            text="HOME",
            size_hint_x=0.25,
            background_normal="",
            background_color=(0.25, 0.05, 0.07, 1)
        )

        back.bind(
            on_release=lambda instance:
            self.manager.switch_to(
                self.manager.get_screen("home")
            )
        )

        title = Label(
            text="[b]MAYOR [color=ff3030]XO[/color][/b]",
            markup=True,
            font_size=24
        )

        header.add_widget(back)
        header.add_widget(title)
        root.add_widget(header)

        self.status = Label(
            text="YOUR TURN — YOU ARE X",
            font_size=17,
            size_hint_y=0.08
        )

        root.add_widget(self.status)

        self.score = Label(
            text="YOU 0   |   CPU 0   |   DRAW 0",
            font_size=15,
            size_hint_y=0.08
        )

        root.add_widget(self.score)

        self.level = Spinner(
            text="Medium",
            values=("Easy", "Medium", "Impossible"),
            size_hint_y=0.09,
            background_normal="",
            background_color=(0.55, 0.03, 0.07, 1)
        )

        self.level.bind(
            text=self.change_difficulty
        )

        root.add_widget(self.level)

        self.board = [""] * 9
        self.buttons = []
        self.game_over = False

        grid = GridLayout(
            cols=3,
            spacing=7,
            size_hint_y=0.57
        )

        for i in range(9):
            button = Button(
                text="",
                font_size=45,
                bold=True,
                background_normal="",
                background_color=(0.12, 0.12, 0.15, 1)
            )

            button.bind(
                on_release=lambda btn, pos=i:
                self.player_move(pos)
            )

            self.buttons.append(button)
            grid.add_widget(button)

        root.add_widget(grid)

        controls = BoxLayout(
            spacing=8,
            size_hint_y=0.12
        )

        restart = Button(
            text="NEW GAME",
            background_normal="",
            background_color=(0.7, 0.03, 0.07, 1)
        )

        restart.bind(
            on_release=self.reset_game
        )

        controls.add_widget(restart)
        root.add_widget(controls)

        screen.add_widget(root)
        self.manager.add_widget(screen)

    def start_game(self, instance):
        self.reset_game(None)
        self.manager.current = "game"

    def change_difficulty(self, spinner, text):
        self.difficulty = text

    def player_move(self, pos):
        if self.game_over or self.board[pos] != "":
            return

        self.board[pos] = "X"

        button = self.buttons[pos]
        button.text = "X"
        button.color = (1, 0.2, 0.25, 1)

        Animation(
            font_size=55,
            duration=0.12
        ).start(button)

        if self.check_result():
            return

        self.status.text = "CPU IS THINKING..."

        Clock.schedule_once(
            self.computer_move, 0.3
        )

    def computer_move(self, dt):
        if self.game_over:
            return

        empty = [
            i for i in range(9)
            if self.board[i] == ""
        ]

        if not empty:
            return

        if self.difficulty == "Easy":
            move = random.choice(empty)

        elif self.difficulty == "Medium":
            move = self.find_move("O")

            if move is None:
                move = self.find_move("X")

            if move is None:
                move = random.choice(empty)

        else:
            _, move = self.minimax(
                self.board[:], True, 0
            )

        if move is None:
            return

        self.board[move] = "O"

        button = self.buttons[move]
        button.text = "O"
        button.color = (1, 0.65, 0.2, 1)

        Animation(
            font_size=55,
            duration=0.12
        ).start(button)

        if not self.check_result():
            self.status.text = "YOUR TURN — YOU ARE X"

    def find_move(self, symbol):
        wins = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6)
        ]

        for a, b, c in wins:
            line = [
                self.board[a],
                self.board[b],
                self.board[c]
            ]

            if (
                line.count(symbol) == 2
                and line.count("") == 1
            ):
                for p in (a, b, c):
                    if self.board[p] == "":
                        return p

        return None

    def minimax(self, board, maximizing, depth):
        result = self.evaluate(board)

        if result is not None:
            if result == 1:
                return 10 - depth, None
            if result == -1:
                return depth - 10, None
            return 0, None

        empty = [
            i for i in range(9)
            if board[i] == ""
        ]

        if maximizing:
            best_score = -math.inf
            best_move = None

            for move in empty:
                board[move] = "O"

                score, _ = self.minimax(
                    board, False, depth + 1
                )

                board[move] = ""

                if score > best_score:
                    best_score = score
                    best_move = move

            return best_score, best_move

        best_score = math.inf
        best_move = None

        for move in empty:
            board[move] = "X"

            score, _ = self.minimax(
                board, True, depth + 1
            )

            board[move] = ""

            if score < best_score:
                best_score = score
                best_move = move

        return best_score, best_move

    def evaluate(self, board):
        wins = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6)
        ]

        for a, b, c in wins:
            if (
                board[a] != ""
                and board[a] == board[b]
                and board[b] == board[c]
            ):
                return 1 if board[a] == "O" else -1

        if "" not in board:
            return 0

        return None

    def check_result(self):
        result = self.evaluate(self.board)

        if result is None:
            return False

        self.game_over = True

        if result == 1:
            self.cpu_score += 1
            self.status.text = "CPU WINS!"

        elif result == -1:
            self.player_score += 1
            self.status.text = "MAYOR WINS!"

        else:
            self.draws += 1
            self.status.text = "IT'S A DRAW!"

        self.score.text = (
            f"YOU {self.player_score}   |   "
            f"CPU {self.cpu_score}   |   "
            f"DRAW {self.draws}"
        )

        return True

    def reset_game(self, instance):
        self.board = [""] * 9
        self.game_over = False

        for button in self.buttons:
            button.text = ""
            button.font_size = 45
            button.color = (1, 1, 1, 1)

        self.status.text = "YOUR TURN — YOU ARE X"


class WidgetSpacer(BoxLayout):
    pass


MayorXO().run()