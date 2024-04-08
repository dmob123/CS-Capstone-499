import tkinter as tk
import tkinter.simpledialog as simpledialog
import tkinter.messagebox as messagebox
import chess
import chess.engine
import math
import sqlite3
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import IncrementalPCA
from sklearn.ensemble import RandomForestClassifier
from gamelog import fetch_and_print_user_games, extract_moves_from_pgn
import numpy as np

class ChessGUI:
    def __init__(self, master):
        # Existing initialization code...
        self.master = master
        self.master.title("Chess")
        self.board = chess.Board()
        self.engine_path = r"C:\Users\lkirk\OneDrive\Desktop\stockfish\stockfish\stockfish-windows-x86-64.exe"  # Update this path
        self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
        self.selected_piece = None
        self.current_player = chess.WHITE
        self.white_name,self.black_name = self.prompt_for_name()
        self.white_elo, self.black_elo = self.prompt_for_elo()
        self.fetch_and_add_player_games()
        self.white_win_probability, self.black_win_probability = self.calculate_initial_probabilities()
        self.create_board()
        self.place_pieces()
        self.create_evaluation_bars()
        self.display_elo_scores()
        self.display_win_probabilities()
        self.create_move_log()
        self.create_prediction_labels()  # Add labels for predictions
        # Fetch all chess game moves from the database
        self.moves = self.fetch_game_moves_from_database('gameslog.db')

        
        # Sample a subset of moves for PCA
        sample_size = 10000  # Adjust as needed
        sampled_moves = self.moves[:sample_size]

        # Preprocess sampled moves and convert them to numerical features
        self.features, self.vectorizer = self.preprocess_moves(sampled_moves)

        # Calculate the expected number of features
        self.expected_num_features = len(self.vectorizer.get_feature_names())

        # Perform Incremental PCA
        self.pca_num_components = min(self.expected_num_features, self.features.shape[1])
        self.ipca = IncrementalPCA(n_components=self.pca_num_components)

        # Train Incremental PCA in batches
        batch_size = 1000  # Adjust as needed
        for i in range(0, sample_size, batch_size):
            batch_features = self.features[i:i+batch_size].toarray()
            self.ipca.partial_fit(batch_features)

        # Reduce dimensionality using Incremental PCA
        self.features_pca = self.ipca.transform(self.features.toarray())

        # Train a random forest classifier
        self.cluster_labels = self.kmeans_model.labels_
        self.classifier = self.train_classifier(self.features_pca, self.cluster_labels)

    # Existing code...
    def fetch_game_moves_from_database(self, database_path):
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute("SELECT move FROM moves")
        moves = cursor.fetchall()
        conn.close()
        return [move[0] for move in moves]

    def fetch_and_add_player_games(self):
        #add here
        conn = sqlite3.connect('gameslog.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM moves WHERE white_username=?", (self.white_name,))
        data = cursor.fetchone()
        if data is None:
            # Fetch games for white player and add to the database
            white_games = self.fetch_player_games(self.white_name, conn, cursor)
            self.add_games_to_database(white_games, conn, cursor)

        cursor.execute("SELECT * FROM moves WHERE black_username=?", (self.black_name,))
        data = cursor.fetchone()
        if data is None:
            # Fetch games for black player and add to the database
            black_games = self.fetch_player_games(self.black_name, conn, cursor)
            self.add_games_to_database(black_games, conn, cursor)

        conn.close()


    

    def fetch_player_games(self, player_name, conn, cursor):
        # Fetch games for the given player (implementation depends on your data source)
        # For example, you could fetch games from an online database or API
        games =  fetch_and_print_user_games([player_name], conn, cursor)
        return games

    def add_games_to_database(self, games, conn, cursor):
        # Add games to the database (implementation depends on your data source)
        extract_moves_from_pgn(games)

        # Commit changes and close connection to the database
        conn.commit()
        conn.close()


    def preprocess_moves(self, moves):
        vectorizer = CountVectorizer(analyzer='word', lowercase=False)
        features = vectorizer.fit_transform(moves)
        return features, vectorizer

    def train_classifier(self, features, labels):
        try:
            if features is None or features.shape[0] == 0:
                print("Error: Features array is None or empty.")
                return None
            
            # Check if the number of samples in features matches the number of labels
            if features.shape[0] != len(labels):
                print("Error: Number of samples in features does not match the number of labels.")
                return None

            classifier = RandomForestClassifier()
            classifier.fit(features, labels)
            return classifier
        except ValueError as e:
            print(f"Error occurred during classifier training: {e}")
            return None

    # Existing code...
    
    def prompt_for_name(self):
        white_name = simpledialog.askstring("White Chess.com Username", "Enter White player's Username:", parent=self.master)
        black_name = simpledialog.askstring("Black Chess.com Username", "Enter Black player's Username:", parent=self.master)
        return white_name, black_name

    def prompt_for_elo(self):
        white_elo = simpledialog.askinteger("ELO Score", "Enter White player's ELO score:", parent=self.master)
        black_elo = simpledialog.askinteger("ELO Score", "Enter Black player's ELO score:", parent=self.master)
        return white_elo, black_elo

    def calculate_initial_probabilities(self):
        delta_elo = self.white_elo - self.black_elo
        probability_white_wins = 1 / (1 + math.exp(-delta_elo / 400))
        probability_black_wins = 1 - probability_white_wins
        return probability_white_wins, probability_black_wins

    def display_elo_scores(self):
        white_elo_label = tk.Label(self.master, text=f"White ELO: {self.white_elo}", fg="black")
        white_elo_label.grid(row=9, column=0, columnspan=4, sticky="w")
        black_elo_label = tk.Label(self.master, text=f"Black ELO: {self.black_elo}", fg="blue")
        black_elo_label.grid(row=9, column=4, columnspan=4, sticky="e")

    def display_win_probabilities(self):
        self.win_prob_label = tk.Label(self.master, text=f"Win Probability - White: {self.white_win_probability*100:.1f}%, Black: {self.black_win_probability*100:.1f}%", fg="green")
        self.win_prob_label.grid(row=10, column=0, columnspan=8)

    def update_win_probabilities(self, score):
        score_difference = score - 0
        adjustment_factor = 1 / (1 + math.exp(-score_difference / 400))
        if self.current_player == chess.WHITE:
            self.white_win_probability *= adjustment_factor
        else:
            self.black_win_probability *= adjustment_factor
        total_probability = self.white_win_probability + self.black_win_probability
        self.white_win_probability /= total_probability
        self.black_win_probability /= total_probability
        self.display_win_probabilities()

    def create_board(self):
        self.buttons = [[None for _ in range(8)] for _ in range(8)]
        for row in range(8):
            for col in range(8):
                color = "#F0D9B5" if (row + col) % 2 != 0 else "#B58863"
                button = tk.Button(self.master, bg=color, width=8, height=4,
                                   command=lambda r=row, c=col: self.on_click(7-r, c))
                button.grid(row=7-row, column=col)
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
                self.buttons[7-row][col].config(text=symbol, fg=color)
            else:
                row, col = divmod(square, 8)
                self.buttons[7-row][col].config(text='', fg='black')

    def create_evaluation_bars(self):
        self.black_bar = tk.Scale(self.master, from_=-10000, to=10000, orient="horizontal", label="Black Evaluation", fg="blue")
        self.black_bar.grid(row=8, column=0, columnspan=4, sticky="ew")
        self.white_bar = tk.Scale(self.master, from_=-10000, to=10000, orient="horizontal", label="White Evaluation", fg="black")
        self.white_bar.grid(row=8, column=4, columnspan=4, sticky="ew")

    def create_move_log(self):
        log_frame = tk.Frame(self.master)
        log_frame.grid(row=0, column=9, rowspan=10, padx=10, pady=10, sticky="nsew")
        self.move_log = tk.Text(log_frame, height=20, width=95, wrap="none")
        h_scroll = tk.Scrollbar(log_frame, orient="horizontal", command=self.move_log.xview)
        self.move_log.configure(xscrollcommand=h_scroll.set)
        h_scroll.pack(side="bottom", fill="x")
        self.move_log.pack(side="top", fill="both", expand=True)
        self.move_log.insert(tk.END, "Move Log:\n")

    def on_click(self, row, col):
        adjusted_row = 7 - row
        square = chess.square(col, adjusted_row)
        piece = self.board.piece_at(square)
        if not self.board.is_game_over():
            if self.selected_piece is None and piece and piece.color == self.current_player:
                self.selected_piece = square
            elif self.selected_piece is not None:
                target_square = chess.square(col, adjusted_row)
                move = chess.Move(self.selected_piece, target_square)
                if move in self.board.legal_moves:
                    pre_move_evaluation = self.evaluate_position()
                    self.board.push(move)
                    post_move_evaluation = self.evaluate_position()
                    move_quality = self.analyze_move_quality(pre_move_evaluation, post_move_evaluation)
                    self.log_move(move, pre_move_evaluation, post_move_evaluation, is_legal=True)
                    self.current_player = not self.current_player
                    self.place_pieces()
                    self.update_evaluation()
                    self.check_game_end()

                    if self.current_player == chess.WHITE:
                        predicted_cluster_white, predicted_cluster_prob_white = self.predict_move()
                        best_move_white = self.suggest_best_move()
                        self.update_prediction_labels(predicted_cluster_white, predicted_cluster_prob_white, best_move_white)
                    else:
                        predicted_cluster_black, predicted_cluster_prob_black = self.predict_move()
                        best_move_black = self.suggest_best_move()
                        self.update_prediction_labels(predicted_cluster_black, predicted_cluster_prob_black, best_move_black)

                    self.selected_piece = None


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
            move_notation = move.uci()
            if is_legal:
                try:
                    move_notation = self.board.san(move)
                except AssertionError:
                    pass
            current_evaluation = self.evaluate_position()
            if hasattr(self, 'provide_in_depth_analysis'):
                in_depth_analysis = self.provide_in_depth_analysis()
            else:
                in_depth_analysis = "In-depth analysis not available."
            self.move_log.insert(tk.END, f"{move_notation}: Pre-move Eval: {pre_move_evaluation}, Post-move Eval: {post_move_evaluation}, Stockfish Eval: {current_evaluation}\n{in_depth_analysis}\n")
            self.save_move_to_database(move_notation)
        except Exception as e:
            self.move_log.insert(tk.END, f"Error logging move: {e}\n")
        finally:
            self.move_log.see(tk.END)

    def evaluate_position(self):
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return 0

        total_evaluation = 0
        for move in legal_moves:
            self.board.push(move)
            evaluation = self.engine.analyse(self.board, chess.engine.Limit(depth=10))['score'].white().score()
            total_evaluation += evaluation
            self.board.pop()

        return total_evaluation / len(legal_moves)

    def analyze_move_quality(self, pre_move_evaluation, post_move_evaluation):
        if self.current_player == chess.WHITE:
            delta_evaluation = post_move_evaluation - pre_move_evaluation
        else:
            delta_evaluation = pre_move_evaluation - post_move_evaluation

        if delta_evaluation > 0:
            return "Good Move!"
        elif delta_evaluation < 0:
            return "Bad Move!"
        else:
            return "Neutral Move"

    def update_evaluation(self):
        if not self.board.is_game_over():
            evaluation = self.evaluate_position()
            if self.current_player == chess.WHITE:
                self.white_bar.set(evaluation)
                self.update_win_probabilities(evaluation)
            else:
                self.black_bar.set(evaluation)
                self.update_win_probabilities(-evaluation)

    def check_game_end(self):
        if self.board.is_game_over():
            result = self.board.result()
            if result == '1-0':
                messagebox.showinfo("Game Over", "White wins!")
            elif result == '0-1':
                messagebox.showinfo("Game Over", "Black wins!")
            else:
                messagebox.showinfo("Game Over", "It's a draw!")

    def predict_move(self):
        if self.pca is None or self.classifier is None:
            print("Error: PCA or classifier is not initialized.")
            return None, None

        # Combine current game moves with database moves
        combined_moves = self.moves + self.fetch_game_moves_from_database('gameslog.db')

        # Preprocess combined moves and convert them to numerical features
        combined_features = self.vectorizer.transform(combined_moves)

        # Reduce dimensionality using PCA
        combined_features_pca = self.pca.transform(combined_features.toarray())

        # Check if the number of features matches the expected number
        if combined_features_pca.shape[1] != self.expected_num_features:
            print("Error: Number of features after PCA does not match the expected number.")
            return None, None

        # Predict cluster label and probability
        try:
            cluster_label = self.kmeans_model.predict(combined_features_pca)[-1]
            predicted_cluster_prob = self.classifier.predict_proba(combined_features_pca)[-1][cluster_label]
            predicted_cluster = self.classifier.classes_[cluster_label]

            return predicted_cluster, predicted_cluster_prob
        except AttributeError as e:
            print(f"Error occurred during prediction: {e}")
            return None, None



    def suggest_best_move(self):
        with chess.engine.SimpleEngine.popen_uci(r"C:\Users\lkirk\OneDrive\Desktop\stockfish\stockfish\stockfish-windows-x86-64.exe") as engine:
            result = engine.play(self.board, chess.engine.Limit(time=0.1))
            return result.move

    #def create_prediction_labels(self):
       # self.prediction_label = tk.Label(self.master, text="Predicted Cluster: N/A\nProbability: N/A%\nBest Move: N/A", fg="purple")
       # self.prediction_label.grid(row=11, column=0, columnspan=8)

    def create_prediction_labels(self):
        self.prediction_label_white = tk.Label(self.master, text="White's Predictions:Predicted Cluster: N/A,Probability: N/A%,Best Move: N/A", fg="purple")
        self.prediction_label_white.grid(row=11, column=0, columnspan=8)
        self.prediction_label_black = tk.Label(self.master, text="Black's Predictions:Predicted Cluster: N/A,Probability: N/A%,Best Move: N/A", fg="purple")
        self.prediction_label_black.grid(row=12, column=0, columnspan=8)

    def update_prediction_labels(self, predicted_cluster, predicted_cluster_prob, best_move):
        if self.current_player == chess.WHITE:
            self.prediction_label_white.config(text=f"White's Predictions:Predicted Cluster: {predicted_cluster},Probability: {predicted_cluster_prob:.2f},Best Move: {best_move}")
        else:
            self.prediction_label_black.config(text=f"Black's Predictions:Predicted Cluster: {predicted_cluster},Probability: {predicted_cluster_prob:.2f},Best Move: {best_move}")

    #def update_prediction_labels(self, predicted_cluster, predicted_cluster_prob, best_move):
       # self.prediction_label.config(text=f"Predicted Cluster: {predicted_cluster},Probability: {predicted_cluster_prob:.2f},Best Move: {best_move}")

    def save_move_to_database(self, move_notation):
        conn = sqlite3.connect('gameslog.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO moves (move) VALUES (?)''', (move_notation,))
        conn.commit()
        conn.close()



def main():
    root = tk.Tk()
    gui = ChessGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
