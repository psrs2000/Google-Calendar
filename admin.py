import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="Painel Administrativo",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS MODERNO E PROFISSIONAL
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
    .admin-header {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .admin-header h1 {
        color: #1f2937;
        font-size: 2rem;
        margin: 0;
        font-weight: 700;
    }
    
    .admin-header .badge {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 600;
    }
    
    /* Cards de estatísticas */
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
    
    .stat-card.warning::before {
        background: linear-gradient(90deg, #f59e0b, #d97706);
    }
    
    .stat-card.success::before {
        background: linear-gradient(90deg, #10b981, #059669);
    }
    
    .stat-card.danger::before {
        background: linear-gradient(90deg, #ef4444, #dc2626);
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
    
    .stat-icon {
        font-size: 3rem;
        opacity: 0.1;
        position: absolute;
        top: 1rem;
        right: 1rem;
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
    
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #f1f3f5;
    }
    
    .card-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1f2937;
        margin: 0;
    }
    
    /* Inputs customizados */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stDateInput > div > div > input,
    .stMultiSelect > div > div > div {
        border: 2px solid #e9ecef !important;
        border-radius: 8px !important;
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
    .stDateInput > label,
    .stMultiSelect > label {
        font-weight: 600 !important;
        color: #374151 !important;
        font-size: 16px !important;
        margin-bottom: 8px !important;
    }
    
    /* Botões modernos */
    .stButton > button {
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        border: 2px solid transparent !important;
    }
    
    /* Botão primário */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Botão secundário */
    .stButton > button[kind="secondary"] {
        background: white !important;
        color: #667eea !important;
        border-color: #667eea !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: #667eea !important;
        color: white !important;
    }
    
    /* Alertas profissionais */
    .alert {
        padding: 16px 20px;
        border-radius: 8px;
        margin: 16px 0;
        font-weight: 500;
        border-left: 4px solid;
    }
    
    .alert-success {
        background: #ecfdf5;
        color: #047857;
        border-left-color: #10b981;
    }
    
    .alert-error {
        background: #fef2f2;
        color: #b91c1c;
        border-left-color: #ef4444;
    }
    
    .alert-warning {
        background: #fffbeb;
        color: #b45309;
        border-left-color: #f59e0b;
    }
    
    .alert-info {
        background: #eff6ff;
        color: #1d4ed8;
        border-left-color: #3b82f6;
    }
    
    /* Lista de agendamentos */
    .appointment-list {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .appointment-item {
        background: white;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .appointment-item:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    .appointment-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .appointment-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1f2937;
    }
    
    .appointment-time {
        color: #667eea;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    .appointment-details {
        color: #6b7280;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    .appointment-actions {
        margin-top: 1rem;
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
    }
    
    /* Status badges */
    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .status-pending {
        background: #fef3c7;
        color: #92400e;
    }
    
    .status-confirmed {
        background: #dcfce7;
        color: #166534;
    }
    
    .status-cancelled {
        background: #fee2e2;
        color: #991b1b;
    }
    
    /* Configurações de dias */
    .days-config {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .day-card {
        background: #f8f9fa;
        border: 2px solid #e9ecef;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .day-card.selected {
        background: #667eea;
        color: white;
        border-color: #667eea;
    }
    
    .day-card:hover {
        border-color: #667eea;
    }
    
    /* Blocked dates */
    .blocked-date {
        background: #fee2e2;
        border: 1px solid #fecaca;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .blocked-date-text {
        color: #991b1b;
        font-weight: 500;
    }
    
    /* Responsividade */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }
        
        .admin-header {
            flex-direction: column;
            gap: 1rem;
            text-align: center;
        }
        
        .stats-container {
            grid-template-columns: 1fr;
        }
        
        .main-card {
            padding: 1.5rem;
        }
        
        .appointment-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.5rem;
        }
        
        .appointment-actions {
            justify-content: flex-start;
        }
    }
    
    /* Animações */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* DataFrames customizados */
    .stDataFrame {
        border: 1px solid #e9ecef;
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Métricas customizadas */
    [data-testid="metric-container"] {
        background: white;
        border: 1px solid #e9ecef;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# Configurações
DB = "agenda.db"
# DEBUG: Verificar banco
import os
st.write(f"🔍 DEBUG Admin - Banco existe? {os.path.exists(DB)}")
st.write(f"📁 DEBUG Admin - Caminho: {os.path.abspath(DB)}")
# NOVO DEBUG: Contar agendamentos
conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute("SELECT COUNT(*) FROM agendamentos")
total = c.fetchone()[0]
conn.close()
st.write(f"📊 DEBUG Admin - Total de agendamentos no banco: {total}")

# Senha segura via Streamlit Secrets
try:
    SENHA_CORRETA = st.secrets["ADMIN_PASSWORD"]
except:
    SENHA_CORRETA = "admin123"  # Fallback para desenvolvimento local

# Funções do banco
def conectar():
    return sqlite3.connect(DB)

def init_config():
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

    # Tabela de dias úteis
    c.execute('''
        CREATE TABLE IF NOT EXISTS dias_uteis (
            dia TEXT PRIMARY KEY
        )
    ''')

    # Tabela de datas bloqueadas
    c.execute('''
        CREATE TABLE IF NOT EXISTS bloqueios (
            data TEXT PRIMARY KEY
        )
    ''')

    # Tabela de configurações gerais
    c.execute('''
        CREATE TABLE IF NOT EXISTS configuracoes (
            chave TEXT PRIMARY KEY,
            valor TEXT
        )
    ''')

    # Verificar se a coluna status existe, se não, adicionar
    try:
        c.execute("SELECT status FROM agendamentos LIMIT 1")
    except sqlite3.OperationalError:
        # Coluna status não existe, vamos adicionar
        c.execute("ALTER TABLE agendamentos ADD COLUMN status TEXT DEFAULT 'pendente'")
        print("✅ Coluna 'status' adicionada à tabela agendamentos")

    # Tabela de bloqueios de horários específicos
    c.execute('''
        CREATE TABLE IF NOT EXISTS bloqueios_horarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            horario TEXT,
            UNIQUE(data, horario)
        )
    ''')
    
    # Tabela de bloqueios permanentes (horários que ficam sempre bloqueados)
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

def salvar_dias_uteis(dias):
    conn = conectar()
    c = conn.cursor()
    c.execute("DELETE FROM dias_uteis")
    for dia in dias:
        c.execute("INSERT INTO dias_uteis (dia) VALUES (?)", (dia,))
    conn.commit()
    conn.close()

def salvar_configuracao(chave, valor):
    conn = conectar()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO configuracoes (chave, valor) VALUES (?, ?)", (chave, str(valor)))
    conn.commit()
    conn.close()

def obter_configuracao(chave, padrao=None):
    conn = conectar()
    c = conn.cursor()
    try:
        c.execute("SELECT valor FROM configuracoes WHERE chave=?", (chave,))
        resultado = c.fetchone()
        if resultado:
            valor = resultado[0]
            
            # Converter strings boolean de volta para boolean
            if valor == "True":
                return True
            elif valor == "False":
                return False
            
            # Tentar converter para int se possível
            try:
                return int(valor)
            except ValueError:
                # Tentar converter para float
                try:
                    return float(valor)
                except ValueError:
                    return valor
        return padrao
    except:
        return padrao
    finally:
        conn.close()

def obter_dias_uteis():
    conn = conectar()
    c = conn.cursor()
    try:
        c.execute("SELECT dia FROM dias_uteis")
        dias = [linha[0] for linha in c.fetchall()]
        if not dias:  # Se não há dias configurados, usar padrão
            dias = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    except:
        dias = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    conn.close()
    return dias

def adicionar_bloqueio(data):
    conn = conectar()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO bloqueios (data) VALUES (?)", (data,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def remover_bloqueio(data):
    conn = conectar()
    c = conn.cursor()
    c.execute("DELETE FROM bloqueios WHERE data=?", (data,))
    conn.commit()
    conn.close()

def obter_bloqueios():
    conn = conectar()
    c = conn.cursor()
    try:
        c.execute("SELECT data FROM bloqueios ORDER BY data")
        datas = [linha[0] for linha in c.fetchall()]
    except:
        datas = []
    conn.close()
    return datas

def adicionar_bloqueio_horario(data, horario):
    conn = conectar()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO bloqueios_horarios (data, horario) VALUES (?, ?)", (data, horario))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def remover_bloqueio_horario(data, horario):
    conn = conectar()
    c = conn.cursor()
    c.execute("DELETE FROM bloqueios_horarios WHERE data=? AND horario=?", (data, horario))
    conn.commit()
    conn.close()

def obter_bloqueios_horarios():
    conn = conectar()
    c = conn.cursor()
    try:
        c.execute("SELECT data, horario FROM bloqueios_horarios ORDER BY data, horario")
        bloqueios = c.fetchall()
    except:
        bloqueios = []
    conn.close()
    return bloqueios
    
def adicionar_bloqueio_permanente(horario_inicio, horario_fim, dias_semana, descricao):
    """Adiciona um bloqueio permanente"""
    conn = conectar()
    c = conn.cursor()
    try:
        dias_str = ",".join(dias_semana)
        c.execute("INSERT INTO bloqueios_permanentes (horario_inicio, horario_fim, dias_semana, descricao) VALUES (?, ?, ?, ?)", 
                  (horario_inicio, horario_fim, dias_str, descricao))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao adicionar bloqueio permanente: {e}")
        return False
    finally:
        conn.close()

def obter_bloqueios_permanentes():
    """Obtém todos os bloqueios permanentes"""
    conn = conectar()
    c = conn.cursor()
    try:
        c.execute("SELECT id, horario_inicio, horario_fim, dias_semana, descricao FROM bloqueios_permanentes ORDER BY horario_inicio")
        bloqueios = c.fetchall()
        return bloqueios
    except:
        return []
    finally:
        conn.close()

def remover_bloqueio_permanente(bloqueio_id):
    """Remove um bloqueio permanente"""
    conn = conectar()
    c = conn.cursor()
    try:
        c.execute("DELETE FROM bloqueios_permanentes WHERE id=?", (bloqueio_id,))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def horario_bloqueado_permanente(data, horario):
    """Verifica se um horário está bloqueado permanentemente"""
    conn = conectar()
    c = conn.cursor()
    try:
        # Descobrir o dia da semana
        from datetime import datetime
        data_obj = datetime.strptime(data, "%Y-%m-%d")
        dia_semana = data_obj.strftime("%A")  # Monday, Tuesday, etc.
        
        # Buscar bloqueios permanentes
        c.execute("SELECT horario_inicio, horario_fim, dias_semana FROM bloqueios_permanentes")
        bloqueios = c.fetchall()
        
        for inicio, fim, dias in bloqueios:
            # Verificar se o dia está nos dias bloqueados
            if dia_semana in dias.split(","):
                # Verificar se o horário está no intervalo
                if inicio <= horario <= fim:
                    return True
        
        return False
    except:
        return False
    finally:
        conn.close()    

def horario_esta_bloqueado(data, horario):
    """Verifica se um horário específico está bloqueado"""
    conn = conectar()
    c = conn.cursor()
    try:
        # Verificar se o dia inteiro está bloqueado
        c.execute("SELECT 1 FROM bloqueios WHERE data=?", (data,))
        if c.fetchone():
            return True
        
        # Verificar se o horário específico está bloqueado
        c.execute("SELECT 1 FROM bloqueios_horarios WHERE data=? AND horario=?", (data, horario))
        if c.fetchone():
            return True
        
        # NOVO: Verificar bloqueios permanentes
        if horario_bloqueado_permanente(data, horario):
            return True
        
        return False
    except:
        return False
    finally:
        conn.close()

def buscar_agendamentos():
    conn = conectar()
    c = conn.cursor()
    
    # GARANTIR que a coluna email e status existem
    try:
        c.execute("SELECT email FROM agendamentos LIMIT 1")
    except sqlite3.OperationalError:
        # Coluna email não existe
        try:
            c.execute("ALTER TABLE agendamentos ADD COLUMN email TEXT DEFAULT ''")
            conn.commit()
        except:
            pass
    
    try:
        c.execute("SELECT status FROM agendamentos LIMIT 1")
    except sqlite3.OperationalError:
        # Coluna status não existe
        try:
            c.execute("ALTER TABLE agendamentos ADD COLUMN status TEXT DEFAULT 'pendente'")
            conn.commit()
        except:
            pass
    
    # Buscar agendamentos com todas as colunas
    try:
        c.execute("SELECT id, data, horario, nome_cliente, telefone, email, status FROM agendamentos ORDER BY data, horario")
        agendamentos = c.fetchall()
    except:
        # Fallback caso alguma coluna ainda não exista
        try:
            c.execute("SELECT id, data, horario, nome_cliente, telefone FROM agendamentos ORDER BY data, horario")
            agendamentos_sem_extras = c.fetchall()
            # Adicionar campos vazios para compatibilidade
            agendamentos = [ag + ('', 'pendente') for ag in agendamentos_sem_extras]
        except:
            agendamentos = []
    
    conn.close()
    return agendamentos

def atualizar_status_agendamento(agendamento_id, novo_status):
    conn = conectar()
    c = conn.cursor()
    
    # Buscar dados do agendamento antes de atualizar
    c.execute("SELECT nome_cliente, email, data, horario FROM agendamentos WHERE id = ?", (agendamento_id,))
    agendamento_dados = c.fetchone()
    
    # Atualizar status
    c.execute("UPDATE agendamentos SET status = ? WHERE id = ?", (novo_status, agendamento_id))
    conn.commit()
    conn.close()
    
    # Se foi confirmado e tem dados de email, enviar confirmação
    if novo_status == 'confirmado' and agendamento_dados and len(agendamento_dados) >= 4:
        nome_cliente, email, data, horario = agendamento_dados
        if email:  # Só enviar se tem email
            try:
                enviar_email_confirmacao(agendamento_id, nome_cliente, email, data, horario)
            except Exception as e:
                print(f"Erro ao enviar email de confirmação: {e}")

def deletar_agendamento(agendamento_id):
    conn = conectar()
    c = conn.cursor()
    c.execute("DELETE FROM agendamentos WHERE id=?", (agendamento_id,))
    conn.commit()
    conn.close()

# Inicializar banco
init_config()

# INTERFACE PRINCIPAL
def main():
    # Header com autenticação
    st.markdown("""
    <div class="admin-header">
        <h1>🔐 Painel Administrativo</h1>
        <div class="badge">Sistema de Agendamento</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Verificação de senha
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("🔒 Acesso Restrito")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            senha = st.text_input("Digite a senha de administrador:", type="password", placeholder="Digite sua senha")
            
            if st.button("🚪 Entrar", type="primary", use_container_width=True):
                if senha == SENHA_CORRETA:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.markdown("""
                    <div class="alert alert-error">
                        ❌ <strong>Senha incorreta!</strong> Tente novamente.
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Interface administrativa autenticada
    admin_interface()

def admin_interface():
    # Botão de logout no sidebar
    with st.sidebar:
        st.markdown("### 🔧 Menu Administrativo")
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
        
        st.markdown("---")
        
        # Menu de navegação
        opcao = st.selectbox(
            "Escolha uma opção:",
            ["📊 Dashboard", "⚙️ Configurações Gerais", "📅 Configurar Agenda", "🗓️ Gerenciar Bloqueios", "👥 Lista de Agendamentos"],
            key="menu_opcao"
        )
    
    # Carregar dados
    agendamentos = buscar_agendamentos()
    bloqueios = obter_bloqueios()
    
    # Estatísticas
    hoje = datetime.now().strftime("%Y-%m-%d")
    agendamentos_hoje = [a for a in agendamentos if a[1] == hoje]
    agendamentos_mes = [a for a in agendamentos if a[1].startswith(datetime.now().strftime("%Y-%m"))]
    
    # Cards de estatísticas
    st.markdown("""
    <div class="stats-container">
        <div class="stat-card">
            <div class="stat-icon">📅</div>
            <div class="stat-number">{}</div>
            <div class="stat-label">Agendamentos Hoje</div>
        </div>
        <div class="stat-card success">
            <div class="stat-icon">📊</div>
            <div class="stat-number">{}</div>
            <div class="stat-label">Total Este Mês</div>
        </div>
        <div class="stat-card warning">
            <div class="stat-icon">🚫</div>
            <div class="stat-number">{}</div>
            <div class="stat-label">Datas Bloqueadas</div>
        </div>
        <div class="stat-card danger">
            <div class="stat-icon">⏰</div>
            <div class="stat-number">{}</div>
            <div class="stat-label">Total de Agendamentos</div>
        </div>
    </div>
    """.format(len(agendamentos_hoje), len(agendamentos_mes), len(bloqueios), len(agendamentos)), unsafe_allow_html=True)
    
    # Conteúdo baseado na opção selecionada
    if opcao == "📊 Dashboard":
        dashboard_view(agendamentos)
    elif opcao == "⚙️ Configurações Gerais":
        configuracoes_gerais_view()
    elif opcao == "📅 Configurar Agenda":
        configurar_agenda_view()
    elif opcao == "🗓️ Gerenciar Bloqueios":
        gerenciar_bloqueios_view()
    elif opcao == "👥 Lista de Agendamentos":
        lista_agendamentos_view(agendamentos)

def dashboard_view(agendamentos):
    st.markdown('<div class="main-card fade-in">', unsafe_allow_html=True)
    st.markdown('<div class="card-header"><h2 class="card-title">📊 Dashboard</h2></div>', unsafe_allow_html=True)
    
    if agendamentos:
        # DEBUG: Ver quantas colunas temos
        num_colunas = len(agendamentos[0]) if agendamentos else 0
        st.write(f"DEBUG: Dados têm {num_colunas} colunas")
        
        # Criar DataFrame baseado no número real de colunas
        if num_colunas >= 7:
            # Com email e status
            df = pd.DataFrame(agendamentos, columns=['ID', 'Data', 'Horário', 'Nome', 'Telefone', 'Email', 'Status'])
        elif num_colunas == 6:
            # Com email mas sem status
            df = pd.DataFrame(agendamentos, columns=['ID', 'Data', 'Horário', 'Nome', 'Telefone', 'Email'])
        else:
            # Dados básicos
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
            <div class="appointment-item">
                <div class="appointment-header">
                    <div class="appointment-title">👤 {agendamento['Nome']}</div>
                    <div class="appointment-time">🕐 {agendamento['Horário']}</div>
                </div>
                <div class="appointment-details">
                    📅 {data_formatada}<br>
                    📱 {agendamento['Telefone']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("📊 Ainda não há dados suficientes para exibir estatísticas.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def configuracoes_gerais_view():
    st.markdown('<div class="main-card fade-in">', unsafe_allow_html=True)
    st.markdown('<div class="card-header"><h2 class="card-title">⚙️ Configurações Gerais</h2></div>', unsafe_allow_html=True)
    
    # Configurações de agenda
    st.subheader("📅 Configurações de Agendamento")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📆 Período de Agendamento**")
        
        # Dias futuros disponíveis
        dias_futuros_atual = obter_configuracao("dias_futuros", 30)
        dias_futuros = st.slider(
            "Quantos dias no futuro a agenda ficará aberta:",
            min_value=7,
            max_value=120,
            value=dias_futuros_atual,
            step=1,
            help="Defina até quantos dias no futuro os clientes podem agendar"
        )
        
        # Antecedência mínima
        antecedencia_atual = obter_configuracao("antecedencia_minima", 2)
        antecedencia_opcoes = {
            "30 minutos": 0.5,
            "1 hora": 1,
            "2 horas": 2,
            "4 horas": 4,
            "12 horas": 12,
            "24 horas": 24
        }
        
        antecedencia_texto = "2 horas"  # padrão
        for texto, horas in antecedencia_opcoes.items():
            if horas == antecedencia_atual:
                antecedencia_texto = texto
                break
        
        antecedencia_selecionada = st.selectbox(
            "Antecedência mínima para agendamento:",
            list(antecedencia_opcoes.keys()),
            index=list(antecedencia_opcoes.keys()).index(antecedencia_texto),
            help="Tempo mínimo necessário entre o agendamento e a consulta"
        )
        
        antecedencia_valor = antecedencia_opcoes[antecedencia_selecionada]
    
    with col2:
        st.markdown("**🕐 Horários de Funcionamento**")
        
        # Horário de início
        horario_inicio_atual = obter_configuracao("horario_inicio", "09:00")
        try:
            hora_inicio, min_inicio = map(int, horario_inicio_atual.split(":"))
            time_inicio = datetime.strptime(horario_inicio_atual, "%H:%M").time()
        except:
            time_inicio = datetime.strptime("09:00", "%H:%M").time()
        
        horario_inicio = st.time_input(
            "Horário de início:",
            value=time_inicio,
            help="Primeiro horário disponível para agendamento"
        )
        
        # Horário de fim
        horario_fim_atual = obter_configuracao("horario_fim", "18:00")
        try:
            time_fim = datetime.strptime(horario_fim_atual, "%H:%M").time()
        except:
            time_fim = datetime.strptime("18:00", "%H:%M").time()
        
        horario_fim = st.time_input(
            "Horário de término:",
            value=time_fim,
            help="Último horário disponível para agendamento"
        )
        
        # Intervalo entre consultas
        intervalo_atual = obter_configuracao("intervalo_consultas", 60)
        intervalo_opcoes = {
            "15 minutos": 15,
            "30 minutos": 30,
            "45 minutos": 45,
            "1 hora": 60,
            "1h 30min": 90,
            "2 horas": 120
        }
        
        intervalo_texto = "1 hora"  # padrão
        for texto, minutos in intervalo_opcoes.items():
            if minutos == intervalo_atual:
                intervalo_texto = texto
                break
        
        intervalo_selecionado = st.selectbox(
            "Duração de cada agendamento:",
            list(intervalo_opcoes.keys()),
            index=list(intervalo_opcoes.keys()).index(intervalo_texto),
            help="Tempo padrão reservado para cada agendamento"
        )
        
        intervalo_valor = intervalo_opcoes[intervalo_selecionado]
    
    # Configurações de contato
    st.markdown("---")
    st.subheader("📞 Informações de Contato")
    
    col1, col2 = st.columns(2)
    
    # Configuração de confirmação automática
    st.markdown("**🔄 Modo de Confirmação**")
    confirmacao_automatica = st.checkbox(
        "Confirmação automática de agendamentos",
        value=obter_configuracao("confirmacao_automatica", False),
        help="Se ativado, agendamentos são confirmados automaticamente."
    )


    st.markdown("---")
    st.subheader("📞 Informações de Contato")
    
    with col1:
        nome_profissional = st.text_input(
            "Nome do profissional:",
            value=obter_configuracao("nome_profissional", "Dr. João Silva"),
            help="Nome que aparecerá no sistema"
        )
        
        nome_clinica = st.text_input(
            "Nome da clínica/estabelecimento:",
            value=obter_configuracao("nome_clinica", "Clínica São Lucas"),
            help="Nome do local de atendimento"
        )
    
    with col2:
        telefone_contato = st.text_input(
            "Telefone de contato:",
            value=obter_configuracao("telefone_contato", "(11) 3333-4444"),
            help="Telefone que aparecerá no sistema"
        )
        
        endereco = st.text_input(
            "Endereço:",
            value=obter_configuracao("endereco", "Rua das Flores, 123"),
            help="Endereço do local de atendimento"
        )
    
    # Configurações de email
    st.markdown("---")
    st.subheader("📧 Configurações de Email")
    
    col1, col2 = st.columns(2)
    
    with col1:
        email_sistema = st.text_input(
            "Email do sistema:",
            value=obter_configuracao("email_sistema", ""),
            placeholder="sistema@clinica.com",
            help="Email que enviará as confirmações automáticas"
        )
        
        servidor_smtp = st.text_input(
            "Servidor SMTP:",
            value=obter_configuracao("servidor_smtp", "smtp.gmail.com"),
            help="Para Gmail: smtp.gmail.com"
        )
    
    with col2:
        senha_email = st.text_input(
            "Senha do email:",
            value=obter_configuracao("senha_email", ""),
            type="password",
            help="Para Gmail: use senha de app (não a senha normal)"
        )
        
        porta_smtp = st.number_input(
            "Porta SMTP:",
            value=obter_configuracao("porta_smtp", 587),
            help="Para Gmail: 587"
        )
    
    # Checkbox para ativar envio automático
    envio_automatico = st.checkbox(
        "Envio automático de confirmação por email",
        value=obter_configuracao("envio_automatico", False),
        help="Se ativado, enviará email automaticamente quando confirmar agendamento"
    )
    
    # Botão para salvar
    st.markdown("---")
    if st.button("💾 Salvar Todas as Configurações", type="primary", use_container_width=True):
        # Salvar todas as configurações
        salvar_configuracao("dias_futuros", dias_futuros)
        salvar_configuracao("antecedencia_minima", antecedencia_valor)
        salvar_configuracao("horario_inicio", horario_inicio.strftime("%H:%M"))
        salvar_configuracao("horario_fim", horario_fim.strftime("%H:%M"))
        salvar_configuracao("intervalo_consultas", intervalo_valor)
        salvar_configuracao("confirmacao_automatica", confirmacao_automatica)
        salvar_configuracao("confirmacao_automatica", confirmacao_automatica)
        salvar_configuracao("nome_profissional", nome_profissional)
        salvar_configuracao("nome_clinica", nome_clinica)
        salvar_configuracao("telefone_contato", telefone_contato)
        salvar_configuracao("endereco", endereco)
        salvar_configuracao("email_sistema", email_sistema)
        salvar_configuracao("senha_email", senha_email)
        salvar_configuracao("servidor_smtp", servidor_smtp)
        salvar_configuracao("porta_smtp", porta_smtp)
        salvar_configuracao("envio_automatico", envio_automatico)
        
        st.markdown("""
        <div class="alert alert-success">
            ✅ <strong>Configurações salvas com sucesso!</strong><br>
            Todas as alterações foram aplicadas ao sistema.
        </div>
        """, unsafe_allow_html=True)
    
    # Preview das configurações atuais
    st.markdown("---")
    st.subheader("👁️ Resumo das Configurações Atuais")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📅 Dias Futuros", f"{dias_futuros} dias")
        st.metric("⏰ Antecedência Mínima", antecedencia_selecionada)
    
    with col2:
        st.metric("🕐 Horário de Funcionamento", f"{horario_inicio.strftime('%H:%M')} - {horario_fim.strftime('%H:%M')}")
        st.metric("⏱️ Duração por Agendamento", intervalo_selecionado)
    
    with col3:
        st.metric("👨‍⚕️ Profissional", nome_profissional)
        st.metric("🏥 Local", nome_clinica)
    
    # Informações úteis
    st.markdown("---")
    st.markdown("""
    <div class="alert alert-info">
        💡 <strong>Dicas importantes:</strong><br>
        • <strong>Dias futuros:</strong> Período muito longo pode gerar cancelamentos, muito curto pode frustrar clientes<br>
        • <strong>Antecedência:</strong> Considere o tempo necessário para se preparar para os atendimentos<br>
        • <strong>Horários:</strong> Lembre-se de incluir intervalos para almoço e pausas<br>
        • <strong>Duração:</strong> Considere tempo para limpeza/preparação entre atendimentos
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def configurar_agenda_view():
    st.markdown('<div class="main-card fade-in">', unsafe_allow_html=True)
    st.markdown('<div class="card-header"><h2 class="card-title">📅 Configuração de Agenda</h2></div>', unsafe_allow_html=True)
    
    st.subheader("📋 Dias de Atendimento")
    
    dias_semana = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dias_pt = {
        "Monday": "Segunda-feira",
        "Tuesday": "Terça-feira", 
        "Wednesday": "Quarta-feira",
        "Thursday": "Quinta-feira",
        "Friday": "Sexta-feira",
        "Saturday": "Sábado",
        "Sunday": "Domingo"
    }
    
    dias_atuais = obter_dias_uteis()
    
    st.markdown("Selecione os dias da semana em que você atende:")
    
    # Layout em colunas para os dias
    cols = st.columns(4)
    dias_selecionados = []
    
    for i, (dia_en, dia_pt) in enumerate(dias_pt.items()):
        with cols[i % 4]:
            if st.checkbox(dia_pt, value=(dia_en in dias_atuais), key=f"dia_{dia_en}"):
                dias_selecionados.append(dia_en)
    
    if st.button("💾 Salvar Configuração", type="primary", use_container_width=True):
        salvar_dias_uteis(dias_selecionados)
        st.markdown("""
        <div class="alert alert-success">
            ✅ <strong>Configuração salva com sucesso!</strong><br>
            Os dias de atendimento foram atualizados.
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def gerenciar_bloqueios_view():
    st.markdown('<div class="main-card fade-in">', unsafe_allow_html=True)
    st.markdown('<div class="card-header"><h2 class="card-title">🗓️ Gerenciar Bloqueios</h2></div>', unsafe_allow_html=True)
    
    # Tabs para diferentes tipos de bloqueio
    tab1, tab2, tab3 = st.tabs(["📅 Bloquear Dias Inteiros", "🕐 Bloquear Horários Específicos", "⏰ Bloqueios Permanentes"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📌 Bloquear Data")
            data_bloqueio = st.date_input("Selecionar data para bloquear:", min_value=datetime.today())
            
            if st.button("🚫 Bloquear Dia Inteiro", type="primary", use_container_width=True):
                data_str = data_bloqueio.strftime("%Y-%m-%d")
                if adicionar_bloqueio(data_str):
                    st.markdown("""
                    <div class="alert alert-success">
                        ✅ <strong>Dia bloqueado com sucesso!</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    st.rerun()
                else:
                    st.markdown("""
                    <div class="alert alert-warning">
                        ⚠️ <strong>Esta data já está bloqueada.</strong>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            st.subheader("📋 Bloquear Período")
            data_inicio = st.date_input("Data inicial:", min_value=datetime.today())
            data_fim = st.date_input("Data final:", min_value=data_inicio)
            
            if st.button("🚫 Bloquear Período", type="primary", use_container_width=True):
                if data_fim >= data_inicio:
                    dias_bloqueados = 0
                    for i in range((data_fim - data_inicio).days + 1):
                        data = (data_inicio + timedelta(days=i)).strftime("%Y-%m-%d")
                        if adicionar_bloqueio(data):
                            dias_bloqueados += 1
                    
                    st.markdown(f"""
                    <div class="alert alert-success">
                        ✅ <strong>Período bloqueado com sucesso!</strong><br>
                        {dias_bloqueados} dias foram bloqueados.
                    </div>
                    """, unsafe_allow_html=True)
                    st.rerun()
                else:
                    st.markdown("""
                    <div class="alert alert-error">
                        ❌ <strong>Data final deve ser posterior à data inicial.</strong>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Lista de datas bloqueadas (dias inteiros)
        st.subheader("🚫 Dias Inteiros Bloqueados")
        bloqueios = obter_bloqueios()
        
        if bloqueios:
            for data in bloqueios:
                data_obj = datetime.strptime(data, "%Y-%m-%d")
                data_formatada = data_obj.strftime("%d/%m/%Y - %A")
                data_formatada = data_formatada.replace('Monday', 'Segunda-feira')\
                    .replace('Tuesday', 'Terça-feira').replace('Wednesday', 'Quarta-feira')\
                    .replace('Thursday', 'Quinta-feira').replace('Friday', 'Sexta-feira')\
                    .replace('Saturday', 'Sábado').replace('Sunday', 'Domingo')
                
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"""
                    <div style="background: #fee2e2; border: 1px solid #fecaca; border-radius: 8px; padding: 1rem; margin: 0.5rem 0;">
                        <span style="color: #991b1b; font-weight: 500;">🚫 {data_formatada}</span>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("🗑️", key=f"remove_dia_{data}", help="Remover bloqueio"):
                        remover_bloqueio(data)
                        st.rerun()
        else:
            st.info("📅 Nenhum dia inteiro bloqueado atualmente.")
    
    with tab2:
        st.subheader("🕐 Bloquear Horários Específicos")
        
        # Seleção de data
        data_horario = st.date_input("Selecionar data:", min_value=datetime.today(), key="data_horario")
        data_horario_str = data_horario.strftime("%Y-%m-%d")
        
        # Obter configurações de horários
        horario_inicio = obter_configuracao("horario_inicio", "09:00")
        horario_fim = obter_configuracao("horario_fim", "18:00")
        intervalo_consultas = obter_configuracao("intervalo_consultas", 60)
        
        # Gerar horários possíveis
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
        
        # Verificar quais horários já estão bloqueados
        bloqueios_dia = obter_bloqueios_horarios()
        horarios_bloqueados_dia = [h for d, h in bloqueios_dia if d == data_horario_str]
        
        # Interface para selecionar horários
        st.markdown("**Selecione os horários que deseja bloquear:**")
        
        # Layout em colunas para os horários
        cols = st.columns(4)
        horarios_selecionados = []
        
        for i, horario in enumerate(horarios_possiveis):
            with cols[i % 4]:
                ja_bloqueado = horario in horarios_bloqueados_dia
                if ja_bloqueado:
                    st.markdown(f"""
                    <div style="background: #fee2e2; border: 2px solid #ef4444; border-radius: 8px; padding: 8px; text-align: center; margin: 4px 0;">
                        <span style="color: #991b1b; font-weight: 600;">🚫 {horario}</span><br>
                        <small style="color: #991b1b;">Bloqueado</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    if st.checkbox(f"🕐 {horario}", key=f"horario_{horario}"):
                        horarios_selecionados.append(horario)
        
        # Botões de ação
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚫 Bloquear Horários Selecionados", type="primary", use_container_width=True):
                if horarios_selecionados:
                    bloqueados = 0
                    for horario in horarios_selecionados:
                        if adicionar_bloqueio_horario(data_horario_str, horario):
                            bloqueados += 1
                    
                    if bloqueados > 0:
                        st.markdown(f"""
                        <div class="alert alert-success">
                            ✅ <strong>{bloqueados} horário(s) bloqueado(s) com sucesso!</strong><br>
                            Data: {data_horario.strftime('%d/%m/%Y')}
                        </div>
                        """, unsafe_allow_html=True)
                        st.rerun()
                    else:
                        st.markdown("""
                        <div class="alert alert-warning">
                            ⚠️ <strong>Horários já estavam bloqueados.</strong>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="alert alert-warning">
                        ⚠️ <strong>Selecione pelo menos um horário para bloquear.</strong>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            if st.button("🔓 Desbloquear Todos os Horários do Dia", type="secondary", use_container_width=True):
                if horarios_bloqueados_dia:
                    for horario in horarios_bloqueados_dia:
                        remover_bloqueio_horario(data_horario_str, horario)
                    
                    st.markdown(f"""
                    <div class="alert alert-success">
                        ✅ <strong>Todos os horários do dia {data_horario.strftime('%d/%m/%Y')} foram desbloqueados!</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    st.rerun()
                else:
                    st.markdown("""
                    <div class="alert alert-info">
                        ℹ️ <strong>Nenhum horário bloqueado neste dia.</strong>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Lista de horários bloqueados
        st.subheader("🕐 Horários Específicos Bloqueados")
        bloqueios_horarios = obter_bloqueios_horarios()
        
        if bloqueios_horarios:
            # Agrupar por data
            bloqueios_por_data = {}
            for data, horario in bloqueios_horarios:
                if data not in bloqueios_por_data:
                    bloqueios_por_data[data] = []
                bloqueios_por_data[data].append(horario)
            
            for data, horarios in sorted(bloqueios_por_data.items()):
                data_obj = datetime.strptime(data, "%Y-%m-%d")
                data_formatada = data_obj.strftime("%d/%m/%Y - %A")
                data_formatada = data_formatada.replace('Monday', 'Segunda-feira')\
                    .replace('Tuesday', 'Terça-feira').replace('Wednesday', 'Quarta-feira')\
                    .replace('Thursday', 'Quinta-feira').replace('Friday', 'Sexta-feira')\
                    .replace('Saturday', 'Sábado').replace('Sunday', 'Domingo')
                
                st.markdown(f"**📅 {data_formatada}**")
                
                # Mostrar horários bloqueados em colunas
                cols = st.columns(6)
                for i, horario in enumerate(sorted(horarios)):
                    with cols[i % 6]:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"🚫 **{horario}**")
                        with col2:
                            if st.button("🗑️", key=f"remove_horario_{data}_{horario}", help="Remover bloqueio"):
                                remover_bloqueio_horario(data, horario)
                                st.rerun()
                
                st.markdown("---")
        else:
            st.info("🕐 Nenhum horário específico bloqueado atualmente.")

        with tab3:
                st.subheader("⏰ Bloqueios Permanentes")
                
                st.markdown("""
                <div class="alert alert-info">
                    ℹ️ <strong>Bloqueios Permanentes:</strong><br>
                    Configure horários que ficam sempre bloqueados (ex: almoço, intervalos, etc.)
                </div>
                """, unsafe_allow_html=True)
                
                # Formulário para novo bloqueio
                st.markdown("### ➕ Criar Novo Bloqueio Permanente")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    horario_inicio = st.time_input("Horário de início:", key="inicio_permanente")
                    
                with col2:
                    horario_fim = st.time_input("Horário de fim:", key="fim_permanente")
                
                # Seleção de dias da semana
                st.markdown("**Dias da semana:**")
                
                dias_opcoes = {
                    "Monday": "Segunda-feira",
                    "Tuesday": "Terça-feira", 
                    "Wednesday": "Quarta-feira",
                    "Thursday": "Quinta-feira",
                    "Friday": "Sexta-feira",
                    "Saturday": "Sábado",
                    "Sunday": "Domingo"
                }
                
                cols = st.columns(4)
                dias_selecionados = []
                
                for i, (dia_en, dia_pt) in enumerate(dias_opcoes.items()):
                    with cols[i % 4]:
                        if st.checkbox(dia_pt, key=f"dia_perm_{dia_en}"):
                            dias_selecionados.append(dia_en)
                
                # Descrição
                descricao = st.text_input("Descrição:", placeholder="Ex: Horário de Almoço", key="desc_permanente")
                
                # Botão para salvar
                if st.button("💾 Salvar Bloqueio Permanente", type="primary", use_container_width=True):
                    if horario_inicio and horario_fim and dias_selecionados and descricao:
                        if horario_fim > horario_inicio:
                            inicio_str = horario_inicio.strftime("%H:%M")
                            fim_str = horario_fim.strftime("%H:%M")
                            
                            if adicionar_bloqueio_permanente(inicio_str, fim_str, dias_selecionados, descricao):
                                st.markdown("""
                                <div class="alert alert-success">
                                    ✅ <strong>Bloqueio permanente criado com sucesso!</strong>
                                </div>
                                """, unsafe_allow_html=True)
                                st.rerun()
                            else:
                                st.markdown("""
                                <div class="alert alert-error">
                                    ❌ <strong>Erro ao criar bloqueio.</strong>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div class="alert alert-warning">
                                ⚠️ <strong>Horário de fim deve ser posterior ao horário de início.</strong>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="alert alert-warning">
                            ⚠️ <strong>Preencha todos os campos obrigatórios.</strong>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Lista de bloqueios permanentes existentes
                st.markdown("---")
                st.subheader("📋 Bloqueios Permanentes Ativos")
                
                bloqueios_permanentes = obter_bloqueios_permanentes()
                
                if bloqueios_permanentes:
                    for bloqueio in bloqueios_permanentes:
                        bloqueio_id, inicio, fim, dias, descricao = bloqueio
                        
                        # Converter dias de volta para português
                        dias_lista = dias.split(",")
                        dias_pt = [dias_opcoes.get(dia, dia) for dia in dias_lista]
                        dias_texto = ", ".join(dias_pt)
                        
                        col1, col2 = st.columns([4, 1])
                        
                        with col1:
                            st.markdown(f"""
                            <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 1rem; margin: 0.5rem 0;">
                                <h4 style="color: #856404; margin: 0 0 0.5rem 0;">⏰ {descricao}</h4>
                                <p style="margin: 0; color: #856404;">
                                    <strong>Horário:</strong> {inicio} às {fim}<br>
                                    <strong>Dias:</strong> {dias_texto}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            if st.button("🗑️", key=f"remove_perm_{bloqueio_id}", help="Remover bloqueio permanente"):
                                if remover_bloqueio_permanente(bloqueio_id):
                                    st.success("Bloqueio removido!")
                                    st.rerun()
                else:
                    st.info("📅 Nenhum bloqueio permanente configurado.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def lista_agendamentos_view(agendamentos):
    st.markdown('<div class="main-card fade-in">', unsafe_allow_html=True)
    st.markdown('<div class="card-header"><h2 class="card-title">👥 Lista de Agendamentos</h2></div>', unsafe_allow_html=True)
    
    if agendamentos:
        # Filtros
        col1, col2, col3 = st.columns(3)
        with col1:
            filtro_data = st.selectbox(
                "Filtrar por período:",
                ["Todos", "Hoje", "Esta Semana", "Este Mês", "Próximos 7 dias"]
            )
        
        with col2:
            busca_nome = st.text_input("Buscar por nome:", placeholder="Digite o nome do cliente")
        
        with col3:
            filtro_status = st.selectbox("Filtrar por status:", ["Todos", "Pendentes", "Confirmados", "Atendidos", "Cancelados"])
        
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
        elif filtro_data == "Próximos 7 dias":
            proximos_7 = hoje + timedelta(days=7)
            agendamentos_filtrados = [a for a in agendamentos_filtrados 
                                    if hoje <= datetime.strptime(a[1], "%Y-%m-%d").date() <= proximos_7]
        
        if busca_nome:
            agendamentos_filtrados = [a for a in agendamentos_filtrados 
                                    if busca_nome.lower() in a[3].lower()]
        
        # Filtrar por status
        if filtro_status != "Todos":
            status_map = {
                "Pendentes": "pendente",
                "Confirmados": "confirmado", 
                "Atendidos": "atendido",
                "Cancelados": "cancelado"
            }
            status_procurado = status_map[filtro_status]
            agendamentos_filtrados = [a for a in agendamentos_filtrados 
                                    if len(a) > 6 and a[6] == status_procurado]
        
        # Ordenação por data
        agendamentos_filtrados.sort(key=lambda x: (x[1], x[2]))
        
        st.markdown(f"**📊 Exibindo {len(agendamentos_filtrados)} agendamento(s)**")
        
        # Lista de agendamentos
        for agendamento in agendamentos_filtrados:
            if len(agendamento) == 7:  # Com email e status
                agendamento_id, data, horario, nome, telefone, email, status = agendamento
            elif len(agendamento) == 6:  # Com email mas sem status
                agendamento_id, data, horario, nome, telefone, email = agendamento
                status = "pendente"  # Status padrão
            else:  # Sem email nem status (compatibilidade)
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
            
            # Definir ícones e cores por status
            status_config = {
                'pendente': {'icon': '⏳', 'color': '#f59e0b', 'text': 'Aguardando Confirmação'},
                'confirmado': {'icon': '✅', 'color': '#3b82f6', 'text': 'Confirmado'},
                'atendido': {'icon': '🎉', 'color': '#10b981', 'text': 'Atendido'},
                'cancelado': {'icon': '❌', 'color': '#ef4444', 'text': 'Cancelado'}
            }
            
            config = status_config.get(status, status_config['pendente'])
            
            col1, col2 = st.columns([5, 1])
            
            with col1:
                st.markdown(f"""
                <div class="appointment-item">
                    <div class="appointment-header">
                        <div class="appointment-title">{config['icon']} {nome}</div>
                        <div class="appointment-time">🕐 {horario}</div>
                    </div>
                    <div class="appointment-details">
                        📅 {data_formatada}<br>
                        📱 {telefone}<br>
                        📧 {email}<br>
                        <span style="background: {config['color']}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: 600;">
                            {config['text']}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Botões de ação funcionais na coluna da direita
                if status == 'pendente':
                    if st.button("✅", key=f"confirm_{agendamento_id}", help="Confirmar agendamento"):
                        atualizar_status_agendamento(agendamento_id, 'confirmado')
                        
                        # Verificar se email foi enviado
                        envio_automatico = obter_configuracao("envio_automatico", False)
                        if envio_automatico and email and email != "Não informado":
                            st.success(f"✅ Agendamento de {nome} confirmado e email enviado!")
                        else:
                            st.success(f"✅ Agendamento de {nome} confirmado!")
                        st.rerun()
                    if st.button("❌", key=f"reject_{agendamento_id}", help="Recusar agendamento"):
                        atualizar_status_agendamento(agendamento_id, 'cancelado')
                        
                        # Enviar email de cancelamento
                        envio_automatico = obter_configuracao("envio_automatico", False)
                        if envio_automatico and email and email != "Não informado":
                            try:
                                enviar_email_cancelamento(nome, email, data, horario, "admin")
                                st.success(f"❌ Agendamento de {nome} recusado e email enviado!")
                            except:
                                st.success(f"❌ Agendamento de {nome} recusado!")
                        else:
                            st.success(f"❌ Agendamento de {nome} recusado!")
                        st.rerun()
                
                elif status == 'confirmado':
                    if st.button("🎉", key=f"attend_{agendamento_id}", help="Marcar como atendido"):
                        atualizar_status_agendamento(agendamento_id, 'atendido')
                        st.success(f"Agendamento de {nome} marcado como atendido!")
                        st.rerun()
                    if st.button("❌", key=f"cancel_{agendamento_id}", help="Cancelar agendamento"):
                        atualizar_status_agendamento(agendamento_id, 'cancelado')
                        
                        # Enviar email de cancelamento
                        envio_automatico = obter_configuracao("envio_automatico", False)
                        if envio_automatico and email and email != "Não informado":
                            try:
                                enviar_email_cancelamento(nome, email, data, horario, "admin")
                                st.success(f"❌ Agendamento de {nome} cancelado e email enviado!")
                            except:
                                st.success(f"❌ Agendamento de {nome} cancelado!")
                        else:
                            st.success(f"❌ Agendamento de {nome} cancelado!")
                        st.rerun()
                
                # Botão de exclusão sempre disponível
                if st.button("🗑️", key=f"delete_{agendamento_id}", help="Excluir agendamento"):
                    if st.session_state.get(f"confirm_delete_{agendamento_id}", False):
                        deletar_agendamento(agendamento_id)
                        st.success(f"Agendamento de {nome} excluído!")
                        st.rerun()
                    else:
                        st.session_state[f"confirm_delete_{agendamento_id}"] = True
                        st.warning("Clique novamente para confirmar exclusão")
        
        # Estatísticas da lista filtrada
        if agendamentos_filtrados:
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📊 Total Filtrado", len(agendamentos_filtrados))
            
            with col2:
                horarios = [a[2] for a in agendamentos_filtrados]
                horario_comum = max(set(horarios), key=horarios.count) if horarios else "N/A"
                st.metric("⏰ Horário Mais Comum", horario_comum)
            
            with col3:
                hoje_count = len([a for a in agendamentos_filtrados if a[1] == hoje.strftime("%Y-%m-%d")])
                st.metric("📅 Agendamentos Hoje", hoje_count)
    
    else:
        st.markdown("""
        <div class="alert alert-info">
            📅 <strong>Nenhum agendamento encontrado.</strong><br>
            Os agendamentos aparecerão aqui conforme forem sendo realizados pelos clientes.
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def enviar_email_confirmacao(agendamento_id, cliente_nome, cliente_email, data, horario):
    """Envia email de confirmação automático"""
    
    # Verificar se envio automático está ativado
    if not obter_configuracao("envio_automatico", False):
        return False
    
    try:
        # Obter configurações de email
        email_sistema = obter_configuracao("email_sistema", "")
        senha_email = obter_configuracao("senha_email", "")
        servidor_smtp = obter_configuracao("servidor_smtp", "smtp.gmail.com")
        porta_smtp = obter_configuracao("porta_smtp", 587)
        
        # Obter dados do profissional
        nome_profissional = obter_configuracao("nome_profissional", "Dr. João Silva")
        nome_clinica = obter_configuracao("nome_clinica", "Clínica São Lucas")
        telefone_contato = obter_configuracao("telefone_contato", "(11) 3333-4444")
        endereco = obter_configuracao("endereco", "Rua das Flores, 123")
        
        # Formatar data
        from datetime import datetime
        data_obj = datetime.strptime(data, "%Y-%m-%d")
        data_formatada = data_obj.strftime("%d/%m/%Y - %A")
        data_formatada = data_formatada.replace('Monday', 'Segunda-feira')\
            .replace('Tuesday', 'Terça-feira').replace('Wednesday', 'Quarta-feira')\
            .replace('Thursday', 'Quinta-feira').replace('Friday', 'Sexta-feira')\
            .replace('Saturday', 'Sábado').replace('Sunday', 'Domingo')
        
        # Criar mensagem
        msg = MIMEMultipart()
        msg['From'] = email_sistema
        msg['To'] = cliente_email
        msg['Subject'] = f"✅ Agendamento Confirmado - {nome_profissional}"
        
        # Corpo do email
        corpo = f"""
Olá {cliente_nome}!

Seu agendamento foi CONFIRMADO com sucesso!

📅 Data: {data_formatada}
⏰ Horário: {horario}
🏥 Local: {nome_clinica}
📍 Endereço: {endereco}
📞 Contato: {telefone_contato}

Aguardamos você!

Atenciosamente,
{nome_profissional}
{nome_clinica}
"""
        
        msg.attach(MIMEText(corpo, 'plain', 'utf-8'))
        
        # Enviar email
        server = smtplib.SMTP(servidor_smtp, porta_smtp)
        server.starttls()
        server.login(email_sistema, senha_email)
        server.send_message(msg)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        return False

def enviar_email_cancelamento(cliente_nome, cliente_email, data, horario, cancelado_por="cliente"):
    """Envia email de cancelamento"""
    
    # Verificar se envio automático está ativado
    if not obter_configuracao("envio_automatico", False):
        return False
    
    try:
        # Obter configurações de email
        email_sistema = obter_configuracao("email_sistema", "")
        senha_email = obter_configuracao("senha_email", "")
        servidor_smtp = obter_configuracao("servidor_smtp", "smtp.gmail.com")
        porta_smtp = obter_configuracao("porta_smtp", 587)
        
        # Se não tem configuração de email, não enviar
        if not email_sistema or not senha_email:
            return False
        
        # Obter dados do profissional
        nome_profissional = obter_configuracao("nome_profissional", "Dr. João Silva")
        nome_clinica = obter_configuracao("nome_clinica", "Clínica São Lucas")
        telefone_contato = obter_configuracao("telefone_contato", "(11) 3333-4444")
        endereco = obter_configuracao("endereco", "Rua das Flores, 123")
        
        # Formatar data
        from datetime import datetime
        data_obj = datetime.strptime(data, "%Y-%m-%d")
        data_formatada = data_obj.strftime("%d/%m/%Y - %A")
        data_formatada = data_formatada.replace('Monday', 'Segunda-feira')\
            .replace('Tuesday', 'Terça-feira').replace('Wednesday', 'Quarta-feira')\
            .replace('Thursday', 'Quinta-feira').replace('Friday', 'Sexta-feira')\
            .replace('Saturday', 'Sábado').replace('Sunday', 'Domingo')
        
        # Criar mensagem baseada em quem cancelou
        msg = MIMEMultipart()
        msg['From'] = email_sistema
        msg['To'] = cliente_email
        
        if cancelado_por == "cliente":
            # Cancelamento pelo próprio cliente
            msg['Subject'] = f"✅ Cancelamento Confirmado - {nome_profissional}"
            corpo = f"""
Olá {cliente_nome}!

Seu cancelamento foi processado com sucesso!

📅 Data cancelada: {data_formatada}
⏰ Horário cancelado: {horario}
🏥 Local: {nome_clinica}

Você pode fazer um novo agendamento quando desejar através do nosso sistema online.

📞 Dúvidas? Entre em contato: {telefone_contato}

Atenciosamente,
{nome_profissional}
{nome_clinica}
"""
        else:
            # Cancelamento pelo administrador
            msg['Subject'] = f"⚠️ Agendamento Cancelado - {nome_profissional}"
            corpo = f"""
Olá {cliente_nome}!

Infelizmente precisamos cancelar seu agendamento:

📅 Data: {data_formatada}
⏰ Horário: {horario}
🏥 Local: {nome_clinica}

Pedimos desculpas pelo inconveniente. 

Por favor, entre em contato conosco para reagendar:
📞 {telefone_contato}
📍 {endereco}

Ou faça um novo agendamento através do nosso sistema online.

Atenciosamente,
{nome_profissional}
{nome_clinica}
"""
        
        msg.attach(MIMEText(corpo, 'plain', 'utf-8'))
        
        # Enviar email
        server = smtplib.SMTP(servidor_smtp, porta_smtp)
        server.starttls()
        server.login(email_sistema, senha_email)
        server.send_message(msg)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Erro ao enviar email de cancelamento: {e}")
        return False

# Executar aplicação
if __name__ == "__main__":
    main()
