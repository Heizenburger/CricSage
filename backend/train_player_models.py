# train_player_models.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Batter model
batters = pd.read_csv('player_data/batter_features.csv')
batters['is_key_player'] = (batters['recent_runs'] > 30).astype(int)  # 30+ runs in recent matches

batter_model = RandomForestClassifier()
batter_model.fit(batters[['avg_runs', 'recent_runs', 'strike_rate']], batters['is_key_player'])
joblib.dump(batter_model, 'models/key_batter_model.pkl')

# For batters
X = batters[['avg_runs', 'recent_runs', 'strike_rate']]
y = batters['is_key_player']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
batter_model.fit(X_train, y_train)
print("Batter Model Report:\n", classification_report(y_test, batter_model.predict(X_test)))

# Bowler model
bowlers = pd.read_csv('player_data/bowler_features.csv')
bowlers['is_key_player'] = (bowlers['recent_dots'] > 12).astype(int)  # 12+ dot balls recently

bowler_model = RandomForestClassifier()
bowler_model.fit(bowlers[['avg_wickets', 'economy_rate', 'recent_dots']], bowlers['is_key_player'])
joblib.dump(bowler_model, 'models/key_bowler_model.pkl')

# For bowlers
X = bowlers[['avg_wickets', 'economy_rate', 'recent_dots']]
y = bowlers['is_key_player']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
bowler_model.fit(X_train, y_train)
print("Bowler Model Report:\n", classification_report(y_test, bowler_model.predict(X_test)))