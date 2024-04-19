from sklearn.ensemble import RandomForestClassifier
import numpy as np
import chess
import chess.engine
import pandas as pd
import pickle

CSVPATH = "chess_features.csv"

class chessGame:
    ...
    def __init__(self):
        ...
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)

    def train_model(self, X_train, y_train):
        self.model.fit(X_train, y_train)

    def softmax(self, x):
        """Adjust values of x such that sum(x)=1, allowing interpretation as probability"""
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum(axis=0)

    def evaluate_position(self):
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return 0  # No legal moves implies a stalemate or checkmate scenario
        
        move_features = [self.features(move) for move in legal_moves]  # Extract features for each move
        move_features = np.array(move_features)  # Convert to numpy array for sklearn
        
        move_scores = self.model.predict_proba(move_features)[:, 1]  # Predict probabilities for class 1 (e.g., good move)
        move_probabilities = self.softmax(move_scores)  # Apply softmax to convert scores to probabilities

        total_evaluation = 0
        for i, move in enumerate(legal_moves):
            self.board.push(move)
            move_evaluation = self.engine.analyse(self.board, chess.engine.Limit(time=0.1))["score"].white().score(mate_score=10000)
            self.board.pop()
            total_evaluation += move_probabilities[i] * move_evaluation  # Weighted sum of evaluations

        return total_evaluation

def main():
    CG = chessGame()
    df = pd.read_csv(CSVPATH)
    y_train = df['MovePlayed']
    x_train = df.drop(columns=['MovePlayed'])
    CG.train_model(x_train,y_train)
    # predict probabilities; amplify differences so p(m) is still differentiable after softmax is applied
    scaling_factor = 5
    probabilities = np.array(CG.model.predict_proba(x_train[150:250]))*scaling_factor 
    print("Probabilities on the training data:")
    pVec = np.array(CG.softmax(probabilities[:,1]))
    print(pVec)
    print(sum(pVec))
    print(max(pVec))
    print(min(pVec))
    with open('RF_model.pkl', 'wb') as file:
        pickle.dump(CG.model, file)

if __name__ == "__main__":
    main()