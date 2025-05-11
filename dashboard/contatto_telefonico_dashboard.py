import streamlit as st
import plotly.express as px
import pandas as pd

def show_contatto_telefonico_dashboard(df):
    """Specialized dashboard for 'Contatto Telefonico' dataset with enhanced visualizations"""
    st.title("📈 Contatto Telefonico Analytics Dashboard")
    
    # Custom CSS for styling
    st.markdown("""
        <style>
            .metric-card {background-color: #f5f0f6; padding: 1rem; border-radius: 10px; margin: 0.5rem 0;}
            .section-header {color: white; font-weight: 600;}
            .plot-container {box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-radius: 10px; padding: 1rem;}
        </style>
    """, unsafe_allow_html=True)

    # === Key Metrics Section ===
    st.markdown('<div class="section-header">📊 Key Metrics</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Records", df.shape[0], delta="+0", delta_color="off")
        st.caption("Current entries in dataset")
        
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        unique_pct = round((df.nunique().sum() / df.size) * 100, 1)
        st.metric("Data Uniqueness", f"{unique_pct}%", help="Percentage of unique values across all columns")
        
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Feature Count", df.shape[1], help="Number of data attributes")

    # === Data Quality Section ===
    st.markdown('<div class="section-header">🔍 Data Quality Check</div>', unsafe_allow_html=True)
    missing_values = df.isnull().sum().sum()
    duplicated_rows = df.duplicated().sum()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Missing Values", missing_values, 
                 delta=f"{round((missing_values/df.size)*100, 2)}% of total",
                 delta_color="inverse")
                 
    with col2:
        st.metric("Duplicate Rows", duplicated_rows,
                 delta=f"{round((duplicated_rows/len(df))*100, 2)}% of total",
                 delta_color="inverse")

    # === Interactive Visualizations ===
    st.markdown('<div class="section-header">📊 Interactive Analysis</div>', unsafe_allow_html=True)
    
    # Column Explorer
    with st.expander("🔍 Column Explorer"):
        selected_col = st.selectbox("Select column to analyze", df.columns)
        
        if selected_col:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f'**Distribution of {selected_col}**')
                if pd.api.types.is_numeric_dtype(df[selected_col]):
                    fig = px.histogram(df, x=selected_col, marginal="box", 
                                     hover_data=df.columns,
                                     title=f"Distribution of {selected_col}")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    fig = px.bar(df[selected_col].value_counts(), 
                                title=f"Category Distribution of {selected_col}")
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown(f'**Statistics for {selected_col}**')
                if pd.api.types.is_numeric_dtype(df[selected_col]):
                    st.write(df[selected_col].describe())
                else:
                    st.write("Top 5 Categories:")
                    st.dataframe(df[selected_col].value_counts().head(5))

    # Correlation Heatmap
    if any(df.dtypes.apply(lambda x: pd.api.types.is_numeric_dtype(x))):
        st.markdown('<div class="section-header">🔥 Correlation Analysis</div>', unsafe_allow_html=True)
        numeric_df = df.select_dtypes(include=['number'])
        
        if len(numeric_df.columns) > 1:
            fig = px.imshow(numeric_df.corr(),
                        labels=dict(color="Correlation"),
                        x=numeric_df.columns,
                        y=numeric_df.columns,
                        color_continuous_scale='RdBu',
                        range_color=[-1, 1])
            fig.update_layout(title="Feature Correlation Heatmap")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("At least two numeric columns needed for correlation analysis")

   