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

class Lig4Board:
    ROWS = 6
    COLS = 7

    def __init__(self):
        self.grid = [[" " for _ in range(self.COLS)] for _ in range(self.ROWS)]
        self.last_move = None

    def display(self, show_numbers=True):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\n  {BOLD}{CYAN}[ LIG-4 - CONECTE 4 ]{RESET}\n")

        def format_cell(cell):
            if cell == "X": return f"{RED}{BOLD}X{RESET}"
            elif cell == "O": return f"{BLUE}{BOLD}O{RESET}"
            return " "

        if show_numbers:
            nums = "       " + "  ".join(f"{DIM}{i+1}{RESET}" for i in range(self.COLS))
            print(f"  {nums}")
            print(f"  {CYAN}+-----+-----+-----+-----+-----+-----+-----+{RESET}")
        else:
            print(f"  {CYAN}+-----+-----+-----+-----+-----+-----+-----+{RESET}")

        for r in range(self.ROWS):
            cells = " | ".join(format_cell(self.grid[r][c]) for c in range(self.COLS))
            print(f"  {CYAN}|{RESET} {cells} {CYAN}|{RESET}")
            print(f"  {CYAN}+-----+-----+-----+-----+-----+-----+-----+{RESET}")
        print()

    def display_with_hint(self, col):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\n  {BOLD}{CYAN}[ LIG-4 - CONECTE 4 ]{RESET}\n")

        def format_cell(cell):
            if cell == "X": return f"{RED}{BOLD}X{RESET}"
            elif cell == "O": return f"{BLUE}{BOLD}O{RESET}"
            return " "

        nums = "       " + "  ".join(f"{DIM}{i+1}{RESET}" for i in range(self.COLS))
        print(f"  {nums}")
        print(f"  {CYAN}+-----+-----+-----+-----+-----+-----+-----+{RESET}")

        for r in range(self.ROWS):
            cells = []
            for c in range(self.COLS):
                if self.last_move and r == self.last_move[0] and c == col:
                    cells.append(f"{GREEN}{BOLD}*{RESET}")
                else:
                    cells.append(format_cell(self.grid[r][c]))
            print(f"  {CYAN}|{RESET} {cells[0]} | {cells[1]} | {cells[2]} | {cells[3]} | {cells[4]} | {cells[5]} | {cells[6]} {CYAN}|{RESET}")
            print(f"  {CYAN}+-----+-----+-----+-----+-----+-----+-----+{RESET}")
        print()

    def drop_piece(self, col, marker):
        for row in reversed(range(self.ROWS)):
            if self.grid[row][col] == " ":
                self.grid[row][col] = marker
                self.last_move = (row, col)
                return True
        return False

    def get_available_row(self, col):
        for row in reversed(range(self.ROWS)):
            if self.grid[row][col] == " ":
                return row
        return -1

    def is_winner(self, marker):
        for r in range(self.ROWS):
            for c in range(self.COLS - 3):
                if all(self.grid[r][c+i] == marker for i in range(4)):
                    return [(r, c+i) for i in range(4)]
        for r in range(self.ROWS - 3):
            for c in range(self.COLS):
                if all(self.grid[r+i][c] == marker for i in range(4)):
                    return [(r+i, c) for i in range(4)]
        for r in range(3, self.ROWS):
            for c in range(self.COLS - 3):
                if all(self.grid[r-i][c+i] == marker for i in range(4)):
                    return [(r-i, c+i) for i in range(4)]
        for r in range(self.ROWS - 3):
            for c in range(self.COLS - 3):
                if all(self.grid[r+i][c+i] == marker for i in range(4)):
                    return [(r+i, c+i) for i in range(4)]
        return False

    def is_full(self):
        return all(self.grid[0][c] != " " for c in range(self.COLS))

    def get_available_moves(self):
        return [c for c in range(self.COLS) if self.grid[0][c] == " "]

    def can_win(self, marker):
        for c in self.get_available_moves():
            row = self.get_available_row(c)
            self.grid[row][c] = marker
            if self.is_winner(marker):
                self.grid[row][c] = " "
                return True
            self.grid[row][c] = " "
        return False

    def reset(self):
        self.grid = [[" " for _ in range(self.COLS)] for _ in range(self.ROWS)]
        self.last_move = None

class Player:
    def __init__(self, name, marker):
        self.name = name
        self.marker = marker
        self.wins = 0

class HumanPlayer(Player):
    def get_move(self, board):
        while True:
            try:
                col = int(input(f"{BOLD}{self.name}{RESET} ({self.marker}), escolha coluna (1-7): ")) - 1
                if 0 <= col < board.COLS:
                    if board.grid[0][col] == " ":
                        return col
                    print(f"{RED}  [X] Coluna cheia! Escolha outra.{RESET}")
                else:
                    print(f"{RED}  [X] Coluna invalida! Escolha 1-7.{RESET}")
            except ValueError:
                print(f"{RED}  [X] Entrada invalida! Digite 1-7.{RESET}")

class AIPlayer(Player):
    def __init__(self, name, marker, difficulty="medium"):
        super().__init__(name, marker)
        self.difficulty = difficulty

    def get_move(self, board):
        available = board.get_available_moves()

        if self.difficulty == "easy":
            time.sleep(0.5)
            return random.choice(available)

        elif self.difficulty == "medium":
            time.sleep(0.8)
            move = self._smart_move(board, available)
            if move is not None:
                print(f"{MAGENTA}  [*] Computador jogou na coluna {move + 1}{RESET}")
                time.sleep(0.5)
                return move
            return random.choice(available)

        else:
            time.sleep(0.8)
            move = self.minimax(board, 5, True)['column']
            print(f"{MAGENTA}  [*] Computador (Dificil) jogou na coluna {move + 1}{RESET}")
            time.sleep(0.5)
            return move

    def _smart_move(self, board, available):
        opponent = "O" if self.marker == "X" else "X"

        for col in available:
            row = board.get_available_row(col)
            board.grid[row][col] = self.marker
            if board.is_winner(self.marker):
                board.grid[row][col] = " "
                return col
            board.grid[row][col] = " "

        for col in available:
            row = board.get_available_row(col)
            board.grid[row][col] = opponent
            if board.is_winner(opponent):
                board.grid[row][col] = " "
                return col
            board.grid[row][col] = " "

        center = board.COLS // 2
        if center in available:
            return center

        return random.choice(available)

    def minimax(self, board, depth, is_maximizing):
        opponent = "O" if self.marker == "X" else "X"
        available = board.get_available_moves()

        if depth == 0 or board.is_full() or board.is_winner(self.marker) or board.is_winner(opponent):
            return {'score': self._evaluate(board), 'column': random.choice(available) if available else 0}

        if is_maximizing:
            best = {'score': -10000, 'column': random.choice(available)}
            for col in available:
                row = board.get_available_row(col)
                board.grid[row][col] = self.marker
                score = self.minimax(board, depth - 1, False)['score']
                board.grid[row][col] = " "
                if score > best['score']:
                    best = {'score': score, 'column': col}
            return best
        else:
            best = {'score': 10000, 'column': random.choice(available)}
            for col in available:
                row = board.get_available_row(col)
                board.grid[row][col] = opponent
                score = self.minimax(board, depth - 1, True)['score']
                board.grid[row][col] = " "
                if score < best['score']:
                    best = {'score': score, 'column': col}
            return best

    def _evaluate(self, board):
        opponent = "O" if self.marker == "X" else "X"
        if board.is_winner(self.marker): return 1000
        if board.is_winner(opponent): return -1000
        return self._count_threats(board)

    def _count_threats(self, board):
        score = 0
        for r in range(board.ROWS):
            for c in range(board.COLS):
                if board.grid[r][c] == self.marker:
                    score += self._eval_position(board, r, c)
                elif board.grid[r][c] == "O" if self.marker == "X" else "X":
                    score -= self._eval_position(board, r, c) // 2
        return score

    def _eval_position(self, board, r, c):
        count = 0
        directions = [(0,1), (1,0), (1,1), (1,-1)]
        for dr, dc in directions:
            consecutive = 0
            gaps = 0
            for i in range(4):
                nr, nc = r + dr*i, c + dc*i
                if 0 <= nr < board.ROWS and 0 <= nc < board.COLS:
                    if board.grid[nr][nc] == self.marker:
                        consecutive += 1
                    elif board.grid[nr][nc] == " ":
                        gaps += 1
            if consecutive >= 2:
                count += consecutive * 2
        return count

class Lig4Game:
    def __init__(self, p1, p2):
        self.board = Lig4Board()
        self.players = [p1, p2]
        self.current_idx = 0
        self.moves_count = 0

    def play_round(self):
        self.board.reset()
        self.current_idx = 0
        self.moves_count = 0

        self._print_round_start()

        while True:
            self.board.display()
            self._print_score()

            player = self.players[self.current_idx]
            marker = f"{RED}X{RESET}" if player.marker == "X" else f"{BLUE}O{RESET}"
            print(f"  {BOLD}[>] Vez de {player.name} {marker}{RESET}")

            col = player.get_move(self.board)
            self.moves_count += 1

            self.board.display_with_hint(col)
            time.sleep(0.3)
            self.board.drop_piece(col, player.marker)

            win_line = self.board.is_winner(player.marker)
            if win_line:
                self.board.display()
                self._print_victory(player, win_line)
                return player

            if self.board.is_full():
                self.board.display()
                self._print_draw()
                return None

            self.current_idx = 1 - self.current_idx

    def _print_round_start(self):
        print(f"\n  {CYAN}{'=' * 40}{RESET}")
        print(f"  {BOLD}         INICIANDO RODADA{RESET}")
        print(f"  {CYAN}{'=' * 40}{RESET}")
        time.sleep(1)

    def _print_score(self):
        p1 = self.players[0]
        p2 = self.players[1]
        print(f"\n  {BOLD}[ PLACAR ]{RESET}")
        print(f"  {RED}{p1.name}{RESET}: {GREEN}{p1.wins}{RESET}  |  {BLUE}{p2.name}{RESET}: {GREEN}{p2.wins}{RESET}")

    def _print_victory(self, winner, win_line):
        color = RED if winner.marker == "X" else BLUE
        print(f"\n  {color}{BOLD}========================================{RESET}")
        print(f"  {color}{BOLD}    PARABENS! {winner.name} VENCEU!{RESET}")
        print(f"  {color}{BOLD}========================================{RESET}")
        print(f"\n  {YELLOW}Jogadas: {self.moves_count}{RESET}")
        winner.wins += 1

    def _print_draw(self):
        print(f"\n  {YELLOW}{BOLD}========================================{RESET}")
        print(f"  {YELLOW}{BOLD}           EMPATE!{RESET}")
        print(f"  {YELLOW}{BOLD}========================================{RESET}")
        print(f"\n  {DIM}Jogadas: {self.moves_count}{RESET}")

class SeriesManager:
    def __init__(self):
        self.total_games_played = 0

    def main_menu(self):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            self._print_header()
            print(f"  {BOLD}1.{RESET} [H-H] Humano vs Humano")
            print(f"  {BOLD}2.{RESET} [H-?] Humano vs Computador (Facil)")
            print(f"  {BOLD}3.{RESET} [H-?] Humano vs Computador (Medio)")
            print(f"  {BOLD}4.{RESET} [H-?] Humano vs Computador (Dificil)")
            print(f"  {BOLD}5.{RESET} [i] Estatisticas")
            print(f"  {BOLD}0.{RESET} [X] Sair")
            print()

            choice = input(f"  {BOLD}[>] Escolha uma opcao:{RESET} ").strip()

            if choice == '1':
                self.start_series("PvP")
            elif choice == '2':
                self.start_series("PvC", "easy")
            elif choice == '3':
                self.start_series("PvC", "medium")
            elif choice == '4':
                self.start_series("PvC", "hard")
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
        print(f"  {CYAN}{BOLD}     LIG-4 - CONECTE 4{RESET}")
        print(f"  {CYAN}==================================={RESET}\n")

    def _print_error(self):
        print(f"\n  {RED}[X] Opcao invalida!{RESET}")
        time.sleep(1)

    def _print_goodbye(self):
        print(f"\n  {GREEN}Obrigado por jogar! Ate logo!{RESET}\n")

    def start_series(self, mode, difficulty="medium"):
        os.system('cls' if os.name == 'nt' else 'clear')

        if mode == "PvP":
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

            game = Lig4Game(p1, p2)
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

        print(f"\n  {color}{BOLD}========================================{RESET}")
        print(f"  {color}{BOLD}      VENCEDOR DA SERIE!{RESET}")
        print(f"  {color}{BOLD}========================================{RESET}")
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
    SeriesManager().main_menu()
