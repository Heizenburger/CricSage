# data_preprocessing.py
import pandas as pd
import os

def combine_ipl_data(data_folder='ipl_data'):
    all_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
    dfs = [pd.read_csv(os.path.join(data_folder, f)) for f in all_files]
    return pd.concat(dfs, ignore_index=True)

def preprocess_data(df):
    """Original match stats processing"""
    os.makedirs('processed_data', exist_ok=True)
    
    # Match stats calculation
    match_stats = df.groupby(['match_id', 'venue', 'batting_team', 'bowling_team']).agg(
        total_runs=('runs_of_bat', 'sum'),
        avg_runs=('runs_of_bat', 'mean'),
        max_runs=('runs_of_bat', 'max'),
        wickets=('player_dismissed', 'count'),
        deliveries=('wicket_type', 'count')
    ).reset_index()
    
    match_stats.to_csv('processed_data/match_stats.csv', index=False)
    print(f"Processed {len(match_stats)} matches!")
    return match_stats

# Add new function for 2025 player data
def create_2025_player_stats():
    """Create player stats using ONLY 2025 data"""
    os.makedirs('player_data', exist_ok=True)
    
    # Load specific 2025 data
    df_2025 = pd.read_csv('ipl_data/ipl_2025_deliveries.csv')

    # Process batters (2025 only)
    batters_2025 = df_2025.groupby(['striker', 'match_id', 'venue', 'batting_team']).agg(
        runs=('runs_of_bat', 'sum'),
        balls=('runs_of_bat', 'count'),
        fours=('runs_of_bat', lambda x: (x == 4).sum()),
        sixes=('runs_of_bat', lambda x: (x == 6).sum())
    ).reset_index().rename(columns={'batting_team': 'team'})

    # Process bowlers (2025 only)
    bowlers_2025 = df_2025.groupby(['bowler', 'match_id', 'venue', 'bowling_team']).agg(
        wickets=('player_dismissed', 'count'),
        runs_conceded=('runs_of_bat', 'sum'),
        balls=('runs_of_bat', 'count'),
        dot_balls=('runs_of_bat', lambda x: (x == 0).sum())
    ).reset_index().rename(columns={'bowling_team': 'team'})

    # Overwrite player data with 2025-only records
    batters_2025.to_csv('player_data/batters.csv', index=False)
    bowlers_2025.to_csv('player_data/bowlers.csv', index=False)

if __name__ == '__main__':
    try:
        print("Starting processing...")
        # Process ALL data for win/scores
        df = combine_ipl_data()  
        preprocess_data(df)
    
        # Process 2025-only for players
        create_2025_player_stats()  
        print("All data processed successfully!")
    except Exception as e:
        print(f"Error: {str(e)}")