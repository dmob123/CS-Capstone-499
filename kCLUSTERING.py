import matplotlib.pyplot as plt
import sqlite3
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD


# Function to fetch chess game moves from the database
def fetch_game_moves_from_database(database_path):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("SELECT move FROM moves")
    moves = cursor.fetchall()
    conn.close()
    return [move[0] for move in moves]


# Function to convert chess moves to numerical features
def preprocess_moves(moves):
    vectorizer = CountVectorizer(analyzer='word', lowercase=False)
    features = vectorizer.fit_transform(moves)
    return features


# Function to perform K-Means clustering
def kmeans_clustering(features, num_clusters):
    kmeans = KMeans(n_clusters=num_clusters)
    kmeans.fit(features)
    return kmeans.labels_


# Main function
def main():
    # Fetch chess game moves from the database
    database_path = 'gameslog.db'
    moves = fetch_game_moves_from_database(database_path)


    # Preprocess moves and convert them to numerical features
    features = preprocess_moves(moves)


    # Reduce dimensionality using TruncatedSVD (similar to PCA but for sparse data)
    svd = TruncatedSVD(n_components=2)  # Reduced to 2 dimensions for plotting
    features_svd = svd.fit_transform(features)


    # Define the number of clusters for K-Means
    num_clusters = 5  # Adjust as needed


    # Perform K-Means clustering
    cluster_labels = kmeans_clustering(features_svd, num_clusters)


    # Output cluster labels
    print("Cluster labels:")
    for i in range(len(moves)):
        print(f"Game {i+1}: Cluster {cluster_labels[i]}")


    # Plot the clustered data
    plt.figure(figsize=(8, 6))
    for cluster in range(num_clusters):
        plt.scatter(features_svd[cluster_labels == cluster, 0],
                    features_svd[cluster_labels == cluster, 1],
                    label=f'Cluster {cluster}')
    plt.title('Clustered Data')
    plt.xlabel('Principal Component 1')
    plt.ylabel('Principal Component 2')
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()



