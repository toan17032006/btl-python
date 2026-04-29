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
    
    for col in numeric_cols:
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
    axes[0].set_xlabel('Number of Clusters (K)', fontsize=12)
    axes[0].set_ylabel('Inertia (Within-cluster variance)', fontsize=12)
    axes[0].set_title('Elbow Method - Find Optimal K', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    for i, v in enumerate(inertias):
        axes[0].annotate(f'{v:.0f}', (k_range[i], v), textcoords="offset points", 
                        xytext=(0,10), ha='center', fontsize=9)
    
    axes[1].plot(k_range, silhouette_scores, 'ro-', linewidth=2, markersize=8)
    axes[1].set_xlabel('Number of Clusters (K)', fontsize=12)
    axes[1].set_ylabel('Silhouette Score', fontsize=12)
    axes[1].set_title('Silhouette Analysis - Cluster Quality', fontsize=14, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    axes[1].axhline(y=0, color='k', linestyle='--', linewidth=1)
    for i, v in enumerate(silhouette_scores):
        axes[1].annotate(f'{v:.3f}', (k_range[i], v), textcoords="offset points", 
                        xytext=(0,10), ha='center', fontsize=9)
    
    plt.tight_layout()
    return fig

def analyze_clusters(X_scaled, df_original, k=4):
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(X_scaled)
    
    df_original['cluster'] = cluster_labels
    
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
    
    return cluster_stats, cluster_labels, kmeans

def plot_pca_scatter(X_scaled, cluster_labels, kmeans, n_components=2):
    pca = PCA(n_components=n_components)
    X_pca = pca.fit_transform(X_scaled)
    
    if n_components == 2:
        fig, ax = plt.subplots(figsize=(10, 8))
        scatter = ax.scatter(X_pca[:, 0], X_pca[:, 1], 
                            c=cluster_labels, cmap='viridis', 
                            alpha=0.6, s=50, edgecolors='black', linewidth=0.5)
        plt.colorbar(scatter, label='Cluster', ax=ax)
        
        centers_pca = pca.transform(kmeans.cluster_centers_)
        ax.scatter(centers_pca[:, 0], centers_pca[:, 1], 
                  c='red', s=300, marker='X', 
                  edgecolors='black', linewidth=2, label='Centroids')
        
        ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)', fontsize=12)
        ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)', fontsize=12)
        ax.set_title(f'PCA 2D Scatter Plot - K-Means Clustering (K={len(np.unique(cluster_labels))})', 
                    fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
    elif n_components == 3:
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        scatter = ax.scatter(X_pca[:, 0], X_pca[:, 1], X_pca[:, 2],
                            c=cluster_labels, cmap='viridis',
                            alpha=0.6, s=50, edgecolors='black', linewidth=0.5)
        plt.colorbar(scatter, label='Cluster', ax=ax, shrink=0.6)
        
        centers_pca = pca.transform(kmeans.cluster_centers_)
        ax.scatter(centers_pca[:, 0], centers_pca[:, 1], centers_pca[:, 2],
                  c='red', s=400, marker='X',
                  edgecolors='black', linewidth=2, label='Centroids')
        
        ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%})', fontsize=11)
        ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%})', fontsize=11)
        ax.set_zlabel(f'PC3 ({pca.explained_variance_ratio_[2]:.1%})', fontsize=11)
        ax.set_title(f'PCA 3D Scatter Plot - K-Means Clustering (K={len(np.unique(cluster_labels))})', 
                    fontsize=14, fontweight='bold')
        ax.legend()
    
    return fig, pca

def main():
    print("Loading data...")
    df = load_data()
    df_features, df_original = prepare_features(df)
    
    print("Scaling features...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_features)
    
    print("Finding optimal K...")
    k_range = range(2, 11)
    inertias, sil_scores = find_optimal_k(X_scaled, k_range)
    
    print("\n" + "="*70)
    print("PART 1: OPTIMAL K SELECTION")
    print("="*70)
    
    print("\nElbow Method Results:")
    for k, inertia in zip(k_range, inertias):
        print(f"  K={k}: Inertia = {inertia:.2f}")
    
    print("\nSilhouette Scores:")
    for k, score in zip(k_range, sil_scores):
        print(f"  K={k}: Silhouette = {score:.3f}")
    
    best_k_silhouette = k_range[np.argmax(sil_scores)]
    print(f"\nBest K by Silhouette Score: {best_k_silhouette} (score = {max(sil_scores):.3f})")
    
    fig_elbow = plot_elbow_silhouette(inertias, sil_scores, k_range)
    fig_elbow.savefig('elbow_silhouette_analysis.png', dpi=150, bbox_inches='tight')
    print("Saved: elbow_silhouette_analysis.png")
    
    print("\n" + "="*70)
    print("PART 2: K-MEANS CLUSTERING WITH K=4")
    print("="*70)
    
    cluster_stats, cluster_labels, kmeans = analyze_clusters(X_scaled, df_original, k=4)
    
    print("\nCluster Distribution:")
    print(df_original['cluster'].value_counts().sort_index())
    
    print("\nCluster Statistics:")
    print(cluster_stats)
    
    sil_score = silhouette_score(X_scaled, cluster_labels)
    print(f"\nOverall Silhouette Score: {sil_score:.3f}")
    
    print("\n" + "="*70)
    print("PART 3: PCA VISUALIZATION")
    print("="*70)
    
    fig_2d, pca_2d = plot_pca_scatter(X_scaled, cluster_labels, kmeans, n_components=2)
    fig_2d.savefig('pca_2d_scatter.png', dpi=150, bbox_inches='tight')
    print(f"\nPCA 2D: PC1={pca_2d.explained_variance_ratio_[0]:.1%}, PC2={pca_2d.explained_variance_ratio_[1]:.1%}")
    print("Total variance retained: {pca_2d.explained_variance_ratio_.sum():.1%}")
    print("Saved: pca_2d_scatter.png")
    
    fig_3d, pca_3d = plot_pca_scatter(X_scaled, cluster_labels, kmeans, n_components=3)
    fig_3d.savefig('pca_3d_scatter.png', dpi=150, bbox_inches='tight')
    print(f"\nPCA 3D: PC1={pca_3d.explained_variance_ratio_[0]:.1%}, PC2={pca_3d.explained_variance_ratio_[1]:.1%}, PC3={pca_3d.explained_variance_ratio_[2]:.1%}")
    print("Total variance retained: {pca_3d.explained_variance_ratio_.sum():.1%}")
    print("Saved: pca_3d_scatter.png")
    
    df_result = df_original.copy()
    df_result['PCA1'] = pca_2d.transform(X_scaled)[:, 0]
    df_result['PCA2'] = pca_2d.transform(X_scaled)[:, 1]
    df_result.to_csv('kmeans_pca_results.csv', index=False, encoding='utf-8-sig')
    print("\nSaved: kmeans_pca_results.csv")
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE!")
    print("="*70)
    print("\nGenerated files:")
    print("  1. elbow_silhouette_analysis.png - Elbow & Silhouette plots")
    print("  2. pca_2d_scatter.png - 2D PCA scatter plot")
    print("  3. pca_3d_scatter.png - 3D PCA scatter plot")
    print("  4. kmeans_pca_results.csv - Full results with cluster assignments")

if __name__ == "__main__":
    main()
