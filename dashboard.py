import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import base64
from streamlit_lottie import st_lottie
import requests
import altair as alt
from streamlit_pandas_profiling import st_profile_report
from ydata_profiling import ProfileReport   
# Set page config
st.set_page_config(page_title="Gelişmiş Excel/CSV Gösterge Paneli", layout="wide", page_icon="📊")

# Geliştirilmiş tasarım için özel CSS
st.markdown("""
<style>
    .reportview-container {
        background: linear-gradient(to right, #f0f2f6, #e0e2e6);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(to bottom, #f0f2f6, #e0e2e6);
    }
    .Widget>label {
        color: #31333F;
        font-weight: bold;
    }
    .stButton>button {
        color: #ffffff;
        background-color: #4CAF50;
        border-radius: 5px;
    }
    .stTextInput>div>div>input {
        color: #31333F;
    }
    h1, h2, h3 {
        color: #31333F;
    }
</style>
""", unsafe_allow_html=True)

# Lottie animasyonlarını yüklemek için fonksiyon
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Lottie animasyonunu yükle
lottie_url = "https://assets5.lottiefiles.com/packages/lf20_qp1q7mct.json"
lottie_json = load_lottieurl(lottie_url)

# Kenar çubuğu
with st.sidebar:
    st_lottie(lottie_json, speed=1, height=200, key="initial")
    st.header("Veri Yükle")
    uploaded_file = st.file_uploader("Excel veya CSV dosyası seçin", type=["xlsx", "csv"])

# Ana içerik
st.title("🚀 Gelişmiş Excel/CSV Gösterge Paneli")

if uploaded_file is not None:
    # Dosya türünü belirle ve oku
    if uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)
    
    # Ham veriyi stil ile göster
    st.subheader("📋 Ham Veri Önizlemesi")
    st.dataframe(df.head().style.highlight_max(axis=0))
    
    # Animasyonlu sayaçlarla veri genel bakışı
    st.subheader("📊 Veri Genel Bakışı")
    col1, col2, col3, col4 = st.columns(4)
    
    def counter_metric(label, value, prefix="", suffix=""):
        st.markdown(
            f"""
            <div style="border:2px solid #4CAF50; border-radius:10px; padding:10px; text-align:center;">
                <h3 style="color:#4CAF50;">{label}</h3>
                <h2>{prefix}{value:,}{suffix}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col1:
        counter_metric("Toplam Satır", df.shape[0])
    with col2:
        counter_metric("Toplam Sütun", df.shape[1])
    with col3:
        counter_metric("Eksik Değerler", df.isnull().sum().sum())
    with col4:
        counter_metric("Veri Tipleri", len(df.dtypes.unique()))
    
    # Analiz için gelişmiş sütun seçimi
    st.subheader("🔍 Analiz için Sütun Seçin")
    numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
    categorical_columns = df.select_dtypes(include=['object']).columns
    date_columns = df.select_dtypes(include=['datetime64']).columns
    
    col1, col2, col3 = st.columns(3)
    with col1:
        x_axis = st.selectbox("X ekseni seçin", options=df.columns)
    with col2:
        y_axis = st.selectbox("Y ekseni seçin", options=numeric_columns)
    with col3:
        color_column = st.selectbox("Renk Sütunu Seçin (İsteğe Bağlı)", options=['Yok'] + list(categorical_columns))
    
    # Gelişmiş Filtreleme
    st.subheader("🔧 Gelişmiş Veri Filtreleme")
    filter_container = st.expander("Filtreleme seçeneklerini genişletmek için tıklayın")
    with filter_container:
        filter_column = st.selectbox("Filtrelenecek sütunu seçin", options=['Yok'] + list(df.columns))
        if filter_column != 'Yok':
            if df[filter_column].dtype in ['int64', 'float64']:
                min_value, max_value = st.slider(f"{filter_column} için aralık seçin", 
                                                 float(df[filter_column].min()), 
                                                 float(df[filter_column].max()),
                                                 (float(df[filter_column].min()), float(df[filter_column].max())))
                df = df[(df[filter_column] >= min_value) & (df[filter_column] <= max_value)]
            else:
                unique_values = df[filter_column].unique()
                selected_values = st.multiselect(f"{filter_column} için değerler seçin", options=unique_values)
                if selected_values:
                    df = df[df[filter_column].isin(selected_values)]
    
    # Sekmeli görselleştirme
    st.subheader("📈 Veri Görselleştirme")
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Temel Grafikler", "🔗 Korelasyon", "📅 Zaman Serisi", "🗺 Coğrafi Görselleştirme"])
    
    with tab1:
        chart_type = st.radio("Grafik Türü Seçin", options=['Dağılım', 'Çizgi', 'Çubuk', 'Kutu'])
        
        if chart_type == 'Dağılım':
            fig = px.scatter(df, x=x_axis, y=y_axis, color=None if color_column == 'Yok' else color_column,
                             title=f"{y_axis} ve {x_axis}")
        elif chart_type == 'Çizgi':
            fig = px.line(df, x=x_axis, y=y_axis, color=None if color_column == 'Yok' else color_column,
                          title=f"{x_axis} boyunca {y_axis}")
        elif chart_type == 'Çubuk':
            fig = px.bar(df, x=x_axis, y=y_axis, color=None if color_column == 'Yok' else color_column,
                         title=f"{x_axis}'e göre {y_axis}")
        else:
            fig = px.box(df, x=x_axis, y=y_axis, color=None if color_column == 'Yok' else color_column,
                         title=f"{x_axis}'e göre {y_axis} Dağılımı")
        
        fig.update_layout(height=600, width=800)
        st.plotly_chart(fig)
    
    with tab2:
        st.subheader("Korelasyon Isı Haritası")
        corr = df[numeric_columns].corr()
        fig = go.Figure(data=go.Heatmap(z=corr.values, x=corr.index, y=corr.columns, colorscale='Viridis'))
        fig.update_layout(height=600, width=800)
        st.plotly_chart(fig)
    
    with tab3:
        if len(date_columns) > 0:
            st.subheader("Zaman Serisi Analizi")
            date_column = st.selectbox("Tarih Sütunu Seçin", options=date_columns)
            value_column = st.selectbox("Değer Sütunu Seçin", options=numeric_columns)
            
            df[date_column] = pd.to_datetime(df[date_column])
            df_grouped = df.groupby(df[date_column].dt.to_period('M')).agg({value_column: 'mean'}).reset_index()
            df_grouped[date_column] = df_grouped[date_column].dt.to_timestamp()
            
            chart = alt.Chart(df_grouped).mark_line().encode(
                x=alt.X(date_column, title='Tarih'),
                y=alt.Y(value_column, title='Değer'),
                tooltip=[date_column, value_column]
            ).interactive()
            
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("Veri setinde tarih sütunu bulunamadı.")
    
    with tab4:
        st.subheader("Coğrafi Görselleştirme")
        lat_col = st.selectbox("Enlem Sütunu Seçin", options=['Yok'] + list(df.columns))
        lon_col = st.selectbox("Boylam Sütunu Seçin", options=['Yok'] + list(df.columns))
        
        if lat_col != 'Yok' and lon_col != 'Yok':
            st.map(df[[lat_col, lon_col]])
        else:
            st.info("Coğrafi görselleştirme için lütfen hem Enlem hem de Boylam sütunlarını seçin.")
    
    # Özet istatistikler ve stil
    st.subheader("📉 Özet İstatistikler")
    st.dataframe(df.describe().style.highlight_max(axis=0).highlight_min(axis=0))
    
    # İşlenmiş veriyi indirme ve ilerleme çubuğu
    st.subheader("💾 İşlenmiş Veriyi İndir")
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="islenmis_veri.csv">CSV Dosyasını İndir</a>'
    st.markdown(href, unsafe_allow_html=True)
    
    # Veri Profili Oluşturma
    st.subheader("🔬 Veri Profili")
    from ydata_profiling import ProfileReport

    if st.button("Veri Profili Oluştur"):
        profile = ProfileReport(df, title="Pandas Profiling Raporu")
        st_profile_report(profile)
else:
    st.info("Veri keşif yolculuğunuza başlamak için lütfen bir Excel veya CSV dosyası yükleyin! 🚀")

# Altbilgi
st.markdown("---")
st.markdown("Streamlit kullanılarak ❤️ ile oluşturuldu | © 2023 Gelişmiş Veri Gösterge Paneli")
