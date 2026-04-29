import sqlite3
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import seaborn as sns

def load_data():
    conn = sqlite3.connect('player premier legaue.db')
    df = pd.read_sql_query("SELECT * FROM player_stats", conn)
    conn.close()
    return df

def prepare_features(df):
    numeric_cols = ['minutes', 'gls', 'ast', 'g_plus_a', 'mp', 'starts', 
                    'crdy', 'crdr', 'per90_gls', 'per90_ast', 'per90_g_a']
    
    df_features = df[numeric_cols].copy()
    
    for col in df_features.columns:
        df_features[col] = pd.to_numeric(df_features[col], errors='coerce')
    
    df_features = df_features.fillna(0)
    
    mask = (df_features['minutes'] > 0) & (df_features['mp'] > 0)
    df_features = df_features[mask].reset_index(drop=True)
    df_original = df[mask].copy().reset_index(drop=True)
    
    for col in ['minutes', 'gls', 'ast', 'g_plus_a', 'mp', 'starts', 
                'crdy', 'crdr', 'per90_gls', 'per90_ast', 'per90_g_a']:
        df_original[col] = pd.to_numeric(df_original[col], errors='coerce').fillna(0)
    
    return df_features, df_original

def find_optimal_k(X_scaled, k_range=range(2, 11)):
    inertias = []
    silhouette_scores = []
    
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
        inertias.append(kmeans.inertia_)
        silhouette_scores.append(silhouette_score(X_scaled, labels))
    
    return inertias, silhouette_scores

def plot_elbow_silhouette(inertias, silhouette_scores, k_range):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    axes[0].plot(k_range, inertias, 'bo-', linewidth=2, markersize=8)
    axes[0].set_xlabel('Số cụm (K)', fontsize=12)
    axes[0].set_ylabel('Inertia', fontsize=12)
    axes[0].set_title('Biểu đồ Elbow - Tìm K tối ưu', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    
    axes[1].plot(k_range, silhouette_scores, 'ro-', linewidth=2, markersize=8)
    axes[1].set_xlabel('Số cụm (K)', fontsize=12)
    axes[1].set_ylabel('Silhouette Score', fontsize=12)
    axes[1].set_title('Biểu đồ Silhouette - Đánh giá chất lượng cụm', fontsize=14, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def run_kmeans_pca(k=4):
    df = load_data()
    df_features, df_original = prepare_features(df)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_features)
    
    inertias, sil_scores = find_optimal_k(X_scaled)
    k_range = range(2, 11)
    
    fig_elbow = plot_elbow_silhouette(inertias, sil_scores, k_range)
    
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(X_scaled)
    
    df_original['cluster'] = cluster_labels
    df_features_scaled = pd.DataFrame(X_scaled, columns=df_features.columns)
    df_features_scaled['cluster'] = cluster_labels
    
    cluster_counts = df_original['cluster'].value_counts().sort_index()
    
    cluster_stats = df_original.groupby('cluster').agg({
        'player': 'count',
        'minutes': 'mean',
        'gls': 'mean',
        'ast': 'mean',
        'g_plus_a': 'mean',
        'per90_gls': 'mean',
        'per90_ast': 'mean',
        'per90_g_a': 'mean'
    }).round(2)
    cluster_stats.columns = ['Players', 'Avg_Minutes', 'Avg_Goals', 'Avg_Assists', 
                              'Avg_G+A', 'Per90_Goals', 'Per90_Assists', 'Per90_G+A']
    
    pca_2d = PCA(n_components=2)
    X_pca_2d = pca_2d.fit_transform(X_scaled)
    
    pca_3d = PCA(n_components=3)
    X_pca_3d = pca_3d.fit_transform(X_scaled)
    
    df_result = df_original.copy()
    df_result['PCA1'] = X_pca_2d[:, 0]
    df_result['PCA2'] = X_pca_2d[:, 1]
    df_result['PCA3'] = X_pca_3d[:, 2]
    
    fig_2d = plt.figure(figsize=(10, 8))
    scatter = plt.scatter(X_pca_2d[:, 0], X_pca_2d[:, 1], 
                          c=cluster_labels, cmap='viridis', 
                          alpha=0.6, s=50, edgecolors='black', linewidth=0.5)
    plt.colorbar(scatter, label='Cụm')
    plt.xlabel(f'PC1 ({pca_2d.explained_variance_ratio_[0]:.1%})', fontsize=12)
    plt.ylabel(f'PC2 ({pca_2d.explained_variance_ratio_[1]:.1%})', fontsize=12)
    plt.title('Phân cụm K-Means trên PCA 2D', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    
    centers_2d = pca_2d.transform(kmeans.cluster_centers_)
    plt.scatter(centers_2d[:, 0], centers_2d[:, 1], 
                c='red', s=200, marker='X', 
                edgecolors='black', linewidth=2, label='Tâm cụm')
    plt.legend()
    
    fig_3d = plt.figure(figsize=(12, 10))
    ax = fig_3d.add_subplot(111, projection='3d')
    scatter_3d = ax.scatter(X_pca_3d[:, 0], X_pca_3d[:, 1], X_pca_3d[:, 2],
                            c=cluster_labels, cmap='viridis',
                            alpha=0.6, s=50, edgecolors='black', linewidth=0.5)
    plt.colorbar(scatter_3d, label='Cụm', shrink=0.6)
    ax.set_xlabel(f'PC1 ({pca_3d.explained_variance_ratio_[0]:.1%})', fontsize=11)
    ax.set_ylabel(f'PC2 ({pca_3d.explained_variance_ratio_[1]:.1%})', fontsize=11)
    ax.set_zlabel(f'PC3 ({pca_3d.explained_variance_ratio_[2]:.1%})', fontsize=11)
    ax.set_title('Phân cụm K-Means trên PCA 3D', fontsize=14, fontweight='bold')
    
    centers_3d = pca_3d.transform(kmeans.cluster_centers_)
    ax.scatter(centers_3d[:, 0], centers_3d[:, 1], centers_3d[:, 2],
               c='red', s=300, marker='X',
               edgecolors='black', linewidth=2, label='Tâm cụm')
    
    return {
        'total_players': len(df_original),
        'cluster_counts': cluster_counts,
        'cluster_stats': cluster_stats,
        'df_result': df_result,
        'fig_elbow': fig_elbow,
        'fig_2d': fig_2d,
        'fig_3d': fig_3d,
        'pca_2d': pca_2d,
        'pca_3d': pca_3d,
        'kmeans': kmeans,
        'silhouette_score': silhouette_score(X_scaled, cluster_labels)
    }

if __name__ == "__main__":
    result = run_kmeans_pca(k=4)
    
    print("="*60)
    print("K-MEANS CLUSTERING RESULTS - PREMIER LEAGUE 2024/25")
    print("="*60)
    print(f"\nTotal players: {result['total_players']}")
    print(f"\nCluster distribution:")
    print(result['cluster_counts'])
    print(f"\nSilhouette Score: {result['silhouette_score']:.3f}")
    print("\nCluster statistics:")
    print(result['cluster_stats'])
    print("\nSaving plots to files...")
    
    result['fig_elbow'].savefig('elbow_silhouette.png', dpi=150, bbox_inches='tight')
    result['fig_2d'].savefig('pca_2d_clusters.png', dpi=150, bbox_inches='tight')
    result['fig_3d'].savefig('pca_3d_clusters.png', dpi=150, bbox_inches='tight')
    
    print("Plots saved: elbow_silhouette.png, pca_2d_clusters.png, pca_3d_clusters.png")
    result['df_result'].to_csv('kmeans_clustering_result.csv', index=False, encoding='utf-8-sig')
    print("CSV saved: kmeans_clustering_result.csv")
