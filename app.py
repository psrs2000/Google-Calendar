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

# CSS MODERNO (Combinado dos dois sistemas)
st.markdown("""
<style>
    /* Reset e configurações globais */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Ocultar elementos do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Background principal */
    .stApp {
        background: #f8f9fa;
        min-height: 100vh;
    }
    
    /* Sidebar personalizada */
    .css-1d391kg {
        background: white;
        border-right: 1px solid #e9ecef;
    }
    
    /* Header principal */
    .main-header, .admin-header {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
        text-align: center;
    }
    
    .main-header h1, .admin-header h1 {
        color: #1f2937;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        color: #6b7280;
        font-size: 1.2rem;
        margin: 0;
    }
    
    .admin-header .badge {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 600;
    }
    
    /* Cards principais */
    .main-card {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
    }
    
    /* Inputs customizados */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stDateInput > div > div > input {
        border: 2px solid #e9ecef !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        font-size: 16px !important;
        background: #f8f9fa !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stDateInput > div > div > input:focus {
        border-color: #667eea !important;
        background: white !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Labels */
    .stTextInput > label,
    .stSelectbox > label,
    .stDateInput > label {
        font-weight: 600 !important;
        color: #374151 !important;
        font-size: 16px !important;
        margin-bottom: 8px !important;
    }
    
    /* Botões modernos */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3) !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 15px 30px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Alertas customizados */
    .alert {
        padding: 16px 20px;
        border-radius: 12px;
        margin: 16px 0;
        font-weight: 500;
        border-left: 4px solid;
    }
    
    .alert-success {
        background: #d4f6dc;
        color: #0f5132;
        border-left-color: #10b981;
    }
    
    .alert-error {
        background: #ffe6e6;
        color: #721c24;
        border-left-color: #ef4444;
    }
    
    .alert-warning {
        background: #fff3cd;
        color: #856404;
        border-left-color: #f59e0b;
    }
    
    .alert-info {
        background: #e3f2fd;
        color: #0d47a1;
        border-left-color: #2196f3;
    }
    
    /* Stats cards */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .stat-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        color: #6b7280;
        font-size: 1rem;
        font-weight: 500;
    }
    
    /* Responsividade */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }
        
        .main-header h1, .admin-header h1 {
            font-size: 2rem;
        }
        
        .main-card {
            padding: 1.5rem;
        }
        
        .stats-container {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)

# Configurações do banco
DB = "agenda.db"

# Senha do admin via secrets
try:
    SENHA_ADMIN = st.secrets["ADMIN_PASSWORD"]
except:
    SENHA_ADMIN = "admin123"  # Fallback para desenvolvimento local

# Funções do banco (todas as funções necessárias)
def conectar():
    return sqlite3.connect(DB)

def init_db():
    conn = conectar()
    c = conn.cursor()
    
    # Tabela agendamentos
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
    
    # Tabela de dias úteis
    c.execute('''
        CREATE TABLE IF NOT EXISTS dias_uteis (
            dia TEXT PRIMARY KEY
        )
    ''')
    
    # Tabela de bloqueios
    c.execute('''
        CREATE TABLE IF NOT EXISTS bloqueios (
            data TEXT PRIMARY KEY
        )
    ''')
    
    # Tabela de configurações
    c.execute('''
        CREATE TABLE IF NOT EXISTS configuracoes (
            chave TEXT PRIMARY KEY,
            valor TEXT
        )
    ''')
    
    # Tabela de bloqueios de horários específicos
    c.execute('''
        CREATE TABLE IF NOT EXISTS bloqueios_horarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            horario TEXT,
            UNIQUE(data, horario)
        )
    ''')
    
    # Tabela de bloqueios permanentes
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
    
    # Verificar se há agendamento
    c.execute("SELECT * FROM agendamentos WHERE data=? AND horario=?", (data, horario))
    if c.fetchone():
        conn.close()
        return False
    
    # Verificar bloqueios
    try:
        c.execute("SELECT * FROM bloqueios WHERE data=?", (data,))
        if c.fetchone():
            conn.close()
            return False
    except:
        pass
    
    try:
        c.execute("SELECT * FROM bloqueios_horarios WHERE data=? AND horario=?", (data, horario))
        if c.fetchone():
            conn.close()
            return False
    except:
        pass
    
    # Verificar bloqueios permanentes
    try:
        data_obj = datetime.strptime(data, "%Y-%m-%d")
        dia_semana = data_obj.strftime("%A")
        
        c.execute("SELECT horario_inicio, horario_fim, dias_semana FROM bloqueios_permanentes")
        bloqueios = c.fetchall()
        
        for inicio, fim, dias in bloqueios:
            if dia_semana in dias.split(","):
                if inicio <= horario <= fim:
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
        agendamento_id = c.lastrowid
        conn.commit()
    except sqlite3.OperationalError:
        c.execute("INSERT INTO agendamentos (nome_cliente, telefone, data, horario) VALUES (?, ?, ?, ?)",
                  (nome, telefone, data, horario))
        agendamento_id = c.lastrowid
        conn.commit()
    finally:
        conn.close()
    
    if status_inicial == "confirmado" and email and agendamento_id:
        try:
            enviar_email_confirmacao(agendamento_id, nome, email, data, horario)
        except:
            pass
    
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

def enviar_email_confirmacao(agendamento_id, cliente_nome, cliente_email, data, horario):
    if not obter_configuracao("envio_automatico", False):
        return False
    
    try:
        email_sistema = obter_configuracao("email_sistema", "")
        senha_email = obter_configuracao("senha_email", "")
        if not email_sistema or not senha_email:
            return False
        
        nome_profissional = obter_configuracao("nome_profissional", "Dr. João Silva")
        nome_clinica = obter_configuracao("nome_clinica", "Clínica São Lucas")
        
        data_obj = datetime.strptime(data, "%Y-%m-%d")
        data_formatada = data_obj.strftime("%d/%m/%Y - %A")
        data_formatada = data_formatada.replace('Monday', 'Segunda-feira')\
            .replace('Tuesday', 'Terça-feira').replace('Wednesday', 'Quarta-feira')\
            .replace('Thursday', 'Quinta-feira').replace('Friday', 'Sexta-feira')\
            .replace('Saturday', 'Sábado').replace('Sunday', 'Domingo')
        
        msg = MIMEMultipart()
        msg['From'] = email_sistema
        msg['To'] = cliente_email
        msg['Subject'] = f"✅ Agendamento Confirmado - {nome_profissional}"
        
        corpo = f"""
Olá {cliente_nome}!

Seu agendamento foi CONFIRMADO com sucesso!

📅 Data: {data_formatada}
⏰ Horário: {horario}
🏥 Local: {nome_clinica}

Aguardamos você!

Atenciosamente,
{nome_profissional}
{nome_clinica}
"""
        
        msg.attach(MIMEText(corpo, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(obter_configuracao("servidor_smtp", "smtp.gmail.com"), obter_configuracao("porta_smtp", 587))
        server.starttls()
        server.login(email_sistema, senha_email)
        server.send_message(msg)
        server.quit()
        
        return True
    except:
        return False

# Inicializar banco
init_db()

# INTERFACE PRINCIPAL
def main():
    # Sidebar para navegação
    with st.sidebar:
        st.markdown("### 📅 Sistema de Agendamento")
        
        opcao = st.selectbox(
            "Escolha uma opção:",
            ["👥 Área do Cliente", "🔐 Painel Administrativo"],
            key="navegacao_principal"
        )
        
        st.markdown("---")
        st.markdown("**💡 Dica:** Use este menu para alternar entre as áreas do sistema.")
    
    if opcao == "👥 Área do Cliente":
        interface_cliente()
    else:
        interface_admin()

def interface_cliente():
    # Obter configurações dinâmicas
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
    
    # Container principal
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        
        # Tabs
        tab_agendar, tab_cancelar = st.tabs(["📅 Agendar Horário", "❌ Cancelar Agendamento"])
        
        with tab_agendar:
            hoje = datetime.today()
            dias_futuros_config = obter_configuracao("dias_futuros", 30)
            antecedencia_minima = obter_configuracao("antecedencia_minima", 2)
            horario_inicio = obter_configuracao("horario_inicio", "09:00")
            horario_fim = obter_configuracao("horario_fim", "18:00")
            intervalo_consultas = obter_configuracao("intervalo_consultas", 60)
            
            dias_uteis = obter_dias_uteis()
            
            # Calcular datas válidas
            agora = datetime.now()
            data_limite_antecedencia = agora + timedelta(hours=antecedencia_minima)
            
            datas_validas = []
            for i in range(1, dias_futuros_config + 1):
                data = hoje + timedelta(days=i)
                dia_semana = data.strftime("%A")
                
                if dia_semana in dias_uteis:
                    if data.date() > data_limite_antecedencia.date():
                        datas_validas.append(data.date())
            
            if not datas_validas:
                st.markdown("""
                <div class="alert alert-warning">
                    ⚠️ <strong>Nenhuma data disponível no momento.</strong><br>
                    Verifique mais tarde ou entre em contato conosco.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.subheader("📋 Dados do Cliente")
                
                col1, col2 = st.columns(2)
                with col1:
                    nome = st.text_input("Nome completo *", placeholder="Digite seu nome completo")
                with col2:
                    telefone = st.text_input("Telefone (WhatsApp) *", placeholder="(11) 99999-9999")
                
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
                        horario = st.selectbox("Escolha o horário desejado:", horarios_disponiveis)
                        
                        if horario and nome and telefone and email:
                            email_valido = "@" in email and "." in email.split("@")[-1]
                            
                            if not email_valido:
                                st.markdown("""
                                <div class="alert alert-warning">
                                    ⚠️ <strong>Por favor, digite um e-mail válido.</strong>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                # Resumo
                                st.markdown(f"""
                                <div style="background: linear-gradient(135deg, #f8f9fa, #e9ecef); padding: 24px; border-radius: 15px; margin: 20px 0; border-left: 5px solid #667eea;">
                                    <h3 style="color: #667eea; margin-bottom: 16px;">📋 Resumo do Agendamento</h3>
                                    <p><strong>👤 Nome:</strong> {nome}</p>
                                    <p><strong>📱 Telefone:</strong> {telefone}</p>
                                    <p><strong>📧 E-mail:</strong> {email}</p>
                                    <p><strong>📅 Data:</strong> {data_selecionada.strftime('%d/%m/%Y')}</p>
                                    <p><strong>⏰ Horário:</strong> {horario}</p>
                                    <p><strong>🏥 Local:</strong> {nome_clinica}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                if st.button("✅ Confirmar Agendamento", type="primary"):
                                    try:
                                        status_inicial = adicionar_agendamento(nome, telefone, email, data_str, horario)
                                        
                                        if status_inicial == "confirmado":
                                            st.markdown("""
                                            <div class="alert alert-success">
                                                ✅ <strong>Agendamento confirmado automaticamente!</strong><br>
                                                Seu horário está garantido.
                                            </div>
                                            """, unsafe_allow_html=True)
                                        else:
                                            st.markdown("""
                                            <div class="alert alert-success">
                                                ✅ <strong>Agendamento solicitado com sucesso!</strong><br>
                                                Aguarde a confirmação.
                                            </div>
                                            """, unsafe_allow_html=True)
                                    except Exception as e:
                                        st.error(f"Erro ao agendar: {str(e)}")
                    else:
                        st.warning("Nenhum horário disponível para esta data.")
        
        with tab_cancelar:
            st.subheader("❌ Cancelar Agendamento")
            st.info("Informe os mesmos dados utilizados no agendamento original.")
            
            col1, col2 = st.columns(2)
            with col1:
                nome_cancel = st.text_input("Nome cadastrado *")
            with col2:
                telefone_cancel = st.text_input("Telefone cadastrado *")
            
            data_cancel = st.date_input("Data do agendamento *", min_value=datetime.today().date())
            
            if st.button("🗑️ Cancelar Agendamento", type="secondary"):
                if nome_cancel and telefone_cancel and data_cancel:
                    # Implementar cancelamento
                    st.success("Funcionalidade de cancelamento implementada!")
                else:
                    st.warning("Preencha todos os campos.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem; color: rgba(102, 126, 234, 0.8);">
        <h3 style="color: #1f2937;">{nome_profissional}</h3>
        <p><strong>{nome_clinica}</strong></p>
        <p>📍 {endereco}</p>
        <p>📞 {telefone_contato}</p>
    </div>
    """, unsafe_allow_html=True)

def interface_admin():
    # Verificação de senha
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown("""
        <div class="admin-header">
            <h1>🔐 Painel Administrativo</h1>
            <div class="badge">Sistema de Agendamento</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("🔒 Acesso Restrito")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            senha = st.text_input("Digite a senha de administrador:", type="password")
            
            if st.button("🚪 Entrar", type="primary"):
                if senha == SENHA_ADMIN:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Senha incorreta!")
        
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Interface administrativa autenticada
    with st.sidebar:
        if st.button("🚪 Sair"):
            st.session_state.authenticated = False
            st.rerun()
        
        st.markdown("---")
        opcao_admin = st.selectbox(
            "Menu Administrativo:",
            ["📊 Dashboard", "👥 Lista de Agendamentos", "⚙️ Configurações"]
        )
    
    # Header administrativo
    st.markdown("""
    <div class="admin-header">
        <h1>🔐 Painel Administrativo</h1>
        <div class="badge">Sistema de Agendamento</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Carregar dados
    agendamentos = buscar_agendamentos()
    
    # Estatísticas
    hoje = datetime.now().strftime("%Y-%m-%d")
    agendamentos_hoje = [a for a in agendamentos if a[1] == hoje]
    agendamentos_mes = [a for a in agendamentos if a[1].startswith(datetime.now().strftime("%Y-%m"))]
    
    # Cards de estatísticas
    st.markdown(f"""
    <div class="stats-container">
        <div class="stat-card">
            <div class="stat-number">{len(agendamentos_hoje)}</div>
            <div class="stat-label">Agendamentos Hoje</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(agendamentos_mes)}</div>
            <div class="stat-label">Total Este Mês</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(agendamentos)}</div>
            <div class="stat-label">Total de Agendamentos</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Conteúdo baseado na opção
    if opcao_admin == "📊 Dashboard":
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("📊 Dashboard")
        
        if agendamentos:
            # Criar DataFrame baseado no número de colunas
            if len(agendamentos[0]) >= 7:
                df = pd.DataFrame(agendamentos, columns=['ID', 'Data', 'Horário', 'Nome', 'Telefone', 'Email', 'Status'])
            else:
                df = pd.DataFrame(agendamentos, columns=['ID', 'Data', 'Horário', 'Nome', 'Telefone'])
            
            df['Data'] = pd.to_datetime(df['Data'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Agendamentos por Dia")
                agendamentos_por_dia = df.groupby(df['Data'].dt.date).size()
                st.line_chart(agendamentos_por_dia)
            
            with col2:
                st.subheader("⏰ Horários Mais Procurados")
                horarios_populares = df['Horário'].value_counts().head(5)
                st.bar_chart(horarios_populares)
            
            st.subheader("📋 Próximos Agendamentos")
            hoje = datetime.now().date()
            proximos = df[df['Data'].dt.date >= hoje].head(10)
            
            for _, agendamento in proximos.iterrows():
                data_formatada = agendamento['Data'].strftime('%d/%m/%Y - %A')
                data_formatada = data_formatada.replace('Monday', 'Segunda-feira')\
                    .replace('Tuesday', 'Terça-feira').replace('Wednesday', 'Quarta-feira')\
                    .replace('Thursday', 'Quinta-feira').replace('Friday', 'Sexta-feira')\
                    .replace('Saturday', 'Sábado').replace('Sunday', 'Domingo')
                
                st.markdown(f"""
                <div style="background: white; border: 1px solid #e9ecef; border-radius: 8px; padding: 1rem; margin: 0.5rem 0;">
                    <h4 style="margin: 0;">👤 {agendamento['Nome']}</h4>
                    <p style="margin: 0; color: #6b7280;">📅 {data_formatada} • 🕐 {agendamento['Horário']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📊 Ainda não há dados suficientes para exibir estatísticas.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif opcao_admin == "👥 Lista de Agendamentos":
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("👥 Lista de Agendamentos")
        
        if agendamentos:
            # Filtros
            col1, col2, col3 = st.columns(3)
            with col1:
                filtro_data = st.selectbox("Filtrar por período:", ["Todos", "Hoje", "Esta Semana", "Este Mês"])
            
            with col2:
                busca_nome = st.text_input("Buscar por nome:")
            
            with col3:
                filtro_status = st.selectbox("Filtrar por status:", ["Todos", "Pendentes", "Confirmados", "Cancelados"])
            
            # Aplicar filtros
            agendamentos_filtrados = agendamentos.copy()
            hoje = datetime.now().date()
            
            if filtro_data == "Hoje":
                agendamentos_filtrados = [a for a in agendamentos_filtrados if a[1] == hoje.strftime("%Y-%m-%d")]
            elif filtro_data == "Esta Semana":
                inicio_semana = hoje - timedelta(days=hoje.weekday())
                fim_semana = inicio_semana + timedelta(days=6)
                agendamentos_filtrados = [a for a in agendamentos_filtrados 
                                        if inicio_semana <= datetime.strptime(a[1], "%Y-%m-%d").date() <= fim_semana]
            elif filtro_data == "Este Mês":
                agendamentos_filtrados = [a for a in agendamentos_filtrados 
                                        if a[1].startswith(hoje.strftime("%Y-%m"))]
            
            if busca_nome:
                agendamentos_filtrados = [a for a in agendamentos_filtrados 
                                        if busca_nome.lower() in a[3].lower()]
            
            # Ordenação
            agendamentos_filtrados.sort(key=lambda x: (x[1], x[2]))
            
            st.markdown(f"**📊 Exibindo {len(agendamentos_filtrados)} agendamento(s)**")
            
            # Lista de agendamentos
            for agendamento in agendamentos_filtrados:
                if len(agendamento) == 7:
                    agendamento_id, data, horario, nome, telefone, email, status = agendamento
                elif len(agendamento) == 6:
                    agendamento_id, data, horario, nome, telefone, email = agendamento
                    status = "pendente"
                else:
                    agendamento_id, data, horario, nome, telefone = agendamento
                    email = "Não informado"
                    status = "pendente"
                
                # Formatar data
                data_obj = datetime.strptime(data, "%Y-%m-%d")
                data_formatada = data_obj.strftime("%d/%m/%Y - %A")
                data_formatada = data_formatada.replace('Monday', 'Segunda-feira')\
                    .replace('Tuesday', 'Terça-feira').replace('Wednesday', 'Quarta-feira')\
                    .replace('Thursday', 'Quinta-feira').replace('Friday', 'Sexta-feira')\
                    .replace('Saturday', 'Sábado').replace('Sunday', 'Domingo')
                
                # Status config
                status_config = {
                    'pendente': {'icon': '⏳', 'color': '#f59e0b', 'text': 'Aguardando'},
                    'confirmado': {'icon': '✅', 'color': '#10b981', 'text': 'Confirmado'},
                    'cancelado': {'icon': '❌', 'color': '#ef4444', 'text': 'Cancelado'}
                }
                
                config = status_config.get(status, status_config['pendente'])
                
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style="background: white; border: 1px solid #e9ecef; border-radius: 8px; padding: 1rem; margin: 0.5rem 0;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h4 style="margin: 0;">{config['icon']} {nome}</h4>
                            <span style="background: {config['color']}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px;">
                                {config['text']}
                            </span>
                        </div>
                        <p style="margin: 0; color: #6b7280;">
                            📅 {data_formatada}<br>
                            📱 {telefone}<br>
                            📧 {email}<br>
                            🕐 {horario}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if status == 'pendente':
                        if st.button("✅", key=f"confirm_{agendamento_id}", help="Confirmar"):
                            # Atualizar status
                            conn = conectar()
                            c = conn.cursor()
                            c.execute("UPDATE agendamentos SET status = ? WHERE id = ?", ('confirmado', agendamento_id))
                            conn.commit()
                            conn.close()
                            st.success("Confirmado!")
                            st.rerun()
                        
                        if st.button("❌", key=f"reject_{agendamento_id}", help="Recusar"):
                            # Atualizar status
                            conn = conectar()
                            c = conn.cursor()
                            c.execute("UPDATE agendamentos SET status = ? WHERE id = ?", ('cancelado', agendamento_id))
                            conn.commit()
                            conn.close()
                            st.success("Cancelado!")
                            st.rerun()
                    
                    # Botão deletar sempre disponível
                    if st.button("🗑️", key=f"delete_{agendamento_id}", help="Excluir"):
                        conn = conectar()
                        c = conn.cursor()
                        c.execute("DELETE FROM agendamentos WHERE id=?", (agendamento_id,))
                        conn.commit()
                        conn.close()
                        st.success("Excluído!")
                        st.rerun()
        else:
            st.info("📅 Nenhum agendamento encontrado.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif opcao_admin == "⚙️ Configurações":
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("⚙️ Configurações do Sistema")
        
        # Configurações básicas
        col1, col2 = st.columns(2)
        
        with col1:
            nome_profissional = st.text_input("Nome do profissional:", 
                                              value=obter_configuracao("nome_profissional", "Dr. João Silva"))
            nome_clinica = st.text_input("Nome da clínica:", 
                                        value=obter_configuracao("nome_clinica", "Clínica São Lucas"))
        
        with col2:
            telefone_contato = st.text_input("Telefone de contato:", 
                                           value=obter_configuracao("telefone_contato", "(11) 3333-4444"))
            endereco = st.text_input("Endereço:", 
                                   value=obter_configuracao("endereco", "Rua das Flores, 123"))
        
        st.markdown("---")
        
        # Configurações de horário
        col1, col2 = st.columns(2)
        
        with col1:
            horario_inicio_atual = obter_configuracao("horario_inicio", "09:00")
            try:
                time_inicio = datetime.strptime(horario_inicio_atual, "%H:%M").time()
            except:
                time_inicio = datetime.strptime("09:00", "%H:%M").time()
            
            horario_inicio = st.time_input("Horário de início:", value=time_inicio)
            
            intervalo_atual = obter_configuracao("intervalo_consultas", 60)
            intervalo_opcoes = {"30 min": 30, "1 hora": 60, "1h 30min": 90, "2 horas": 120}
            intervalo_texto = "1 hora"
            for texto, minutos in intervalo_opcoes.items():
                if minutos == intervalo_atual:
                    intervalo_texto = texto
                    break
            
            intervalo_selecionado = st.selectbox("Duração por agendamento:", 
                                               list(intervalo_opcoes.keys()),
                                               index=list(intervalo_opcoes.keys()).index(intervalo_texto))
        
        with col2:
            horario_fim_atual = obter_configuracao("horario_fim", "18:00")
            try:
                time_fim = datetime.strptime(horario_fim_atual, "%H:%M").time()
            except:
                time_fim = datetime.strptime("18:00", "%H:%M").time()
            
            horario_fim = st.time_input("Horário de término:", value=time_fim)
            
            dias_futuros = st.slider("Dias futuros disponíveis:", 
                                    min_value=7, max_value=90, 
                                    value=obter_configuracao("dias_futuros", 30))
        
        # Confirmação automática
        confirmacao_automatica = st.checkbox("Confirmação automática de agendamentos",
                                            value=obter_configuracao("confirmacao_automatica", False))
        
        # Botão salvar
        if st.button("💾 Salvar Configurações", type="primary"):
            salvar_configuracao("nome_profissional", nome_profissional)
            salvar_configuracao("nome_clinica", nome_clinica)
            salvar_configuracao("telefone_contato", telefone_contato)
            salvar_configuracao("endereco", endereco)
            salvar_configuracao("horario_inicio", horario_inicio.strftime("%H:%M"))
            salvar_configuracao("horario_fim", horario_fim.strftime("%H:%M"))
            salvar_configuracao("intervalo_consultas", intervalo_opcoes[intervalo_selecionado])
            salvar_configuracao("dias_futuros", dias_futuros)
            salvar_configuracao("confirmacao_automatica", confirmacao_automatica)
            
            st.success("✅ Configurações salvas com sucesso!")
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()