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

class Board:
    def __init__(self):
        self.cells = [" " for _ in range(9)]

    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\n {BOLD}{CYAN}=== TABULEIRO JOGO DA VELHA ==={RESET}")
        
        def format_cell(cell):
            if cell == "X": return f"{RED}{BOLD}X{RESET}"
            if cell == "O": return f"{BLUE}{BOLD}O{RESET}"
            return " "

        print("\n")
        print(f"  {format_cell(self.cells[0])} | {format_cell(self.cells[1])} | {format_cell(self.cells[2])} ")
        print(" ---+---+---")
        print(f"  {format_cell(self.cells[3])} | {format_cell(self.cells[4])} | {format_cell(self.cells[5])} ")
        print(" ---+---+---")
        print(f"  {format_cell(self.cells[6])} | {format_cell(self.cells[7])} | {format_cell(self.cells[8])} ")
        print("\n")

    def update(self, position, marker):
        if self.cells[position] == " ":
            self.cells[position] = marker
            return True
        return False

    def is_winner(self, marker):
        win_conditions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8], # Linhas
            [0, 3, 6], [1, 4, 7], [2, 5, 8], # Colunas
            [0, 4, 8], [2, 4, 6]             # Diagonais
        ]
        for condition in win_conditions:
            if all(self.cells[i] == marker for i in condition):
                return True
        return False

    def is_full(self):
        return " " not in self.cells

    def reset(self):
        self.cells = [" " for _ in range(9)]

class Player:
    def __init__(self, name, marker):
        self.name = name
        self.marker = marker

class HumanPlayer(Player):
    def get_move(self, board):
        while True:
            try:
                move = int(input(f"{self.name} ({self.marker}), escolha uma posição (1-9): ")) - 1
                if 0 <= move <= 8 and board.cells[move] == " ":
                    return move
                else:
                    print("Posição ocupada ou inválida. Tente novamente.")
            except ValueError:
                print("Por favor, insira um número de 1 a 9.")

class AIPlayer(Player):
    def get_move(self, board):
        print(f"{self.name} pensando...")
        time.sleep(1)
        # 1. Tentar vencer
        for i in range(9):
            if board.cells[i] == " ":
                board.cells[i] = self.marker
                if board.is_winner(self.marker):
                    board.cells[i] = " " # Reset temporário
                    return i
                board.cells[i] = " "

        # 2. Bloquear oponente
        opponent_marker = "O" if self.marker == "X" else "X"
        for i in range(9):
            if board.cells[i] == " ":
                board.cells[i] = opponent_marker
                if board.is_winner(opponent_marker):
                    board.cells[i] = " "
                    return i
                board.cells[i] = " "

        # 3. Escolher aleatório
        available_moves = [i for i, cell in enumerate(board.cells) if cell == " "]
        return random.choice(available_moves)

class TicTacToeGame:
    def __init__(self, player1, player2):
        self.board = Board()
        self.players = [player1, player2]
        self.start_time = 0

    def play_round(self):
        self.board.reset()
        self.start_time = time.time()
        current_player_idx = 0

        while True:
            self.board.display()
            current_player = self.players[current_player_idx]
            
            move = current_player.get_move(self.board)
            self.board.update(move, current_player.marker)

            if self.board.is_winner(current_player.marker):
                self.board.display()
                total_time = time.time() - self.start_time
                print(f"{GREEN}{BOLD}Parabéns! {current_player.name} venceu esta rodada!{RESET}")
                print(f"{YELLOW}Tempo total da rodada: {total_time:.2f} segundos.{RESET}")
                return current_player

            if self.board.is_full():
                self.board.display()
                total_time = time.time() - self.start_time
                print(f"{BLUE}Empate!{RESET}")
                print(f"{YELLOW}Tempo total da rodada: {total_time:.2f} segundos.{RESET}")
                return None

            current_player_idx = 1 - current_player_idx

class SeriesManager:
    def __init__(self):
        pass

    def main_menu(self):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{CYAN}{BOLD}==========================={RESET}")
            print(f"{CYAN}{BOLD}      JOGO DA VELHA        {RESET}")
            print(f"{CYAN}{BOLD}==========================={RESET}")
            print(f"1. {RED}Humano vs Humano{RESET}")
            print(f"2. {BLUE}Humano vs Computador{RESET}")
            print("3. Sair")
            choice = input(f"\n{BOLD}Escolha uma opção:{RESET} ")

            if choice == '1':
                self.start_series(mode="HvH")
            elif choice == '2':
                self.start_series(mode="HvC")
            elif choice == '3':
                print("Obrigado por jogar!")
                break
            else:
                input("Opção inválida. Pressione Enter para tentar novamente.")

    def start_series(self, mode):
        if mode == "HvH":
            p1_name = input("Nome do Jogador 1 (X): ") or "Jogador 1"
            p2_name = input("Nome do Jogador 2 (O): ") or "Jogador 2"
            p1 = HumanPlayer(p1_name, "X")
            p2 = HumanPlayer(p2_name, "O")
        else:
            p1_name = input("Seu nome (X): ") or "Humano"
            p1 = HumanPlayer(p1_name, "X")
            p2 = AIPlayer("Computador", "O")

        wins_p1 = 0
        wins_p2 = 0
        round_count = 1

        while wins_p1 < 2 and wins_p2 < 2:
            print(f"\n{BOLD}--- Iniciando Rodada {round_count} ---{RESET}")
            print(f"{CYAN}Placar: {RED}{p1.name} {wins_p1}{RESET} x {BLUE}{wins_p2} {p2.name}{RESET}")
            input(f"\nPressione {GREEN}Enter{RESET} para começar...")
            
            game = TicTacToeGame(p1, p2)
            winner = game.play_round()

            if winner == p1:
                wins_p1 += 1
            elif winner == p2:
                wins_p2 += 1
            
            round_count += 1
            if wins_p1 < 2 and wins_p2 < 2:
                input("\nFim da rodada. Pressione Enter para a próxima...")

        series_winner = p1.name if wins_p1 == 2 else p2.name
        color = RED if wins_p1 == 2 else BLUE
        print(f"\n{color}{BOLD}{'='*30}{RESET}")
        print(f"{color}{BOLD}VENCEDOR FINAL DA SÉRIE: {series_winner}!{RESET}")
        print(f"{color}{BOLD}Placar Final: {p1.name} {wins_p1} x {wins_p2} {p2.name}{RESET}")
        print(f"{color}{BOLD}{'='*30}{RESET}")
        
        input("\nPressione Enter para voltar ao menu principal...")

if __name__ == "__main__":
    manager = SeriesManager()
    manager.main_menu()
