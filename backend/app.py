import traceback
from flask import Flask, request, jsonify
import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TEAM_ABBREVIATIONS = {
    "MI": "Mumbai Indians",
    "CSK": "Chennai Super Kings",
    "RCB": "Royal Challengers Bangalore",
    "KKR": "Kolkata Knight Riders",
    "DC": "Delhi Capitals",
    "RR": "Rajasthan Royals",
    "GT": "Gujarat Titans",
    "LSG": "Lucknow Super Giants",
    "PBKS": "Punjab Kings",
    "SRH": "Sunrisers Hyderabad"
}

# Load model and columns
# Update the model loading section
try:
    # Win probability model
    win_model = joblib.load('models/win_model.pkl')
    model_columns = joblib.load('models/model_columns.pkl')
    
    # Score prediction model
    score_model = joblib.load('models/score_model.pkl')
    score_model_columns = joblib.load('models/score_model_columns.pkl')
    
    # Player models
    batter_model = joblib.load('models/key_batter_model.pkl')
    bowler_model = joblib.load('models/key_bowler_model.pkl')
    
    print("All models loaded successfully!")
except Exception as e:
    print(f"Error loading models: {str(e)}")
    raise e  # Add this to see full error during startup

@app.route('/api/predict', methods=['POST'])
def predict():
    if not win_model:
        return jsonify({'error': 'Model not loaded'}), 500
    print(f"Model type: {type(win_model)}")
    try:
        data = request.get_json()
        # Validate and convert team names
        team1 = data.get('team1')
        team2 = data.get('team2')

        if team1 not in TEAM_ABBREVIATIONS or team2 not in TEAM_ABBREVIATIONS:
            return jsonify({'error': 'Invalid team name provided'}), 400
        
        if not data:
            return jsonify({'error': 'No data received'}), 400

        # Validate required fields
        required = ['team1', 'team2', 'venue']
        if not all(k in data for k in required):
            return jsonify({'error': f'Missing required fields. Needed: {required}'}), 400

        # Create input dataframe
        input_df = pd.DataFrame([{
            'venue': data['venue'],
            'batting_team': TEAM_ABBREVIATIONS[team1],  # Use abbreviation for processing
            'bowling_team': TEAM_ABBREVIATIONS[team2]  
        }])

        # Create dummy variables
        input_encoded = pd.get_dummies(input_df)
        
        # Align columns with training data
        missing_cols = set(model_columns) - set(input_encoded.columns)
        for col in missing_cols:
            input_encoded[col] = 0
        input_encoded = input_encoded[model_columns]
        
        input_score_df = pd.DataFrame([{
            'venue': data['venue'],
            'batting_team': team1,
            'bowling_team': team2
        }])
        
        input_score_encoded = pd.get_dummies(input_score_df)
        missing_score_cols = set(score_model_columns) - set(input_score_encoded.columns)
        for col in missing_score_cols:
            input_score_encoded[col] = 0
        input_score_encoded = input_score_encoded[score_model_columns]
        
        # Get prediction
        if hasattr(win_model, 'predict_proba'):
            win_prob = win_model.predict_proba(input_encoded)[0]
            score_prediction = score_model.predict(input_score_encoded)[0]
        else:  # Fallback for regression models
            score_prediction = win_model.predict(input_encoded)[0]
            win_prob = [1 - score_prediction, score_prediction]  # Simple normalization
        
        return jsonify({
            'team1': team1,
            'team2': team2,
            'winProbability': {
                team1: f"{win_prob[1]*100:.1f}%",
                team2: f"{win_prob[0]*100:.1f}%"
            },
            'predictedScore': f"{int(score_prediction - 10)}-{int(score_prediction + 10)}"
        })

    except Exception as e:
        app.logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': str(e), 'message': 'Prediction failed'}), 500

@app.route('/api/predict_players', methods=['POST'])
def predict_players():
    try:
        data = request.get_json()

        # Load FEATURE-ENGINEERED data
        batters = pd.read_csv('player_data/batter_features.csv')
        bowlers = pd.read_csv('player_data/bowler_features.csv')

        # Validate team abbreviations
        team1 = data['team1']
        team2 = data['team2']

        # Get top 3 batters and bowlers FROM FEATURE DATA
        team_batters = batters[batters['team'] == team1].nlargest(3, 'avg_runs')
        team_bowlers = bowlers[bowlers['team'] == team2].nsmallest(3, 'economy_rate')

        # Create predictions
        key_players = {}
        for _, batter in team_batters.iterrows():
            prob = batter_model.predict_proba([[
                batter['avg_runs'],
                batter['recent_runs'],
                batter['strike_rate']
            ]])[0][1]
            prob_percent = max(1.0, min(99.0, prob*100))  # No 0% or 100%
            key_players[batter['striker']] = f"{prob_percent:.1f}%"

        for _, bowler in team_bowlers.iterrows():
            prob = bowler_model.predict_proba([[
                bowler['avg_wickets'],
                bowler['economy_rate'],
                bowler['recent_dots']
            ]])[0][1]
            key_players[bowler['bowler']] = f"{prob*100:.1f}%"

        return jsonify({'key_players': key_players})

    except Exception as e:
        app.logger.error(f"Player prediction error: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)