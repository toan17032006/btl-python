import sqlite3
import pandas as pd
import numpy as np

def load_data():
    conn = sqlite3.connect('player premier legaue.db')
    df = pd.read_sql_query("SELECT * FROM player_stats", conn)
    conn.close()
    return df

def prepare_data(df):
    numeric_cols = ['minutes', 'gls', 'ast', 'g_plus_a', 'mp', 'starts', 
                    'crdy', 'crdr', 'per90_gls', 'per90_ast', 'per90_g_a']
    
    df_processed = df.copy()
    for col in numeric_cols:
        df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce').fillna(0)
    
    df_processed = df_processed[df_processed['minutes'] > 0]
    
    return df_processed

def calculate_team_stats(df):
    numeric_cols = ['minutes', 'gls', 'ast', 'g_plus_a', 'mp', 'starts', 
                    'crdy', 'crdr', 'per90_gls', 'per90_ast', 'per90_g_a']
    
    stats_list = []
    
    for squad in df['squad'].unique():
        team_df = df[df['squad'] == squad]
        
        for col in numeric_cols:
            values = team_df[col]
            stats_list.append({
                'squad': squad,
                'statistic': col,
                'mean': values.mean(),
                'median': values.median(),
                'std': values.std(),
                'count': len(values),
                'sum': values.sum(),
                'max': values.max(),
                'min': values.min()
            })
    
    stats_df = pd.DataFrame(stats_list)
    
    pivot_stats = stats_df.pivot_table(
        index='squad', 
        columns='statistic',
        values=['mean', 'median', 'std'],
        aggfunc='first'
    )
    
    pivot_stats.columns = ['_'.join(col).strip() for col in pivot_stats.columns.values]
    pivot_stats = pivot_stats.reset_index()
    
    return stats_df, pivot_stats

def find_best_teams(df):
    numeric_cols = ['minutes', 'gls', 'ast', 'g_plus_a', 'mp', 'starts', 
                    'per90_gls', 'per90_ast', 'per90_g_a']
    
    best_teams = {}
    
    for col in numeric_cols:
        team_sums = df.groupby('squad')[col].sum()
        best_team = team_sums.idxmax()
        best_value = team_sums.max()
        best_teams[col] = {
            'team': best_team,
            'value': best_value
        }
    
    team_power_ranking = df.groupby('squad').agg({
        'gls': 'sum',
        'ast': 'sum',
        'g_plus_a': 'sum',
        'per90_gls': 'mean',
        'per90_ast': 'mean',
        'per90_g_a': 'mean',
        'minutes': 'sum',
        'mp': 'sum'
    }).round(2)
    
    team_power_ranking.columns = ['Total_Goals', 'Total_Assists', 'Total_G+A', 
                                   'Avg_Per90_Goals', 'Avg_Per90_Assists', 'Avg_Per90_G+A',
                                   'Total_Minutes', 'Total_Matches']
    
    team_power_ranking['Offensive_Score'] = (
        team_power_ranking['Total_Goals'] * 0.4 + 
        team_power_ranking['Total_Assists'] * 0.3 + 
        team_power_ranking['Avg_Per90_G+A'] * 10 * 0.3
    )
    
    return best_teams, team_power_ranking

def main():
    print("Loading data...")
    df = load_data()
    df_processed = prepare_data(df)
    
    print(f"Total players analyzed: {len(df_processed)}")
    print(f"Total teams: {df_processed['squad'].nunique()}")
    
    print("\n" + "="*70)
    print("PART 1: TEAM STATISTICS (MEAN, MEDIAN, STD)")
    print("="*70)
    
    stats_df, pivot_stats = calculate_team_stats(df_processed)
    
    pivot_stats.to_csv('team_statistics_mean_median_std.csv', index=False, encoding='utf-8-sig')
    print("\nSaved: team_statistics_mean_median_std.csv")
    
    print("\nSample of team statistics:")
    print(pivot_stats.head(10).to_string())
    
    print("\n" + "="*70)
    print("PART 2: BEST TEAM FOR EACH STATISTIC")
    print("="*70)
    
    best_teams, team_power_ranking = find_best_teams(df_processed)
    
    print("\nTeam with highest value for each statistic:")
    for stat, info in best_teams.items():
        print(f"  {stat}: {info['team']} ({info['value']:.2f})")
    
    best_teams_df = pd.DataFrame([
        {'statistic': stat, 'best_team': info['team'], 'total_value': info['value']}
        for stat, info in best_teams.items()
    ])
    best_teams_df.to_csv('best_teams_by_statistic.csv', index=False, encoding='utf-8-sig')
    print("\nSaved: best_teams_by_statistic.csv")
    
    print("\n" + "="*70)
    print("PART 3: TEAM POWER RANKING")
    print("="*70)
    
    team_power_ranking = team_power_ranking.sort_values('Offensive_Score', ascending=False)
    
    print("\nTop 10 Teams by Offensive Score:")
    print(team_power_ranking.head(10).to_string())
    
    team_power_ranking.to_csv('team_power_ranking.csv', encoding='utf-8-sig')
    print("\nSaved: team_power_ranking.csv")
    
    print("\n" + "="*70)
    print("CONCLUSION: BEST TEAM IN PREMIER LEAGUE 2024/25")
    print("="*70)
    
    best_offensive = team_power_ranking.index[0]
    best_goals = df_processed.groupby('squad')['gls'].sum().idxmax()
    best_assists = df_processed.groupby('squad')['ast'].sum().idxmax()
    best_per90 = df_processed.groupby('squad')['per90_g_a'].mean().idxmax()
    
    print(f"\n  Best Offensive Score: {best_offensive}")
    print(f"  Most Goals Scored: {best_goals}")
    print(f"  Most Assists: {best_assists}")
    print(f"  Best Per90 G+A: {best_per90}")
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE!")
    print("="*70)
    print("\nGenerated files:")
    print("  1. team_statistics_mean_median_std.csv - Full stats per team")
    print("  2. best_teams_by_statistic.csv - Best team for each stat")
    print("  3. team_power_ranking.csv - Team power ranking")

if __name__ == "__main__":
    main()
