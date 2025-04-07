# player_features.py
import pandas as pd

def create_batter_features():
    df = pd.read_csv('player_data/batters.csv')
    
    
    # Handle missing data
    df = df.fillna(0)
    df = df[df['balls'] >= 10]  # Only consider players with ≥10 balls faced
    df = df[df['runs'] > 0]  # Filter out zero-run records

    # Handle empty data
    if df.empty:
        raise ValueError("Batters data is empty! Check batters.csv")

    # Add required features
    df['strike_rate'] = df['runs'] / df['balls'] * 100  # Add this

    try:
        # Convert date if available
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(['striker', 'date'])
    except KeyError:
        # Fallback: Use match_id for ordering
        df = df.sort_values(['striker', 'match_id'])

# Feature calculation remains same
    features = df.groupby(['striker', 'team']).agg(  # Add 'team' to groupby
        avg_runs=('runs', 'mean'),
        recent_runs=('runs', lambda x: x.tail(3).mean()),
        strike_rate=('runs', lambda x: x.sum() / x.count() * 100)
    ).reset_index()

    features.to_csv('player_data/batter_features.csv', index=False)
    return features

def create_bowler_features():
    df = pd.read_csv('player_data/bowlers.csv')
    df = df[(df['balls'] >= 12)]  # Min 12 balls bowled

    if df.empty:
        raise ValueError("Bowlers data is empty! Check bowlers.csv")

    # Calculate economy rate safely
    df['economy_rate'] = df.apply(
        lambda x: (x['runs_conceded'] / (x['balls']/6)) if x['balls'] > 0 else 0,
        axis=1
    )

    try:
        # Convert date if available
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(['bowler', 'date'])
    except KeyError:
        # Fallback: Use match_id for ordering
        df = df.sort_values(['bowler', 'match_id'])

# Feature calculation remains same
    features = df.groupby(['bowler', 'team']).agg(  # Add 'team' to groupby
        avg_wickets=('wickets', 'mean'),
        economy_rate=('runs_conceded', lambda x: (x.sum() / (x.count()/6))),
        recent_dots=('dot_balls', lambda x: x.tail(3).sum())
    ).reset_index()

    features.to_csv('player_data/bowler_features.csv', index=False)
    return features

if __name__ == '__main__':
    create_batter_features()
    create_bowler_features()