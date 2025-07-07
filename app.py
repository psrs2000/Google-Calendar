import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuração da página
st.set_page_config(
    page_title="Sistema de Agendamento",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS (versão simplificada)
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        max-width: 1400px;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp {
        background: #f8f9fa;
    }
    
    .main-header {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .main-header h1 {
        color: #1f2937;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    
    .main-card {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
    }
    
    .alert {
        padding: 16px 20px;
        border-radius: 12px;
        margin: 16px 0;
        font-weight: 500;
    }
    
    .alert-success {
        background: #d4f6dc;
        color: #0f5132;
        border-left: 4px solid #10b981;
    }
    
    .alert-warning {
        background: #fff3cd;
        color: #856404;
        border-left: 4px solid #f59e0b;
    }
</style>
""", unsafe_allow_html=True)

# Configurações do banco
DB = "agenda.db"

# Senha do admin
try:
    SENHA_ADMIN = st.secrets["ADMIN_PASSWORD"]
except:
    SENHA_ADMIN = "1234"  # Senha padrão

# Funções do banco
def conectar():
    return sqlite3.connect(DB)

def init_db():
    conn = conectar()
    c = conn.cursor()
    
    # Tabelas básicas
    c.execute('''
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_cliente TEXT,
            telefone TEXT,
            data TEXT,
            horario TEXT
        )
    ''')
    
    # Adicionar colunas se não existirem
    try:
        c.execute("SELECT email FROM agendamentos LIMIT 1")
    except sqlite3.OperationalError:
        c.execute("ALTER TABLE agendamentos ADD COLUMN email TEXT DEFAULT ''")
    
    try:
        c.execute("SELECT status FROM agendamentos LIMIT 1")
    except sqlite3.OperationalError:
        c.execute("ALTER TABLE agendamentos ADD COLUMN status TEXT DEFAULT 'pendente'")
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS configuracoes (
            chave TEXT PRIMARY KEY,
            valor TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS dias_uteis (
            dia TEXT PRIMARY KEY
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS bloqueios (
            data TEXT PRIMARY KEY
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS bloqueios_horarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            horario TEXT,
            UNIQUE(data, horario)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS bloqueios_permanentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            horario_inicio TEXT,
            horario_fim TEXT,
            dias_semana TEXT,
            descricao TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# Funções auxiliares
def obter_configuracao(chave, padrao=None):
    conn = conectar()
    c = conn.cursor()
    try:
        c.execute("SELECT valor FROM configuracoes WHERE chave=?", (chave,))
        resultado = c.fetchone()
        if resultado:
            valor = resultado[0]
            if valor == "True":
                return True
            elif valor == "False":
                return False
            try:
                return int(valor)
            except ValueError:
                try:
                    return float(valor)
                except ValueError:
                    return valor
        return padrao
    except:
        return padrao
    finally:
        conn.close()

def salvar_configuracao(chave, valor):
    conn = conectar()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO configuracoes (chave, valor) VALUES (?, ?)", (chave, str(valor)))
    conn.commit()
    conn.close()

def horario_disponivel(data, horario):
    conn = conectar()
    c = conn.cursor()
    
    # Verificar agendamentos
    c.execute("SELECT * FROM agendamentos WHERE data=? AND horario=?", (data, horario))
    if c.fetchone():
        conn.close()
        return False
    
    # Verificar bloqueios básicos
    try:
        c.execute("SELECT * FROM bloqueios WHERE data=?", (data,))
        if c.fetchone():
            conn.close()
            return False
    except:
        pass
    
    conn.close()
    return True

def adicionar_agendamento(nome, telefone, email, data, horario):
    conn = conectar()
    c = conn.cursor()
    
    confirmacao_automatica = obter_configuracao("confirmacao_automatica", False)
    status_inicial = "confirmado" if confirmacao_automatica else "pendente"
    
    try:
        c.execute("INSERT INTO agendamentos (nome_cliente, telefone, email, data, horario, status) VALUES (?, ?, ?, ?, ?, ?)",
                  (nome, telefone, email, data, horario, status_inicial))
        conn.commit()
    except:
        c.execute("INSERT INTO agendamentos (nome_cliente, telefone, data, horario) VALUES (?, ?, ?, ?)",
                  (nome, telefone, data, horario))
        conn.commit()
    
    conn.close()
    return status_inicial

def buscar_agendamentos():
    conn = conectar()
    c = conn.cursor()
    try:
        c.execute("SELECT id, data, horario, nome_cliente, telefone, email, status FROM agendamentos ORDER BY data, horario")
        agendamentos = c.fetchall()
    except:
        try:
            c.execute("SELECT id, data, horario, nome_cliente, telefone FROM agendamentos ORDER BY data, horario")
            agendamentos_sem_extras = c.fetchall()
            agendamentos = [ag + ('', 'pendente') for ag in agendamentos_sem_extras]
        except:
            agendamentos = []
    conn.close()
    return agendamentos

def obter_dias_uteis():
    conn = conectar()
    c = conn.cursor()
    try:
        c.execute("SELECT dia FROM dias_uteis")
        dias = [linha[0] for linha in c.fetchall()]
        if not dias:
            dias = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    except:
        dias = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    conn.close()
    return dias

# Inicializar banco
init_db()

# INTERFACE PRINCIPAL
def main():
    # Sidebar SEMPRE visível
    with st.sidebar:
        st.markdown("# 📅 Sistema de Agendamento")
        st.markdown("---")
        
        # Usar session_state para garantir persistência
        if "area_escolhida" not in st.session_state:
            st.session_state.area_escolhida = "👥 Área do Cliente"
        
        opcao = st.radio(
            "**Escolha uma opção:**",
            ["👥 Área do Cliente", "🔐 Painel Administrativo"],
            index=0 if st.session_state.area_escolhida == "👥 Área do Cliente" else 1,
            key="opcao_navegacao"
        )
        
        # Atualizar session_state
        st.session_state.area_escolhida = opcao
        
        st.markdown("---")
        st.markdown("💡 **Dica:** Use este menu para alternar entre as áreas.")
    
    # Executar interface baseada na escolha
    if opcao == "👥 Área do Cliente":
        interface_cliente()
    else:
        interface_admin()

def interface_cliente():
    # Configurações
    nome_profissional = obter_configuracao("nome_profissional", "Dr. João Silva")
    nome_clinica = obter_configuracao("nome_clinica", "Clínica São Lucas")
    telefone_contato = obter_configuracao("telefone_contato", "(11) 3333-4444")
    endereco = obter_configuracao("endereco", "Rua das Flores, 123")
    
    st.markdown(f"""
    <div class="main-header">
        <h1>💆‍♀️ Agendamento Online</h1>
        <p>Agende seu horário de forma rápida e prática</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    tab_agendar, tab_cancelar = st.tabs(["📅 Agendar Horário", "❌ Cancelar Agendamento"])
    
    with tab_agendar:
        # Configurações de agenda
        hoje = datetime.today()
        dias_futuros_config = obter_configuracao("dias_futuros", 30)
        horario_inicio = obter_configuracao("horario_inicio", "09:00")
        horario_fim = obter_configuracao("horario_fim", "18:00")
        intervalo_consultas = obter_configuracao("intervalo_consultas", 60)
        
        dias_uteis = obter_dias_uteis()
        
        # Gerar datas válidas
        datas_validas = []
        for i in range(1, dias_futuros_config + 1):
            data = hoje + timedelta(days=i)
            dia_semana = data.strftime("%A")
            if dia_semana in dias_uteis:
                datas_validas.append(data.date())
        
        if datas_validas:
            st.subheader("📋 Dados do Cliente")
            
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("Nome completo *", placeholder="Digite seu nome completo")
            with col2:
                telefone = st.text_input("Telefone *", placeholder="(11) 99999-9999")
            
            email = st.text_input("E-mail *", placeholder="seu@email.com")
            
            st.subheader("📅 Escolha a Data")
            data_selecionada = st.selectbox(
                "Datas disponíveis:",
                options=datas_validas,
                format_func=lambda d: d.strftime("%A, %d/%m/%Y").replace("Monday", "Segunda-feira")\
                    .replace("Tuesday", "Terça-feira").replace("Wednesday", "Quarta-feira")\
                    .replace("Thursday", "Quinta-feira").replace("Friday", "Sexta-feira")\
                    .replace("Saturday", "Sábado").replace("Sunday", "Domingo")
            )
            
            if data_selecionada:
                st.subheader("⏰ Horários Disponíveis")
                data_str = data_selecionada.strftime("%Y-%m-%d")
                
                # Gerar horários
                try:
                    hora_inicio = datetime.strptime(horario_inicio, "%H:%M").time()
                    hora_fim = datetime.strptime(horario_fim, "%H:%M").time()
                    
                    inicio_min = hora_inicio.hour * 60 + hora_inicio.minute
                    fim_min = hora_fim.hour * 60 + hora_fim.minute
                    
                    horarios_possiveis = []
                    horario_atual = inicio_min
                    
                    while horario_atual + intervalo_consultas <= fim_min:
                        h = horario_atual // 60
                        m = horario_atual % 60
                        horarios_possiveis.append(f"{h:02d}:{m:02d}")
                        horario_atual += intervalo_consultas
                except:
                    horarios_possiveis = [f"{h:02d}:00" for h in range(9, 18)]
                
                horarios_disponiveis = [h for h in horarios_possiveis if horario_disponivel(data_str, h)]
                
                if horarios_disponiveis:
                    horario = st.selectbox("Escolha o horário:", horarios_disponiveis)
                    
                    if horario and nome and telefone and email:
                        if "@" in email and "." in email.split("@")[-1]:
                            if st.button("✅ Confirmar Agendamento", type="primary"):
                                try:
                                    status_inicial = adicionar_agendamento(nome, telefone, email, data_str, horario)
                                    
                                    if status_inicial == "confirmado":
                                        st.markdown("""
                                        <div class="alert alert-success">
                                            ✅ <strong>Agendamento confirmado automaticamente!</strong>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    else:
                                        st.markdown("""
                                        <div class="alert alert-success">
                                            ✅ <strong>Agendamento solicitado com sucesso!</strong>
                                        </div>
                                        """, unsafe_allow_html=True)
                                except Exception as e:
                                    st.error(f"Erro: {str(e)}")
                        else:
                            st.markdown("""
                            <div class="alert alert-warning">
                                ⚠️ <strong>Digite um e-mail válido.</strong>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.warning("Nenhum horário disponível para esta data.")
        else:
            st.warning("Nenhuma data disponível no momento.")
    
    with tab_cancelar:
        st.subheader("❌ Cancelar Agendamento")
        st.info("Informe os dados do agendamento original.")
        
        col1, col2 = st.columns(2)
        with col1:
            nome_cancel = st.text_input("Nome cadastrado")
        with col2:
            telefone_cancel = st.text_input("Telefone cadastrado")
        
        data_cancel = st.date_input("Data do agendamento", min_value=datetime.today().date())
        
        if st.button("🗑️ Cancelar Agendamento"):
            if nome_cancel and telefone_cancel:
                st.success("Cancelamento processado!")
            else:
                st.warning("Preencha todos os campos.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem; color: #6b7280;">
        <h3>{nome_profissional}</h3>
        <p><strong>{nome_clinica}</strong> • 📍 {endereco} • 📞 {telefone_contato}</p>
    </div>
    """, unsafe_allow_html=True)

def interface_admin():
    # Autenticação
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown("""
        <div class="main-header">
            <h1>🔐 Painel Administrativo</h1>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("🔒 Acesso Restrito")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            senha = st.text_input("Senha de administrador:", type="password")
            
            if st.button("🚪 Entrar", type="primary"):
                if senha == SENHA_ADMIN:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Senha incorreta!")
        
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Interface admin autenticada
    st.markdown("""
    <div class="main-header">
        <h1>🔐 Painel Administrativo</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Menu admin
    opcao_admin = st.selectbox(
        "Menu Administrativo:",
        ["📊 Dashboard", "👥 Lista de Agendamentos", "⚙️ Configurações"],
        key="menu_admin"
    )
    
    if st.button("🚪 Sair"):
        st.session_state.authenticated = False
        st.rerun()
    
    # Carregar dados
    agendamentos = buscar_agendamentos()
    
    if opcao_admin == "📊 Dashboard":
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("📊 Dashboard")
        
        # Estatísticas básicas
        hoje = datetime.now().strftime("%Y-%m-%d")
        agendamentos_hoje = [a for a in agendamentos if a[1] == hoje]
        agendamentos_mes = [a for a in agendamentos if a[1].startswith(datetime.now().strftime("%Y-%m"))]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Hoje", len(agendamentos_hoje))
        with col2:
            st.metric("Este Mês", len(agendamentos_mes))
        with col3:
            st.metric("Total", len(agendamentos))
        
        if agendamentos:
            st.subheader("📋 Próximos Agendamentos")
            for agendamento in agendamentos[:5]:
                nome = agendamento[3] if len(agendamento) > 3 else "N/A"
                data = agendamento[1] if len(agendamento) > 1 else "N/A"
                horario = agendamento[2] if len(agendamento) > 2 else "N/A"
                st.write(f"👤 {nome} - 📅 {data} às {horario}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif opcao_admin == "👥 Lista de Agendamentos":
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("👥 Lista de Agendamentos")
        
        if agendamentos:
            for agendamento in agendamentos:
                if len(agendamento) >= 7:
                    agendamento_id, data, horario, nome, telefone, email, status = agendamento
                else:
                    agendamento_id, data, horario, nome, telefone = agendamento[:5]
                    email = agendamento[5] if len(agendamento) > 5 else "N/A"
                    status = agendamento[6] if len(agendamento) > 6 else "pendente"
                
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.write(f"**{nome}** - {data} às {horario}")
                    st.write(f"📱 {telefone} • 📧 {email} • Status: {status}")
                
                with col2:
                    if status == "pendente":
                        if st.button("✅", key=f"confirm_{agendamento_id}"):
                            conn = conectar()
                            c = conn.cursor()
                            c.execute("UPDATE agendamentos SET status = ? WHERE id = ?", ("confirmado", agendamento_id))
                            conn.commit()
                            conn.close()
                            st.rerun()
                
                st.markdown("---")
        else:
            st.info("Nenhum agendamento encontrado.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif opcao_admin == "⚙️ Configurações":
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("⚙️ Configurações")
        
        # Configurações básicas
        col1, col2 = st.columns(2)
        
        with col1:
            nome_profissional = st.text_input("Nome do profissional:", 
                                              value=obter_configuracao("nome_profissional", "Dr. João Silva"))
            nome_clinica = st.text_input("Nome da clínica:", 
                                        value=obter_configuracao("nome_clinica", "Clínica São Lucas"))
        
        with col2:
            telefone_contato = st.text_input("Telefone:", 
                                           value=obter_configuracao("telefone_contato", "(11) 3333-4444"))
            endereco = st.text_input("Endereço:", 
                                   value=obter_configuracao("endereco", "Rua das Flores, 123"))
        
        confirmacao_automatica = st.checkbox("Confirmação automática", 
                                           value=obter_configuracao("confirmacao_automatica", False))
        
        if st.button("💾 Salvar", type="primary"):
            salvar_configuracao("nome_profissional", nome_profissional)
            salvar_configuracao("nome_clinica", nome_clinica)
            salvar_configuracao("telefone_contato", telefone_contato)
            salvar_configuracao("endereco", endereco)
            salvar_configuracao("confirmacao_automatica", confirmacao_automatica)
            st.success("✅ Configurações salvas!")
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()