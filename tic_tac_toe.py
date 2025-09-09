WIN = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
)


def draw_board(board):
    def v(i):
        return board[i] if board[i] != " " else str(i + 1)
    print()
    print(f" {v(0)} | {v(1)} | {v(2)} ")
    print("---+---+---")
    print(f" {v(3)} | {v(4)} | {v(5)} ")
    print("---+---+---")
    print(f" {v(6)} | {v(7)} | {v(8)} ")
    print()


def winner(board):
    for a, b, c in WIN:
        if board[a] != " " and board[a] == board[b] == board[c]:
            return board[a]
    return None


def board_full(board):
    return all(cell != " " for cell in board)


def prompt_move(board, mark):
    while True:
        s = input(f"Player {mark}, choose 1-9: ").strip()
        if not s.isdigit():
            print("Enter a number 1-9."); continue
        pos = int(s)
        if not 1 <= pos <= 9:
            print("Must be 1-9."); continue
        i = pos - 1
        if board[i] != " ":
            print("Taken. Choose another."); continue
        return i


def computer_move(board, mark):
    opp = "O" if mark == "X" else "X"

    def line_move(m):
        for a, b, c in WIN:
            line = [board[a], board[b], board[c]]
            if line.count(m) == 2 and line.count(" ") == 1:
                if board[a] == " ": return a
                if board[b] == " ": return b
                if board[c] == " ": return c
        return None

    move = line_move(mark)
    if move is not None: return move
    move = line_move(opp)
    if move is not None: return move
    if board[4] == " ": return 4
    for i in (0, 2, 6, 8):
        if board[i] == " ": return i
    for i in (1, 3, 5, 7):
        if board[i] == " ": return i
    for i, v in enumerate(board):
        if v == " ": return i
    raise RuntimeError("No moves left")


def play_pvp():
    board, mark = [" "] * 9, "X"
    while True:
        draw_board(board)
        board[prompt_move(board, mark)] = mark
        w = winner(board)
        if w:
            draw_board(board); print(f"Player {w} wins!"); return
        if board_full(board):
            draw_board(board); print("Draw!"); return
        mark = "O" if mark == "X" else "X"


def play_pvc(human="X"):
    board, mark = [" "] * 9, "X"
    comp = "O" if human == "X" else "X"
    print(f"You are {human}. Computer is {comp}.")
    while True:
        draw_board(board)
        if mark == human:
            board[prompt_move(board, human)] = human
        else:
            print("Computer is thinking...")
            board[computer_move(board, comp)] = comp
        w = winner(board)
        if w:
            draw_board(board); print("You win!" if w == human else "Computer wins!"); return
        if board_full(board):
            draw_board(board); print("Draw!"); return
        mark = "O" if mark == "X" else "X"


def main():
    print("Tic-Tac-Toe")
    print("1) Player vs Player")
    print("2) Player vs Computer")
    while True:
        mode = input("Choose 1 or 2: ").strip()
        if mode in ("1", "2"): break
        print("Enter 1 or 2.")
    if mode == "1":
        play_pvp()
    else:
        while True:
            m = input("Be X or O? (X first): ").strip().upper()
            if m in ("X", "O"): break
            print("Enter X or O.")
        play_pvc(human=m)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye!")
