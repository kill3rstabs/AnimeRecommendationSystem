import pandas as pd
import random
# from flask import Flask, jsonify, request

# app = Flask(__name__)

def fetch_random_games(game_tags, user_id, num_games=100):
    # Read datasets
    game_data = pd.read_csv('Dataset\Cleaned_games.csv')
    interaction_data = pd.read_csv(r'Dataset\user_item_matrix.csv')

    # Filter games with specified tags
    similar_games = game_data[game_data['tags'].apply(lambda x: any(tag in x for tag in game_tags))]

    # Filter out games already interacted by the user
    if user_id in interaction_data.columns:
        user_interactions = interaction_data[user_id]
        similar_games = similar_games[~similar_games['title'].isin(user_interactions[user_interactions == 1].index)]

    # If there are no similar games or all similar games are already rated, return empty dictionary
    if len(similar_games) == 0:
        return {}

    # Sample random games from the filtered list
    random_games = similar_games.sample(n=min(num_games, len(similar_games)))

    # Create dictionary of random games
    random_games_dict = {title: 1 for title in random_games['title']}

    return random_games_dict

def generate_interaction_matrix(games_dict, tags_list):

    dataset = pd.read_csv("Dataset\Cleaned_games.csv")

    interaction_matrix = []

    for game in games_dict.keys():

        row = []


        if game in dataset['title'].values:

            game_tags = dataset.loc[dataset['title'] == game, 'tags'].iloc[0]
            game_tags = game_tags.strip("[]").replace("'", "")
            game_tags_list = game_tags.split(', ')


            for tag in tags_list:
                if tag in game_tags_list:
                    row.append(1)  
                else:
                    row.append(0)  
        else:
            row.extend([0] * len(tags_list))

        interaction_matrix.append(row)

    interaction_df = pd.DataFrame(interaction_matrix, columns=tags_list, index=games_dict.keys())

    return interaction_df

def multiply_rating(interaction_matrix, games_dict):
    for game, rating in games_dict.items():
        interaction_matrix.loc[game] *= rating

    return interaction_matrix



def get_game_details(games):
    dataset = pd.read_csv("Dataset\Cleaned_games.csv")
    all_tags = set()

    for game in games:
        if game in dataset['title'].values:
            tags = dataset.loc[dataset['title'] == game, 'tags'].iloc[0]
            tags = tags.strip("[]").replace("'", "")  
            tags_list = tags.split(', ')
            all_tags.update(tags_list)

    unique_tags = list(all_tags)

    return unique_tags


def content_based_recommendation(user_profile, random_games_im):

    recommended_matrix = random_games_im.copy()
    for tag in user_profile.index:
        recommended_matrix[tag] *= user_profile[tag]

    return recommended_matrix

def check_games(games,user_id):
    print(games)

    game_tags = get_game_details(games)
    print(game_tags)


    games_interaction_matrix = generate_interaction_matrix(games, game_tags)

    games_matrix = multiply_rating(games_interaction_matrix, games)
    print(games_matrix)

    column_sums = games_matrix.sum(axis=0)

    total_sum = games_matrix.sum().sum()

    user_profile = column_sums / total_sum

    print(user_profile)

    random_games = fetch_random_games(game_tags, user_id)
    print(random_games)

    random_games_im=generate_interaction_matrix(random_games, game_tags)
    print(random_games_im)


    recommendation= content_based_recommendation(user_profile, random_games_im)
    print(recommendation)

    rec_weighted_sum = recommendation.sum(axis=1)

    sorted_rec_weighted_sum= rec_weighted_sum.sort_values(ascending=False)

    return sorted_rec_weighted_sum.index[:5]


if __name__ == '__main__':
    games = ['Escape Dead Island', 'BRINK: Agents of Change', "Monaco: What's Yours Is Mine"]
    user_rating = [2, 8, 10]
    user_id = 58
    combined_dict = dict(zip(games, user_rating))

    recommendation = check_games(combined_dict, user_id)

    print("Top 5 movie Recommendation")
    for games in recommendation:
        print(games)
