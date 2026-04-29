import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Premier League Stats", layout="wide")
st.title("⚽ Thống Kê Cầu Thủ Premier League")

col1, col2, col3 = st.columns([3, 3, 1])
with col1:
    name = st.text_input("Ten cầu thủ")
with col2:
    club = st.text_input("Tên club")
with col3:
    search_btn = st.button("Tìm kiếm")

url = "http://127.0.0.1:5000/api/stats"

if search_btn or (name.strip() or club.strip()):
    params = {}
    if name.strip():
        params['name'] = name
    if club.strip():
        params['club'] = club
    with st.spinner("Truy vấn dữ liệu"):
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if data.get("error"):
            st.error(f" Lỗi từ server: {data['error']}")
        elif data.get("total", 0) == 0:
            st.warning(" Không tìm thấy cầu thủ nào phù hợp.")
        else:
            st.success(f" Tìm thấy {data['total']} cầu thủ")
            df = pd.DataFrame(data["players"])
            
            column_map = {
                "player": "Tên cầu thủ", "cau_thu": "Tên cầu thủ",
                "club": "Câu lạc bộ", "cau_lac_bo": "Câu lạc bộ",
                "goals": "Bàn thắng", "ban_thang": "Bàn thắng",
                "assists": "Kiến tạo", "kien_tao": "Kiến tạo",
                "matches": "Trận đấu", "tran_dau": "Trận đấu",
                "position": "Vị trí", "vi_tri": "Vị trí"
            }
            df = df.rename(columns={k: v for k, v in column_map.items() if k in df.columns})
            st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("👉 Nhập thông tin và nhấn **Tìm kiếm** để xem kết quả.")


# =============================================================================
# PHẦN III.3 - K-MEANS CLUSTERING & PCA
# =============================================================================
st.divider()
st.header("🎯 Bài III.3 - Phân cụm K-Means & PCA")

from analyis import run_kmeans_pca

k_value = st.sidebar.slider("Chọn số cụm (K)", min_value=2, max_value=10, value=4)

if st.button("🚀 Chạy K-Means + PCA", type="primary"):
    with st.spinner(f"⏳ Đang phân cụm với K={k_value}..."):
        try:
            result = run_kmeans_pca(k=k_value)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Tổng cầu thủ", result['total_players'])
            col2.metric("Số cụm", k_value)
            col3.metric("PCA giữ lại", f"{result['pca_2d'].explained_variance_ratio_.sum():.1%}")
            
            st.subheader("📊 Phân bố cầu thủ theo cụm")
            st.bar_chart(result['cluster_counts'])
            
            st.subheader("📈 Đặc điểm trung bình từng cụm")
            st.dataframe(result['cluster_stats'], use_container_width=True)
            
            st.subheader("🎨 PCA 2D Scatter Plot")
            st.pyplot(result['fig_2d'])
            
            st.info(f"**PCA 2D giữ lại:** {result['pca_2d'].explained_variance_ratio_.sum():.1%} thông tin")
            
            st.subheader("🌐 PCA 3D Scatter Plot")
            st.pyplot(result['fig_3d'])
            
            csv_data = result['df_result'].to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="⬇️ Tải file CSV",
                data=csv_data,
                file_name=f"III.3_kmeans_K{k_value}.csv",
                mime="text/csv"
            )
            
        except Exception as e:
            st.error(f"❌ Lỗi: {e}")
            import traceback
            st.code(traceback.format_exc())