from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Sample user-item matrix (replace this with your data)
data = {
    'User1': [5, 4, 0, 0, 3],
    'User2': [0, 5, 4, 0, 4],
    'User3': [4, 0, 0, 5, 0],
    'User4': [0, 0, 5, 0, 4],
    'User5': [0, 4, 0, 3, 5]
}
items = ['Item1', 'Item2', 'Item3', 'Item4', 'Item5']

# Convert data to DataFrame
df = pd.DataFrame(data, index=items)

# Function to calculate similarity between users
def calculate_similarity(user1, user2):
    user1_ratings = df.loc[:, user1]
    user2_ratings = df.loc[:, user2]
    common_items = ~(user1_ratings.isna() | user2_ratings.isna())
    if not common_items.any():
        return np.nan  # No common items
    user1_ratings = user1_ratings[common_items]
    user2_ratings = user2_ratings[common_items]
    return cosine_similarity([user1_ratings], [user2_ratings])[0][0]

# Function to get top N similar users for a given user
def get_top_similar_users(target_user, n=5):
    similarities = [(user, calculate_similarity(target_user, user)) for user in df.columns if user != target_user]
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:n]

# Function to generate recommendations for a user
def generate_recommendations(target_user, n=5):
    top_similar_users = get_top_similar_users(target_user)
    target_user_ratings = df.loc[:, target_user]
    recommendations = {}
    for item in df.index:
        if pd.isna(target_user_ratings[item]) or target_user_ratings[item] == 0:
            numerator = 0
            denominator = 0
            for user, similarity in top_similar_users:
                user_rating = df.loc[item, user]
                if not pd.isna(user_rating) and user_rating != 0:
                    numerator += similarity * user_rating
                    denominator += similarity
            if denominator != 0:
                recommendations[item] = numerator / denominator
    recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
    return recommendations[:n]

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    target_user = data.get('user')
    recommendations = generate_recommendations(target_user)
    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True)
