import time
import random
import os
import sys

if sys.platform == "win32":
    os.system("chcp 65001 > nul")

RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
DIM = "\033[2m"

class Board:
    def __init__(self):
        self.cells = [" " for _ in range(9)]

    def display(self, show_numbers=False):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\n  {BOLD}{CYAN}[ JOGO DA VELHA ]{RESET}\n")

        def format_cell(cell, index):
            if cell == "X":
                return f"{RED}{BOLD}X{RESET}"
            elif cell == "O":
                return f"{BLUE}{BOLD}O{RESET}"
            elif show_numbers:
                return f"{DIM}{index + 1}{RESET}"
            return " "

        print(f"       {DIM}1     2     3{RESET}")
        print(f"     +-----+-----+-----+")
        print(f"  A  |  {format_cell(self.cells[0], 0)}  |  {format_cell(self.cells[1], 1)}  |  {format_cell(self.cells[2], 2)}  |")
        print(f"     +-----+-----+-----+")
        print(f"  B  |  {format_cell(self.cells[3], 3)}  |  {format_cell(self.cells[4], 4)}  |  {format_cell(self.cells[5], 5)}  |")
        print(f"     +-----+-----+-----+")
        print(f"  C  |  {format_cell(self.cells[6], 6)}  |  {format_cell(self.cells[7], 7)}  |  {format_cell(self.cells[8], 8)}  |")
        print(f"     +-----+-----+-----+")
        print()

    def display_with_hint(self, move):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\n  {BOLD}{CYAN}[ JOGO DA VELHA ]{RESET}\n")

        def format_cell(cell, index):
            if cell == "X":
                return f"{RED}{BOLD}X{RESET}"
            elif cell == "O":
                return f"{BLUE}{BOLD}O{RESET}"
            elif index == move:
                return f"{GREEN}{BOLD}*{RESET}"
            return " "

        print(f"       {DIM}1     2     3{RESET}")
        print(f"     +-----+-----+-----+")
        print(f"  A  |  {format_cell(self.cells[0], 0)}  |  {format_cell(self.cells[1], 1)}  |  {format_cell(self.cells[2], 2)}  |")
        print(f"     +-----+-----+-----+")
        print(f"  B  |  {format_cell(self.cells[3], 3)}  |  {format_cell(self.cells[4], 4)}  |  {format_cell(self.cells[5], 5)}  |")
        print(f"     +-----+-----+-----+")
        print(f"  C  |  {format_cell(self.cells[6], 6)}  |  {format_cell(self.cells[7], 7)}  |  {format_cell(self.cells[8], 8)}  |")
        print(f"     +-----+-----+-----+")
        print()

    def update(self, position, marker):
        if self.cells[position] == " ":
            self.cells[position] = marker
            return True
        return False

    def is_winner(self, marker):
        win_conditions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
        for condition in win_conditions:
            if all(self.cells[i] == marker for i in condition):
                return condition
        return False

    def is_full(self):
        return " " not in self.cells

    def can_win(self):
        win_conditions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
        for condition in win_conditions:
            x_count = sum(1 for i in condition if self.cells[i] == "X")
            o_count = sum(1 for i in condition if self.cells[i] == "O")
            if x_count == 0 or o_count == 0:
                return True
        return False

    def get_available_moves(self):
        return [i for i, cell in enumerate(self.cells) if cell == " "]

    def reset(self):
        self.cells = [" " for _ in range(9)]

class Player:
    def __init__(self, name, marker):
        self.name = name
        self.marker = marker
        self.wins = 0

class HumanPlayer(Player):
    def get_move(self, board):
        while True:
            try:
                move = input(f"{BOLD}{self.name}{RESET} ({self.marker}), escolha sua posicao: ").strip().upper()
                if move in ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']:
                    pos_map = {'A1': 0, 'A2': 1, 'A3': 2, 'B1': 3, 'B2': 4, 'B3': 5, 'C1': 6, 'C2': 7, 'C3': 8}
                    pos = pos_map[move]
                    if board.cells[pos] == " ":
                        return pos
                    print(f"{RED}  [X] Posicao ja ocupada!{RESET}")
                elif move in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                    pos = int(move) - 1
                    if board.cells[pos] == " ":
                        return pos
                    print(f"{RED}  [X] Posicao ja ocupada!{RESET}")
                else:
                    print(f"{RED}  [X] Posicao invalida! Use A1-C3 ou 1-9{RESET}")
            except ValueError:
                print(f"{RED}  [X] Entrada invalida!{RESET}")

class AIPlayer(Player):
    def __init__(self, name, marker, difficulty="medium"):
        super().__init__(name, marker)
        self.difficulty = difficulty

    def get_move(self, board):
        self.board = board
        move_labels = ['A1', 'B1', 'C1', 'A2', 'B2', 'C2', 'A3', 'B3', 'C3']

        if self.difficulty == "easy":
            time.sleep(0.5)
            return random.choice(board.get_available_moves())

        elif self.difficulty == "medium":
            move = self.minimax(board, self.marker)['position']
            time.sleep(0.8)
            print(f"{MAGENTA}  [*] Computador escolheu: {move_labels[move]}{RESET}")
            time.sleep(0.5)
            return move

        else:
            move = self.minimax(board, self.marker)['position']
            time.sleep(0.8)
            print(f"{MAGENTA}  [*] Computador (Dificil) escolheu: {move_labels[move]}{RESET}")
            time.sleep(0.5)
            return move

    def minimax(self, board, player, depth=0):
        available_moves = board.get_available_moves()
        opponent = "O" if player == "X" else "X"

        if board.is_winner(self.marker):
            return {'score': 10 - depth}
        elif board.is_winner(opponent):
            return {'score': depth - 10}
        elif board.is_full():
            return {'score': 0}

        if len(available_moves) == 9:
            return {'position': 4, 'score': 0}

        moves = []
        for move in available_moves:
            board.cells[move] = player
            result = self.minimax(board, opponent, depth + 1)
            result['position'] = move
            board.cells[move] = " "
            moves.append(result)

        if player == self.marker:
            best = max(moves, key=lambda x: x['score'])
        else:
            best = min(moves, key=lambda x: x['score'])

        return best

class TicTacToeGame:
    def __init__(self, player1, player2):
        self.board = Board()
        self.players = [player1, player2]
        self.current_player_idx = 0
        self.moves_count = 0

    def play_round(self):
        self.board.reset()
        self.current_player_idx = 0
        self.moves_count = 0

        self._print_round_start()

        while True:
            self.board.display(show_numbers=True)
            self._print_score()

            current_player = self.players[self.current_player_idx]
            marker = f"{RED}X{RESET}" if current_player.marker == "X" else f"{BLUE}O{RESET}"
            print(f"\n  {BOLD}[>] Vez de {current_player.name} {marker}{RESET}")

            move = current_player.get_move(self.board)
            self.moves_count += 1

            self.board.display_with_hint(move)
            time.sleep(0.3)
            self.board.update(move, current_player.marker)

            win_line = self.board.is_winner(current_player.marker)
            if win_line:
                self.board.display()
                self._print_victory(current_player, win_line)
                return current_player

            if not self.board.can_win():
                self.board.display()
                self._print_draw()
                return None

            self.current_player_idx = 1 - self.current_player_idx

    def _print_round_start(self):
        print(f"\n  {CYAN}{'=' * 35}{RESET}")
        print(f"  {BOLD}         INICIANDO RODADA{RESET}")
        print(f"  {CYAN}{'=' * 35}{RESET}")
        time.sleep(1)

    def _print_score(self):
        p1 = self.players[0]
        p2 = self.players[1]
        print(f"\n  {BOLD}[ PLACAR ]{RESET}")
        print(f"  {RED}{p1.name}{RESET}: {GREEN}{p1.wins}{RESET}  |  {BLUE}{p2.name}{RESET}: {GREEN}{p2.wins}{RESET}")

    def _print_victory(self, winner, win_line):
        labels = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']
        line_str = " -> ".join(labels[i] for i in win_line)
        color = RED if winner.marker == "X" else BLUE

        print(f"\n  {color}{BOLD}==================================={RESET}")
        print(f"  {color}{BOLD}    PARABENS! {winner.name} VENCEU!{RESET}")
        print(f"  {color}{BOLD}==================================={RESET}")
        print(f"\n  {YELLOW}Linha vencedora: {line_str}{RESET}")
        print(f"  {DIM}Jogadas: {self.moves_count}{RESET}")
        winner.wins += 1

    def _print_draw(self):
        print(f"\n  {YELLOW}{BOLD}==================================={RESET}")
        print(f"  {YELLOW}{BOLD}           EMPATE!{RESET}")
        print(f"  {YELLOW}{BOLD}==================================={RESET}")
        print(f"\n  {DIM}Jogadas: {self.moves_count}{RESET}")

class SeriesManager:
    def __init__(self):
        self.total_games_played = 0

    def main_menu(self):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            self._print_header()
            print(f"  {BOLD}1.{RESET} [H-H] Humano vs Humano")
            print(f"  {BOLD}2.{RESET} [H-?) Humano vs Computador (Facil)")
            print(f"  {BOLD}3.{RESET} [H-?] Humano vs Computador (Medio)")
            print(f"  {BOLD}4.{RESET} [H-?] Humano vs Computador (Dificil)")
            print(f"  {BOLD}5.{RESET} [i] Estatisticas")
            print(f"  {BOLD}0.{RESET} [X] Sair")
            print()

            choice = input(f"  {BOLD}[>] Escolha uma opcao:{RESET} ").strip()

            if choice == '1':
                self.start_series("HvH")
            elif choice == '2':
                self.start_series("HvC", "easy")
            elif choice == '3':
                self.start_series("HvC", "medium")
            elif choice == '4':
                self.start_series("HvC", "hard")
            elif choice == '5':
                self.show_stats()
            elif choice == '0':
                self._print_goodbye()
                break
            else:
                self._print_error()
                input()

    def _print_header(self):
        print(f"\n  {CYAN}==================================={RESET}")
        print(f"  {CYAN}{BOLD}     JOGO DA VELHA{RESET}")
        print(f"  {CYAN}==================================={RESET}\n")

    def _print_error(self):
        print(f"\n  {RED}[X] Opcao invalida!{RESET}")
        time.sleep(1)

    def _print_goodbye(self):
        print(f"\n  {GREEN}Obrigado por jogar! Até logo!{RESET}\n")

    def start_series(self, mode, difficulty="medium"):
        os.system('cls' if os.name == 'nt' else 'clear')

        if mode == "HvH":
            p1_name = self._get_name("Jogador 1")
            p2_name = self._get_name("Jogador 2")
            p1 = HumanPlayer(p1_name, "X")
            p2 = HumanPlayer(p2_name, "O")
        else:
            p1_name = self._get_name("Jogador")
            p1 = HumanPlayer(p1_name, "X")
            p2 = AIPlayer("Computador", "O", difficulty)

        wins_needed = 2
        rounds = 1

        while p1.wins < wins_needed and p2.wins < wins_needed:
            print(f"\n  {CYAN}{'-' * 40}{RESET}")
            print(f"  {BOLD}[>] RODADA {rounds}{RESET}")
            print(f"  {CYAN}{'-' * 40}{RESET}")

            game = TicTacToeGame(p1, p2)
            input(f"\n  {GREEN}Pressione ENTER para comecar...{RESET}")

            winner = game.play_round()
            self.total_games_played += 1

            if p1.wins < wins_needed and p2.wins < wins_needed:
                input(f"\n  {YELLOW}Pressione ENTER para proxima rodada...{RESET}")
            rounds += 1

        self._print_series_end(p1, p2)
        input(f"\n  {CYAN}Pressione ENTER para voltar ao menu...{RESET}")

    def _get_name(self, default):
        return input(f"\n  Nome do {default} (X): ").strip() or default

    def _print_series_end(self, p1, p2):
        winner = p1 if p1.wins >= 2 else p2
        color = RED if winner == p1 else BLUE

        print(f"\n  {color}{BOLD}==================================={RESET}")
        print(f"  {color}{BOLD}      VENCEDOR DA SERIE!{RESET}")
        print(f"  {color}{BOLD}==================================={RESET}")
        print(f"\n  {color}{BOLD}>> {winner.name} com 2 vitorias!{RESET}")
        print(f"\n  [ PLACAR FINAL ]")
        print(f"  {RED}{p1.name}{RESET}: {GREEN}{p1.wins}{RESET}")
        print(f"  {BLUE}{p2.name}{RESET}: {GREEN}{p2.wins}{RESET}")

    def show_stats(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\n  {YELLOW}{BOLD}==================================={RESET}")
        print(f"  {YELLOW}{BOLD}        ESTATISTICAS{RESET}")
        print(f"  {YELLOW}{BOLD}==================================={RESET}")
        print(f"\n  Partidas jogadas: {self.total_games_played}")
        input(f"\n  {CYAN}Pressione ENTER para voltar...{RESET}")

if __name__ == "__main__":
    manager = SeriesManager()
    manager.main_menu()
