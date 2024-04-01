import tkinter as tk
import tkinter.simpledialog as simpledialog
import tkinter.messagebox as messagebox
import chess
import chess.engine
import math

class ChessGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Chess")
        self.board = chess.Board()
        self.engine_path = r"C:\Users\lkirk\Documents\stockfish\stockfish\stockfish-windows-x86-64.exe"  # Update this path
        self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
        self.selected_piece = None  # Track the currently selected piece
        self.current_player = chess.WHITE  # Track the current player (white starts)
        self.white_elo, self.black_elo = self.prompt_for_elo()  # NEW: Prompt for ELO scores
        self.white_win_probability, self.black_win_probability = self.calculate_initial_probabilities()
        self.create_board()
        self.place_pieces()
        self.create_evaluation_bars()
        self.display_elo_scores()  # NEW: Display ELO scores
        self.display_win_probabilities()  # NEW: Display initial winning probabilities
        self.update_evaluation()  # Initial evaluation
        self.create_move_log()  # NEW: Create move log for real-time reporting

    def prompt_for_elo(self):
        # Prompt the user for white and black player's ELO scores
        white_elo = simpledialog.askinteger("ELO Score", "Enter White player's ELO score:", parent=self.master)
        black_elo = simpledialog.askinteger("ELO Score", "Enter Black player's ELO score:", parent=self.master)
        return white_elo, black_elo

    def calculate_initial_probabilities(self):
        # Calculate initial winning probabilities based on ELO scores
        delta_elo = self.white_elo - self.black_elo
        probability_white_wins = 1 / (1 + math.exp(-delta_elo / 400))  # Using a sigmoid function
        probability_black_wins = 1 - probability_white_wins
        return probability_white_wins, probability_black_wins

    def display_elo_scores(self):
        # Display ELO scores on the game window
        white_elo_label = tk.Label(self.master, text=f"White ELO: {self.white_elo}", fg="black")
        white_elo_label.grid(row=9, column=0, columnspan=4, sticky="w")
        black_elo_label = tk.Label(self.master, text=f"Black ELO: {self.black_elo}", fg="blue")
        black_elo_label.grid(row=9, column=4, columnspan=4, sticky="e")

    def display_win_probabilities(self):
        # Display winning probabilities on the game window
        self.win_prob_label = tk.Label(self.master, text=f"Win Probability - White: {self.white_win_probability*100:.1f}%, Black: {self.black_win_probability*100:.1f}%", fg="green")
        self.win_prob_label.grid(row=10, column=0, columnspan=8)
    
    def update_win_probabilities(self, score):
        # This is a conceptual implementation; you'll need to adjust the logic based on how you interpret the evaluation scores
        # For simplicity, we assume the score is in centipawns and directly proportional to winning probability
       # Update win probabilities based on evaluation score
        score_difference = score - 0  # Assuming 0 is the starting score for an even match
        adjustment_factor = 1 / (1 + math.exp(-score_difference / 400))  # Sigmoid function
        if self.current_player == chess.WHITE:
            self.white_win_probability *= adjustment_factor
        else:
            self.black_win_probability *= adjustment_factor
        # Ensure total probability sums to 1
        total_probability = self.white_win_probability + self.black_win_probability
        self.white_win_probability /= total_probability
        self.black_win_probability /= total_probability
        self.display_win_probabilities()  # Update display after adjustment

    def create_board(self):
        self.buttons = [[None for _ in range(8)] for _ in range(8)]
        for row in range(8):
            for col in range(8):
                # Invert the board's color pattern to match the inverted piece placement
                color = "#F0D9B5" if (row + col) % 2 != 0 else "#B58863"
                button = tk.Button(self.master, bg=color, width=8, height=4,
                                   command=lambda r=row, c=col: self.on_click(7-r, c)) # Invert row index for clicks
                button.grid(row=7-row, column=col) # Invert grid placement to flip the board
                self.buttons[7-row][col] = button

    def place_pieces(self):
        piece_symbols = {
            chess.PAWN: 'P', chess.KNIGHT: 'N', chess.BISHOP: 'B',
            chess.ROOK: 'R', chess.QUEEN: 'Q', chess.KING: 'K'
        }
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                symbol = piece_symbols.get(piece.piece_type, '')
                color = 'white' if piece.color == chess.WHITE else 'black'
                row, col = divmod(square, 8)
                self.buttons[7-row][col].config(text=symbol, fg=color) # Invert row for piece placement
            else:
                row, col = divmod(square, 8)
                self.buttons[7-row][col].config(text='', fg='black') # Invert row for empty squares


    def create_evaluation_bars(self):
        self.black_bar = tk.Scale(self.master, from_=-10000, to=10000, orient="horizontal", label="Black Evaluation", fg="blue")
        self.black_bar.grid(row=8, column=0, columnspan=4, sticky="ew")
        self.white_bar = tk.Scale(self.master, from_=-10000, to=10000, orient="horizontal", label="White Evaluation", fg="black")
        self.white_bar.grid(row=8, column=4, columnspan=4, sticky="ew")

    def create_move_log(self):
        # Create a frame to hold the Text widget and the Scrollbar
        log_frame = tk.Frame(self.master)
        log_frame.grid(row=0, column=9, rowspan=10, padx=10, pady=10, sticky="nsew")

        # Create the Text widget for logging moves and evaluations
        self.move_log = tk.Text(log_frame, height=20, width=95, wrap="none")  # wrap="none" is important for horizontal scrolling

        # Create a horizontal Scrollbar and attach it to the Text widget
        h_scroll = tk.Scrollbar(log_frame, orient="horizontal", command=self.move_log.xview)
        self.move_log.configure(xscrollcommand=h_scroll.set)

        # Pack the Scrollbar before packing the Text widget so it appears at the bottom
        h_scroll.pack(side="bottom", fill="x")
        self.move_log.pack(side="top", fill="both", expand=True)

        self.move_log.insert(tk.END, "Move Log:\n")

    def on_click(self, row, col):
        # Invert row index to match internal board representation
        adjusted_row = 7 - row
        square = chess.square(col, adjusted_row)
        piece = self.board.piece_at(square)
        if not self.board.is_game_over():
            if self.selected_piece is None and piece and piece.color == self.current_player:
                # Select the piece
                self.selected_piece = square
            elif self.selected_piece is not None:
                # Calculate the target square based on the inverted board
                target_square = chess.square(col, adjusted_row)
                move = chess.Move(self.selected_piece, target_square)
                if move in self.board.legal_moves:
                    # Make the move if it's legal
                    pre_move_evaluation = self.evaluate_position()  # Evaluate before making the move
                    self.board.push(move)
                    post_move_evaluation = self.evaluate_position()  # Evaluate after making the move
                    move_quality = self.analyze_move_quality(pre_move_evaluation, post_move_evaluation)  # Analyze move quality
                    messagebox.showinfo("Move Quality", move_quality)  # Display move quality feedback
    
                    
                    # Log the move and its evaluation
                    self.log_move(move, pre_move_evaluation, post_move_evaluation, is_legal=True)
                    
                    # Change the current player after a successful move
                    self.current_player = not self.current_player
                    self.place_pieces()  # Re-draw the pieces on the board
                    self.update_evaluation()
                    self.check_game_end()
                # Clear the selected piece after an attempt to move, regardless of its legality
                self.selected_piece = None


    def explain_fen(self, fen):
        # Split the FEN string into its components
        parts = fen.split(' ')
        board, turn, castling, en_passant, halfmove, fullmove = parts

        # Translate the board part of FEN to a more understandable format
        board_rows = board.split('/')
        board_explanation = "Board setup:\n"
        for row in board_rows:
            readable_row = row.replace('1', '.').replace('2', '..').replace('3', '...').replace('4', '....').replace('5', '.....').replace('6', '......').replace('7', '.......').replace('8', '........')
            board_explanation += f"{readable_row}\n"
    
        # Explain whose turn it is
        turn_explanation = "White's turn" if turn == 'w' else "Black's turn"

        # Explain castling rights
        castling_explanation = "Castling rights: " + (castling if castling != '-' else 'None')

        # Explain en passant target square
        en_passant_explanation = "En passant target square: " + (en_passant if en_passant != '-' else 'None')

        # Explain halfmove clock (steps since last capture or pawn move)
        halfmove_explanation = f"Halfmove clock (for 50-move rule): {halfmove}"

        # Explain fullmove number (incremented after Black's turn)
        fullmove_explanation = f"Fullmove number: {fullmove}"

        # Combine all explanations into one string
        explanation = f"{board_explanation}\n{turn_explanation}\n{castling_explanation}\n{en_passant_explanation}\n{halfmove_explanation}\n{fullmove_explanation}"
    
        return explanation

    def provide_in_depth_analysis(self):
        info = self.engine.analyse(self.board, chess.engine.Limit(depth=20))
        score = info.get("score", None)
        message = "In-depth Analysis: "
        if score is not None:
            cp = score.white().score(mate_score=10000)
            mate = score.white().mate()

            if mate is not None:
                message += f"Checkmate in {mate} moves by {'White' if mate > 0 else 'Black'}.\n"
            elif cp is not None:
                adv = abs(cp) / 100.0
                message += f"{'White' if cp > 0 else 'Black'} has a {adv:.2f} point advantage. "

                '''
                as of right now i am giving simplistic general analysis of the game on side as the evaluation bars are 
                being updated during the game if we can adjust these but it is not a must

                '''
            # General Analysis based on score
            if abs(cp) < 100:
                message += "The game is relatively balanced. "
            elif abs(cp) < 300:
                message += "Slight advantage, consider developing pieces or controlling the center. "
            else:
                message += "Significant advantage, look for tactical opportunities or increase pressure. "

            # Pawn Structure Analysis (Simplistic)
            pawns = self.board.pieces(chess.PAWN, chess.WHITE) | self.board.pieces(chess.PAWN, chess.BLACK)
            if len(pawns) < 12:
                message += "Open pawn structure, consider piece mobility and king safety. "
            else:
                message += "Closed pawn structure, consider pawn breaks and space advantage. "

            # King Safety (Very Simplistic)
            if self.board.is_checkmate():
                message += "One of the kings is in checkmate. "
            elif self.board.is_check():
                message += "Active check, consider defensive moves. "
            else:
                message += "No immediate threats, but always consider king safety. "

            # Piece Mobility (Simplistic)
            # Considering the number of legal moves as a proxy for mobility
            num_legal_moves = len(list(self.board.legal_moves))
            if num_legal_moves < 20:
                message += "Limited mobility, consider improving the positioning of your pieces. "
            else:
                message += "Good mobility, look for opportunities to exploit. "
        else:
            message += "Unable to provide an in-depth analysis at this time."

        return message


    
    def log_move(self, move, pre_move_evaluation, post_move_evaluation, is_legal=False):
        try:
            move_notation = move.uci()  # Use UCI notation as a fallback
            if is_legal:
                try:
                    move_notation = self.board.san(move)
                except AssertionError:
                    pass
            current_evaluation = self.evaluate_position()
            in_depth_analysis = self.provide_in_depth_analysis()
            self.move_log.insert(tk.END, f"{move_notation}: Pre-move Eval: {pre_move_evaluation}, Post-move Eval: {post_move_evaluation}, Stockfish Eval: {current_evaluation}\n{in_depth_analysis}\n")
        except Exception as e:
            self.move_log.insert(tk.END, f"Error logging move: {e}\n")
        finally:
            self.move_log.see(tk.END)



    def evaluate_position(self):
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return 0  # No legal moves implies a stalemate or checkmate scenario

        total_evaluation = 0
        for move in legal_moves:
            # Simulate the move
            self.board.push(move)
            move_evaluation = self.engine.analyse(self.board, chess.engine.Limit(time=0.1))["score"].white().score(mate_score=10000)
            # Undo the move to restore the board
            self.board.pop()

            # probability for each move 
            p_mi = 1 / len(legal_moves)
            total_evaluation += p_mi * move_evaluation

        return total_evaluation

        
    def analyze_move_quality(self, pre_move_evaluation, post_move_evaluation):
        evaluation_change = post_move_evaluation - pre_move_evaluation
        # may need to adjust thresholds or logic based on the phase of the game (e.g., opening to endgame)
        if self.board.fullmove_number <= 10:  # Considers opening phase adjustments first 10 moves
            if evaluation_change > 20:
                return "Strategically sound move"
            elif evaluation_change > -10:
                return "Decent move"
            else:
                return "Dubious move"
        else:
            # Original thresholds with slight adjustments
            if evaluation_change > 100:
                return "Excellent move"
            elif evaluation_change > 50:
                return "Great move"
            elif evaluation_change > 20:
                return "Good move"
            elif evaluation_change > -20:
                return "Decent move"
            elif evaluation_change > -50:
                return "Questionable move"
            elif evaluation_change > -100:
                return "Bad move"
            else:
                return "Blunder"


    def update_evaluation(self):
        if not self.board.is_game_over():
            current_evaluation = self.evaluate_position()
            if current_evaluation is not None:
                self.white_bar.set(current_evaluation)
                self.black_bar.set(-current_evaluation)
                self.update_win_probabilities(current_evaluation)  # Update win probabilities based on current evaluation

    def check_game_end(self):
        if self.board.is_checkmate():
            result = "Checkmate. " + ("White wins!" if self.current_player == chess.BLACK else "Black wins!")
            tk.messagebox.showinfo("Game Over", result)
        elif self.board.is_stalemate() or self.board.is_insufficient_material():
            tk.messagebox.showinfo("Game Over", "Draw due to stalemate or insufficient material.")
        elif self.board.can_claim_threefold_repetition():
            tk.messagebox.showinfo("Game Over", "Draw due to threefold repetition.")
        elif self.board.can_claim_fifty_moves():
            tk.messagebox.showinfo("Game Over", "Draw due to fifty-move rule.")

def main():
    root = tk.Tk()
    gui = ChessGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
