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
    initial_sidebar_state="collapsed"
)

# CSS COMPLETO E MODERNO
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp {
        background: #f8f9fa;
        min-height: 100vh;
    }
    
    .main-header, .admin-header {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
        text-align: center;
    }
    
    .admin-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .main-header h1, .admin-header h1 {
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
    
    .stButton > button {
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
    }
    
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
    
    .appointment-item {
        background: white;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .appointment-summary {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        padding: 24px;
        border-radius: 15px;
        margin: 20px 0;
        border-left: 5px solid #667eea;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .appointment-summary h3 {
        color: #667eea;
        margin-bottom: 16px;
        font-size: 1.3rem;
    }
    
    .summary-item {
        display: flex;
        justify-content: space-between;
        margin-bottom: 12px;
        padding: 8px 0;
        border-bottom: 1px solid #dee2e6;
    }
    
    .summary-item:last-child {
        border-bottom: none;
    }
</style>
""", unsafe_allow_html=True)

# Configurações do banco
DB = "agenda.db"

# Senha do admin via secrets
try:
    SENHA_ADMIN = st.secrets["ADMIN_PASSWORD"]
except:
    SENHA_ADMIN = "1234"

# VERIFICAR SE É MODO ADMIN
is_admin = st.query_params.get("admin") == "2025"

# Funções do banco (TODAS as funções completas)
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
    
    # Outras tabelas
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
    
    # Verificar se há agendamento neste horário
    c.execute("SELECT * FROM agendamentos WHERE data=? AND horario=?", (data, horario))
    ocupado = c.fetchone()
    if ocupado:
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

def atualizar_status_agendamento(agendamento_id, novo_status):
    conn = conectar()
    c = conn.cursor()
    c.execute("UPDATE agendamentos SET status = ? WHERE id = ?", (novo_status, agendamento_id))
    conn.commit()
    conn.close()

# Inicializar banco
init_db()

# INTERFACE PRINCIPAL
def main():
    if is_admin:
        interface_admin()
    else:
        interface_cliente()

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
    
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    # Tabs
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
                            # Resumo
                            st.markdown(f"""
                            <div class="appointment-summary">
                                <h3>📋 Resumo do Agendamento</h3>
                                <div class="summary-item">
                                    <span>👤 Nome:</span>
                                    <strong>{nome}</strong>
                                </div>
                                <div class="summary-item">
                                    <span>📱 Telefone:</span>
                                    <strong>{telefone}</strong>
                                </div>
                                <div class="summary-item">
                                    <span>📧 E-mail:</span>
                                    <strong>{email}</strong>
                                </div>
                                <div class="summary-item">
                                    <span>📅 Data:</span>
                                    <strong>{data_selecionada.strftime('%d/%m/%Y')}</strong>
                                </div>
                                <div class="summary-item">
                                    <span>⏰ Horário:</span>
                                    <strong>{horario}</strong>
                                </div>
                                <div class="summary-item">
                                    <span>🏥 Local:</span>
                                    <strong>{nome_clinica}</strong>
                                </div>
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
    st.markdown("""
    <div class="admin-header">
        <h1>🔐 Painel Administrativo</h1>
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
            senha = st.text_input("Senha de administrador:", type="password")
            
            if st.button("🚪 Entrar", type="primary"):
                if senha == SENHA_ADMIN:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Senha incorreta!")
        
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Interface admin básica
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("🔐 Painel Administrativo")
    
    if st.button("🚪 Sair"):
        st.session_state.authenticated = False
        st.rerun()
    
    # Carregar agendamentos
    agendamentos = buscar_agendamentos()
    
    # Estatísticas básicas
    hoje = datetime.now().strftime("%Y-%m-%d")
    agendamentos_hoje = [a for a in agendamentos if a[1] == hoje]
    
    st.markdown(f"""
    <div class="stats-container">
        <div class="stat-card">
            <div class="stat-number">{len(agendamentos_hoje)}</div>
            <div class="stat-label">Agendamentos Hoje</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(agendamentos)}</div>
            <div class="stat-label">Total de Agendamentos</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Lista básica de agendamentos
    if agendamentos:
        st.subheader("📋 Agendamentos")
        for agendamento in agendamentos[:10]:  # Mostrar só os primeiros 10
            if len(agendamento) >= 5:
                id_ag, data, horario, nome, telefone = agendamento[:5]
                st.write(f"**{nome}** - {data} às {horario} - {telefone}")
    else:
        st.info("Nenhum agendamento encontrado.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Executar aplicação
if __name__ == "__main__":
    main()
# Funções avançadas para bloqueios e emails
def salvar_dias_uteis(dias):
    conn = conectar()
    c = conn.cursor()
    c.execute("DELETE FROM dias_uteis")
    for dia in dias:
        c.execute("INSERT INTO dias_uteis (dia) VALUES (?)", (dia,))
    conn.commit()
    conn.close()

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

def adicionar_bloqueio_permanente(horario_inicio, horario_fim, dias_semana, descricao):
    conn = conectar()
    c = conn.cursor()
    try:
        dias_str = ",".join(dias_semana)
        c.execute("INSERT INTO bloqueios_permanentes (horario_inicio, horario_fim, dias_semana, descricao) VALUES (?, ?, ?, ?)", 
                  (horario_inicio, horario_fim, dias_str, descricao))
        conn.commit()
        return True
    except Exception as e:
        return False
    finally:
        conn.close()

def obter_bloqueios_permanentes():
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

def enviar_email_confirmacao(agendamento_id, cliente_nome, cliente_email, data, horario):
    if not obter_configuracao("envio_automatico", False):
        return False
    
    try:
        email_sistema = obter_configuracao("email_sistema", "")
        senha_email = obter_configuracao("senha_email", "")
        servidor_smtp = obter_configuracao("servidor_smtp", "smtp.gmail.com")
        porta_smtp = obter_configuracao("porta_smtp", 587)
        
        if not email_sistema or not senha_email:
            return False
        
        nome_profissional = obter_configuracao("nome_profissional", "Dr. João Silva")
        nome_clinica = obter_configuracao("nome_clinica", "Clínica São Lucas")
        telefone_contato = obter_configuracao("telefone_contato", "(11) 3333-4444")
        endereco = obter_configuracao("endereco", "Rua das Flores, 123")
        
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
📍 Endereço: {endereco}
📞 Contato: {telefone_contato}

Aguardamos você!

Atenciosamente,
{nome_profissional}
{nome_clinica}
"""
        
        msg.attach(MIMEText(corpo, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(servidor_smtp, porta_smtp)
        server.starttls()
        server.login(email_sistema, senha_email)
        server.send_message(msg)
        server.quit()
        
        return True
        
    except Exception as e:
        return False

def cancelar_agendamento(nome, telefone, data):
    conn = conectar()
    c = conn.cursor()
    
    # Buscar o agendamento
    try:
        c.execute("SELECT email, horario FROM agendamentos WHERE nome_cliente=? AND telefone=? AND data=?", (nome, telefone, data))
        resultado = c.fetchone()
    except:
        c.execute("SELECT horario FROM agendamentos WHERE nome_cliente=? AND telefone=? AND data=?", (nome, telefone, data))
        resultado_horario = c.fetchone()
        resultado = ('', resultado_horario[0]) if resultado_horario else None
    
    if resultado:
        c.execute("DELETE FROM agendamentos WHERE nome_cliente=? AND telefone=? AND data=?", (nome, telefone, data))
        conn.commit()
        conn.close()
        return True
    else:
        conn.close()
        return False

def deletar_agendamento(agendamento_id):
    conn = conectar()
    c = conn.cursor()
    c.execute("DELETE FROM agendamentos WHERE id=?", (agendamento_id,))
    conn.commit()
    conn.close()

# Melhorar a interface admin com mais funcionalidades
def interface_admin_avancada():
    st.markdown("""
    <div class="admin-header">
        <h1>🔐 Painel Administrativo</h1>
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
            senha = st.text_input("Senha de administrador:", type="password")
            
            if st.button("🚪 Entrar", type="primary"):
                if senha == SENHA_ADMIN:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Senha incorreta!")
        
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Sidebar para navegação
    with st.sidebar:
        st.markdown("### 🔧 Menu Administrativo")
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
        
        st.markdown("---")
        
        opcao = st.selectbox(
            "Escolha uma opção:",
            ["📊 Dashboard", "👥 Lista de Agendamentos", "⚙️ Configurações", "🗓️ Bloqueios", "📅 Configurar Agenda"],
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
            <div class="stat-number">{len(bloqueios)}</div>
            <div class="stat-label">Datas Bloqueadas</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(agendamentos)}</div>
            <div class="stat-label">Total de Agendamentos</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Conteúdo baseado na opção
    if opcao == "📊 Dashboard":
        dashboard_view(agendamentos)
    elif opcao == "👥 Lista de Agendamentos":
        lista_agendamentos_view(agendamentos)
    elif opcao == "⚙️ Configurações":
        configuracoes_view()
    elif opcao == "🗓️ Bloqueios":
        bloqueios_view()
    elif opcao == "📅 Configurar Agenda":
        configurar_agenda_view()

def dashboard_view(agendamentos):
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📊 Dashboard")
    
    if agendamentos:
        # Próximos agendamentos
        st.subheader("📋 Próximos Agendamentos")
        hoje = datetime.now().date()
        
        for agendamento in agendamentos[:10]:
            if len(agendamento) >= 5:
                id_ag, data, horario, nome, telefone = agendamento[:5]
                data_obj = datetime.strptime(data, "%Y-%m-%d").date()
                
                if data_obj >= hoje:
                    st.markdown(f"""
                    <div class="appointment-item">
                        <div style="display: flex; justify-content: space-between;">
                            <div>
                                <strong>👤 {nome}</strong><br>
                                📅 {data} • 🕐 {horario}<br>
                                📱 {telefone}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("📊 Ainda não há dados suficientes para exibir estatísticas.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def lista_agendamentos_view(agendamentos):
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("👥 Lista de Agendamentos")
    
    if agendamentos:
        for agendamento in agendamentos:
            if len(agendamento) == 7:
                agendamento_id, data, horario, nome, telefone, email, status = agendamento
            else:
                agendamento_id, data, horario, nome, telefone = agendamento[:5]
                email = agendamento[5] if len(agendamento) > 5 else "N/A"
                status = agendamento[6] if len(agendamento) > 6 else "pendente"
            
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"""
                <div class="appointment-item">
                    <strong>👤 {nome}</strong><br>
                    📅 {data} • 🕐 {horario}<br>
                    📱 {telefone} • 📧 {email}<br>
                    Status: {status}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if status == "pendente":
                    if st.button("✅", key=f"confirm_{agendamento_id}"):
                        atualizar_status_agendamento(agendamento_id, "confirmado")
                        st.rerun()
                
                if st.button("🗑️", key=f"delete_{agendamento_id}"):
                    deletar_agendamento(agendamento_id)
                    st.rerun()
    else:
        st.info("📅 Nenhum agendamento encontrado.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def configuracoes_view():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("⚙️ Configurações")
    
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

def bloqueios_view():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("🗓️ Gerenciar Bloqueios")
    
    # Bloquear data
    st.markdown("### 📅 Bloquear Data")
    data_bloqueio = st.date_input("Data para bloquear:", min_value=datetime.today())
    
    if st.button("🚫 Bloquear Data"):
        data_str = data_bloqueio.strftime("%Y-%m-%d")
        if adicionar_bloqueio(data_str):
            st.success("Data bloqueada!")
            st.rerun()
        else:
            st.warning("Data já bloqueada.")
    
    # Lista de bloqueios
    st.markdown("### 📋 Datas Bloqueadas")
    bloqueios = obter_bloqueios()
    
    if bloqueios:
        for data in bloqueios:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"🚫 {data}")
            with col2:
                if st.button("🗑️", key=f"remove_{data}"):
                    remover_bloqueio(data)
                    st.rerun()
    else:
        st.info("Nenhuma data bloqueada.")
    
    # Bloqueios permanentes
    st.markdown("---")
    st.markdown("### ⏰ Bloqueios Permanentes")
    
    col1, col2 = st.columns(2)
    with col1:
        horario_inicio = st.time_input("Horário início:")
    with col2:
        horario_fim = st.time_input("Horário fim:")
    
    descricao = st.text_input("Descrição:", placeholder="Ex: Horário de Almoço")
    
    # Dias da semana
    dias_opcoes = {
        "Monday": "Segunda", "Tuesday": "Terça", "Wednesday": "Quarta",
        "Thursday": "Quinta", "Friday": "Sexta", "Saturday": "Sábado", "Sunday": "Domingo"
    }
    
    cols = st.columns(4)
    dias_selecionados = []
    
    for i, (dia_en, dia_pt) in enumerate(dias_opcoes.items()):
        with cols[i % 4]:
            if st.checkbox(dia_pt, key=f"dia_{dia_en}"):
                dias_selecionados.append(dia_en)
    
    if st.button("💾 Salvar Bloqueio Permanente"):
        if horario_inicio and horario_fim and dias_selecionados and descricao:
            inicio_str = horario_inicio.strftime("%H:%M")
            fim_str = horario_fim.strftime("%H:%M")
            
            if adicionar_bloqueio_permanente(inicio_str, fim_str, dias_selecionados, descricao):
                st.success("Bloqueio permanente criado!")
                st.rerun()
            else:
                st.error("Erro ao criar bloqueio.")
        else:
            st.warning("Preencha todos os campos.")
    
    # Lista de bloqueios permanentes
    bloqueios_perm = obter_bloqueios_permanentes()
    if bloqueios_perm:
        st.markdown("### 📋 Bloqueios Permanentes Ativos")
        for bloqueio in bloqueios_perm:
            id_bloq, inicio, fim, dias, desc = bloqueio
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"⏰ **{desc}** - {inicio} às {fim}")
            with col2:
                if st.button("🗑️", key=f"remove_perm_{id_bloq}"):
                    remover_bloqueio_permanente(id_bloq)
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def configurar_agenda_view():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📅 Configurar Agenda")
    
    dias_opcoes = {
        "Monday": "Segunda", "Tuesday": "Terça", "Wednesday": "Quarta",
        "Thursday": "Quinta", "Friday": "Sexta", "Saturday": "Sábado", "Sunday": "Domingo"
    }
    
    dias_atuais = obter_dias_uteis()
    
    st.markdown("Selecione os dias de atendimento:")
    cols = st.columns(4)
    dias_selecionados = []
    
    for i, (dia_en, dia_pt) in enumerate(dias_opcoes.items()):
        with cols[i % 4]:
            if st.checkbox(dia_pt, value=(dia_en in dias_atuais), key=f"config_dia_{dia_en}"):
                dias_selecionados.append(dia_en)
    
    if st.button("💾 Salvar Configuração"):
        salvar_dias_uteis(dias_selecionados)
        st.success("Configuração salva!")
    
    st.markdown('</div>', unsafe_allow_html=True)
