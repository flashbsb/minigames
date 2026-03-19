import time
import random
import os

# Cores ANSI
RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
BOLD = "\033[1m"

class Lig4Board:
    ROWS = 6
    COLS = 7

    def __init__(self):
        self.grid = [[" " for _ in range(self.COLS)] for _ in range(self.ROWS)]

    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\n  {CYAN}{BOLD}=== TABULEIRO LIG-4 ==={RESET}")
        print(f"\n  {YELLOW}1   2   3   4   5   6   7{RESET}")
        print(" +---+---+---+---+---+---+---+")
        for row in self.grid:
            formatted_row = []
            for cell in row:
                if cell == "X": formatted_row.append(f"{RED}{BOLD}X{RESET}")
                elif cell == "O": formatted_row.append(f"{BLUE}{BOLD}O{RESET}")
                else: formatted_row.append(" ")
            print(" | " + " | ".join(formatted_row) + " |")
            print(" +---+---+---+---+---+---+---+")
        print("\n")

    def drop_piece(self, col, marker):
        for row in reversed(range(self.ROWS)):
            if self.grid[row][col] == " ":
                self.grid[row][col] = marker
                return True
        return False

    def is_winner(self, marker):
        # Horizontal
        for r in range(self.ROWS):
            for c in range(self.COLS - 3):
                if all(self.grid[r][c+i] == marker for i in range(4)):
                    return True
        # Vertical
        for r in range(self.ROWS - 3):
            for c in range(self.COLS):
                if all(self.grid[r+i][c] == marker for i in range(4)):
                    return True
        # Diagonal /
        for r in range(3, self.ROWS):
            for c in range(self.COLS - 3):
                if all(self.grid[r-i][c+i] == marker for i in range(4)):
                    return True
        # Diagonal \
        for r in range(self.ROWS - 3):
            for c in range(self.COLS - 3):
                if all(self.grid[r+i][c+i] == marker for i in range(4)):
                    return True
        return False

    def is_full(self):
        return all(self.grid[0][c] != " " for c in range(self.COLS))

    def reset(self):
        self.grid = [[" " for _ in range(self.COLS)] for _ in range(self.ROWS)]

class Player:
    def __init__(self, name, marker):
        self.name = name
        self.marker = marker

class HumanPlayer(Player):
    def get_move(self, board):
        while True:
            try:
                col = int(input(f"{self.name} ({self.marker}), escolha uma coluna (1-7): ")) - 1
                if 0 <= col < board.COLS:
                    if board.grid[0][col] == " ":
                        return col
                    else:
                        print("Coluna cheia! Tente outra.")
                else:
                    print("Coluna inválida. Escolha entre 1 e 7.")
            except ValueError:
                print("Entrada inválida. Digite um número de 1 a 7.")

class AIPlayer(Player):
    def get_move(self, board):
        print(f"{self.name} pensando...")
        time.sleep(1)
        
        # 1. Tentar vencer
        for col in range(board.COLS):
            if board.grid[0][col] == " ":
                # Simula a queda da peça
                for row in reversed(range(board.ROWS)):
                    if board.grid[row][col] == " ":
                        board.grid[row][col] = self.marker
                        if board.is_winner(self.marker):
                            board.grid[row][col] = " "
                            return col
                        board.grid[row][col] = " "
                        break

        # 2. Bloquear oponente
        opponent = "O" if self.marker == "X" else "X"
        for col in range(board.COLS):
            if board.grid[0][col] == " ":
                for row in reversed(range(board.ROWS)):
                    if board.grid[row][col] == " ":
                        board.grid[row][col] = opponent
                        if board.is_winner(opponent):
                            board.grid[row][col] = " "
                            return col
                        board.grid[row][col] = " "
                        break

        # 3. Preferência pelo centro, depois aleatório
        center_col = board.COLS // 2
        if board.grid[0][center_col] == " ":
            return center_col
            
        available_cols = [c for c in range(board.COLS) if board.grid[0][c] == " "]
        return random.choice(available_cols)

class Lig4Game:
    def __init__(self, p1, p2):
        self.board = Lig4Board()
        self.players = [p1, p2]
        self.start_time = 0

    def play_round(self):
        self.board.reset()
        self.start_time = time.time()
        current_idx = 0

        while True:
            self.board.display()
            player = self.players[current_idx]
            
            col = player.get_move(self.board)
            self.board.drop_piece(col, player.marker)

            if self.board.is_winner(player.marker):
                self.board.display()
                duration = time.time() - self.start_time
                print(f"{GREEN}{BOLD}Parabéns! {player.name} venceu a rodada!{RESET}")
                print(f"{YELLOW}Tempo total da rodada: {duration:.2f} segundos.{RESET}")
                return player

            if self.board.is_full():
                self.board.display()
                duration = time.time() - self.start_time
                print(f"{BLUE}Empate! O tabuleiro está cheio.{RESET}")
                print(f"{YELLOW}Tempo total da rodada: {duration:.2f} segundos.{RESET}")
                return None

            current_idx = 1 - current_idx

class SeriesManager:
    def __init__(self):
        pass

    def main_menu(self):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{CYAN}{BOLD}==========================={RESET}")
            print(f"{CYAN}{BOLD}          LIG-4            {RESET}")
            print(f"{CYAN}{BOLD}==========================={RESET}")
            print(f"1. {RED}Jogador x Jogador{RESET}")
            print(f"2. {BLUE}Jogador x Computador{RESET}")
            print("3. Sair")
            choice = input(f"\n{BOLD}Escolha uma opção:{RESET} ")

            if choice == '1':
                self.start_series(mode="PvP")
            elif choice == '2':
                self.start_series(mode="PvC")
            elif choice == '3':
                print("Obrigado por jogar Lig-4!")
                break
            else:
                input("Opção inválida. Pressione Enter...")

    def start_series(self, mode):
        if mode == "PvP":
            n1 = input("Nome Jogador 1 (X): ") or "Jogador 1"
            n2 = input("Nome Jogador 2 (O): ") or "Jogador 2"
            p1 = HumanPlayer(n1, "X")
            p2 = HumanPlayer(n2, "O")
        else:
            n1 = input("Seu nome (X): ") or "Humano"
            p1 = HumanPlayer(n1, "X")
            p2 = AIPlayer("Computador", "O")

        wins1, wins2 = 0, 0
        round_n = 1

        while wins1 < 2 and wins2 < 2:
            print(f"\n{BOLD}--- Rodada {round_n} ---{RESET}")
            print(f"{CYAN}Placar: {RED}{p1.name} {wins1}{RESET} x {BLUE}{wins2} {p2.name}{RESET}")
            input(f"\nPressione {GREEN}Enter{RESET} para começar...")
            
            round_winner = Lig4Game(p1, p2).play_round()

            if round_winner == p1: wins1 += 1
            elif round_winner == p2: wins2 += 1
            
            round_n += 1
            if wins1 < 2 and wins2 < 2:
                input("\nFim da rodada. Enter para continuar...")

        final_winner = p1.name if wins1 == 2 else p2.name
        color = RED if wins1 == 2 else BLUE
        print(f"\n{color}{BOLD}{'='*40}{RESET}")
        print(f"{color}{BOLD}VENCEDOR FINAL DA SÉRIE LIG-4: {final_winner}!{RESET}")
        print(f"{color}{BOLD}Placar Final: {p1.name} {wins1} x {wins2} {p2.name}{RESET}")
        print(f"{color}{BOLD}{'='*40}{RESET}")
        input(f"\nRetornar ao menu principal ({GREEN}Enter{RESET})...")

if __name__ == "__main__":
    SeriesManager().main_menu()
