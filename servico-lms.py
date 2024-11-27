import pandas as pd
import streamlit as st

# Inicialização do estado da sessão
if 'processed_df' not in st.session_state:
    st.session_state.processed_df = None
if 'total_royalty' not in st.session_state:
    st.session_state.total_royalty = 0
if 'total_royalty_gross' not in st.session_state:
    st.session_state.total_royalty_gross = 0

st.title('RASA Statement Conversor')

# Seleção do distribuidor
distributor = st.selectbox(
    'Selecione o distribuidor',
    ['FUGA', 'Altafonte', 'ONErpm', 'ONErpm Share-In' ]
)

# Definição da taxa de imposto com base no distribuidor
default_tax_rates = {
    'FUGA': 18.5,
    'Altafonte': 28.5,
    'ONErpm': 18.5,  # Ajuste conforme necessário
    'ONErpm Share-In': 18.5
}

tax_rate = st.number_input(
    'Taxa de imposto (%)',
    min_value=0.0,
    max_value=100.0,
    value=default_tax_rates.get(distributor, 18.5),
    step=0.1
)

def process_tax(df, royalty_column):
    return df[royalty_column].sum()

def process_fuga_statement(file, tax_rate):
    try:
        df = pd.read_csv(file)
        filtered_df = df[df['Product Label'].isin(['Elemess', 'Elemess Label Services'])]
        
        st.session_state.total_royalty_gross = process_tax(filtered_df, 'Reported Royalty')
        
        filtered_df['Reported Royalty'] = filtered_df['Reported Royalty'] * (1 - tax_rate / 100)
        st.session_state.total_royalty = filtered_df['Reported Royalty'].sum()
        
        return filtered_df
    except Exception as e:
        st.error(f'Erro ao processar arquivo: {str(e)}')
        return None

def process_altafonte_statement(file, tax_rate):
    try:
        df = pd.read_csv(file, sep=';', decimal=',', thousands='.')  # Altafonte usa separador ';'
        filtered_df = df[df['SELLO'].isin(['Elemess'])]
        
        st.session_state.total_royalty_gross = process_tax(filtered_df, 'NET')
        filtered_df['NET'] = filtered_df['NET'] * (1 - tax_rate / 100)
        st.session_state.total_royalty = filtered_df['NET'].sum()
        
        return filtered_df
    except Exception as e:
        st.error(f'Erro ao processar arquivo: {str(e)}')
        return None

def process_onerpm_statement(file, tax_rate):
    try:
        df = pd.read_excel(file, sheet_name='Sales')
        # Adicione o processamento específico da ONErpm aqui
        st.session_state.total_royalty_gross = process_tax(df, 'Net')  # Ajuste conforme necessário
        df['Net'] = df['Net'] * (1 - tax_rate / 100)
        st.session_state.total_royalty = df['Net'].sum()
        return df
    except Exception as e:
        st.error(f'Erro ao processar arquivo: {str(e)}')
        return None
    
def process_onerpm_sharein_statement(file, tax_rate):
    try:
        df = pd.read_excel(file, sheet_name='Shares In & Out')
        filtered_df = df[df['Share Type'].str.contains('In', na=False)] 
        # Adicione o processamento específico da ONErpm aqui
        st.session_state.total_royalty_gross = process_tax(filtered_df, 'Net')  # Ajuste conforme necessário
        filtered_df['Net'] = filtered_df['Net'] * (1 - tax_rate / 100)
        st.session_state.total_royalty = filtered_df['Net'].sum()
        return df
    except Exception as e:
        st.error(f'Erro ao processar arquivo: {str(e)}')
        return None


# Carregador de arquivos
if distributor == "ONErpm" or distributor == "ONErpm Share-In" :
    uploaded_file = st.file_uploader('Upload statement', type=['xlsx'])
else:
    uploaded_file = st.file_uploader('Upload statement', type=['csv'])

if uploaded_file is not None:
    # Processamento baseado no distribuidor selecionado
    processor_map = {
        'FUGA': process_fuga_statement,
        'Altafonte': process_altafonte_statement,
        'ONErpm': process_onerpm_statement,
        'ONErpm Share-In': process_onerpm_sharein_statement
    }
    
    processor = processor_map[distributor]
    st.session_state.processed_df = processor(uploaded_file, tax_rate)
    
    if st.session_state.processed_df is not None:
        if distributor == 'FUGA':
            st.warning('⚠️ Considerando apenas labels: Elemess e Elemess Label Services')
        elif distributor == 'Altafonte':
            st.warning('⚠️ Considerando apenas labels: Elemess')
        elif distributor == 'ONErpm Share-In':
            st.warning('⚠️ Considerando apenas Share-In')
        # Adicione avisos específicos para ONErpm se necessário
        
        st.info(f'⚠️ Mostrando dados processados para {distributor} com desconto de {tax_rate}%')
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.metric(
                label="Total de Royalties Gross",
                value=f"{st.session_state.total_royalty_gross:,.2f}"
            )
        
        with col2:
            st.metric(
                label="Total de Royalties com desconto",
                value=f"{st.session_state.total_royalty:,.2f}"
            )
        
        st.dataframe(st.session_state.processed_df)
        
        csv = st.session_state.processed_df.to_csv(sep=',', index=False)
        st.download_button(
            label="Download CSV processado",
            data=csv,
            file_name=f"{distributor.lower()}_processed.csv",
            mime="text/csv"
        )
