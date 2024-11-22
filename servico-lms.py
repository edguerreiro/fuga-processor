import pandas as pd
import streamlit as st

# Inicializando session state
if 'processed_df' not in st.session_state:
    st.session_state.processed_df = None
if 'total_royalty' not in st.session_state:
    st.session_state.total_royalty = 0

st.title('FUGA Processor')

# File uploader
uploaded_file = st.file_uploader('Upload FUGA statement', type=['csv'])

def process_fuga_statement(file):
    """Processa o arquivo da FUGA e retorna o DataFrame filtrado"""
    try:
        # Leitura do arquivo
        df = pd.read_csv(file)
        
        # Filtro para Elemess e Elemess Label Services
        filtered_df = df[df['Product Label'].isin(['Elemess', 'Elemess Label Services'])]
        
        # Cálculo do total de royalties
        total_royalty = filtered_df['Reported Royalty'].sum()
        
        return filtered_df, total_royalty
    
    except Exception as e:
        st.error(f'Erro ao processar arquivo: {str(e)}')
        return None, 0

if uploaded_file is not None:
    # Processamento do arquivo
    st.session_state.processed_df, st.session_state.total_royalty = process_fuga_statement(uploaded_file)
    
    if st.session_state.processed_df is not None:
        # Mostra alerta sobre os filtros
        st.info('⚠️ Mostrando apenas dados para os labels: Elemess e Elemess Label Services')
        
        # Mostra o total de royalties
        st.metric(
            label="Total de Royalties (EUR)",
            value=f"€ {st.session_state.total_royalty:,.2f}"
        )
        
        # Mostra o DataFrame filtrado
        st.dataframe(st.session_state.processed_df)
        
        # Botão para download do CSV processado
        csv = st.session_state.processed_df.to_csv(sep=',', index=False)
        st.download_button(
            label="Download CSV processado",
            data=csv,
            file_name="fuga_processed.csv",
            mime="text/csv"
        )
