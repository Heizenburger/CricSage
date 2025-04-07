import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor

# Load processed data
match_stats = pd.read_csv('processed_data/match_stats.csv')

# Prepare features and target for score prediction
X_score = pd.get_dummies(match_stats[['venue', 'batting_team', 'bowling_team']])
y_score = match_stats['total_runs']  # Assuming total_runs is the target for score prediction

# Train the regression model
score_model = RandomForestRegressor()
score_model.fit(X_score, y_score)

# Save the model
joblib.dump(score_model, 'models/score_model.pkl')
joblib.dump(list(X_score.columns), 'models/score_model_columns.pkl')
print("Score prediction model trained and saved successfully!")