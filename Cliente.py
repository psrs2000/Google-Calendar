import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuração da página
st.set_page_config(
    page_title="Agendamento Online",
    page_icon="💆‍♀️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS MODERNO E RESPONSIVO
st.markdown("""
<style>
    /* Reset e configurações globais */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
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
    
    /* Header principal */
    .main-header {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
        border: 1px solid #e9ecef;
    }
    
    .main-header h1 {
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
    
    /* Cards principais */
    .main-card {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
    }
    
    /* Tabs personalizadas */
    .custom-tabs {
        display: flex;
        background: #f8f9fa;
        border-radius: 15px;
        padding: 5px;
        margin-bottom: 2rem;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .custom-tab {
        flex: 1;
        padding: 15px 20px;
        text-align: center;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 600;
        color: #6b7280;
    }
    
    .custom-tab.active {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        transform: translateY(-2px);
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
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
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
    
    /* Calendário visual */
    .calendar-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 8px;
        margin: 20px 0;
        padding: 20px;
        background: #f8f9fa;
        border-radius: 15px;
    }
    
    .calendar-day {
        aspect-ratio: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 10px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        border: 2px solid transparent;
    }
    
    .calendar-day.available {
        background: white;
        border-color: #e9ecef;
        color: #495057;
    }
    
    .calendar-day.available:hover {
        background: #e3f2fd;
        border-color: #667eea;
        transform: scale(1.05);
    }
    
    .calendar-day.unavailable {
        background: #f1f3f5;
        color: #adb5bd;
        cursor: not-allowed;
    }
    
    .calendar-day.selected {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-color: #667eea;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Grid de horários */
    .time-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 12px;
        margin: 20px 0;
        padding: 20px;
        background: #f8f9fa;
        border-radius: 15px;
    }
    
    .time-slot {
        padding: 12px;
        text-align: center;
        border: 2px solid #e9ecef;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 600;
        background: white;
    }
    
    .time-slot:hover {
        border-color: #667eea;
        background: #e3f2fd;
        transform: translateY(-2px);
    }
    
    .time-slot.selected {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-color: #667eea;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    .time-slot.unavailable {
        background: #f1f3f5;
        color: #adb5bd;
        cursor: not-allowed;
        opacity: 0.6;
    }
    
    /* Resumo do agendamento */
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
    
    .summary-item strong {
        color: #495057;
    }
    
    /* Radio buttons customizados */
    .stRadio > div {
        display: flex;
        gap: 20px;
        background: #f8f9fa;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
    }
    
    /* Responsividade */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }
        
        .main-header h1 {
            font-size: 2rem;
        }
        
        .main-card {
            padding: 1.5rem;
        }
        
        .calendar-grid {
            gap: 4px;
            padding: 15px;
        }
        
        .time-grid {
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 8px;
            padding: 15px;
        }
        
        .custom-tabs {
            flex-direction: column;
        }
        
        .custom-tab {
            margin-bottom: 5px;
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
    
    /* Loading spinner */
    .loading-spinner {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 20px;
    }
    
    .spinner {
        width: 40px;
        height: 40px;
        border: 4px solid #f3f3f3;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

# Configurações do banco
DB = "agenda.db"

def conectar():
    return sqlite3.connect(DB)

def init_db():
    # DEBUG: Verificar banco
import os
st.write(f"🔍 DEBUG Cliente - Banco existe? {os.path.exists(DB)}")
st.write(f"📁 DEBUG Cliente - Caminho: {os.path.abspath(DB)}")

    conn = conectar()
    c = conn.cursor()
    
    # Criar tabela agendamentos (estrutura antiga primeiro)
    c.execute('''
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_cliente TEXT,
            telefone TEXT,
            data TEXT,
            horario TEXT
        )
    ''')
    
    # Verificar se a coluna email existe, se não, adicionar
    try:
        c.execute("SELECT email FROM agendamentos LIMIT 1")
    except sqlite3.OperationalError:
        # Coluna email não existe, vamos adicionar
        c.execute("ALTER TABLE agendamentos ADD COLUMN email TEXT DEFAULT ''")
        print("✅ Coluna 'email' adicionada à tabela agendamentos")
    
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
    
    # Verificar se o dia inteiro está bloqueado
    try:
        c.execute("SELECT * FROM bloqueios WHERE data=?", (data,))
        dia_bloqueado = c.fetchone()
        if dia_bloqueado:
            conn.close()
            return False
    except:
        pass
    
    # Verificar se o horário específico está bloqueado
    try:
        c.execute("SELECT * FROM bloqueios_horarios WHERE data=? AND horario=?", (data, horario))
        horario_bloqueado = c.fetchone()
        if horario_bloqueado:
            conn.close()
            return False
    except:
        pass
    
    # NOVO: Verificar bloqueios permanentes
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
                    conn.close()
                    return False
    except:
        pass
    
    conn.close()
    return True

def adicionar_agendamento(nome, telefone, email, data, horario):
    conn = conectar()
    c = conn.cursor()
    
    # GARANTIR que as colunas email e status existem antes de inserir
    try:
        c.execute("SELECT email FROM agendamentos LIMIT 1")
    except sqlite3.OperationalError:
        # Coluna email não existe, vamos adicionar
        c.execute("ALTER TABLE agendamentos ADD COLUMN email TEXT DEFAULT ''")
        conn.commit()
    
    try:
        c.execute("SELECT status FROM agendamentos LIMIT 1")
    except sqlite3.OperationalError:
        # Coluna status não existe, vamos adicionar
        c.execute("ALTER TABLE agendamentos ADD COLUMN status TEXT DEFAULT 'pendente'")
        conn.commit()
    
    # Verificar modo de confirmação
    confirmacao_automatica = obter_configuracao("confirmacao_automatica", False)
    status_inicial = "confirmado" if confirmacao_automatica else "pendente"
    
    # Agora inserir com segurança
    agendamento_id = None
    try:
        c.execute("INSERT INTO agendamentos (nome_cliente, telefone, email, data, horario, status) VALUES (?, ?, ?, ?, ?, ?)",
                  (nome, telefone, email, data, horario, status_inicial))
        agendamento_id = c.lastrowid
        conn.commit()
    except sqlite3.OperationalError as e:
        # Se ainda der erro, inserir sem email e status (fallback)
        if "email" in str(e) or "status" in str(e):
            c.execute("INSERT INTO agendamentos (nome_cliente, telefone, data, horario) VALUES (?, ?, ?, ?)",
                      (nome, telefone, data, horario))
            agendamento_id = c.lastrowid
            conn.commit()
        else:
            raise e
    finally:
        conn.close()
    
    # Se confirmação automática E tem email, enviar confirmação
    if status_inicial == "confirmado" and email and agendamento_id:
        try:
            enviar_email_confirmacao(agendamento_id, nome, email, data, horario)
        except Exception as e:
            print(f"Erro ao enviar email de confirmação automática: {e}")
    
    return status_inicial

def cancelar_agendamento(nome, telefone, data):
    conn = conectar()
    c = conn.cursor()
    
    # Buscar o agendamento com dados completos (incluindo email e horário)
    try:
        c.execute("SELECT email, horario FROM agendamentos WHERE nome_cliente=? AND telefone=? AND data=?", (nome, telefone, data))
        resultado = c.fetchone()
    except:
        # Fallback caso não tenha coluna email
        c.execute("SELECT horario FROM agendamentos WHERE nome_cliente=? AND telefone=? AND data=?", (nome, telefone, data))
        resultado_horario = c.fetchone()
        resultado = ('', resultado_horario[0]) if resultado_horario else None
    
    if resultado:
        # Deletar agendamento
        c.execute("DELETE FROM agendamentos WHERE nome_cliente=? AND telefone=? AND data=?", (nome, telefone, data))
        conn.commit()
        conn.close()
        
        # Enviar email de cancelamento se tiver email
        if len(resultado) >= 2:
            email, horario = resultado
            if email:  # Só envia se tem email
                try:
                    enviar_email_cancelamento(nome, email, data, horario, "cliente")
                except Exception as e:
                    print(f"Erro ao enviar email de cancelamento: {e}")
        
        return True
    else:
        conn.close()
        return False

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
    except:
        dias = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]  # Padrão
    conn.close()
    return dias

def obter_datas_bloqueadas():
    conn = conectar()
    c = conn.cursor()
    try:
        c.execute("SELECT data FROM bloqueios")
        datas = [linha[0] for linha in c.fetchall()]
    except:
        datas = []
    conn.close()
    return datas
    
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
        
        # Se não tem configuração de email, não enviar
        if not email_sistema or not senha_email:
            return False
        
        # Obter dados do profissional
        nome_profissional = obter_configuracao("nome_profissional", "Dr. João Silva")
        nome_clinica = obter_configuracao("nome_clinica", "Clínica São Lucas")
        telefone_contato = obter_configuracao("telefone_contato", "(11) 3333-4444")
        endereco = obter_configuracao("endereco", "Rua das Flores, 123")
        
        # Formatar data
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
# Inicializa banco
init_db()

# INTERFACE PRINCIPAL
# Obter configurações dinâmicas
nome_profissional = obter_configuracao("nome_profissional", "Dr. João Silva")
nome_clinica = obter_configuracao("nome_clinica", "Clínica São Lucas")
telefone_contato = obter_configuracao("telefone_contato", "(11) 3333-4444")
endereco = obter_configuracao("endereco", "Rua das Flores, 123")

st.markdown(f"""
<div class="main-header">
    <h1>⏳ Agendamento Online</h1>
    <p>Agende seu horário de forma rápida e prática</p>
</div>
""", unsafe_allow_html=True)

# Container principal
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    # Tabs personalizadas
    tab_agendar, tab_cancelar = st.tabs(["📅 Agendar Horário", "❌ Cancelar Agendamento"])
    
    with tab_agendar:
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        
        # Obter configurações dinâmicas
        hoje = datetime.today()
        dias_futuros_config = obter_configuracao("dias_futuros", 30)
        antecedencia_minima = obter_configuracao("antecedencia_minima", 2)  # em horas
        horario_inicio = obter_configuracao("horario_inicio", "09:00")
        horario_fim = obter_configuracao("horario_fim", "18:00")
        intervalo_consultas = obter_configuracao("intervalo_consultas", 60)  # em minutos
        
        dias_uteis = obter_dias_uteis()
        datas_bloqueadas = obter_datas_bloqueadas()
        datas_bloqueadas_dt = [datetime.strptime(d, "%Y-%m-%d").date() for d in datas_bloqueadas]
        
        # Calcular data limite considerando antecedência mínima
        agora = datetime.now()
        data_limite_antecedencia = agora + timedelta(hours=antecedencia_minima)
        
        # Gerar datas válidas baseadas nas configurações
        datas_validas = []
        for i in range(1, dias_futuros_config + 1):
            data = hoje + timedelta(days=i)
            dia_semana = data.strftime("%A")
            
            # Verificar se está dentro dos dias úteis e não bloqueada
            if dia_semana in dias_uteis and data.date() not in datas_bloqueadas_dt:
                # Verificar antecedência mínima
                if data.date() > data_limite_antecedencia.date() or \
                   (data.date() == data_limite_antecedencia.date() and 
                    datetime.combine(data.date(), datetime.strptime(horario_inicio, "%H:%M").time()) > data_limite_antecedencia):
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
            
            email = st.text_input("E-mail *", placeholder="seu@email.com", help="Usado para confirmações e lembretes")
            
            st.subheader("📅 Escolha a Data")
            data_selecionada = st.selectbox(
                "Datas disponíveis:",
                options=datas_validas,
                format_func=lambda d: d.strftime("%A, %d/%m/%Y").replace("Monday", "Segunda-feira")\
                    .replace("Tuesday", "Terça-feira").replace("Wednesday", "Quarta-feira")\
                    .replace("Thursday", "Quinta-feira").replace("Friday", "Sexta-feira")\
                    .replace("Saturday", "Sábado").replace("Sunday", "Domingo"),
                help="Selecione uma data disponível para seu agendamento"
            )
            
            if data_selecionada:
                st.subheader("⏰ Horários Disponíveis")
                
                data_str = data_selecionada.strftime("%Y-%m-%d")
                
                # Gerar horários baseados nas configurações
                try:
                    hora_inicio = datetime.strptime(horario_inicio, "%H:%M").time()
                    hora_fim = datetime.strptime(horario_fim, "%H:%M").time()
                    
                    # Converter para minutos para facilitar cálculo
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
                    # Fallback para horários padrão se houver erro
                    horarios_possiveis = [f"{h:02d}:00" for h in range(9, 18)]
                
                horarios_disponiveis = [h for h in horarios_possiveis if horario_disponivel(data_str, h)]
                
                if horarios_disponiveis:
                    # Seleção via selectbox
                    horario = st.selectbox(
                        "Escolha o horário desejado:",
                        horarios_disponiveis,
                        help="Selecione o horário que melhor se adequa à sua agenda"
                    )
                    
                    # Mostrar resumo se todos os campos estão preenchidos
                    if horario and nome and telefone and email:
                        # Validação simples de email
                        email_valido = "@" in email and "." in email.split("@")[-1]
                        
                        if not email_valido:
                            st.markdown("""
                            <div class="alert alert-warning">
                                ⚠️ <strong>Por favor, digite um e-mail válido.</strong>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Resumo do agendamento
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
                                <strong>{data_selecionada.strftime('%d/%m/%Y - %A').replace('Monday', 'Segunda-feira').replace('Tuesday', 'Terça-feira').replace('Wednesday', 'Quarta-feira').replace('Thursday', 'Quinta-feira').replace('Friday', 'Sexta-feira').replace('Saturday', 'Sábado')}</strong>
                            </div>
                            <div class="summary-item">
                                <span>⏰ Horário:</span>
                                <strong>{horario}</strong>
                            </div>
                            <div class="summary-item">
                                <span>🏥 Local:</span>
                                <strong>{nome_clinica}</strong>
                            </div>
                            <div class="summary-item">
                                <span>📍 Endereço:</span>
                                <strong>{endereco}</strong>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Botão de confirmação (sempre aparece se todos os campos estão preenchidos)
                        if email_valido:
                            if st.button("✅ Confirmar Agendamento", type="primary", use_container_width=True):
                                try:
                                    status_inicial = adicionar_agendamento(nome, telefone, email, data_str, horario)
                                    
                                    if status_inicial == "confirmado":
                                        st.markdown("""
                                        <div class="alert alert-success">
                                            ✅ <strong>Agendamento confirmado automaticamente!</strong><br>
                                            Seu horário está garantido.
                                        </div>
                                        """, unsafe_allow_html=True)
                                        st.info(f"💡 **Seu agendamento:** {data_selecionada.strftime('%d/%m/%Y')} às {horario} está confirmado!")
                                    else:
                                        st.markdown("""
                                        <div class="alert alert-success">
                                            ✅ <strong>Agendamento solicitado com sucesso!</strong><br>
                                            Aguarde a confirmação que será enviada em breve.
                                        </div>
                                        """, unsafe_allow_html=True)
                                        st.info(f"💡 **Próximos passos:** Você receberá uma confirmação por telefone, WhatsApp ou e-mail.")
                                    
                                    if st.button("🔄 Fazer Novo Agendamento"):
                                        st.rerun()
                                        
                                except Exception as e:
                                    st.markdown(f"""
                                    <div class="alert alert-error">
                                        ❌ <strong>Erro ao agendar!</strong><br>
                                        Erro: {str(e)}<br>
                                        Tente novamente ou entre em contato.
                                    </div>
                                    """, unsafe_allow_html=True)
                    
                    elif nome or telefone or email:
                        # Mostrar o que está faltando
                        campos_faltando = []
                        if not nome: campos_faltando.append("Nome")
                        if not telefone: campos_faltando.append("Telefone") 
                        if not email: campos_faltando.append("E-mail")
                        
                        if campos_faltando:
                            st.markdown(f"""
                            <div class="alert alert-info">
                                📝 <strong>Para continuar, preencha:</strong> {', '.join(campos_faltando)}
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="alert alert-warning">
                        ⚠️ <strong>Nenhum horário disponível para esta data.</strong><br>
                        Tente escolher outra data.
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab_cancelar:
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        st.subheader("❌ Cancelar Agendamento")
        
        st.markdown("""
        <div class="alert alert-info">
            ℹ️ <strong>Para cancelar um agendamento:</strong><br>
            Informe os mesmos dados utilizados no agendamento original.
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            nome_cancel = st.text_input("Nome cadastrado *", placeholder="Nome usado no agendamento")
        with col2:
            telefone_cancel = st.text_input("Telefone cadastrado *", placeholder="(11) 99999-9999")
        
        data_cancel = st.date_input(
            "Data do agendamento *",
            min_value=datetime.today().date(),
            help="Selecione a data do agendamento que deseja cancelar"
        )
        
        if st.button("🗑️ Cancelar Agendamento", type="secondary", use_container_width=True):
            if nome_cancel and telefone_cancel and data_cancel:
                data_str = data_cancel.strftime("%Y-%m-%d")
                sucesso = cancelar_agendamento(nome_cancel, telefone_cancel, data_str)
                
                if sucesso:
                    st.markdown("""
                    <div class="alert alert-success">
                        ✅ <strong>Agendamento cancelado com sucesso!</strong><br>
                        Você pode fazer um novo agendamento quando desejar.
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="alert alert-error">
                        ❌ <strong>Agendamento não encontrado!</strong><br>
                        Verifique se os dados estão corretos.
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="alert alert-warning">
                    ⚠️ <strong>Preencha todos os campos obrigatórios.</strong>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer dinâmico
st.markdown(f"""
<div style="text-align: center; padding: 2rem; color: rgba(102, 126, 234, 0.8);">
    <h3 style="color: #1f2937; margin-bottom: 1rem;">{nome_profissional}</h3>
    <p><strong>{nome_clinica}</strong></p>
    <p>📍 {endereco}</p>
    <p>📞 {telefone_contato}</p>
    <hr style="margin: 1.5rem 0; border: none; height: 1px; background: #e9ecef;">
    <p>💡 <strong>Dica:</strong> Mantenha seus dados atualizados para receber confirmações</p>
    <p style="font-size: 0.9rem; opacity: 0.7;">Sistema de Agendamento Online - Desenvolvido com ❤️</p>
</div>
""", unsafe_allow_html=True)
