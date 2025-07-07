import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Sistema de Agendamento",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Navegação principal na sidebar
with st.sidebar:
    st.markdown("# 📅 Sistema de Agendamento")
    st.markdown("---")
    
    opcao = st.radio(
        "**Escolha uma opção:**",
        ["👥 Área do Cliente", "🔐 Painel Administrativo"],
        key="navegacao_principal"
    )
    
    st.markdown("---")
    st.markdown("💡 **Dica:** Use este menu para alternar entre as áreas do sistema.")

# Execução baseada na escolha
if opcao == "👥 Área do Cliente":
    # IMPORTAR E EXECUTAR TODO O CÓDIGO DO Cliente.py
    exec(open('Cliente.py').read())
    
else:  # Painel Administrativo
    # IMPORTAR E EXECUTAR TODO O CÓDIGO DO admin.py
    exec(open('admin.py').read())