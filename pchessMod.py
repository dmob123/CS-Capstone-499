from tkinter import *
import tkinter as tk
import tkinter.simpledialog as simpledialog
import tkinter.messagebox as messagebox
import chess
import chess.engine
import math
from PIL import Image, ImageTk
import os
import pickle
import numpy as np
import pandas as pd

class ChessGUI:
    def __init__(self, master):
        with open('RF_model.pkl', 'rb') as file:
            self.model = pickle.load(file)
        self.master = master
        self.master.title("Chess")
        self.board = chess.Board()
        self.engine_path = os.path.abspath('stockfish_win/stockfish-windows-x86-64.exe') if self.is_windows() else os.path.abspath('stockfish/stockfish-ubuntu-x86-64-avx2')       
        self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
        self.selected_piece = None  # Track the currently selected piece
        self.current_player = chess.WHITE  # Track the current player (white starts)
        self.white_elo, self.black_elo = self.prompt_for_elo()  # Prompt for ELO scores
        self.white_win_probability, self.black_win_probability = self.calculate_initial_probabilities() # Set the win probability for black and white
        self.display_elo_scores()  # Display ELO scores
        self.button_width = 32  # Initial width of the images
        self.button_height = 32  # Initial height of the images
        self.create_board() # Create chess board
        self.side_labels()  # Display side labels
        self.place_pieces() # Place pieces on the board
        self.create_evaluation_bars()   # Display evaluation bars
        self.display_win_probabilities()  # Display initial winning probabilities
        self.update_evaluation()  # Initial evaluation
        self.create_increase_image_size_button()    # Display the increase image (chess pieces) button
        self.create_decrease_image_size_button()    # Display the decrease image (chess pieces) button
        self.piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0
        }

                
    def prompt_for_elo(self):   # Prompt the user for white and black player's ELO scores as well as if they are using the color blind mode
        white_elo = simpledialog.askinteger("ELO Score", "Enter White player's ELO score:", parent=self.master)
        black_elo = simpledialog.askinteger("ELO Score", "Enter Black player's ELO score:", parent=self.master)
        return white_elo, black_elo
    

    def calculate_initial_probabilities(self):
        # Calculate initial winning probabilities based on ELO scores
        delta_elo = self.white_elo - self.black_elo
        probability_white_wins = 1 / (1 + 10 ** (delta_elo / -400))
        probability_black_wins = 1 - probability_white_wins
        return probability_white_wins, probability_black_wins

    def display_elo_scores(self):   # Display ELO scores on the game window
        white_elo_label = tk.Label(self.master, text=f"White ELO: {self.white_elo}", fg="black")
        white_elo_label.grid(row=12, column=1, columnspan=2, sticky="")
        black_elo_label = tk.Label(self.master, text=f"Black ELO: {self.black_elo}", fg="black")
        black_elo_label.grid(row=12, column=5, columnspan=2, sticky="")

    def display_win_probabilities(self):    # Display win probabilities
        self.win_prob_label = tk.Label(self.master, text=f"Win Probability - White: {self.white_win_probability*100:.1f}%, Black: {self.black_win_probability*100:.1f}%", fg="green")
        self.win_prob_label.grid(row=13, column=1, columnspan=6)
    

    def update_win_probabilities(self, score):  # Update display after adjustment
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

    def create_board(self): # Create chess board
        self.buttons = [[None for _ in range(8)] for _ in range(8)]
        for row in range(8):
            for col in range(8):
                color = "#F0D9B5" if (row + col) % 2 != 0 else "#B58863"
                button = tk.Button(self.master, bg=color, width=14, height=1,
                    command=lambda r=row, c=col: self.on_click(7-r, c))
                button.grid(row=7-row, column=col, sticky="nsew") 
                self.master.grid_rowconfigure(7-row, weight=1)
                self.master.grid_columnconfigure(col, weight=1)  
                self.buttons[7-row][col] = button

    
    def side_labels(self):  # Place labels on the side of the chessboard
        labela = tk.Label(self.master, text=f"a", fg="black")
        labela.grid(row=9, column=0, columnspan=1, sticky="")
        labelb = tk.Label(self.master, text=f"b", fg="black")
        labelb.grid(row=9, column=1, columnspan=1, sticky="")
        labelc = tk.Label(self.master, text=f"c", fg="black")
        labelc.grid(row=9, column=2, columnspan=1, sticky="")
        labeld = tk.Label(self.master, text=f"d", fg="black")
        labeld.grid(row=9, column=3, columnspan=1, sticky="")
        labele = tk.Label(self.master, text=f"e", fg="black")
        labele.grid(row=9, column=4, columnspan=1, sticky="")
        labelf = tk.Label(self.master, text=f"f", fg="black")
        labelf.grid(row=9, column=5, columnspan=1, sticky="")
        labelg = tk.Label(self.master, text=f"g", fg="black")
        labelg.grid(row=9, column=6, columnspan=1, sticky="")
        labelh = tk.Label(self.master, text=f"h", fg="black")
        labelh.grid(row=9, column=7, columnspan=1, sticky="")
        label1 = tk.Label(self.master, text=f"8", fg="black")
        label1.grid(row=0, column=8, columnspan=1, sticky="")
        label2 = tk.Label(self.master, text=f"7", fg="black")
        label2.grid(row=1, column=8, columnspan=1, sticky="")
        label3 = tk.Label(self.master, text=f"6", fg="black")
        label3.grid(row=2, column=8, columnspan=1, sticky="")
        label4 = tk.Label(self.master, text=f"5", fg="black")
        label4.grid(row=3, column=8, columnspan=1, sticky="")
        label5 = tk.Label(self.master, text=f"4", fg="black")
        label5.grid(row=4, column=8, columnspan=1, sticky="")
        label6 = tk.Label(self.master, text=f"3", fg="black")
        label6.grid(row=5, column=8, columnspan=1, sticky="")
        label7 = tk.Label(self.master, text=f"2", fg="black")
        label7.grid(row=6, column=8, columnspan=1, sticky="")
        label8 = tk.Label(self.master, text=f"1", fg="black")
        label8.grid(row=7, column=8, columnspan=1, sticky="")
    
    def place_pieces(self): # Place the pieces along with their images on the board
        piece_images = {
            chess.PAWN: {
                
                chess.WHITE: Image.open(os.path.abspath("chess_pieces/white/pawn.png")),
                chess.BLACK: Image.open(os.path.abspath("chess_pieces/black/pawn.png"))
        },
            chess.ROOK: {
                chess.WHITE: Image.open(os.path.abspath("chess_pieces/white/rook.png")),
                chess.BLACK: Image.open(os.path.abspath("chess_pieces/black/rook.png"))
        },
            chess.KNIGHT: {
                chess.WHITE: Image.open(os.path.abspath("chess_pieces/white/knight.png")),
                chess.BLACK: Image.open(os.path.abspath("chess_pieces/black/knight.png"))
        },
            chess.BISHOP: {
                chess.WHITE: Image.open(os.path.abspath("chess_pieces/white/bishop.png")),
                chess.BLACK: Image.open(os.path.abspath("chess_pieces/black/bishop.png"))
        },
            chess.QUEEN: {
                chess.WHITE: Image.open(os.path.abspath("chess_pieces/white/queen.png")),
                chess.BLACK: Image.open(os.path.abspath("chess_pieces/black/queen.png"))
        },
            chess.KING: {
                chess.WHITE: Image.open(os.path.abspath("chess_pieces/white/king.png")),
                chess.BLACK: Image.open(os.path.abspath("chess_pieces/black/king.png"))    
        },
    }
        button_width = 32  # Default width of the button
        button_height = 32  # Default height of the button
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                color = 'white' if piece.color == chess.WHITE else 'black'
                row, col = divmod(square, 8)
                image = piece_images[piece.piece_type][piece.color].resize((button_width, button_height))
                photo_image = ImageTk.PhotoImage(image)
                button = self.buttons[7 - row][col]
                button.config(image=photo_image)
                button.image = photo_image  
            else:
                row, col = divmod(square, 8)
                button = self.buttons[7 - row][col]
                button.config(image='')  
    
    def create_increase_image_size_button(self): # Create an "increase image size" button
        self.increase_image_size_button = tk.Button(self.master, text="Increase Image Size", command=self.increase_image_size)
        self.increase_image_size_button.grid(row=13, column=9, columnspan=1, pady=5)

    def increase_image_size(self):  # Increase the image sizes of the chess pieces
        if self.button_width < 64:  # Set a max width for the images
            self.button_width += 8  # Increase the width of the images
        if self.button_height < 64:  # Set a max height for the image
            self.button_height += 8  # Increase the height of the images
        self.update_image_size()    # Update the image sizes of the pieces

    def create_decrease_image_size_button(self): # Create a "decrease image size" button
        self.increase_image_size_button = tk.Button(self.master, text="Decrease Image Size", command=self.decrease_image_size)
        self.increase_image_size_button.grid(row=14, column=9, columnspan=8, pady=5) 

    def decrease_image_size(self):  # Decrease the image sizes of the chess pieces
        if self.button_width > 16 :  # Set a min width for the images
            self.button_width -= 8  # Decrease the width of the images
        if self.button_height > 16:  # Set a min height for the images
            self.button_height -= 8  # Decrease the height of the images
        self.update_image_size()   # Update the image sizes of the pieces

    def update_image_size(self): # Update image size based on the increasement or decreasement of the images
        piece_images = {
            chess.PAWN: {
                
                chess.WHITE: Image.open(os.path.abspath("chess_pieces/white/pawn.png")),
                chess.BLACK: Image.open(os.path.abspath("chess_pieces/black/pawn.png"))    
        },
            chess.ROOK: {
                chess.WHITE: Image.open(os.path.abspath("chess_pieces/white/rook.png")),  
                chess.BLACK: Image.open(os.path.abspath("chess_pieces/black/rook.png"))    
        },
            chess.KNIGHT: {
                chess.WHITE: Image.open(os.path.abspath("chess_pieces/white/knight.png")),
                chess.BLACK: Image.open(os.path.abspath("chess_pieces/black/knight.png")) 
        },
            chess.BISHOP: {
                chess.WHITE: Image.open(os.path.abspath("chess_pieces/white/bishop.png")),
                chess.BLACK: Image.open(os.path.abspath("chess_pieces/black/bishop.png"))  
        },
            chess.QUEEN: {
                chess.WHITE: Image.open(os.path.abspath("chess_pieces/white/queen.png")),  
                chess.BLACK: Image.open(os.path.abspath("chess_pieces/black/queen.png"))  
        },
            chess.KING: {
                chess.WHITE: Image.open(os.path.abspath("chess_pieces/white/king.png")),   
                chess.BLACK: Image.open(os.path.abspath("chess_pieces/black/king.png"))
        },
    }
        
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                color = 'white' if piece.color == chess.WHITE else 'black'
                row, col = divmod(square, 8)
                image = piece_images[piece.piece_type][piece.color].resize((self.button_width, self.button_height))
                photo_image = ImageTk.PhotoImage(image)
                button = self.buttons[7 - row][col]
                button.config(image=photo_image)
                button.image = photo_image
    
    def create_evaluation_bars(self): # Create evaluation bars for each player
        white_elo_label1 = tk.Label(self.master, text=f"White Evaluation", fg="black")
        white_elo_label1.grid(row=10, column=1, columnspan=2, sticky="")
        black_elo_label1 = tk.Label(self.master, text=f"Black Evaluation", fg="black")
        black_elo_label1.grid(row=10, column=5, columnspan=2, sticky="")
        self.black_bar = tk.Scale(self.master, from_=-100, to=100, orient="horizontal", resolution=0.1)
        self.black_bar.grid(row=11, column=0, columnspan=4, sticky="ew")
        self.white_bar = tk.Scale(self.master, from_=-100, to=100, orient="horizontal", resolution=0.1)
        self.white_bar.grid(row=11, column=4, columnspan=4, sticky="ew")
    
    def on_click(self, row, col):
        adjusted_row = 7 - row
        square = chess.square(col, adjusted_row)
        piece = self.board.piece_at(square)
        if not self.board.is_game_over():
            if self.selected_piece is None and piece and piece.color == self.current_player:
                self.selected_piece = square  # Select the piece
            elif self.selected_piece is not None:
                target_square = chess.square(col, adjusted_row)
                move = chess.Move(self.selected_piece, target_square)
                if move in self.board.legal_moves:
                    self.board.push(move)  # Make the move
                    self.current_player = not self.current_player
                    self.place_pieces()
                    self.update_evaluation()
                    self.check_game_end()
                self.selected_piece = None


    def evaluate_position(self):
        print("Evaluation Started")
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return 0  # No legal moves implies a stalemate or checkmate scenario
        total_evaluation = 0


        evals = []

        column_names = ['IsCapture', 'IsPromotion', 'MaterialCaptured', 'Capturable',
                'Sacrifice', 'MaterialSacrificed', 'TEval', 'WhiteElo', 'BlackElo']
        df = pd.DataFrame(columns=column_names)
        print("pre-calculating")
        for move in legal_moves:
            # Simulate the move
            self.board.push(move)
            move_evaluation = self.engine.analyse(self.board, chess.engine.Limit(time=0.01))["score"].white().score(mate_score=10000)
            # Undo the move to restore the board
            self.board.pop()


            # probability for each move 
            # p_mi = 1 / len(legal_moves)

            features = self.features(move)
                    
            # move_played = 1 if legal_move == considered_moves[i+1] else 0
            row = features + [self.white_elo, self.black_elo]
            df.loc[len(df)] = row




            evals.append(move_evaluation)
        print("Calc probabilities")
        scaling_factor = 5
        probabilities = np.array(self.model.predict_proba(df))*scaling_factor 
        pVec = np.array(self.softmax(probabilities[:,1])) 
        npEvals = np.array(evals)
        print("Evaluation finished")
        return np.dot(pVec, npEvals)
    

    def update_evaluation(self):    # Updates evaluation
        if not self.board.is_game_over():
            current_evaluation = self.evaluate_position()
            if current_evaluation is not None:
                self.white_bar.set(current_evaluation)
                self.black_bar.set(-current_evaluation)
                self.update_win_probabilities(current_evaluation)  # Update win probabilities based on current evaluation


    def check_game_end(self):   # Check to see if a checkmate was reached or if there can be no moves left (stalemate)
        if self.board.is_checkmate():
            result = "Checkmate. " + ("White wins!" if self.current_player == chess.BLACK else "Black wins!")
            tk.messagebox.showinfo("Game Over", result)
        elif self.board.is_stalemate() or self.board.is_insufficient_material():
            tk.messagebox.showinfo("Game Over", "Draw due to stalemate or insufficient material.")
        elif self.board.can_claim_threefold_repetition():
            tk.messagebox.showinfo("Game Over", "Draw due to threefold repetition.")
        elif self.board.can_claim_fifty_moves():
            tk.messagebox.showinfo("Game Over", "Draw due to fifty-move rule.")

    def is_windows(self):
        return os.name == 'nt'

    def whose_turn(self):
        return chess.WHITE if self.board.turn else chess.BLACK


    def switchp(self, player):
        return chess.WHITE if player == chess.BLACK else chess.BLACK


    def softmax(self, x):
        """Adjust values of x such that sum(x)=1, allowing interpretation as probability"""
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum(axis=0)

    def features(self, move):
        player = self.whose_turn()
        moves = list(self.board.legal_moves)
        piece = self.board.piece_at(move.from_square).piece_type
        piece_moves = len([mi for mi in moves if mi.from_square == move.from_square])
        target_square = move.to_square
        isCapture = self.board.is_capture(move)
        isPromotion = move.promotion is not None
        material_captured = 0
        attackers = self.board.attackers(self.switchp(player), target_square)
        defenders = self.board.attackers(player, target_square)
        if isCapture:
            captured_piece = self.board.piece_at(target_square)
            material_captured = self.piece_values[captured_piece.piece_type]
        capturable = len(attackers) > 0
        sacrifice = len(attackers) > len(defenders)
        material_sacrificed = self.piece_values[piece] if capturable else 0

        self.board.push(move)
        teval = self.engine.analyse(self.board, chess.engine.Limit(time=0.1))["score"].white().score(mate_score=10000)
        self.board.pop()

        return [isCapture, isPromotion, material_captured, capturable, sacrifice, material_sacrificed, teval]

def main():
    root = tk.Tk()
    gui = ChessGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
