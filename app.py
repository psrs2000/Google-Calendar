import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import calendar
from streamlit_calendar import calendar

# Verificar se é modo admin através do parâmetro da URL
# Compatibilidade com Streamlit Cloud e versões locais
try:
    # Streamlit versão mais nova (local)
    query_params = st.query_params
    admin_key = st.secrets.get("ADMIN_URL_KEY", "desenvolvimento")
    is_admin = query_params.get("admin") == admin_key
except:
    try:
        # Streamlit Cloud (versão mais antiga)
        query_params = st.experimental_get_query_params()
        admin_key = st.secrets.get("ADMIN_URL_KEY", "desenvolvimento")
        is_admin = query_params.get("admin") == admin_key
    except:
        # Fallback se nenhum funcionar
        is_admin = False

# Configuração da página
if is_admin:
    st.set_page_config(
        page_title="Painel Administrativo",
        page_icon="🔐",
        layout="wide",
        initial_sidebar_state="expanded"
    )
else:
    st.set_page_config(
        page_title="Agendamento Online",
        page_icon="💆‍♀️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

# CSS UNIFICADO
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
    
    .stat-card.success::before {
        background: linear-gradient(90deg, #10b981, #059669);
    }
    
    .stat-card.warning::before {
        background: linear-gradient(90deg, #f59e0b, #d97706);
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
    
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stDateInput > div > div > input {
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
        box-shadow: 0px 0px 0px 3px rgba(102,126,234,0.1) !important;
    }
    
    .stTextInput > label,
    .stSelectbox > label,
    .stDateInput > label {
        font-weight: 600 !important;
        color: #374151 !important;
        font-size: 16px !important;
        margin-bottom: 8px !important;
    }
    
    .stButton > button {
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        border: 2px solid transparent !important;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        box-shadow: 0px 4px 12px rgba(102,126,234,0.3) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0px 6px 16px rgba(102,126,234,0.4) !important;
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
    
    .appointment-summary {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        padding: 24px;
        border-radius: 15px;
        margin: 20px 0;
        border-left: 5px solid #667eea;
        box-shadow: 0px 5px 15px rgba(0,0,0,0.1);
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
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# Configurações
DB = "agenda.db"
SENHA_CORRETA = st.secrets.get("ADMIN_PASSWORD", "admin123")


# Funções do banco
def conectar():
    return sqlite3.connect(DB)

def init_config():
    conn = conectar()
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_cliente TEXT,
            telefone TEXT,
            data TEXT,
            horario TEXT
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
        CREATE TABLE IF NOT EXISTS configuracoes (
            chave TEXT PRIMARY KEY,
            valor TEXT
        )
    ''')

    try:
        c.execute("SELECT email FROM agendamentos LIMIT 1")
    except sqlite3.OperationalError:
        c.execute("ALTER TABLE agendamentos ADD COLUMN email TEXT DEFAULT ''")

    try:
        c.execute("SELECT status FROM agendamentos LIMIT 1")
    except sqlite3.OperationalError:
        c.execute("ALTER TABLE agendamentos ADD COLUMN status TEXT DEFAULT 'pendente'")

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
    if c.fetchone():
        conn.close()
        return False
    
    # Verificar se o dia inteiro está bloqueado
    try:
        c.execute("SELECT * FROM bloqueios WHERE data=?", (data,))
        if c.fetchone():
            conn.close()
            return False
    except:
        pass
    
    # Verificar se o horário específico está bloqueado
    try:
        c.execute("SELECT * FROM bloqueios_horarios WHERE data=? AND horario=?", (data, horario))
        if c.fetchone():
            conn.close()
            return False
    except:
        pass
    
    # NOVO: Verificar bloqueios permanentes
    if horario_bloqueado_permanente(data, horario):
        conn.close()
        return False
    
    conn.close()
    return True

def adicionar_agendamento(nome, telefone, email, data, horario):
    conn = conectar()
    c = conn.cursor()
    
    confirmacao_automatica = obter_configuracao("confirmacao_automatica", False)
    status_inicial = "confirmado" if confirmacao_automatica else "pendente"
    
    agendamento_id = None
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
    
    # Se confirmação automática E tem email E envio automático ativado, enviar confirmação
    envio_automatico = obter_configuracao("envio_automatico", False)
    enviar_confirmacao = obter_configuracao("enviar_confirmacao", True)
    
    if status_inicial == "confirmado" and email and agendamento_id and envio_automatico and enviar_confirmacao:
        try:
            enviar_email_confirmacao(agendamento_id, nome, email, data, horario)
        except Exception as e:
            print(f"Erro ao enviar email de confirmação automática: {e}")
    
    return status_inicial

def cancelar_agendamento(nome, telefone, data):
    conn = conectar()
    c = conn.cursor()
    
    # Buscar o agendamento com dados completos ANTES de deletar
    email_cliente = None
    horario_cliente = None
    
    try:
        # Tentar buscar com email
        c.execute("SELECT email, horario FROM agendamentos WHERE nome_cliente=? AND telefone=? AND data=?", (nome, telefone, data))
        resultado = c.fetchone()
        if resultado:
            email_cliente, horario_cliente = resultado
    except sqlite3.OperationalError:
        # Se não tem coluna email, buscar só horário
        try:
            c.execute("SELECT horario FROM agendamentos WHERE nome_cliente=? AND telefone=? AND data=?", (nome, telefone, data))
            resultado = c.fetchone()
            if resultado:
                horario_cliente = resultado[0]
                email_cliente = ""
        except:
            pass
    
    # Verificar se agendamento existe
    c.execute("SELECT COUNT(*) FROM agendamentos WHERE nome_cliente=? AND telefone=? AND data=?", (nome, telefone, data))
    existe = c.fetchone()[0] > 0
    
    if existe:
        # Deletar agendamento
        c.execute("DELETE FROM agendamentos WHERE nome_cliente=? AND telefone=? AND data=?", (nome, telefone, data))
        conn.commit()
        conn.close()
        
        # Enviar email de cancelamento se tiver email e configurações ativas
        envio_automatico = obter_configuracao("envio_automatico", False)
        enviar_cancelamento = obter_configuracao("enviar_cancelamento", True)
        
        if email_cliente and horario_cliente and envio_automatico and enviar_cancelamento:
            try:
                sucesso = enviar_email_cancelamento(nome, email_cliente, data, horario_cliente, "cliente")
                if sucesso:
                    print(f"✅ Email de cancelamento enviado para {email_cliente}")
                else:
                    print(f"❌ Falha ao enviar email de cancelamento para {email_cliente}")
            except Exception as e:
                print(f"❌ Erro ao enviar email de cancelamento: {e}")
        
        return True
    else:
        conn.close()
        return False

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

def salvar_dias_uteis(dias):
    conn = conectar()
    c = conn.cursor()
    c.execute("DELETE FROM dias_uteis")
    for dia in dias:
        c.execute("INSERT INTO dias_uteis (dia) VALUES (?)", (dia,))
    conn.commit()
    conn.close()

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
    envio_automatico = obter_configuracao("envio_automatico", False)
    enviar_confirmacao = obter_configuracao("enviar_confirmacao", True)
    
    if novo_status == 'confirmado' and agendamento_dados and len(agendamento_dados) >= 4 and envio_automatico and enviar_confirmacao:
        nome_cliente, email, data, horario = agendamento_dados
        if email:
            try:
                enviar_email_confirmacao(agendamento_id, nome_cliente, email, data, horario)
            except Exception as e:
                print(f"Erro ao enviar email de confirmação: {e}")
    
    # Se foi cancelado pelo admin e tem email, enviar cancelamento
    enviar_cancelamento = obter_configuracao("enviar_cancelamento", True)
    
    if novo_status == 'cancelado' and agendamento_dados and len(agendamento_dados) >= 4 and envio_automatico and enviar_cancelamento:
        nome_cliente, email, data, horario = agendamento_dados
        if email:
            try:
                enviar_email_cancelamento(nome_cliente, email, data, horario, "admin")
            except Exception as e:
                print(f"Erro ao enviar email de cancelamento: {e}")

def deletar_agendamento(agendamento_id):
    conn = conectar()
    c = conn.cursor()
    c.execute("DELETE FROM agendamentos WHERE id=?", (agendamento_id,))
    conn.commit()
    conn.close()

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
    conn = conectar()
    c = conn.cursor()
    try:
        # Criar tabela se não existir
        c.execute('''
            CREATE TABLE IF NOT EXISTS bloqueios_permanentes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                horario_inicio TEXT,
                horario_fim TEXT,
                dias_semana TEXT,
                descricao TEXT
            )
        ''')
        
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

def horario_bloqueado_permanente(data, horario):
    """Verifica se um horário está bloqueado permanentemente"""
    conn = conectar()
    c = conn.cursor()
    try:
        # Descobrir o dia da semana
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

def enviar_email_confirmacao(agendamento_id, cliente_nome, cliente_email, data, horario):
    """Envia email de confirmação automático"""
    
    if not obter_configuracao("envio_automatico", False):
        return False
    
    try:
        # Obter configurações de email
        email_sistema = obter_configuracao("email_sistema", "")
        senha_email = obter_configuracao("senha_email", "")
        servidor_smtp = obter_configuracao("servidor_smtp", "smtp.gmail.com")
        porta_smtp = obter_configuracao("porta_smtp", 587)
        
        if not email_sistema or not senha_email:
            return False
        
        # Obter dados do profissional
        nome_profissional = obter_configuracao("nome_profissional", "Dr. João Silva")
        especialidade = obter_configuracao("especialidade", "Clínico Geral")
        nome_clinica = obter_configuracao("nome_clinica", "Clínica São Lucas")
        telefone_contato = obter_configuracao("telefone_contato", "(11) 3333-4444")
        whatsapp = obter_configuracao("whatsapp", "(11) 99999-9999")
        
        # Endereço completo
        endereco_rua = obter_configuracao("endereco_rua", "Rua das Flores, 123")
        endereco_bairro = obter_configuracao("endereco_bairro", "Centro")
        endereco_cidade = obter_configuracao("endereco_cidade", "São Paulo - SP")
        endereco_completo = f"{endereco_rua}, {endereco_bairro}, {endereco_cidade}"
        
        instrucoes_chegada = obter_configuracao("instrucoes_chegada", "Favor chegar 10 minutos antes do horário agendado.")
        
        # Formatar data
        data_obj = datetime.strptime(data, "%Y-%m-%d")
        data_formatada = data_obj.strftime("%d/%m/%Y - %A")
        data_formatada = data_formatada.replace('Monday', 'Segunda-feira')\
            .replace('Tuesday', 'Terça-feira').replace('Wednesday', 'Quarta-feira')\
            .replace('Thursday', 'Quinta-feira').replace('Friday', 'Sexta-feira')\
            .replace('Saturday', 'Sábado').replace('Sunday', 'Domingo')
        
        # Usar template personalizado ou padrão
        template = obter_configuracao("template_confirmacao", 
            "Olá {nome}!\n\nSeu agendamento foi confirmado:\n📅 Data: {data}\n⏰ Horário: {horario}\n\nAguardamos você!")
        
        # Substituir variáveis no template
        corpo = template.format(
            nome=cliente_nome,
            data=data_formatada,
            horario=horario,
            local=nome_clinica,
            endereco=endereco_completo,
            profissional=nome_profissional,
            especialidade=especialidade
        )
        
        # Adicionar informações extras
        corpo += f"""

📍 Local: {nome_clinica}
🏠 Endereço: {endereco_completo}
📞 Telefone: {telefone_contato}
💬 WhatsApp: {whatsapp}

📝 Instruções importantes:
{instrucoes_chegada}

Atenciosamente,
{nome_profissional} - {especialidade}
{nome_clinica}
"""
        
        # Criar mensagem
        msg = MIMEMultipart()
        msg['From'] = email_sistema
        msg['To'] = cliente_email
        msg['Subject'] = f"✅ Agendamento Confirmado - {nome_profissional}"
        
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
    
    if not obter_configuracao("envio_automatico", False):
        return False
    
    try:
        # Obter configurações de email
        email_sistema = obter_configuracao("email_sistema", "")
        senha_email = obter_configuracao("senha_email", "")
        servidor_smtp = obter_configuracao("servidor_smtp", "smtp.gmail.com")
        porta_smtp = obter_configuracao("porta_smtp", 587)
        
        if not email_sistema or not senha_email:
            return False
        
        # Obter dados do profissional
        nome_profissional = obter_configuracao("nome_profissional", "Dr. João Silva")
        especialidade = obter_configuracao("especialidade", "Clínico Geral")
        nome_clinica = obter_configuracao("nome_clinica", "Clínica São Lucas")
        telefone_contato = obter_configuracao("telefone_contato", "(11) 3333-4444")
        whatsapp = obter_configuracao("whatsapp", "(11) 99999-9999")
        
        # Endereço completo
        endereco_rua = obter_configuracao("endereco_rua", "Rua das Flores, 123")
        endereco_bairro = obter_configuracao("endereco_bairro", "Centro")
        endereco_cidade = obter_configuracao("endereco_cidade", "São Paulo - SP")
        endereco_completo = f"{endereco_rua}, {endereco_bairro}, {endereco_cidade}"
        
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
            msg['Subject'] = f"✅ Cancelamento Confirmado - {nome_profissional}"
            corpo = f"""
Olá {cliente_nome}!

Seu cancelamento foi processado com sucesso!

📅 Data cancelada: {data_formatada}
⏰ Horário cancelado: {horario}
🏥 Local: {nome_clinica}

Você pode fazer um novo agendamento quando desejar através do nosso sistema online.

📞 Dúvidas? Entre em contato:
📱 Telefone: {telefone_contato}
💬 WhatsApp: {whatsapp}

Atenciosamente,
{nome_profissional} - {especialidade}
{nome_clinica}
"""
        else:
            msg['Subject'] = f"⚠️ Agendamento Cancelado - {nome_profissional}"
            corpo = f"""
Olá {cliente_nome}!

Infelizmente precisamos cancelar seu agendamento:

📅 Data: {data_formatada}
⏰ Horário: {horario}
🏥 Local: {nome_clinica}

Pedimos desculpas pelo inconveniente. 

Por favor, entre em contato conosco para reagendar:
📞 Telefone: {telefone_contato}
💬 WhatsApp: {whatsapp}
📍 Endereço: {endereco_completo}

Ou faça um novo agendamento através do nosso sistema online.

Atenciosamente,
{nome_profissional} - {especialidade}
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

def exportar_agendamentos_csv():
    """Exporta todos os agendamentos para CSV"""
    import csv
    import io
    
    try:
        # Buscar todos os agendamentos
        agendamentos = buscar_agendamentos()
        
        if not agendamentos:
            return None
        
        # Criar buffer em memória
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Cabeçalho
        writer.writerow(['ID', 'Data', 'Horário', 'Nome', 'Telefone', 'Email', 'Status'])
        
        # Dados
        for agendamento in agendamentos:
            if len(agendamento) == 7:
                writer.writerow(agendamento)
            elif len(agendamento) == 6:
                # Adicionar status padrão se não existir
                row = list(agendamento) + ['pendente']
                writer.writerow(row)
            else:
                # Formato antigo sem email
                row = list(agendamento) + ['Não informado', 'pendente']
                writer.writerow(row)
        
        # Retornar conteúdo do CSV
        csv_data = output.getvalue()
        output.close()
        
        return csv_data
        
    except Exception as e:
        st.error(f"Erro ao exportar: {e}")
        return None

# ========================================
# 2. ADICIONAR ESTAS FUNÇÕES ANTES DA LINHA "# Inicializar banco":
# ========================================

def criar_menu_horizontal():
    """Cria menu horizontal responsivo para admin"""
    
    # Inicializar opção padrão se não existir
    if 'menu_opcao' not in st.session_state:
        st.session_state.menu_opcao = "⚙️ Configurações Gerais"
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #3b82f6, #1d4ed8); padding: 0.5rem; border-radius: 4px; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(59,130,246,0.2);">
        <p style="color: white; text-align: center; margin: 0; font-size: 1rem; font-weight: 400; letter-spacing: 1px;">🔧 Menu Administrativo</p>
    """, unsafe_allow_html=True)
    
    # Menu responsivo
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("⚙️ **Configurações**", 
                    key="btn_config", 
                    use_container_width=True,
                    help="Configurações gerais do sistema"):
            st.session_state.menu_opcao = "⚙️ Configurações Gerais"
            st.rerun()
    
    with col2:
        if st.button("📅 **Agenda**", 
                    key="btn_agenda", 
                    use_container_width=True,
                    help="Configurar dias úteis"):
            st.session_state.menu_opcao = "📅 Configurar Agenda"
            st.rerun()
    
    with col3:
        if st.button("🗓️ **Bloqueios**", 
                    key="btn_bloqueios", 
                    use_container_width=True,
                    help="Gerenciar bloqueios de datas/horários"):
            st.session_state.menu_opcao = "🗓️ Gerenciar Bloqueios"
            st.rerun()
    
    with col4:
        if st.button("👥 **Agendamentos**", 
                    key="btn_agendamentos", 
                    use_container_width=True,
                    help="Lista de todos os agendamentos"):
            st.session_state.menu_opcao = "👥 Lista de Agendamentos"
            st.rerun()
    
    with col5:
        if st.button("🚪 **Sair**", 
                    key="btn_sair", 
                    use_container_width=True,
                    help="Fazer logout do painel admin"):
            st.session_state.authenticated = False
            st.session_state.menu_opcao = "⚙️ Configurações Gerais"  # Reset
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Mostrar opção atual selecionada
    st.markdown(f"""
    <div style="background: #f8f9fa; border-left: 4px solid #667eea; padding: 1rem; margin: 1rem 0; border-radius: 8px;">
        <span style="color: #667eea; font-weight: 600;">📍 Seção atual: {st.session_state.menu_opcao}</span>
    </div>
    """, unsafe_allow_html=True)
    
    return st.session_state.menu_opcao
    
# Inicializar banco
init_config()

# INTERFACE PRINCIPAL
if is_admin:
    # PAINEL ADMINISTRATIVO
    st.markdown("""
    <div class="admin-header">
        <h1>🔐 Painel Administrativo</h1>
        <div class="badge">Sistema de Agendamento</div>
    </div>
    """, unsafe_allow_html=True)
    
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("🔒 Acesso Restrito")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            senha = st.text_input("Digite a senha de administrador:", type="password")
            
            if st.button("🚪 Entrar", type="primary", use_container_width=True):
                if senha == SENHA_CORRETA:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
    st.header("📅 Agendamento")

    event = calendar(
        events=[],
        options={
            "locale": "pt-br",
            "firstDay": 1,
            "initialView": "dayGridMonth",
            "height": 500,
            "selectable": True,
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": ""
            }
        },
        key="calendar_cliente"
    )

    data = None
    if event and "start" in event:
        data = pd.to_datetime(event["start"]).date()
        st.success(f"📅 Você selecionou: {data.strftime('%d/%m/%Y')}")
    

else:
                    st.error("❌ Senha incorreta!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
