# -*- coding: utf-8 -*-
"""
generate_plots_if_missing.py

- Kiểm tra 4 file ảnh (elbow.png, silhouette.png, pca_2d.png, pca_3d.png).
- Nếu bất kỳ ảnh nào thiếu sẽ thực hiện lại toàn bộ quy trình K‑means + PCA và tạo lại những ảnh còn thiếu.
- Nếu đã có thì không làm gì (tiết kiệm thời gian).
"""

import os, json, sqlite3
import pandas as pd, numpy as np
import matplotlib
matplotlib.use('Agg')               # backend không cần GUI
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

# ------------------------------------------------------------------
# Cấu hình
# ------------------------------------------------------------------
DB_PATH = r'C:\\Users\\Admin\\Desktop\\btl code\\player premier legaue.db'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
IMG_FILES = {
    "elbow":      os.path.join(BASE_DIR, "elbow.png"),
    "silhouette": os.path.join(BASE_DIR, "silhouette.png"),
    "pca2d":      os.path.join(BASE_DIR, "pca_2d.png"),
    "pca3d":      os.path.join(BASE_DIR, "pca_3d.png"),
}

NON_NUMERIC = {"id", "player", "nation", "pos", "squad", "age", "born"}

# ------------------------------------------------------------------
def file_missing(key):
    return not os.path.isfile(IMG_FILES[key])

def load_player_stats(db_path):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM player_stats", conn)
    conn.close()
    return df

def numeric_dataframe(df):
    cols = [c for c in df.columns if c not in NON_NUMERIC]
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    return df[cols]

def evaluate_kmeans(X, ks):
    inertia, sil = [], []
    for k in ks:
        km = KMeans(n_clusters=k, random_state=42, n_init='auto')
        lbl = km.fit_predict(X)
        inertia.append(km.inertia_)
        sil.append(silhouette_score(X, lbl) if k>1 else np.nan)
    return inertia, sil

def plot_curve(x, y, title, xl, yl, out):
    plt.figure(figsize=(6,4))
    plt.plot(x, y, marker='o')
    plt.title(title)
    plt.xlabel(xl)
    plt.ylabel(yl)
    plt.xticks(x)
    plt.grid(True, ls='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(out)
    plt.close()

def plot_pca_2d(data, labels, out):
    plt.figure(figsize=(6,5))
    for lab in np.unique(labels):
        idx = labels==lab
        plt.scatter(data[idx,0], data[idx,1], label=f'Cluster {lab}', alpha=0.7, edgecolor='k')
    plt.title('PCA (2D) – K‑means clusters')
    plt.xlabel('Component 1')
    plt.ylabel('Component 2')
    plt.legend()
    plt.tight_layout()
    plt.savefig(out)
    plt.close()

def plot_pca_3d(data, labels, out):
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
    fig = plt.figure(figsize=(7,5))
    ax = fig.add_subplot(111, projection='3d')
    for lab in np.unique(labels):
        idx = labels==lab
        ax.scatter(data[idx,0], data[idx,1], data[idx,2], label=f'Cluster {lab}', depthshade=True)
    ax.set_title('PCA (3D) – K‑means clusters')
    ax.set_xlabel('Component 1')
    ax.set_ylabel('Component 2')
    ax.set_zlabel('Component 3')
    ax.legend()
    plt.tight_layout()
    plt.savefig(out)
    plt.close()

# ------------------------------------------------------------------
def main():
    need_plot = any(file_missing(k) for k in IMG_FILES)
    if not need_plot:
        print('All plot files already exist – nothing to do.')
        return
    print('Missing plot(s) detected – recomputing...')

    # Load & preprocess
    df_raw = load_player_stats(DB_PATH)
    df_num = numeric_dataframe(df_raw)
    scaler = StandardScaler()
    X = scaler.fit_transform(df_num.values)

    ks = range(2, 11)
    inertia, sil = evaluate_kmeans(X, ks)

    # Elbow & Silhouette (only if missing)
    if file_missing('elbow'):
        plot_curve(list(ks), inertia, 'Elbow Method', 'Number of clusters (k)', 'Inertia', IMG_FILES['elbow'])
        print('-> elbow.png created')
    if file_missing('silhouette'):
        plot_curve(list(ks), sil, 'Silhouette Score', 'Number of clusters (k)', 'Score', IMG_FILES['silhouette'])
        print('-> silhouette.png created')

    # Choose best k (max silhouette)
    k_opt = max([(k, s) for k, s in zip(ks, sil) if not np.isnan(s)], key=lambda x: x[1])[0]
    print(f'Recommended k = {k_opt}')

    km = KMeans(n_clusters=k_opt, random_state=42, n_init='auto')
    labels = km.fit_predict(X)

    if file_missing('pca2d'):
        pca2 = PCA(n_components=2, random_state=42)
        X2 = pca2.fit_transform(X)
        plot_pca_2d(X2, labels, IMG_FILES['pca2d'])
        print('-> pca_2d.png created')
    if file_missing('pca3d'):
        pca3 = PCA(n_components=3, random_state=42)
        X3 = pca3.fit_transform(X)
        plot_pca_3d(X3, labels, IMG_FILES['pca3d'])
        print('-> pca_3d.png created')

    # Optional: save dataframe with clusters & summary
    df_raw['cluster'] = labels
    df_raw.to_csv('player_stats_with_clusters.csv', index=False)
    df_raw.groupby('cluster')[df_num.columns].mean().reset_index().to_csv('cluster_summary.csv', index=False)

    insights = {
        'k_opt': k_opt,
        'silhouette_scores': {k: round(s,3) for k, s in zip(ks, sil) if not np.isnan(s)}
    }
    print('\nInsights:')
    print(json.dumps(insights, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
