import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier

# Load processed data
match_stats = pd.read_csv('processed_data/match_stats.csv')

# Add validation
print("Column structure:\n", match_stats.dtypes)
print("Sample data:\n", match_stats.head(3))

# Ensure numeric types
match_stats['total_runs'] = pd.to_numeric(match_stats['total_runs'], errors='coerce')
match_stats = match_stats.dropna(subset=['total_runs'])

# Prepare features and target
X = pd.get_dummies(match_stats[['venue', 'batting_team', 'bowling_team']])
y = (match_stats['total_runs'] > match_stats.groupby('match_id')['total_runs'].transform('mean')).astype(int)

win_model = RandomForestClassifier()  # Correct variable name
win_model.fit(X, y)


joblib.dump(win_model, 'models/win_model.pkl')
joblib.dump(list(X.columns), 'models/model_columns.pkl')
print("Model trained and saved successfully!")