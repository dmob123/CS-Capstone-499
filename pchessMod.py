from tkinter import *
import tkinter as tk
import tkinter.simpledialog as simpledialog
import tkinter.messagebox as messagebox
import chess
import chess.engine
import math
from PIL import Image, ImageTk
import os

class ChessGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Chess")
        self.board = chess.Board()
        self.engine_path = os.path.abspath('stockfish/stockfish-windows-x86-64.exe') if self.is_windows() else os.path.abspath('stockfish/stockfish-ubuntu-x86-64-avx2')
        self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
        self.selected_piece = None  # Track the currently selected piece
        self.current_player = chess.WHITE  # Track the current player (white starts)
        self.white_elo, self.black_elo = self.prompt_for_elo()  # Prompt for ELO scores
        self.color_blind = self.prompt_for_color_blind()
        self.white_win_probability, self.black_win_probability = self.calculate_initial_probabilities()
        self.display_elo_scores()  # Display ELO scores
        self.button_width = 32  # Initial width of the images
        self.button_height = 32  # Initial height of the images
        for s in self.color_blind:
            if 'OFF' in self.color_blind:
                self.create_board()
                self.side_labels()
                self.place_pieces()
                self.create_evaluation_bars()
                self.display_color_blind_off()
                self.display_win_probabilities()  # Display initial winning probabilities
                self.update_evaluation()  # Initial evaluation
                self.create_move_log()  # Create move log for real-time reporting
                self.create_increase_font_button()  # Display the increase font button
                self.create_decrease_font_button()  # Display the decrease font button
                self.create_increase_image_size_button()    # Display the increase image (chess pieces) button
                self.create_decrease_image_size_button()    # Display the decrease image (chess pieces) button
            elif 'Off' in self.color_blind:
                self.create_board()
                self.side_labels()
                self.place_pieces()
                self.create_evaluation_bars()
                self.display_color_blind_off()
                self.display_win_probabilities()  # Display initial winning probabilities
                self.update_evaluation()  # Initial evaluation
                self.create_move_log()  # NEW: Create move log for real-time reporting
                self.create_increase_font_button()  
                self.create_decrease_font_button()
                self.create_increase_image_size_button()
                self.create_decrease_image_size_button()
            elif 'off' in self.color_blind:
                self.create_board()
                self.side_labels()
                self.place_pieces()
                self.create_evaluation_bars()
                self.display_color_blind_off()
                self.display_win_probabilities()  # Display initial winning probabilities
                self.update_evaluation()  # Initial evaluation
                self.create_move_log()  # Create move log for real-time reporting
                self.create_increase_font_button()  
                self.create_decrease_font_button()
                self.create_increase_image_size_button()
                self.create_decrease_image_size_button()
            elif 'ON' in self.color_blind:
                self.create_board_CBM()
                self.side_labels()
                self.place_pieces()
                self.create_evaluation_bars()
                self.display_color_blind_on()
                self.display_win_probabilities_CBM()  # Display initial winning probabilities
                self.create_move_log()  # Create move log for real-time reporting
                self.update_evaluation_CBM()  # Initial evaluation
                self.create_increase_font_button()  
                self.create_decrease_font_button()
                self.create_increase_image_size_button()
                self.create_decrease_image_size_button()
            elif 'on' in self.color_blind:
                self.create_board_CBM()
                self.side_labels()
                self.place_pieces()
                self.create_evaluation_bars()
                self.display_color_blind_on()
                self.display_win_probabilities_CBM()  # Display initial winning probabilities
                self.create_move_log()  # Create move log for real-time reporting
                self.update_evaluation_CBM()  # Initial evaluation
                self.create_increase_font_button()  
                self.create_decrease_font_button()
                self.create_increase_image_size_button()
                self.create_decrease_image_size_button()
            elif 'On' in self.color_blind:
                self.create_board_CBM()
                self.side_labels()
                self.place_pieces()
                self.create_evaluation_bars()
                self.display_color_blind_on()
                self.display_win_probabilities_CBM()  # Display initial winning probabilities
                self.create_move_log()  # Create move log for real-time reporting
                self.update_evaluation_CBM()  # Initial evaluation
                self.create_increase_font_button()  
                self.create_decrease_font_button()
                self.create_increase_image_size_button()
                self.create_decrease_image_size_button()
            else:
                self.create_board_CBM()
                self.side_labels()
                self.place_pieces()
                self.create_evaluation_bars()
                self.display_color_blind_default()
                self.display_win_probabilities_CBM()  # Display initial winning probabilities
                self.create_move_log()  # Create move log for real-time reporting
                self.update_evaluation_CBM()  # Initial evaluation
                self.create_increase_font_button()  
                self.create_decrease_font_button()
                self.create_increase_image_size_button()
                self.create_decrease_image_size_button()

    def prompt_for_elo(self):   # Prompt the user for white and black player's ELO scores as well as if they are using the color blind mode
        white_elo = simpledialog.askinteger("ELO Score", "Enter White player's ELO score:", parent=self.master)
        black_elo = simpledialog.askinteger("ELO Score", "Enter Black player's ELO score:", parent=self.master)
        return white_elo, black_elo
    
    def prompt_for_color_blind(self):   # Prompt the user for whether or not they want to play in CBM 
        color_blind = simpledialog.askstring("Color Blind Mode", "Enter ON for Color Blind Mode or Enter OFF for No Color Blind Mode", parent=self.master)
        return color_blind

    def calculate_initial_probabilities(self):  # Calculate initial winning probabilities based on ELO scores
        delta_elo = self.white_elo - self.black_elo
        probability_white_wins = 1 / (1 + math.exp(-delta_elo / 400))  # Using a sigmoid function
        probability_black_wins = 1 - probability_white_wins
        return probability_white_wins, probability_black_wins

    def display_elo_scores(self):   # Display ELO scores on the game window
        white_elo_label = tk.Label(self.master, text=f"White ELO: {self.white_elo}", fg="black")
        white_elo_label.grid(row=12, column=1, columnspan=2, sticky="")
        black_elo_label = tk.Label(self.master, text=f"Black ELO: {self.black_elo}", fg="black")
        black_elo_label.grid(row=12, column=5, columnspan=2, sticky="")

    def display_color_blind_on(self): # Set the game to CBM
        color_blind_label = tk.Label(self.master, text=f"CBM: ON", fg="black")
        color_blind_label.grid(row=15, column=2, columnspan=4, sticky="")
    
    def display_color_blind_off(self): # Set the game to non-CBM
        color_blind_label = tk.Label(self.master, text=f"CBM: OFF", fg="black")
        color_blind_label.grid(row=15, column=2, columnspan=4, sticky="")

    def display_color_blind_default(self): # Set the game to CBM if a desired input is not given
        color_blind_label1 = tk.Label(self.master, text=f"By Default, CBM: ON", fg="black")
        color_blind_label1.grid(row=16, column=3, columnspan=2, sticky="")

    def display_win_probabilities(self):    # Display win probabilities
        self.win_prob_label = tk.Label(self.master, text=f"Win Probability - White: {self.white_win_probability*100:.1f}%, Black: {self.black_win_probability*100:.1f}%", fg="green")
        self.win_prob_label.grid(row=13, column=1, columnspan=6)
    
    def display_win_probabilities_CBM(self):    # Display win probabilities for CBM
        self.win_prob_label = tk.Label(self.master, text=f"Win Probability - White: {self.white_win_probability*100:.1f}%, Black: {self.black_win_probability*100:.1f}%", fg="black")
        self.win_prob_label.grid(row=13, column=1, columnspan=6)

    def update_win_probabilities(self, score):  # Update display after adjustment
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

    def update_win_probabilities_CBM(self, score): # Update display after adjustment for CBM
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
        self.display_win_probabilities_CBM()  # Update display after adjustment

    def create_board(self): # Create chess board
        self.buttons = [[None for _ in range(8)] for _ in range(8)]
        for row in range(8):
            for col in range(8):
                color = "#F0D9B5" if (row + col) % 2 != 0 else "#B58863"
                button = tk.Button(self.master, bg=color, width=14, height=1,
                    command=lambda r=row, c=col: self.on_click(7-r, c))
                button.grid(row=7-row, column=col, sticky="nsew") 
                self.master.grid_rowconfigure(7-row, weight=1)  # Weight = tells grid how much the column or row should grow if there is extra room in the master to fill
                self.master.grid_columnconfigure(col, weight=1)  # Weight = tells grid how much the column or row should grow if there is extra room in the master to fill
                self.buttons[7-row][col] = button

    def create_board_CBM(self): # Create chess board for CBM
        self.buttons = [[None for _ in range(8)] for _ in range(8)]
        for row in range(8):
            for col in range(8):
                color = "#B3B3B3" if (row + col) % 2 != 0 else "#666666"    # 2 colors of gray variation
                button = tk.Button(self.master, bg=color, width=14, height=1,
                    command=lambda r=row, c=col: self.on_click(7-r, c))
                button.grid(row=7-row, column=col, sticky="nsew") 
                self.master.grid_rowconfigure(7-row, weight=1) # Weight = tells grid how much the column or row should grow if there is extra room in the master to fill
                self.master.grid_columnconfigure(col, weight=1) # Weight = tells grid how much the column or row should grow if there is extra room in the master to fill
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
                chess.WHITE: Image.open(r"C:\Users\drmob\Downloads\chess_pieces\white\pawn.png"),   # User must update path for image
                chess.BLACK: Image.open(r"C:\Users\drmob\Downloads\chess_pieces\black\pawn.png")    # User must update path for image
        },
            chess.ROOK: {
                chess.WHITE: Image.open(r"C:\Users\drmob\Downloads\chess_pieces\white\rook.png"),   # User must update path for image
                chess.BLACK: Image.open(r"C:\Users\drmob\Downloads\chess_pieces\black\rook.png")    # User must update path for image
        },
            chess.KNIGHT: {
                chess.WHITE: Image.open(r"C:\Users\drmob\Downloads\chess_pieces\white\knight.png"), # User must update path for image
                chess.BLACK: Image.open(r"C:\Users\drmob\Downloads\chess_pieces\black\knight.png")  # User must update path for image
        },
            chess.BISHOP: {
                chess.WHITE: Image.open(r"C:\Users\drmob\Downloads\chess_pieces\white\bishop.png"), # User must update path for image
                chess.BLACK: Image.open(r"C:\Users\drmob\Downloads\chess_pieces\black\bishop.png")  # User must update path for image
        },
            chess.QUEEN: {
                chess.WHITE: Image.open(r"C:\Users\drmob\Downloads\chess_pieces\white\queen.png"),  # User must update path for image
                chess.BLACK: Image.open(r"C:\Users\drmob\Downloads\chess_pieces\black\queen.png")   # User must update path for image
        },
            chess.KING: {
                chess.WHITE: Image.open(r"C:\Users\drmob\Downloads\chess_pieces\white\king.png"),   # User must update path for image
                chess.BLACK: Image.open(r"C:\Users\drmob\Downloads\chess_pieces\black\king.png")    # User must update path for image
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

    def increase_image_size(self):
        if self.button_width < 64:  # Set a max width for the images
            self.button_width += 8  # Increase the width of the images
        if self.button_height < 64:  # Set a max height for the image
            self.button_height += 8  # Increase the height of the images
        self.update_image_size()    # Update the image sizes of the pieces

    def create_decrease_image_size_button(self): # Create a "decrease image size" button
        self.increase_image_size_button = tk.Button(self.master, text="Decrease Image Size", command=self.decrease_image_size)
        self.increase_image_size_button.grid(row=14, column=9, columnspan=8, pady=5) 

    def decrease_image_size(self):
        if self.button_width > 16 :  # Set a min width for the images
            self.button_width -= 8  # Decrease the width of the images
        if self.button_height > 16:  # Set a min height for the images
            self.button_height -= 8  # Decrease the height of the images
        self.update_image_size()   # Update the image sizes of the pieces

    def update_image_size(self): # Update image size based on the increasement or decreasement of the images
        piece_images = {
            chess.PAWN: {
                chess.WHITE: Image.open(r"C:\Users\drmob\Downloads\chess_pieces\white\pawn.png"),   # User must update path for image
                chess.BLACK: Image.open(r"C:\Users\drmob\Downloads\chess_pieces\black\pawn.png")    # User must update path for image
        },
            chess.ROOK: {
                chess.WHITE: Image.open(r"C:\Users\drmob\Downloads\chess_pieces\white\rook.png"),   # User must update path for image
                chess.BLACK: Image.open(r"C:\Users\drmob\Downloads\chess_pieces\black\rook.png")    # User must update path for image
        },
            chess.KNIGHT: {
                chess.WHITE: Image.open(r"C:\Users\drmob\Downloads\chess_pieces\white\knight.png"), # User must update path for image
                chess.BLACK: Image.open(r"C:\Users\drmob\Downloads\chess_pieces\black\knight.png")  # User must update path for image
        },
            chess.BISHOP: {
                chess.WHITE: Image.open(r"C:\Users\drmob\Downloads\chess_pieces\white\bishop.png"), # User must update path for image
                chess.BLACK: Image.open(r"C:\Users\drmob\Downloads\chess_pieces\black\bishop.png")
        },
            chess.QUEEN: {
                chess.WHITE: Image.open(r"C:\Users\drmob\Downloads\chess_pieces\white\queen.png"),  # User must update path for image
                chess.BLACK: Image.open(r"C:\Users\drmob\Downloads\chess_pieces\black\queen.png")   # User must update path for image
        },
            chess.KING: {
                chess.WHITE: Image.open(r"C:\Users\drmob\Downloads\chess_pieces\white\king.png"),   # User must update path for image
                chess.BLACK: Image.open(r"C:\Users\drmob\Downloads\chess_pieces\black\king.png")    # User must update path for image
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
        self.black_bar = tk.Scale(self.master, from_=-10000, to=10000, orient="horizontal")
        self.black_bar.grid(row=11, column=0, columnspan=4, sticky="ew")
        self.white_bar = tk.Scale(self.master, from_=-10000, to=10000, orient="horizontal")
        self.white_bar.grid(row=11, column=4, columnspan=4, sticky="ew")

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

    def create_increase_font_button(self):  # Create an "increase font" button
        self.font_size = 8  # Initial font size
        self.increase_font_button = tk.Button(self.master, text="Increase Font Size", command=self.increase_font)
        self.increase_font_button.grid(row=11, column=9, columnspan=8, pady=5)
    
    def increase_font(self):
         if self.font_size < 12:    # Set the max size of font to 12
            self.font_size += 1  # Increase the font size by 1 unit
            self.update_font_size(self.master)  # Update font size

    def create_decrease_font_button(self):  # Create an "decrease font" button
        self.font_size = 8  # Initial font size
        self.increase_font_button = tk.Button(self.master, text="Decrease Font Size", command=self.decrease_font)
        self.increase_font_button.grid(row=12, column=9, columnspan=8, pady=5)
    
    def decrease_font(self):
         if self.font_size > 6: # Set the min size of font to 6
            self.font_size -= 1  # Decrease the font size by 1 unit
            self.update_font_size(self.master)  # Update font size

    def update_font_size(self, widget): # Update font size utilitizing isinstance and widgets, https://www.w3schools.com/python/ref_func_isinstance.asp
        if isinstance(widget, tk.Text) or isinstance(widget, tk.Label):
            current_font = widget.cget("font")
            new_font = (current_font[0], self.font_size)  
            widget.config(font=new_font)
        for child in widget.winfo_children():
            self.update_font_size(child)
    
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
        parts = fen.split(' ')  # Split the FEN string into its components
        board, turn, castling, en_passant, halfmove, fullmove = parts
        board_rows = board.split('/')   # Translate the board part of FEN to a more understandable format
        board_explanation = "Board setup:\n"
        for row in board_rows:
            readable_row = row.replace('1', '.').replace('2', '..').replace('3', '...').replace('4', '....').replace('5', '.....').replace('6', '......').replace('7', '.......').replace('8', '........')
            board_explanation += f"{readable_row}\n"
        turn_explanation = "White's turn" if turn == 'w' else "Black's turn"    # Explain whose turn it is
        castling_explanation = "Castling rights: " + (castling if castling != '-' else 'None')  # Explain castling rights
        en_passant_explanation = "En passant target square: " + (en_passant if en_passant != '-' else 'None')   # Explain en passant target square
        halfmove_explanation = f"Halfmove clock (for 50-move rule): {halfmove}" # Explain halfmove clock (steps since last capture or pawn move)
        fullmove_explanation = f"Fullmove number: {fullmove}"   # Explain fullmove number (incremented after Black's turn)
        explanation = f"{board_explanation}\n{turn_explanation}\n{castling_explanation}\n{en_passant_explanation}\n{halfmove_explanation}\n{fullmove_explanation}"  # Combine all explanations into one string
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
            pawns = self.board.pieces(chess.PAWN, chess.WHITE) | self.board.pieces(chess.PAWN, chess.BLACK) # Pawn Structure Analysis (Simplistic)
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

    def update_evaluation(self):    # Updates evaluation
        if not self.board.is_game_over():
            current_evaluation = self.evaluate_position()
            if current_evaluation is not None:
                self.white_bar.set(current_evaluation)
                self.black_bar.set(-current_evaluation)
                self.update_win_probabilities(current_evaluation)  # Update win probabilities based on current evaluation

    def update_evaluation_CBM(self):    # Updates the CBM evaluation
        if not self.board.is_game_over():
            current_evaluation = self.evaluate_position()
            if current_evaluation is not None:
                self.white_bar.set(current_evaluation)
                self.black_bar.set(-current_evaluation)
                self.update_win_probabilities_CBM(current_evaluation)  # Update win probabilities based on current evaluation for CBM

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

    def is_windows(self):
        return os.name == 'nt'

def main():
    root = tk.Tk()
    gui = ChessGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
