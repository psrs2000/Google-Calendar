import streamlit as st
import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import calendar
import time
import random
import hashlib
import threading
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    print("✅ Imports Google OK")
except ImportError as e:
    print(f"❌ Erro nos imports Google: {e}")


# Verificar se é modo admin (versão dinâmica corrigida)
is_admin = False
try:
    # Primeiro, tentar obter a chave dos secrets
    try:
        admin_key = st.secrets.get("ADMIN_URL_KEY", "desenvolvimento")
    except:
        admin_key = "desenvolvimento"  # Fallback para desenvolvimento local
    
    # Verificar query params (método novo)
    query_params = st.query_params
    is_admin = query_params.get("admin") == admin_key
    
except:
    try:
        # Método antigo (Streamlit Cloud mais antigo)
        try:
            admin_key = st.secrets.get("ADMIN_URL_KEY", "desenvolvimento")
        except:
            admin_key = "desenvolvimento"
        
        query_params = st.experimental_get_query_params()
        is_admin = query_params.get("admin", [None])[0] == admin_key
        
    except:
        # Fallback final
        is_admin = False

# Configuração da página (AGORA PODE SER PRIMEIRO!)
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
# Configurações
try:
    SENHA_CORRETA = st.secrets.get("ADMIN_PASSWORD", "admin123")
except:
    SENHA_CORRETA = "admin123"  # Para desenvolvimento local

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
    c.execute("SELECT * FROM agendamentos WHERE data=? AND horario=? AND status != 'cancelado'", (data, horario))
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
    
    # NOVO: Verificar se a data está em algum período bloqueado
    if data_em_periodo_bloqueado(data):
        conn.close()
        return False    
    
    # Verificar se o horário específico está bloqueado
    try:
        c.execute("SELECT * FROM bloqueios_horarios WHERE data=? AND horario=?", (data, horario))
        if c.fetchone():
            conn.close()
            return False
    except:
        pass
    
    # Verificar bloqueios permanentes
    if horario_bloqueado_permanente(data, horario):
        conn.close()
        return False
    
    # NOVO: Verificar bloqueios semanais
    if horario_bloqueado_semanal(data, horario):
        conn.close()
        return False
    
    conn.close()
    return True

def adicionar_agendamento(nome, telefone, email, data, horario):
    """Adiciona agendamento com integração Google Calendar"""
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
    
    # NOVO: Integração com Google Calendar
    google_calendar_ativo = obter_configuracao("google_calendar_ativo", False)
    
    if google_calendar_ativo and status_inicial == "confirmado" and agendamento_id:
        try:
            criar_evento_google_calendar(agendamento_id, nome, telefone, email, data, horario)
        except Exception as e:
            print(f"❌ Erro na integração Google Calendar: {e}")
    
    # Envio de emails (código original)
    envio_automatico = obter_configuracao("envio_automatico", False)
    enviar_confirmacao = obter_configuracao("enviar_confirmacao", True)
    
    if status_inicial == "confirmado" and email and agendamento_id and envio_automatico and enviar_confirmacao:
        try:
            enviar_email_confirmacao(agendamento_id, nome, email, data, horario)
        except Exception as e:
            print(f"❌ Erro ao enviar email de confirmação automática: {e}")
    
    return status_inicial

def cancelar_agendamento(nome, telefone, data):
    """Cancela agendamento mudando status para 'cancelado' em vez de deletar"""
    conn = conectar()
    c = conn.cursor()
    
    # MUDANÇA PRINCIPAL: Buscar TODOS os agendamentos do dia, não só o primeiro
    agendamentos_do_dia = []
    
    try:
        # Tentar buscar com email e ID - TODOS OS AGENDAMENTOS DO DIA
        c.execute("SELECT id, email, horario FROM agendamentos WHERE nome_cliente=? AND telefone=? AND data=? AND status IN ('pendente', 'confirmado')", (nome, telefone, data))
        agendamentos_do_dia = c.fetchall()
    except sqlite3.OperationalError:
        # Se não tem coluna email, buscar só ID e horário - TODOS OS AGENDAMENTOS DO DIA
        try:
            c.execute("SELECT id, horario FROM agendamentos WHERE nome_cliente=? AND telefone=? AND data=? AND status IN ('pendente', 'confirmado')", (nome, telefone, data))
            agendamentos_sem_email = c.fetchall()
            # Adicionar email vazio para manter formato
            agendamentos_do_dia = [(ag[0], '', ag[1]) for ag in agendamentos_sem_email]
        except:
            # Fallback para versões muito antigas sem coluna status
            c.execute("SELECT id, horario FROM agendamentos WHERE nome_cliente=? AND telefone=? AND data=?", (nome, telefone, data))
            agendamentos_sem_email = c.fetchall()
            agendamentos_do_dia = [(ag[0], '', ag[1]) for ag in agendamentos_sem_email]
    
    # Verificar se existem agendamentos CANCELÁVEIS
    try:
        c.execute("SELECT COUNT(*) FROM agendamentos WHERE nome_cliente=? AND telefone=? AND data=? AND status IN ('pendente', 'confirmado')", (nome, telefone, data))
        existe = c.fetchone()[0] > 0
    except sqlite3.OperationalError:
        # Fallback para versões antigas sem coluna status
        c.execute("SELECT COUNT(*) FROM agendamentos WHERE nome_cliente=? AND telefone=? AND data=?", (nome, telefone, data))
        existe = c.fetchone()[0] > 0
    
    if existe and agendamentos_do_dia:
        # Cancelar TODOS os agendamentos do dia no sistema
        try:
            c.execute("UPDATE agendamentos SET status = 'cancelado' WHERE nome_cliente=? AND telefone=? AND data=?", 
                     (nome, telefone, data))
            conn.commit()
            conn.close()

            print(f"✅ {len(agendamentos_do_dia)} agendamento(s) cancelado(s): {nome} - {data}")

            # NOVO: Integração com Google Calendar para MÚLTIPLOS eventos
            google_calendar_ativo = obter_configuracao("google_calendar_ativo", False)
            
            if google_calendar_ativo:
                eventos_deletados = 0
                for agendamento in agendamentos_do_dia:
                    agendamento_id = agendamento[0]
                    horario = agendamento[2]
                    
                    try:
                        sucesso = deletar_evento_google_calendar(agendamento_id)
                        if sucesso:
                            eventos_deletados += 1
                            print(f"✅ Evento Google Calendar deletado: {horario}")
                        else:
                            print(f"⚠️ Falha ao deletar evento Google Calendar: {horario}")
                    except Exception as e:
                        print(f"❌ Erro ao deletar evento Google Calendar {horario}: {e}")
                
                print(f"📅 Google Calendar: {eventos_deletados}/{len(agendamentos_do_dia)} eventos deletados")
            
            # Enviar email de cancelamento (usando dados do primeiro agendamento)
            envio_automatico = obter_configuracao("envio_automatico", False)
            enviar_cancelamento = obter_configuracao("enviar_cancelamento", True)
            
            if envio_automatico and enviar_cancelamento and agendamentos_do_dia:
                primeiro_agendamento = agendamentos_do_dia[0]
                email_cliente = primeiro_agendamento[1] if len(primeiro_agendamento) > 1 else ""
                
                if email_cliente:
                    # Se múltiplos agendamentos, mencionar no email
                    if len(agendamentos_do_dia) > 1:
                        horarios_cancelados = ", ".join([ag[2] for ag in agendamentos_do_dia])
                        horario_para_email = f"Horários: {horarios_cancelados}"
                    else:
                        horario_para_email = agendamentos_do_dia[0][2]
                    
                    try:
                        sucesso = enviar_email_cancelamento(nome, email_cliente, data, horario_para_email, "cliente")
                        if sucesso:
                            print(f"✅ Email de cancelamento enviado para {email_cliente}")
                        else:
                            print(f"❌ Falha ao enviar email de cancelamento para {email_cliente}")
                    except Exception as e:
                        print(f"❌ Erro ao enviar email de cancelamento: {e}")
            
            return True
            
        except sqlite3.OperationalError:
            # Se não tem coluna status, criar ela e tentar novamente
            try:
                c.execute("ALTER TABLE agendamentos ADD COLUMN status TEXT DEFAULT 'pendente'")
                conn.commit()
                
                # Tentar novamente
                c.execute("UPDATE agendamentos SET status = 'cancelado' WHERE nome_cliente=? AND telefone=? AND data=?", 
                         (nome, telefone, data))
                conn.commit()
                conn.close()
                
                print(f"✅ {len(agendamentos_do_dia)} agendamento(s) cancelado(s): {nome} - {data}")
                
                # Google Calendar e email (mesmo código de cima)
                google_calendar_ativo = obter_configuracao("google_calendar_ativo", False)
                
                if google_calendar_ativo:
                    eventos_deletados = 0
                    for agendamento in agendamentos_do_dia:
                        agendamento_id = agendamento[0]
                        horario = agendamento[2]
                        
                        try:
                            sucesso = deletar_evento_google_calendar(agendamento_id)
                            if sucesso:
                                eventos_deletados += 1
                                print(f"✅ Evento Google Calendar deletado: {horario}")
                        except Exception as e:
                            print(f"❌ Erro ao deletar evento Google Calendar {horario}: {e}")
                    
                    print(f"📅 Google Calendar: {eventos_deletados}/{len(agendamentos_do_dia)} eventos deletados")
                
                # Email de cancelamento
                envio_automatico = obter_configuracao("envio_automatico", False)
                enviar_cancelamento = obter_configuracao("enviar_cancelamento", True)
                
                if envio_automatico and enviar_cancelamento and agendamentos_do_dia:
                    primeiro_agendamento = agendamentos_do_dia[0]
                    email_cliente = primeiro_agendamento[1] if len(primeiro_agendamento) > 1 else ""
                    
                    if email_cliente:
                        if len(agendamentos_do_dia) > 1:
                            horarios_cancelados = ", ".join([ag[2] for ag in agendamentos_do_dia])
                            horario_para_email = f"Horários: {horarios_cancelados}"
                        else:
                            horario_para_email = agendamentos_do_dia[0][2]
                        
                        try:
                            sucesso = enviar_email_cancelamento(nome, email_cliente, data, horario_para_email, "cliente")
                            if sucesso:
                                print(f"✅ Email de cancelamento enviado para {email_cliente}")
                        except Exception as e:
                            print(f"❌ Erro ao enviar email de cancelamento: {e}")
                
                return True
                
            except Exception as e:
                print(f"❌ Erro ao atualizar status: {e}")
                conn.close()
                return False
        
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
    """Atualiza status do agendamento com integração Google Calendar"""
    conn = conectar()
    c = conn.cursor()
    
    # Buscar dados do agendamento antes de atualizar
    c.execute("SELECT nome_cliente, email, data, horario, telefone FROM agendamentos WHERE id = ?", (agendamento_id,))
    agendamento_dados = c.fetchone()
    
    # Atualizar status
    c.execute("UPDATE agendamentos SET status = ? WHERE id = ?", (novo_status, agendamento_id))
    conn.commit()
    conn.close()
    
    # NOVO: Integração com Google Calendar
    google_calendar_ativo = obter_configuracao("google_calendar_ativo", False)
    
    if google_calendar_ativo and agendamento_dados:
        nome_cliente = agendamento_dados[0]
        email = agendamento_dados[1] if len(agendamento_dados) > 1 else ""
        data = agendamento_dados[2] if len(agendamento_dados) > 2 else ""
        horario = agendamento_dados[3] if len(agendamento_dados) > 3 else ""
        telefone = agendamento_dados[4] if len(agendamento_dados) > 4 else ""
        
        try:
            if novo_status == 'confirmado':
                # Criar evento se não existir
                event_id = obter_event_id_google(agendamento_id)
                if not event_id:
                    criar_evento_google_calendar(agendamento_id, nome_cliente, telefone, email, data, horario)
                
            elif novo_status == 'cancelado':
                # Deletar evento
                deletar_evento_google_calendar(agendamento_id)
                
            elif novo_status == 'atendido':
                # Atualizar evento
                atualizar_evento_google_calendar(agendamento_id, nome_cliente, novo_status)
                
        except Exception as e:
            print(f"❌ Erro na integração Google Calendar: {e}")
    
    # Envio de emails (código original)
    envio_automatico = obter_configuracao("envio_automatico", False)
    enviar_confirmacao = obter_configuracao("enviar_confirmacao", True)
    
    if novo_status == 'confirmado' and agendamento_dados and len(agendamento_dados) >= 4 and envio_automatico and enviar_confirmacao:
        nome_cliente, email, data, horario = agendamento_dados[:4]
        if email:
            try:
                enviar_email_confirmacao(agendamento_id, nome_cliente, email, data, horario)
            except Exception as e:
                print(f"❌ Erro ao enviar email de confirmação: {e}")
    
    # Email de cancelamento
    enviar_cancelamento = obter_configuracao("enviar_cancelamento", True)
    
    if novo_status == 'cancelado' and agendamento_dados and len(agendamento_dados) >= 4 and envio_automatico and enviar_cancelamento:
        nome_cliente, email, data, horario = agendamento_dados[:4]
        if email:
            try:
                enviar_email_cancelamento(nome_cliente, email, data, horario, "admin")
            except Exception as e:
                print(f"❌ Erro ao enviar email de cancelamento: {e}")

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

def adicionar_bloqueio_semanal(dia_semana, horarios_bloqueados, descricao=""):
    """Adiciona bloqueio recorrente para um dia da semana específico"""
    conn = conectar()
    c = conn.cursor()
    try:
        # Criar tabela se não existir
        c.execute('''
            CREATE TABLE IF NOT EXISTS bloqueios_semanais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dia_semana TEXT,
                horarios TEXT,
                descricao TEXT,
                UNIQUE(dia_semana, horarios)
            )
        ''')
        
        horarios_str = ",".join(horarios_bloqueados)
        c.execute("INSERT INTO bloqueios_semanais (dia_semana, horarios, descricao) VALUES (?, ?, ?)", 
                  (dia_semana, horarios_str, descricao))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print(f"Erro ao adicionar bloqueio semanal: {e}")
        return False
    finally:
        conn.close()

def obter_bloqueios_semanais():
    """Obtém todos os bloqueios semanais"""
    conn = conectar()
    c = conn.cursor()
    try:
        c.execute("SELECT id, dia_semana, horarios, descricao FROM bloqueios_semanais ORDER BY dia_semana")
        bloqueios = c.fetchall()
        return bloqueios
    except:
        return []
    finally:
        conn.close()

def remover_bloqueio_semanal(bloqueio_id):
    """Remove um bloqueio semanal"""
    conn = conectar()
    c = conn.cursor()
    try:
        c.execute("DELETE FROM bloqueios_semanais WHERE id=?", (bloqueio_id,))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def horario_bloqueado_semanal(data, horario):
    """Verifica se um horário está bloqueado por regra semanal"""
    conn = conectar()
    c = conn.cursor()
    try:
        # Descobrir o dia da semana
        data_obj = datetime.strptime(data, "%Y-%m-%d")
        dia_semana = data_obj.strftime("%A")  # Monday, Tuesday, etc.
        
        # Buscar bloqueios semanais para este dia
        c.execute("SELECT horarios FROM bloqueios_semanais WHERE dia_semana=?", (dia_semana,))
        bloqueios = c.fetchall()
        
        for (horarios_str,) in bloqueios:
            horarios_bloqueados = horarios_str.split(",")
            if horario in horarios_bloqueados:
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

def importar_agendamentos_csv(csv_content):
    """Importa agendamentos de um arquivo CSV"""
    import csv
    import io
    
    try:
        # Ler o conteúdo CSV
        csv_file = io.StringIO(csv_content)
        reader = csv.DictReader(csv_file)
        
        conn = conectar()
        c = conn.cursor()
        
        importados = 0
        duplicados = 0
        erros = 0
        
        for row in reader:
            try:
                # Extrair dados do CSV
                agendamento_id = row.get('ID', '')
                data = row.get('Data', '')
                horario = row.get('Horário', '') or row.get('Horario', '')
                nome = row.get('Nome', '')
                telefone = row.get('Telefone', '')
                email = row.get('Email', '') or row.get('E-mail', '') or ''
                status = row.get('Status', 'pendente')
                
                # Validar dados obrigatórios
                if not all([data, horario, nome, telefone]):
                    erros += 1
                    continue
                
                # Verificar se já existe (evitar duplicatas)
                c.execute("SELECT COUNT(*) FROM agendamentos WHERE data=? AND horario=? AND nome_cliente=? AND telefone=?", 
                         (data, horario, nome, telefone))
                
                if c.fetchone()[0] > 0:
                    duplicados += 1
                    continue
                
                # Inserir no banco
                try:
                    c.execute("""INSERT INTO agendamentos 
                               (nome_cliente, telefone, email, data, horario, status) 
                               VALUES (?, ?, ?, ?, ?, ?)""",
                             (nome, telefone, email, data, horario, status))
                    importados += 1
                except sqlite3.OperationalError:
                    # Versão antiga sem email e status
                    c.execute("""INSERT INTO agendamentos 
                               (nome_cliente, telefone, data, horario) 
                               VALUES (?, ?, ?, ?)""",
                             (nome, telefone, data, horario))
                    importados += 1
                    
            except Exception as e:
                print(f"Erro ao processar linha: {e}")
                erros += 1
                continue
        
        conn.commit()
        conn.close()
        
        return {
            'importados': importados,
            'duplicados': duplicados, 
            'erros': erros,
            'sucesso': True
        }
        
    except Exception as e:
        return {
            'importados': 0,
            'duplicados': 0,
            'erros': 0,
            'sucesso': False,
            'erro': str(e)
        }

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
    
    # Menu responsivo ATUALIZADO com 6 colunas
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
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
        if st.button("💾 **Backup**", 
                    key="btn_backup", 
                    use_container_width=True,
                    help="Backup e restauração de dados"):
            st.session_state.menu_opcao = "💾 Backup & Restauração"
            st.rerun()
    
    with col6:
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

# PASSO 1: Adicionar esta função no app.py (depois das outras funções do banco)

import requests
import json
import base64

def get_github_config():
    """Obtém configurações do GitHub"""
    
    # Configuração padrão (fallback)
    config_local = {
        "token": "",  # ← Vazio agora!
        "repo": "psrs2000/Agenda_Livre",
        "branch": "main",
        "config_file": "configuracoes.json"
    }    
    # Tentar usar secrets primeiro (para Streamlit Cloud)
    try:
        return {
            "token": st.secrets["GITHUB_TOKEN"],
            "repo": st.secrets["GITHUB_REPO"],
            "branch": st.secrets.get("GITHUB_BRANCH", "main"),
            "config_file": st.secrets.get("CONFIG_FILE", "configuracoes.json")
        }
    except:
        # Fallback para configuração local
        return config_local

def backup_configuracoes_github():
    """Faz backup de todas as configurações para GitHub"""
    try:
        github_config = get_github_config()
        if not github_config or not github_config.get("token"):
            print("❌ Configuração GitHub não encontrada")
            return False
        
        # Buscar todas as configurações do banco local
        conn = conectar()
        c = conn.cursor()
        
        try:
            c.execute("SELECT chave, valor FROM configuracoes")
            configs = dict(c.fetchall())
        except:
            configs = {}
        finally:
            conn.close()
        
        # Adicionar informações do backup
        configs['_backup_timestamp'] = datetime.now().isoformat()
        configs['_backup_version'] = '1.0'
        configs['_sistema'] = 'Agenda Online'
        
        # Converter para JSON bonito
        config_json = json.dumps(configs, indent=2, ensure_ascii=False)
        
        # Enviar para GitHub
        return upload_to_github(config_json, github_config)
        
    except Exception as e:
        print(f"❌ Erro no backup GitHub: {e}")
        return False

def upload_to_github(content, github_config):
    """Upload de arquivo para GitHub"""
    try:
        headers = {
            "Authorization": f"token {github_config['token']}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Sistema-Agendamento"
        }
        
        # URL da API GitHub
        api_url = f"https://api.github.com/repos/{github_config['repo']}/contents/{github_config['config_file']}"
        
        print(f"🔗 Conectando: {api_url}")
        
        # Verificar se arquivo já existe (para obter SHA)
        response = requests.get(api_url, headers=headers)
        sha = None
        
        if response.status_code == 200:
            sha = response.json()["sha"]
            print("📄 Arquivo existente encontrado, atualizando...")
        elif response.status_code == 404:
            print("📄 Criando arquivo novo...")
        else:
            print(f"⚠️ Resposta inesperada: {response.status_code}")
        
        # Preparar dados para upload
        content_encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        data = {
            "message": f"Backup configurações - {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
            "content": content_encoded,
            "branch": github_config['branch']
        }
        
        if sha:
            data["sha"] = sha
        
        # Fazer upload
        print("📤 Enviando backup...")
        response = requests.put(api_url, headers=headers, json=data)
        
        if response.status_code in [200, 201]:
            print("✅ Backup enviado para GitHub com sucesso!")
            return True
        else:
            print(f"❌ Erro no upload GitHub: {response.status_code}")
            print(f"📋 Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no upload GitHub: {e}")
        return False


def restaurar_configuracoes_github():
    """Restaura configurações do GitHub"""
    try:
        github_config = get_github_config()
        if not github_config or not github_config.get("token"):
            print("⚠️ Configuração GitHub não encontrada para restauração")
            return False
        
        # Baixar arquivo do GitHub
        config_json = download_from_github(github_config)
        if not config_json:
            print("📄 Nenhum backup encontrado no GitHub")
            return False
        
        # Parse do JSON
        configs = json.loads(config_json)
        
        # Remover metadados do backup
        configs.pop('_backup_timestamp', None)
        configs.pop('_backup_version', None)
        configs.pop('_sistema', None)
        
        # Salvar no banco local
        conn = conectar()
        c = conn.cursor()
        
        try:
            for chave, valor in configs.items():
                c.execute("INSERT OR REPLACE INTO configuracoes (chave, valor) VALUES (?, ?)", 
                         (chave, valor))
            conn.commit()
            print(f"✅ {len(configs)} configurações restauradas do GitHub")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar configurações restauradas: {e}")
            return False
        finally:
            conn.close()
            
    except Exception as e:
        print(f"❌ Erro na restauração GitHub: {e}")
        return False

def download_from_github(github_config):
    """Download de arquivo do GitHub"""
    try:
        headers = {
            "Authorization": f"token {github_config['token']}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Sistema-Agendamento"
        }
        
        # URL da API GitHub
        api_url = f"https://api.github.com/repos/{github_config['repo']}/contents/{github_config['config_file']}"
        
        print(f"📥 Baixando backup: {api_url}")
        
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200:
            # Decodificar conteúdo base64
            content_encoded = response.json()["content"]
            content = base64.b64decode(content_encoded).decode('utf-8')
            print("✅ Backup baixado com sucesso")
            return content
        elif response.status_code == 404:
            print("📄 Arquivo de backup não encontrado no GitHub")
            return None
        else:
            print(f"❌ Erro no download GitHub: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro no download GitHub: {e}")
        return None

def get_google_calendar_service():
    """Configura Google Calendar usando Streamlit Secrets"""
    try:
        print("🔍 Iniciando get_google_calendar_service...")
        
        # Obter credenciais dos secrets
        creds_info = {
            "client_id": st.secrets["GOOGLE_CLIENT_ID"],
            "client_secret": st.secrets["GOOGLE_CLIENT_SECRET"], 
            "refresh_token": st.secrets["GOOGLE_REFRESH_TOKEN"],
            "token_uri": "https://oauth2.googleapis.com/token"
        }
        
        print("🔍 Secrets lidos com sucesso")
        
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        
        print("🔍 Imports OK")
        
        credentials = Credentials.from_authorized_user_info(creds_info)
        print("🔍 Credentials criadas")
        
        # Renovar token se necessário
        if credentials.expired:
            print("🔍 Token expirado, renovando...")
            credentials.refresh(Request())
            print("🔍 Token renovado")
        
        print("🔍 Criando service...")
        service = build('calendar', 'v3', credentials=credentials)
        print("✅ Service criado com sucesso")
        return service
        
    except Exception as e:
        print(f"❌ ERRO NA FUNÇÃO: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def criar_evento_google_calendar(agendamento_id, nome_cliente, telefone, email, data, horario, max_tentativas=3):
    print(f"🔍 DEBUG: Tentando criar evento - ID: {agendamento_id}, Cliente: {nome_cliente}")  # ← ADICIONAR ESTA LINHA
    """Cria evento no Google Calendar com múltiplas tentativas"""
    
    for tentativa in range(1, max_tentativas + 1):
        try:
            print(f"🔄 Tentativa {tentativa}/{max_tentativas} - Criando evento Google Calendar")
            
            service = get_google_calendar_service()
            if not service:
                print(f"❌ Tentativa {tentativa}: Falha ao conectar com Google Calendar")
                if tentativa < max_tentativas:
                    time.sleep(tentativa * 2)
                    continue
                return False
            
            # Configurações do calendário
            calendar_id = st.secrets.get("GOOGLE_CALENDAR_ID", "primary")
            
            # Montar data/hora do evento
            data_inicio = datetime.strptime(f"{data} {horario}", "%Y-%m-%d %H:%M")
            
            # Duração baseada na configuração
            intervalo_consultas = obter_configuracao("intervalo_consultas", 60)
            data_fim = data_inicio + timedelta(minutes=intervalo_consultas)
            
            # Dados do profissional
            nome_profissional = obter_configuracao("nome_profissional", "Dr. João Silva")
            especialidade = obter_configuracao("especialidade", "Clínico Geral")
            nome_clinica = obter_configuracao("nome_clinica", "Clínica São Lucas")
            
            evento = {
                'summary': f'📅 {nome_cliente} - {especialidade}',
                'description': f'''
🏥 {nome_clinica}
👨‍⚕️ {nome_profissional} - {especialidade}

👤 Cliente: {nome_cliente}
📱 Telefone: {telefone}
📧 Email: {email}

🆔 ID: {agendamento_id}
📝 Sistema de Agendamento Online
                '''.strip(),
                'start': {
                    'dateTime': data_inicio.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
                'end': {
                    'dateTime': data_fim.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
                'attendees': [
                    {'email': email}
                ] if email else [],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 dia antes
                        {'method': 'popup', 'minutes': 60},       # 1 hora antes
                    ],
                },
                'colorId': '2',  # Verde para consultas
            }
            
            evento_criado = service.events().insert(
                calendarId=calendar_id, 
                body=evento
            ).execute()
            
            # Se chegou aqui, deu certo!
            print(f"✅ Evento criado com sucesso na tentativa {tentativa}")
            
            # Salvar ID do evento no banco
            salvar_event_id_google(agendamento_id, evento_criado['id'])
            
            return evento_criado['id']
            
        except Exception as e:
            print(f"❌ Tentativa {tentativa} falhou: {str(e)}")
            
            # Se não é a última tentativa, aguardar antes de tentar novamente
            if tentativa < max_tentativas:
                delay = (tentativa ** 2) + random.uniform(0.5, 1.5)
                print(f"⏳ Aguardando {delay:.1f}s antes da próxima tentativa...")
                time.sleep(delay)
            else:
                print(f"💥 Todas as {max_tentativas} tentativas falharam para criar evento!")
                return False
    
    return False

def deletar_evento_google_calendar(agendamento_id, max_tentativas=3):
    """Deleta evento do Google Calendar com múltiplas tentativas"""
    
    for tentativa in range(1, max_tentativas + 1):
        try:
            print(f"🔄 Tentativa {tentativa}/{max_tentativas} - Deletando evento Google Calendar")
            
            service = get_google_calendar_service()
            if not service:
                print(f"❌ Tentativa {tentativa}: Falha ao conectar com Google Calendar")
                if tentativa < max_tentativas:
                    time.sleep(tentativa * 2)  # 2s, 4s, 6s...
                    continue
                return False
            
            # Buscar ID do evento
            event_id = obter_event_id_google(agendamento_id)
            if not event_id:
                print(f"⚠️ Event ID não encontrado para agendamento {agendamento_id}")
                return False
            
            calendar_id = st.secrets.get("GOOGLE_CALENDAR_ID", "primary")
            
            # Tentar deletar
            service.events().delete(
                calendarId=calendar_id, 
                eventId=event_id
            ).execute()
            
            # Se chegou aqui, deu certo!
            print(f"✅ Evento deletado com sucesso na tentativa {tentativa}")
            
            # Remover ID do banco apenas se deletou com sucesso
            remover_event_id_google(agendamento_id)
            
            return True
            
        except Exception as e:
            print(f"❌ Tentativa {tentativa} falhou: {str(e)}")
            
            # Se não é a última tentativa, aguardar antes de tentar novamente
            if tentativa < max_tentativas:
                # Backoff exponencial com jitter
                delay = (tentativa ** 2) + random.uniform(0.5, 1.5)  # 1-2.5s, 4-5.5s, 9-10.5s
                print(f"⏳ Aguardando {delay:.1f}s antes da próxima tentativa...")
                time.sleep(delay)
            else:
                print(f"💥 Todas as {max_tentativas} tentativas falharam!")
                
                # IMPORTANTE: Mesmo que falhe, marcar como "tentou deletar" 
                # para não ficar tentando infinitamente
                remover_event_id_google(agendamento_id)
                
                return False
    
    return False

def atualizar_evento_google_calendar(agendamento_id, nome_cliente, status, max_tentativas=3):
    """Atualiza evento no Google Calendar com múltiplas tentativas"""
    
    for tentativa in range(1, max_tentativas + 1):
        try:
            print(f"🔄 Tentativa {tentativa}/{max_tentativas} - Atualizando evento Google Calendar")
            
            service = get_google_calendar_service()
            if not service:
                print(f"❌ Tentativa {tentativa}: Falha ao conectar com Google Calendar")
                if tentativa < max_tentativas:
                    time.sleep(tentativa * 2)
                    continue
                return False
            
            event_id = obter_event_id_google(agendamento_id)
            if not event_id:
                print(f"⚠️ Event ID não encontrado para agendamento {agendamento_id}")
                return False
            
            calendar_id = st.secrets.get("GOOGLE_CALENDAR_ID", "primary")
            
            # Buscar evento atual
            evento = service.events().get(
                calendarId=calendar_id, 
                eventId=event_id
            ).execute()
            
            # Atualizar título baseado no status
            if status == 'atendido':
                evento['summary'] = f'✅ ATENDIDO - {nome_cliente}'
                evento['colorId'] = '10'  # Verde escuro para atendidos
            elif status == 'cancelado':
                evento['summary'] = f'❌ CANCELADO - {nome_cliente}'
                evento['colorId'] = '4'  # Vermelho para cancelados
            
            service.events().update(
                calendarId=calendar_id, 
                eventId=event_id, 
                body=evento
            ).execute()
            
            print(f"✅ Evento atualizado com sucesso na tentativa {tentativa}")
            return True
            
        except Exception as e:
            print(f"❌ Tentativa {tentativa} falhou: {str(e)}")
            
            if tentativa < max_tentativas:
                delay = (tentativa ** 2) + random.uniform(0.5, 1.5)
                print(f"⏳ Aguardando {delay:.1f}s antes da próxima tentativa...")
                time.sleep(delay)
            else:
                print(f"💥 Todas as {max_tentativas} tentativas falharam para atualizar evento!")
                return False
    
    return False

def salvar_event_id_google(agendamento_id, event_id):
    """Salva ID do evento Google Calendar no banco"""
    conn = conectar()
    c = conn.cursor()
    try:
        # Criar coluna se não existir
        try:
            c.execute("ALTER TABLE agendamentos ADD COLUMN google_event_id TEXT")
        except sqlite3.OperationalError:
            pass  # Coluna já existe
        
        c.execute("UPDATE agendamentos SET google_event_id = ? WHERE id = ?", 
                  (event_id, agendamento_id))
        conn.commit()
        print(f"💾 Event ID salvo: {event_id}")
    except Exception as e:
        print(f"❌ Erro ao salvar event ID: {e}")
    finally:
        conn.close()

def obter_event_id_google(agendamento_id):
    """Obtém ID do evento Google Calendar"""
    conn = conectar()
    c = conn.cursor()
    try:
        c.execute("SELECT google_event_id FROM agendamentos WHERE id = ?", (agendamento_id,))
        resultado = c.fetchone()
        return resultado[0] if resultado and resultado[0] else None
    except sqlite3.OperationalError:
        return None  # Coluna não existe ainda
    except Exception as e:
        print(f"❌ Erro ao obter event ID: {e}")
        return None
    finally:
        conn.close()

def remover_event_id_google(agendamento_id):
    """Remove ID do evento Google Calendar"""
    conn = conectar()
    c = conn.cursor()
    try:
        c.execute("UPDATE agendamentos SET google_event_id = NULL WHERE id = ?", 
                  (agendamento_id,))
        conn.commit()
        print(f"🗑️ Event ID removido para agendamento {agendamento_id}")
    except Exception as e:
        print(f"❌ Erro ao remover event ID: {e}")
    finally:
        conn.close()

# ========================================
# FUNÇÕES PARA BACKUP POR EMAIL - PASSO 1
# ========================================

def calcular_hash_agendamentos():
    """Calcula hash dos agendamentos para detectar mudanças"""
    try:
        agendamentos = buscar_agendamentos()
        # Converter para string ordenada para hash consistente
        dados_str = str(sorted(agendamentos))
        return hashlib.md5(dados_str.encode()).hexdigest()
    except:
        return ""

def agendamentos_mudaram():
    """Verifica se houve mudanças desde último backup"""
    hash_atual = calcular_hash_agendamentos()
    hash_anterior = obter_configuracao("ultimo_backup_hash", "")
    
    if hash_atual != hash_anterior:
        # Salvar novo hash
        salvar_configuracao("ultimo_backup_hash", hash_atual)
        return True
    return False

def enviar_backup_email_agendamentos(forcar_envio=False):
    """Envia backup dos agendamentos por email"""
    
    # Verificar se backup automático está ativo
    backup_automatico_ativo = obter_configuracao("backup_email_ativo", False)
    if not backup_automatico_ativo and not forcar_envio:
        print("📧 Backup automático por email desativado")
        return False
    
    # Verificar se há mudanças (se não for forçado)
    if not forcar_envio and not agendamentos_mudaram():
        print("📊 Sem mudanças desde último backup - não enviando")
        return False
    
    try:
        # Obter configurações de email
        email_sistema = obter_configuracao("email_sistema", "")
        senha_email = obter_configuracao("senha_email", "")
        servidor_smtp = obter_configuracao("servidor_smtp", "smtp.gmail.com")
        porta_smtp = obter_configuracao("porta_smtp", 587)
        
        # Email de destino para backup
        email_backup = obter_configuracao("email_backup_destino", email_sistema)
        
        if not email_sistema or not senha_email or not email_backup:
            print("❌ Configurações de email incompletas para backup")
            return False
        
        # Gerar CSV dos agendamentos
        csv_data = exportar_agendamentos_csv()
        if not csv_data:
            print("❌ Nenhum agendamento para fazer backup")
            return False
        
        # Estatísticas para o email
        agendamentos = buscar_agendamentos()
        total_agendamentos = len(agendamentos)
        
        # Contar por status
        pendentes = len([a for a in agendamentos if len(a) > 6 and a[6] == "pendente"])
        confirmados = len([a for a in agendamentos if len(a) > 6 and a[6] == "confirmado"])
        atendidos = len([a for a in agendamentos if len(a) > 6 and a[6] == "atendido"])
        cancelados = len([a for a in agendamentos if len(a) > 6 and a[6] == "cancelado"])
        
        # Data/hora atual
        agora = datetime.now()
        data_formatada = agora.strftime("%d/%m/%Y às %H:%M")
        
        # Nome do arquivo
        nome_arquivo = f"agendamentos_backup_{agora.strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Dados do profissional/clínica
        nome_profissional = obter_configuracao("nome_profissional", "Dr. João Silva")
        nome_clinica = obter_configuracao("nome_clinica", "Clínica São Lucas")
        
        # Criar email
        msg = MIMEMultipart()
        msg['From'] = email_sistema
        msg['To'] = email_backup
        msg['Subject'] = f"📊 Backup Agendamentos - {nome_clinica} - {agora.strftime('%d/%m/%Y')}"
        
        # Corpo do email
        corpo = f"""
📋 Backup Automático de Agendamentos

🏥 {nome_clinica}
👨‍⚕️ {nome_profissional}

📅 Data/Hora do Backup: {data_formatada}
📊 Total de Agendamentos: {total_agendamentos}

📈 Estatísticas por Status:
⏳ Pendentes: {pendentes}
✅ Confirmados: {confirmados}
🎉 Atendidos: {atendidos}
❌ Cancelados: {cancelados}

📎 Arquivo em Anexo: {nome_arquivo}
💾 Tamanho: {len(csv_data.encode('utf-8')) / 1024:.1f} KB

🤖 Mensagem automática do Sistema de Agendamento
"""
        
        # Anexar corpo do email
        msg.attach(MIMEText(corpo, 'plain', 'utf-8'))
        
        # Anexar arquivo CSV
        from email.mime.application import MIMEApplication
        anexo = MIMEApplication(csv_data.encode('utf-8'), _subtype="csv")
        anexo.add_header('Content-Disposition', 'attachment', filename=nome_arquivo)
        msg.attach(anexo)
        
        # Enviar email
        server = smtplib.SMTP(servidor_smtp, porta_smtp)
        server.starttls()
        server.login(email_sistema, senha_email)
        server.send_message(msg)
        server.quit()
        
        # Salvar data do último backup
        salvar_configuracao("ultimo_backup_email_data", agora.isoformat())
        
        print(f"✅ Backup enviado por email para {email_backup}")
        print(f"📊 {total_agendamentos} agendamentos incluídos no backup")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao enviar backup por email: {e}")
        return False

def interface_backup_email():
    """Interface para configurar backup automático por email"""
    
    st.subheader("📧 Backup Automático por Email")
    
    # Status atual
    backup_ativo = obter_configuracao("backup_email_ativo", False)
    
    if backup_ativo:
        st.success("✅ Backup automático por email ATIVADO")
        
        # Mostrar configurações atuais
        frequencia = obter_configuracao("backup_email_frequencia", "semanal")
        horario = obter_configuracao("backup_email_horario", "08:00")
        email_destino = obter_configuracao("email_backup_destino", "")
        
        st.info(f"""
**📋 Configurações Atuais:**
• **Frequência:** {frequencia.title()}
• **Horário:** {horario}
• **Email de destino:** {email_destino}
        """)
        
        # Mostrar último backup
        ultimo_backup_str = obter_configuracao("ultimo_backup_email_data", "")
        if ultimo_backup_str:
            try:
                ultimo_backup = datetime.fromisoformat(ultimo_backup_str)
                ultimo_formatado = ultimo_backup.strftime("%d/%m/%Y às %H:%M")
                st.info(f"📅 **Último backup enviado:** {ultimo_formatado}")
            except:
                pass
    else:
        st.warning("⚠️ Backup automático por email DESATIVADO")
    
    # Configurações
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**⚙️ Configurações do Backup**")
        
        # Ativar/desativar
        backup_email_ativo = st.checkbox(
            "Ativar backup automático por email",
            value=backup_ativo,
            help="Envia backup dos agendamentos automaticamente por email"
        )
        
        # Frequência
        frequencia_backup = st.selectbox(
            "Frequência do backup:",
            ["diario", "semanal", "mensal"],
            index=["diario", "semanal", "mensal"].index(obter_configuracao("backup_email_frequencia", "semanal")),
            format_func=lambda x: {"diario": "Diário", "semanal": "Semanal", "mensal": "Mensal"}[x],
            help="Com que frequência enviar o backup"
        )
        
        # Horário
        try:
            horario_atual = datetime.strptime(obter_configuracao("backup_email_horario", "08:00"), "%H:%M").time()
        except:
            horario_atual = datetime.strptime("08:00", "%H:%M").time()
        
        horario_backup = st.time_input(
            "Horário do backup:",
            value=horario_atual,
            help="Horário para enviar o backup automaticamente"
        )
        
        # Email de destino
        email_backup_destino = st.text_input(
            "Email de destino:",
            value=obter_configuracao("email_backup_destino", obter_configuracao("email_sistema", "")),
            placeholder="backup@clinica.com",
            help="Email que receberá os backups automáticos"
        )
    
    with col2:
        st.markdown("**🧪 Teste e Backup Manual**")
        
        # Backup manual
        if st.button("📤 Enviar Backup Agora", type="secondary", help="Enviar backup manual independente das configurações"):
            with st.spinner("Gerando e enviando backup..."):
                sucesso = enviar_backup_email_agendamentos(forcar_envio=True)
                if sucesso:
                    st.success("✅ Backup enviado com sucesso!")
                else:
                    st.error("❌ Erro ao enviar backup. Verifique as configurações de email.")
        
        # Verificar mudanças
        if st.button("🔍 Verificar Mudanças", help="Verificar se há mudanças desde último backup"):
            if agendamentos_mudaram():
                st.info("📊 Há mudanças nos agendamentos desde último backup")
            else:
                st.success("✅ Nenhuma mudança desde último backup")
        
        # Informações
        st.markdown("**ℹ️ Como Funciona:**")
        st.info("""
• **Automático:** Verifica mudanças e envia apenas se necessário
• **Inteligente:** Não envia spam se não houver alterações  
• **Seguro:** Anexa CSV com todos os agendamentos
• **Informativo:** Email com estatísticas detalhadas
        """)
    
    # Botão para salvar configurações
    if st.button("💾 Salvar Configurações de Backup", type="primary", use_container_width=True):
        salvar_configuracao("backup_email_ativo", backup_email_ativo)
        salvar_configuracao("backup_email_frequencia", frequencia_backup)
        salvar_configuracao("backup_email_horario", horario_backup.strftime("%H:%M"))
        salvar_configuracao("email_backup_destino", email_backup_destino)
        
        st.success("✅ Configurações de backup salvas!")
        
        if backup_email_ativo:
            st.info(f"""
🎯 **Backup configurado:**
• **Frequência:** {frequencia_backup.title()}
• **Horário:** {horario_backup.strftime('%H:%M')}  
• **Email:** {email_backup_destino}

📧 Próximo backup será enviado automaticamente se houver mudanças!
            """)
        else:
            st.warning("⚠️ Backup automático foi desativado")
        
        st.rerun()

def verificar_hora_backup():
    """Verifica se chegou a hora do backup automático"""
    try:
        backup_ativo = obter_configuracao("backup_email_ativo", False)
        if not backup_ativo:
            return False
        
        # Configurações de agendamento
        frequencia = obter_configuracao("backup_email_frequencia", "semanal")
        horario = obter_configuracao("backup_email_horario", "08:00")
        
        agora = datetime.now()
        hora_backup = datetime.strptime(horario, "%H:%M").time()
        
        # Verificar se é a hora do backup (com tolerância de 1 minuto)
        if abs((agora.time().hour * 60 + agora.time().minute) - 
               (hora_backup.hour * 60 + hora_backup.minute)) > 1:
            return False
        
        # Verificar frequência
        ultimo_backup_str = obter_configuracao("ultimo_backup_email_data", "")
        
        if not ultimo_backup_str:
            return True  # Primeiro backup
        
        try:
            ultimo_backup = datetime.fromisoformat(ultimo_backup_str)
        except:
            return True  # Se der erro, fazer backup
        
        if frequencia == "diario":
            return (agora - ultimo_backup).days >= 1
        elif frequencia == "semanal":
            return (agora - ultimo_backup).days >= 7
        elif frequencia == "mensal":
            return (agora - ultimo_backup).days >= 30
        
        return False
        
    except Exception as e:
        print(f"❌ Erro ao verificar hora do backup: {e}")
        return False

def iniciar_monitoramento_backup():
    """Inicia thread para monitoramento automático de backup"""
    def monitorar():
        print("🔄 Monitoramento de backup automático iniciado")
        while True:
            try:
                if verificar_hora_backup():
                    print("⏰ Hora do backup automático!")
                    sucesso = enviar_backup_email_agendamentos()
                    if sucesso:
                        print("✅ Backup automático enviado com sucesso!")
                    else:
                        print("❌ Falha no backup automático")
                
                # Verificar a cada minuto
                time.sleep(60)
                
            except Exception as e:
                print(f"❌ Erro no monitoramento de backup: {e}")
                time.sleep(300)  # Esperar 5 minutos se der erro
    
    # Iniciar thread em background
    thread = threading.Thread(target=monitorar, daemon=True)
    thread.start()

# ========================================
# FUNÇÕES NOVAS PARA BLOQUEIOS DE PERÍODO
# ========================================

def init_config_periodos():
    """Adiciona tabela de bloqueios de período ao banco"""
    conn = conectar()
    c = conn.cursor()
    
    # Criar tabela para bloqueios de período
    c.execute('''
        CREATE TABLE IF NOT EXISTS bloqueios_periodos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_inicio TEXT,
            data_fim TEXT,
            descricao TEXT,
            criado_em TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def adicionar_bloqueio_periodo(data_inicio, data_fim, descricao=""):
    """Adiciona um bloqueio de período (ex: férias, viagem)"""
    conn = conectar()
    c = conn.cursor()
    
    try:
        # Salvar o período na nova tabela
        from datetime import datetime
        criado_em = datetime.now().isoformat()
        
        c.execute("""INSERT INTO bloqueios_periodos 
                    (data_inicio, data_fim, descricao, criado_em) 
                    VALUES (?, ?, ?, ?)""", 
                 (data_inicio, data_fim, descricao, criado_em))
        
        periodo_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return periodo_id
        
    except Exception as e:
        conn.close()
        print(f"Erro ao adicionar período: {e}")
        return False

def obter_bloqueios_periodos():
    """Obtém todos os bloqueios de período"""
    conn = conectar()
    c = conn.cursor()
    
    try:
        c.execute("""SELECT id, data_inicio, data_fim, descricao, criado_em 
                    FROM bloqueios_periodos 
                    ORDER BY data_inicio""")
        periodos = c.fetchall()
        return periodos
    except:
        return []
    finally:
        conn.close()

def remover_bloqueio_periodo(periodo_id):
    """Remove um bloqueio de período"""
    conn = conectar()
    c = conn.cursor()
    
    try:
        c.execute("DELETE FROM bloqueios_periodos WHERE id=?", (periodo_id,))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

def data_em_periodo_bloqueado(data):
    """Verifica se uma data está em algum período bloqueado"""
    conn = conectar()
    c = conn.cursor()
    
    try:
        c.execute("""SELECT COUNT(*) FROM bloqueios_periodos 
                    WHERE ? BETWEEN data_inicio AND data_fim""", (data,))
        
        resultado = c.fetchone()[0] > 0
        conn.close()
        return resultado
    except:
        conn.close()
        return False
    
# Inicializar banco
init_config()

# Inicializar monitoramento de backup automático
iniciar_monitoramento_backup()

# Inicializar tabela de períodos
init_config_periodos()

# Restaurar configurações do GitHub
restaurar_configuracoes_github()

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
                    st.error("❌ Senha incorreta!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        
        # Estatísticas
        agendamentos = buscar_agendamentos()
        bloqueios = obter_bloqueios()
        
        hoje = datetime.now().strftime("%Y-%m-%d")
        agendamentos_hoje = [a for a in agendamentos if a[1] == hoje]
        agendamentos_mes = [a for a in agendamentos if a[1].startswith(datetime.now().strftime("%Y-%m"))]
        
        st.markdown("""
        <div class="stats-container">
            <div class="stat-card">
                <div class="stat-number">{}</div>
                <div class="stat-label">Agendamentos Hoje</div>
            </div>
            <div class="stat-card success">
                <div class="stat-number">{}</div>
                <div class="stat-label">Total Este Mês</div>
            </div>
            <div class="stat-card warning">
                <div class="stat-number">{}</div>
                <div class="stat-label">Datas Bloqueadas</div>
            </div>
            <div class="stat-card danger">
                <div class="stat-number">{}</div>
                <div class="stat-label">Total de Agendamentos</div>
            </div>
        </div>
        """.format(len(agendamentos_hoje), len(agendamentos_mes), len(bloqueios), len(agendamentos)), unsafe_allow_html=True)
        
        # Conteúdo baseado na opção
                # Interface administrativa autenticada com menu horizontal
        opcao = criar_menu_horizontal()
        
        # Conteúdo baseado na opção
        if opcao == "⚙️ Configurações Gerais":

            st.markdown('<div class="main-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header"><h2 class="card-title">⚙️ Configurações Gerais</h2></div>', unsafe_allow_html=True)
            
            # Tabs para organizar as configurações
            tab1, tab2, tab3 = st.tabs(["📅 Agendamento", "📞 Contato & Local", "📧 Email & Notificações"])
            
            with tab1:
                st.subheader("📅 Configurações de Agendamento")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**📆 Período de Agendamento**")
                    
                    # Dias futuros disponíveis
                    dias_futuros = st.slider(
                        "Quantos dias no futuro a agenda ficará aberta:",
                        min_value=7,
                        max_value=120,
                        value=obter_configuracao("dias_futuros", 30),
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
                        "6 horas": 6,
                        "12 horas": 12,
                        "24 horas": 24,
                        "48 horas": 48
                    }
                    
                    antecedencia_texto = "2 horas"
                    for texto, horas in antecedencia_opcoes.items():
                        if horas == antecedencia_atual:
                            antecedencia_texto = texto
                            break
                    
                    antecedencia_selecionada = st.selectbox(
                        "Antecedência mínima para agendamento:",
                        list(antecedencia_opcoes.keys()),
                        index=list(antecedencia_opcoes.keys()).index(antecedencia_texto),
                        help="Tempo mínimo necessário entre o agendamento e 00:00 da data da  consulta"
                    )
                
                with col2:
                    st.markdown("**🕐 Horários de Funcionamento**")
                    
                    # Horário de início
                    try:
                        time_inicio = datetime.strptime(obter_configuracao("horario_inicio", "09:00"), "%H:%M").time()
                    except:
                        time_inicio = datetime.strptime("09:00", "%H:%M").time()
                    
                    horario_inicio = st.time_input(
                        "Horário de início:",
                        value=time_inicio,
                        help="Primeiro horário disponível para agendamento"
                    )
                    
                    # Horário de fim
                    try:
                        time_fim = datetime.strptime(obter_configuracao("horario_fim", "18:00"), "%H:%M").time()
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
                        "1h 15min": 75,
                        "1h 30min": 90,
                        "2 horas": 120,
                        "2h 30min": 150,
                        "3 horas": 180
                    }
                    
                    intervalo_texto = "1 hora"
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
                
                # Configurações de confirmação
                st.markdown("---")
                st.markdown("**🔄 Modo de Confirmação**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    confirmacao_automatica = st.checkbox(
                        "Confirmação automática de agendamentos",
                        value=obter_configuracao("confirmacao_automatica", False),
                        help="Se ativado, agendamentos são confirmados automaticamente sem necessidade de aprovação manual"
                    )
                
                with col2:
                    if not confirmacao_automatica:
                        st.info("💡 **Modo Manual:** Você precisará confirmar cada agendamento manualmente na aba 'Lista de Agendamentos'")
                    else:
                        st.success("✅ **Modo Automático:** Agendamentos são confirmados instantaneamente")
                
            
            with tab2:
                st.subheader("📞 Informações de Contato e Local")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**👨‍⚕️ Informações Profissionais**")
                    
                    nome_profissional = st.text_input(
                        "Nome do profissional:",
                        value=obter_configuracao("nome_profissional", "Dr. João Silva"),
                        help="Nome que aparecerá no sistema e nos emails"
                    )
                    
                    especialidade = st.text_input(
                        "Especialidade/Área:",
                        value=obter_configuracao("especialidade", "Clínico Geral"),
                        help="Ex: Dermatologia, Psicologia, etc."
                    )
                    
                    registro_profissional = st.text_input(
                        "Registro profissional:",
                        value=obter_configuracao("registro_profissional", "CRM 12345"),
                        help="Ex: CRM, CRP, CRO, etc."
                    )
                
                with col2:
                    st.markdown("**🏥 Informações do Local**")
                    
                    nome_clinica = st.text_input(
                        "Nome da clínica/estabelecimento:",
                        value=obter_configuracao("nome_clinica", "Clínica São Lucas"),
                        help="Nome do local de atendimento"
                    )
                    
                    telefone_contato = st.text_input(
                        "Telefone de contato:",
                        value=obter_configuracao("telefone_contato", "(11) 3333-4444"),
                        help="Telefone que aparecerá no sistema"
                    )
                    
                    whatsapp = st.text_input(
                        "WhatsApp:",
                        value=obter_configuracao("whatsapp", "(11) 99999-9999"),
                        help="Número do WhatsApp para contato"
                    )
                
                st.markdown("**📍 Endereço Completo**")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    endereco_rua = st.text_input(
                        "Rua/Avenida:",
                        value=obter_configuracao("endereco_rua", "Rua das Flores, 123"),
                        help="Rua, número e complemento"
                    )
                
                with col2:
                    endereco_bairro = st.text_input(
                        "Bairro:",
                        value=obter_configuracao("endereco_bairro", "Centro"),
                        help="Bairro do estabelecimento"
                    )
                
                with col3:
                    endereco_cidade = st.text_input(
                        "Cidade - UF:",
                        value=obter_configuracao("endereco_cidade", "São Paulo - SP"),
                        help="Cidade e estado"
                    )
                
                # Instruções adicionais
                st.markdown("**📝 Instruções Adicionais**")
                
                instrucoes_chegada = st.text_area(
                    "Instruções para chegada:",
                    value=obter_configuracao("instrucoes_chegada", "Favor chegar 10 minutos antes do horário agendado."),
                    help="Instruções que aparecerão nos emails de confirmação",
                    height=100
                )
            
            with tab3:
                st.subheader("📧 Configurações de Email e Notificações")
                
                # Ativar/desativar sistema de email
                envio_automatico = st.checkbox(
                    "Ativar envio automático de emails",
                    value=obter_configuracao("envio_automatico", False),
                    help="Se ativado, emails serão enviados automaticamente para confirmações e cancelamentos"
                )
                
                if envio_automatico:
                    st.markdown("---")
                    st.markdown("**⚙️ Configurações do Servidor SMTP**")
                    
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
                            help="Para Gmail: smtp.gmail.com | Para Outlook: smtp-mail.outlook.com"
                        )
                    
                    with col2:
                        senha_email = st.text_input(
                            "Senha do email:",
                            value=obter_configuracao("senha_email", ""),
                            type="password",
                            help="Para Gmail: use senha de app (não a senha normal da conta)"
                        )
                        
                        try:
                            porta_valor = obter_configuracao("porta_smtp", 587)
                            porta_smtp_value = int(porta_valor) if porta_valor and str(porta_valor).strip() else 587
                        except (ValueError, TypeError):
                            porta_smtp_value = 587

                        porta_smtp = st.number_input(
                            "Porta SMTP:",
                            value=porta_smtp_value,
                            help="Para Gmail: 587 | Para Outlook: 587"
                        )                    
                    # Configurações de envio
                    st.markdown("---")
                    st.markdown("**📬 Tipos de Email Automático**")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        enviar_confirmacao = st.checkbox(
                            "Enviar email de confirmação",
                            value=obter_configuracao("enviar_confirmacao", True),
                            help="Envia email quando agendamento é confirmado"
                        )
                        

                    
                    with col2:
                        enviar_cancelamento = st.checkbox(
                            "Enviar email de cancelamento",
                            value=obter_configuracao("enviar_cancelamento", True),
                            help="Envia email quando agendamento é cancelado"
                        )
                        
                    
                    # Template de email
                    st.markdown("---")
                    st.markdown("**✉️ Personalizar Mensagens**")
                    
                    template_confirmacao = st.text_area(
                        "Template de confirmação:",
                        value=obter_configuracao("template_confirmacao", 
                            "Olá {nome}!\n\nSeu agendamento foi confirmado:\n📅 Data: {data}\n⏰ Horário: {horario}\n\nAguardamos você!"),
                        help="Use {nome}, {data}, {horario}, {local} como variáveis",
                        height=100
                    )
                    
                    # Teste de email
                    st.markdown("---")
                    st.markdown("**🧪 Testar Configurações**")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        email_teste = st.text_input(
                            "Email para teste:",
                            value=obter_configuracao("email_teste", ""),
                            placeholder="seu@email.com",
                            help="Digite um email para receber um teste"
                        )
                    
                    with col2:
                        if st.button("📧 Enviar Email Teste", type="secondary"):
                            if email_teste and email_sistema and senha_email:
                                # Salvar o email de teste
                                salvar_configuracao("email_teste", email_teste)
                                
                                # Tentar envio manual (sem chamar função externa)
                                try:
                                    import smtplib
                                    from email.mime.text import MIMEText
                                    from email.mime.multipart import MIMEMultipart
                                    
                                    # Criar mensagem de teste
                                    msg = MIMEMultipart()
                                    msg['From'] = email_sistema
                                    msg['To'] = email_teste
                                    msg['Subject'] = f"🧪 Teste de Email - {nome_profissional}"
                                    
                                    corpo = f"""
Olá!

Este é um email de teste do sistema de agendamento.

✅ Configurações funcionando corretamente!

📧 Email do sistema: {email_sistema}
🏥 Clínica: {nome_clinica}
👨‍⚕️ Profissional: {nome_profissional}

Se você recebeu este email, significa que as configurações SMTP estão corretas.

Atenciosamente,
Sistema de Agendamento Online
"""
                                    
                                    msg.attach(MIMEText(corpo, 'plain', 'utf-8'))
                                    
                                    # Enviar email
                                    server = smtplib.SMTP(servidor_smtp, porta_smtp)
                                    server.starttls()
                                    server.login(email_sistema, senha_email)
                                    server.send_message(msg)
                                    server.quit()
                                    
                                    st.success("✅ Email de teste enviado com sucesso!")
                                    
                                except Exception as e:
                                    st.error(f"❌ Erro ao enviar email: {str(e)}")
                            else:
                                st.warning("⚠️ Preencha o email de teste e configure o sistema primeiro")
   
                    
                    # Seção Google Calendar
                    st.markdown("---")
                    st.markdown("**📅 Integração Google Calendar**")
                    
                    google_calendar_ativo = st.checkbox(
                        "Ativar sincronização com Google Calendar",
                        value=obter_configuracao("google_calendar_ativo", False),
                        help="Sincroniza automaticamente agendamentos confirmados com seu Google Calendar"
                    )
                    
                    if google_calendar_ativo:
                        st.success("✅ Google Calendar ativado - agendamentos serão sincronizados automaticamente!")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.info("""
                            **📋 Como funciona:**
                            • Agendamento confirmado → Cria evento
                            • Agendamento cancelado → Remove evento  
                            • Agendamento atendido → Marca como concluído
                            """)
                        
                        with col2:

                            if st.button("🧪 Testar Conexão Google Calendar", key="test_google_calendar"):
                                try:
                                    st.write("🔍 Testando imports...")
                                    
                                    # Teste de import direto
                                    import importlib
                                    
                                    # Testar cada biblioteca individualmente
                                    try:
                                        google_auth = importlib.import_module('google.auth')
                                        st.write("✅ google.auth OK")
                                    except ImportError as e:
                                        st.error(f"❌ google.auth: {e}")
                                        
                                    try:
                                        google_oauth2 = importlib.import_module('google.oauth2.credentials')
                                        st.write("✅ google.oauth2.credentials OK")
                                    except ImportError as e:
                                        st.error(f"❌ google.oauth2.credentials: {e}")
                                        
                                    try:
                                        googleapiclient = importlib.import_module('googleapiclient.discovery')
                                        st.write("✅ googleapiclient.discovery OK")
                                    except ImportError as e:
                                        st.error(f"❌ googleapiclient.discovery: {e}")
                                        
                                    st.info("📝 Se algum import falhou, o problema é falta de bibliotecas no requirements.txt")
                                    
                                except Exception as e:
                                    st.error(f"❌ Erro geral: {e}")

                                with st.spinner("Testando conexão..."):
                                    try:
                                        service = get_google_calendar_service()
                                        if service:
                                            # Testar listando calendários
                                            calendars = service.calendarList().list().execute()
                                            st.success("✅ Conexão com Google Calendar funcionando!")
                                            
                                            # Mostrar calendários disponíveis
                                            with st.expander("📅 Calendários disponíveis"):
                                                for calendar in calendars.get('items', []):
                                                    if calendar['id'] == 'primary':
                                                        st.write(f"📋 **{calendar['summary']}** (Principal) ⭐")
                                                    else:
                                                        st.write(f"📋 **{calendar['summary']}**")
                                                        
                                        else:
                                            st.error("❌ Não foi possível conectar. Verifique as credenciais nos Secrets.")
                                    except Exception as e:
                                        st.error(f"❌ Erro na conexão: {str(e)}")
                    else:
                        st.info("💡 Ative a sincronização para ter seus agendamentos automaticamente no Google Calendar!")
                        
                        st.markdown("""
                        **🔧 Configuração necessária:**
                        
                        Configure nos **Streamlit Secrets**:
                        - `GOOGLE_CLIENT_ID`
                        - `GOOGLE_CLIENT_SECRET` 
                        - `GOOGLE_REFRESH_TOKEN`
                        - `GOOGLE_CALENDAR_ID` (opcional, padrão: "primary")
                        """)
                    
                    # Seção de backup GitHub (manter como está)
                    st.markdown("---")
                    st.markdown("**☁️ Backup de Configurações**")   
                
                    # Seção de backup GitHub (ADICIONAR DEPOIS da seção de teste de email)
                    st.markdown("---")
                    st.markdown("**☁️ Backup de Configurações**")
                    
                    backup_github_ativo = st.checkbox(
                        "Ativar backup automático no GitHub",
                        value=obter_configuracao("backup_github_ativo", False),
                        help="Salva automaticamente suas configurações em repositório GitHub privado"
                    )
                    
                    if backup_github_ativo:
                        st.success("✅ Backup automático ativado - suas configurações serão salvas automaticamente!")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("💾 Fazer Backup Manual", type="secondary"):
                                with st.spinner("Enviando backup para GitHub..."):
                                    try:
                                        if backup_configuracoes_github():
                                            st.success("✅ Backup enviado com sucesso!")
                                            st.info("🔗 Confira em: https://github.com/psrs2000/Agenda_Livre")
                                        else:
                                            st.error("❌ Erro no backup. Verifique as configurações.")
                                    except Exception as e:
                                        st.error(f"❌ Erro: {e}")
                        
                        with col2:
                            # Mostrar última data de backup se disponível
                            ultima_config = obter_configuracao("_backup_timestamp", "")
                            if ultima_config:
                                try:
                                    from datetime import datetime
                                    data_backup = datetime.fromisoformat(ultima_config)
                                    data_formatada = data_backup.strftime("%d/%m/%Y às %H:%M")
                                    st.info(f"📅 Último backup: {data_formatada}")
                                except:
                                    st.info("📅 Backup disponível no GitHub")
                            else:
                                st.info("📅 Primeiro backup será feito automaticamente")
                    
                    else:
                        st.info("💡 Ative o backup automático para nunca perder suas configurações quando o Streamlit reiniciar!")
                        
                        # Botão para fazer backup mesmo com função desativada
                        if st.button("💾 Fazer Backup Único", help="Fazer backup sem ativar função automática"):
                            with st.spinner("Enviando backup..."):
                                try:
                                    if backup_configuracoes_github():
                                        st.success("✅ Backup enviado com sucesso!")
                                        st.info("🔗 Confira em: https://github.com/psrs2000/Agenda_Livre")
                                    else:
                                        st.error("❌ Erro no backup. Verifique token GitHub.")
                                except Exception as e:
                                    st.error(f"❌ Erro: {e}")
                
                else:
                    st.info("📧 Sistema de email desativado. Ative acima para configurar o envio automático.")            
            # Botão para salvar todas as configurações
            st.markdown("---")
            if st.button("💾 Salvar Todas as Configurações", type="primary", use_container_width=True):
                # Salvar configurações da tab 1
                salvar_configuracao("dias_futuros", dias_futuros)
                salvar_configuracao("antecedencia_minima", antecedencia_opcoes[antecedencia_selecionada])
                salvar_configuracao("horario_inicio", horario_inicio.strftime("%H:%M"))
                salvar_configuracao("horario_fim", horario_fim.strftime("%H:%M"))
                salvar_configuracao("intervalo_consultas", intervalo_opcoes[intervalo_selecionado])
                salvar_configuracao("confirmacao_automatica", confirmacao_automatica)
                                
                # Salvar configurações da tab 2
                salvar_configuracao("nome_profissional", nome_profissional)
                salvar_configuracao("especialidade", especialidade)
                salvar_configuracao("registro_profissional", registro_profissional)
                salvar_configuracao("nome_clinica", nome_clinica)
                salvar_configuracao("telefone_contato", telefone_contato)
                salvar_configuracao("whatsapp", whatsapp)
                salvar_configuracao("endereco_rua", endereco_rua)
                salvar_configuracao("endereco_bairro", endereco_bairro)
                salvar_configuracao("endereco_cidade", endereco_cidade)
                salvar_configuracao("instrucoes_chegada", instrucoes_chegada)
                
                # Salvar configurações da tab 3
                salvar_configuracao("envio_automatico", envio_automatico)
                salvar_configuracao("google_calendar_ativo", google_calendar_ativo)
                salvar_configuracao("email_teste", email_teste if envio_automatico else "")
                if envio_automatico:
                    salvar_configuracao("email_sistema", email_sistema)
                    salvar_configuracao("senha_email", senha_email)
                    salvar_configuracao("servidor_smtp", servidor_smtp)
                    salvar_configuracao("porta_smtp", porta_smtp)
                    salvar_configuracao("enviar_confirmacao", enviar_confirmacao)
                    salvar_configuracao("enviar_cancelamento", enviar_cancelamento)
                    salvar_configuracao("template_confirmacao", template_confirmacao)
                
                # NOVO: Salvar configuração de backup GitHub
                salvar_configuracao("backup_github_ativo", backup_github_ativo)
                
                st.success("✅ Todas as configurações foram salvas com sucesso!")
                
                # NOVO: Backup automático no GitHub (se ativado)
                if backup_github_ativo:
                    try:
                        with st.spinner("📤 Fazendo backup no GitHub..."):
                            if backup_configuracoes_github():
                                st.success("☁️ Backup automático enviado para GitHub!")
                            else:
                                st.warning("⚠️ Erro no backup automático. Configurações salvas localmente.")
                    except Exception as e:
                        st.warning(f"⚠️ Erro no backup automático: {e}")
                
                # Mostrar resumo
                st.markdown("**📋 Resumo das configurações salvas:**")
                st.info(f"""
                📅 **Agendamento:** {intervalo_selecionado} de {horario_inicio.strftime('%H:%M')} às {horario_fim.strftime('%H:%M')}
                ⏰ **Antecedência:** {antecedencia_selecionada}
                🔄 **Confirmação:** {'Automática' if confirmacao_automatica else 'Manual'}
                📧 **Email:** {'Ativado' if envio_automatico else 'Desativado'}
                ☁️ **Backup:** {'Ativado' if backup_github_ativo else 'Desativado'}
                👨‍⚕️ **Profissional:** {nome_profissional} - {especialidade}
                🏥 **Local:** {nome_clinica}
                """)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        elif opcao == "📅 Configurar Agenda":
            st.markdown('<div class="main-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header"><h2 class="card-title">📅 Configuração de Agenda</h2></div>', unsafe_allow_html=True)
            
            dias_pt = {"Monday": "Segunda-feira", "Tuesday": "Terça-feira", "Wednesday": "Quarta-feira", "Thursday": "Quinta-feira", "Friday": "Sexta-feira", "Saturday": "Sábado", "Sunday": "Domingo"}
            dias_atuais = obter_dias_uteis()
            
            st.markdown("Selecione os dias da semana:")
            
            cols = st.columns(4)
            dias_selecionados = []
            
            for i, (dia_en, dia_pt) in enumerate(dias_pt.items()):
                with cols[i % 4]:
                    if st.checkbox(dia_pt, value=(dia_en in dias_atuais), key=f"dia_{dia_en}"):
                        dias_selecionados.append(dia_en)
            
            if st.button("💾 Salvar Dias", type="primary", use_container_width=True):
                salvar_dias_uteis(dias_selecionados)
                st.success("✅ Dias salvos!")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        elif opcao == "🗓️ Gerenciar Bloqueios":
                    st.markdown('<div class="main-card">', unsafe_allow_html=True)
                    st.markdown('<div class="card-header"><h2 class="card-title">🗓️ Gerenciar Bloqueios</h2></div>', unsafe_allow_html=True)
                    
                    # Tabs para diferentes tipos de bloqueio
                    tab1, tab2, tab3, tab4 = st.tabs(["📅 Dias Específicos", "📆 Períodos", "🕐 Horários Específicos", "⏰ Bloqueios Permanentes"])
                    
                    with tab1:
                        st.subheader("📅 Bloquear Dias Específicos")
                        st.info("💡 Use esta opção para bloquear poucos dias isolados (ex: feriados, faltas pontuais)")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**📌 Bloquear Data Individual**")
                            data_bloqueio = st.date_input("Data para bloquear:", min_value=datetime.today())
                            
                            if st.button("🚫 Bloquear Dia", type="primary", key="btn_bloquear_dia"):
                                if adicionar_bloqueio(data_bloqueio.strftime("%Y-%m-%d")):
                                    st.success("✅ Dia bloqueado!")
                                    st.rerun()
                                else:
                                    st.warning("⚠️ Data já bloqueada.")
                        
                        with col2:
                            st.markdown("**ℹ️ Dias Específicos vs Períodos:**")
                            st.markdown("""
                            **🎯 Use "Dias Específicos" para:**
                            • Feriados isolados
                            • Faltas pontuais  
                            • 1-3 dias não consecutivos
                            
                            **🎯 Use "Períodos" para:**
                            • Férias (vários dias seguidos)
                            • Viagens longas
                            • Congressos/cursos
                            """)
                        
                        # Lista de datas bloqueadas (dias inteiros)
                        st.subheader("🚫 Dias Individuais Bloqueados")
                        bloqueios = obter_bloqueios()
                        
                        if bloqueios:
                            for data in bloqueios:
                                data_obj = datetime.strptime(data, "%Y-%m-%d")
                                data_formatada = data_obj.strftime("%d/%m/%Y - %A")
                                data_formatada = data_formatada.replace('Monday', 'Segunda-feira')\
                                    .replace('Tuesday', 'Terça-feira').replace('Wednesday', 'Quarta-feira')\
                                    .replace('Thursday', 'Quinta-feira').replace('Friday', 'Sexta-feira')\
                                    .replace('Saturday', 'Sábado').replace('Sunday', 'Domingo')
                                
                                col_data, col_btn = st.columns([4, 1])
                                with col_data:
                                    st.markdown(f"""
                                    <div style="background: #fee2e2; border: 1px solid #fecaca; border-radius: 8px; padding: 1rem; margin: 0.5rem 0;">
                                        <span style="color: #991b1b; font-weight: 500;">🚫 {data_formatada}</span>
                                    </div>
                                    """, unsafe_allow_html=True)
                                with col_btn:
                                    if st.button("🗑️", key=f"remove_dia_{data}", help="Remover bloqueio"):
                                        remover_bloqueio(data)
                                        st.rerun()
                        else:
                            st.info("📅 Nenhum dia individual bloqueado atualmente.")
                    
                    with tab2:
                        st.subheader("📆 Bloquear Períodos")
                        st.info("💡 Use esta opção para bloquear vários dias consecutivos (ex: férias, viagens)")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**➕ Criar Novo Período Bloqueado**")
                            
                            data_inicio_periodo = st.date_input(
                                "Data inicial:", 
                                min_value=datetime.today().date(), 
                                key="periodo_inicio"
                            )

                            data_fim_periodo = st.date_input(
                                "Data final:", 
                                key="periodo_fim"
                            )

                            # Validação manual das datas
                            if data_inicio_periodo and data_fim_periodo:
                                if data_fim_periodo < data_inicio_periodo:
                                    st.error("❌ A data final deve ser posterior à data inicial!")
                                    datas_validas = False
                                else:
                                    datas_validas = True
                            else:
                                datas_validas = False

                            descricao_periodo = st.text_input(
                                "Descrição:",
                                placeholder="Ex: Férias de Janeiro, Viagem Europa, Congresso...",
                                key="desc_periodo"
                            )

                            if st.button("🚫 Bloquear Período", type="primary", key="btn_bloquear_periodo_novo"):
                                if datas_validas:
                                    if descricao_periodo.strip():
                                        periodo_id = adicionar_bloqueio_periodo(
                                            data_inicio_periodo.strftime("%Y-%m-%d"),
                                            data_fim_periodo.strftime("%Y-%m-%d"),
                                            descricao_periodo
                                        )
                                        
                                        if periodo_id:
                                            dias_total = (data_fim_periodo - data_inicio_periodo).days + 1
                                            st.success(f"✅ Período bloqueado com sucesso! ({dias_total} dias)")
                                            st.rerun()
                                        else:
                                            st.error("❌ Erro ao bloquear período.")
                                    else:
                                        st.warning("⚠️ Digite uma descrição para o período.")
                                else:
                                    st.warning("⚠️ Verifique se as datas estão corretas.")
                        
                        with col2:
                            st.markdown("**ℹ️ Vantagens dos Períodos:**")
                            st.success("""
                            ✅ **Organizado:** Um período = uma linha na lista
                            ✅ **Fácil remoção:** Exclui tudo de uma vez  
                            ✅ **Visual limpo:** Sem poluição na tela
                            ✅ **Informativo:** Mostra status e duração
                            """)
                        
                        # Lista de períodos bloqueados
                        st.markdown("---")
                        st.subheader("📋 Períodos Bloqueados")
                        
                        periodos = obter_bloqueios_periodos()
                        
                        if periodos:
                            for periodo in periodos:
                                periodo_id, data_inicio, data_fim, descricao, criado_em = periodo
                                
                                # Calcular informações do período
                                try:
                                    inicio_obj = datetime.strptime(data_inicio, "%Y-%m-%d")
                                    fim_obj = datetime.strptime(data_fim, "%Y-%m-%d")
                                    dias_total = (fim_obj - inicio_obj).days + 1
                                    
                                    inicio_formatado = inicio_obj.strftime("%d/%m/%Y")
                                    fim_formatado = fim_obj.strftime("%d/%m/%Y")
                                    
                                    # Verificar se período já passou, está ativo ou é futuro
                                    hoje = datetime.now().date()
                                    if fim_obj.date() < hoje:
                                        status_cor = "#6b7280"  # Cinza para passado
                                        status_texto = "Finalizado"
                                        status_icon = "✅"
                                    elif inicio_obj.date() <= hoje <= fim_obj.date():
                                        status_cor = "#f59e0b"  # Amarelo para ativo
                                        status_texto = "Ativo"
                                        status_icon = "🟡"
                                    else:
                                        status_cor = "#3b82f6"  # Azul para futuro
                                        status_texto = "Agendado"
                                        status_icon = "📅"
                                    
                                except:
                                    inicio_formatado = data_inicio
                                    fim_formatado = data_fim
                                    dias_total = "?"
                                    status_cor = "#6b7280"
                                    status_texto = "Indefinido"
                                    status_icon = "❓"
                                
                                col_info, col_btn = st.columns([5, 1])
                                
                                with col_info:
                                    st.markdown(f"""
                                    <div style="background: white; border-left: 4px solid {status_cor}; border-radius: 8px; padding: 1.5rem; margin: 1rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                            <h4 style="color: #1f2937; margin: 0; font-size: 1.1rem;">📆 {descricao}</h4>
                                            <span style="background: {status_cor}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.8rem; font-weight: 600;">
                                                {status_icon} {status_texto}
                                            </span>
                                        </div>
                                        <div style="color: #374151; font-size: 0.95rem; line-height: 1.4;">
                                            <strong>📅 Período:</strong> {inicio_formatado} até {fim_formatado}<br>
                                            <strong>📊 Duração:</strong> {dias_total} dia(s)
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                with col_btn:
                                    st.markdown("<br><br>", unsafe_allow_html=True)  # Espaçamento para alinhar
                                    if st.button("🗑️", key=f"remove_periodo_{periodo_id}", help="Remover período completo"):
                                        if remover_bloqueio_periodo(periodo_id):
                                            st.success(f"✅ Período '{descricao}' removido!")
                                            st.rerun()
                                        else:
                                            st.error("❌ Erro ao remover período.")
                        else:
                            st.info("📅 Nenhum período bloqueado.")
                    
                    with tab3:
                        st.subheader("🕐 Bloquear Horários Específicos")
                        
                        # Sub-abas para organizar melhor
                        subtab1, subtab2 = st.tabs(["📅 Por Data Específica", "📆 Por Dia da Semana"])
                        
                        # =====================================================
                        # SUBTAB 1: BLOQUEIO POR DATA ESPECÍFICA (código atual)
                        # =====================================================
                        with subtab1:
                            st.markdown("**📅 Bloqueio para uma data específica**")
                            
                            # Seleção de data
                            data_horario = st.date_input("Selecionar data:", min_value=datetime.today(), key="data_horario_especifico")
                            data_horario_str = data_horario.strftime("%Y-%m-%d")
                            
                            # Obter configurações de horários
                            horario_inicio_config = obter_configuracao("horario_inicio", "09:00")
                            horario_fim_config = obter_configuracao("horario_fim", "18:00")
                            intervalo_consultas = obter_configuracao("intervalo_consultas", 60)
                            
                            # Gerar horários possíveis
                            try:
                                hora_inicio = datetime.strptime(horario_inicio_config, "%H:%M").time()
                                hora_fim = datetime.strptime(horario_fim_config, "%H:%M").time()
                                
                                inicio_min = hora_inicio.hour * 60 + hora_inicio.minute
                                fim_min = hora_fim.hour * 60 + hora_fim.minute
                                
                                horarios_possiveis = []
                                horario_atual = inicio_min
                                
                                while horario_atual + intervalo_consultas <= fim_min:
                                    h = horario_atual // 60
                                    m = horario_atual % 60
                                    horarios_possiveis.append(f"{str(h).zfill(2)}:{str(m).zfill(2)}")
                                    horario_atual += intervalo_consultas
                                    
                            except:
                                horarios_possiveis = [f"{str(h).zfill(2)}:00" for h in range(9, 18)]
                            
                            # Verificar quais horários já estão bloqueados
                            bloqueios_dia = obter_bloqueios_horarios()
                            horarios_bloqueados_dia = [h for d, h in bloqueios_dia if d == data_horario_str]
                            
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
                                        if st.checkbox(f"🕐 {horario}", key=f"horario_especifico_{horario}"):
                                            horarios_selecionados.append(horario)
                            
                            # Botões de ação
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if st.button("🚫 Bloquear Horários Selecionados", type="primary", key="btn_bloquear_horarios_data"):
                                    if horarios_selecionados:
                                        bloqueados = 0
                                        for horario in horarios_selecionados:
                                            if adicionar_bloqueio_horario(data_horario_str, horario):
                                                bloqueados += 1
                                        
                                        if bloqueados > 0:
                                            st.success(f"✅ {bloqueados} horário(s) bloqueado(s) com sucesso!")
                                            st.rerun()
                                        else:
                                            st.warning("⚠️ Horários já estavam bloqueados.")
                                    else:
                                        st.warning("⚠️ Selecione pelo menos um horário para bloquear.")
                            
                            with col2:
                                if st.button("🔓 Desbloquear Todos os Horários do Dia", type="secondary", key="btn_desbloquear_dia_data"):
                                    if horarios_bloqueados_dia:
                                        for horario in horarios_bloqueados_dia:
                                            remover_bloqueio_horario(data_horario_str, horario)
                                        
                                        st.success(f"✅ Todos os horários do dia {data_horario.strftime('%d/%m/%Y')} foram desbloqueados!")
                                        st.rerun()
                                    else:
                                        st.info("ℹ️ Nenhum horário bloqueado neste dia.")
                        
                        # =====================================================
                        # SUBTAB 2: BLOQUEIO POR DIA DA SEMANA (NOVO)
                        # =====================================================
                        with subtab2:
                            st.markdown("**📆 Bloqueio recorrente por dia da semana**")
                            st.info("💡 Configure horários que ficam sempre bloqueados em determinados dias da semana (ex: sábados das 12h às 18h)")
                            
                            # Seleção do dia da semana
                            dias_opcoes = {
                                "Monday": "Segunda-feira",
                                "Tuesday": "Terça-feira", 
                                "Wednesday": "Quarta-feira",
                                "Thursday": "Quinta-feira",
                                "Friday": "Sexta-feira",
                                "Saturday": "Sábado",
                                "Sunday": "Domingo"
                            }
                            
                            dia_semana_selecionado = st.selectbox(
                                "Selecione o dia da semana:",
                                list(dias_opcoes.keys()),
                                format_func=lambda x: dias_opcoes[x],
                                key="dia_semana_bloqueio"
                            )
                            
                            # Obter horários possíveis (mesmo cálculo da outra aba)
                            horario_inicio_config = obter_configuracao("horario_inicio", "09:00")
                            horario_fim_config = obter_configuracao("horario_fim", "18:00")
                            intervalo_consultas = obter_configuracao("intervalo_consultas", 60)
                            
                            try:
                                hora_inicio = datetime.strptime(horario_inicio_config, "%H:%M").time()
                                hora_fim = datetime.strptime(horario_fim_config, "%H:%M").time()
                                
                                inicio_min = hora_inicio.hour * 60 + hora_inicio.minute
                                fim_min = hora_fim.hour * 60 + hora_fim.minute
                                
                                horarios_possiveis = []
                                horario_atual = inicio_min
                                
                                while horario_atual + intervalo_consultas <= fim_min:
                                    h = horario_atual // 60
                                    m = horario_atual % 60
                                    horarios_possiveis.append(f"{str(h).zfill(2)}:{str(m).zfill(2)}")
                                    horario_atual += intervalo_consultas
                                    
                            except:
                                horarios_possiveis = [f"{str(h).zfill(2)}:00" for h in range(9, 18)]
                            
                            st.markdown(f"**Selecione os horários para bloquear todas as {dias_opcoes[dia_semana_selecionado].lower()}:**")
                            
                            # Layout em colunas para os horários
                            cols = st.columns(4)
                            horarios_selecionados_semanal = []
                            
                            for i, horario in enumerate(horarios_possiveis):
                                with cols[i % 4]:
                                    if st.checkbox(f"🕐 {horario}", key=f"horario_semanal_{horario}"):
                                        horarios_selecionados_semanal.append(horario)
                            
                            # Descrição opcional
                            descricao_semanal = st.text_input(
                                "Descrição (opcional):",
                                placeholder=f"Ex: {dias_opcoes[dia_semana_selecionado]} - meio período",
                                key="desc_bloqueio_semanal"
                            )
                            
                            # Botão para salvar bloqueio semanal
                            if st.button("💾 Salvar Bloqueio Semanal", type="primary", key="btn_salvar_semanal"):
                                if horarios_selecionados_semanal:
                                    if adicionar_bloqueio_semanal(dia_semana_selecionado, horarios_selecionados_semanal, descricao_semanal):
                                        st.success(f"✅ Bloqueio semanal para {dias_opcoes[dia_semana_selecionado]} criado com sucesso!")
                                        st.rerun()
                                    else:
                                        st.warning("⚠️ Esse bloqueio semanal já existe ou ocorreu um erro.")
                                else:
                                    st.warning("⚠️ Selecione pelo menos um horário para bloquear.")
                            
                            # Lista de bloqueios semanais existentes
                            st.markdown("---")
                            st.subheader("📋 Bloqueios Semanais Ativos")
                            
                            bloqueios_semanais = obter_bloqueios_semanais()
                            
                            if bloqueios_semanais:
                                for bloqueio in bloqueios_semanais:
                                    bloqueio_id, dia_semana, horarios_str, descricao = bloqueio
                                    
                                    horarios_lista = horarios_str.split(",")
                                    horarios_texto = ", ".join(horarios_lista)
                                    
                                    col1, col2 = st.columns([4, 1])
                                    
                                    with col1:
                                        st.markdown(f"""
                                        <div style="background: #fef3c7; border: 1px solid #f59e0b; border-radius: 8px; padding: 1rem; margin: 0.5rem 0;">
                                            <h4 style="color: #92400e; margin: 0 0 0.5rem 0;">📅 {dias_opcoes[dia_semana]}</h4>
                                            <p style="margin: 0; color: #92400e;">
                                                <strong>Horários bloqueados:</strong> {horarios_texto}<br>
                                                {f'<strong>Descrição:</strong> {descricao}' if descricao else ''}
                                            </p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    
                                    with col2:
                                        if st.button("🗑️", key=f"remove_semanal_{bloqueio_id}", help="Remover bloqueio semanal"):
                                            if remover_bloqueio_semanal(bloqueio_id):
                                                st.success("Bloqueio semanal removido!")
                                                st.rerun()
                            else:
                                st.info("📅 Nenhum bloqueio semanal configurado.")
                        
                        # Lista de horários bloqueados por data específica
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
                    
                    with tab4:
                        st.subheader("⏰ Bloqueios Permanentes")
                        
                        st.markdown("""
                        <div style="background: #eff6ff; border: 1px solid #3b82f6; border-radius: 8px; padding: 1rem; margin: 1rem 0;">
                            ℹ️ <strong>Bloqueios Permanentes:</strong><br>
                            Configure horários que ficam sempre bloqueados (ex: almoço, intervalos, etc.)
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Formulário para novo bloqueio
                        st.markdown("### ➕ Criar Novo Bloqueio Permanente")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            horario_inicio_perm = st.time_input("Horário de início:", key="inicio_permanente")
                            
                        with col2:
                            horario_fim_perm = st.time_input("Horário de fim:", key="fim_permanente")
                        
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
                        dias_selecionados_perm = []
                        
                        for i, (dia_en, dia_pt) in enumerate(dias_opcoes.items()):
                            with cols[i % 4]:
                                if st.checkbox(dia_pt, key=f"dia_perm_{dia_en}"):
                                    dias_selecionados_perm.append(dia_en)
                        
                        # Descrição
                        descricao_perm = st.text_input("Descrição:", placeholder="Ex: Horário de Almoço", key="desc_permanente")
                        
                        # Botão para salvar
                        if st.button("💾 Salvar Bloqueio Permanente", type="primary", key="btn_salvar_permanente"):
                            if horario_inicio_perm and horario_fim_perm and dias_selecionados_perm and descricao_perm:
                                if horario_fim_perm > horario_inicio_perm:
                                    inicio_str = horario_inicio_perm.strftime("%H:%M")
                                    fim_str = horario_fim_perm.strftime("%H:%M")
                                    
                                    if adicionar_bloqueio_permanente(inicio_str, fim_str, dias_selecionados_perm, descricao_perm):
                                        st.success("✅ Bloqueio permanente criado com sucesso!")
                                        st.rerun()
                                    else:
                                        st.error("❌ Erro ao criar bloqueio.")
                                else:
                                    st.warning("⚠️ Horário de fim deve ser posterior ao horário de início.")
                            else:
                                st.warning("⚠️ Preencha todos os campos obrigatórios.")
                        
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
        
        elif opcao == "👥 Lista de Agendamentos":
            st.markdown('<div class="main-card fade-in">', unsafe_allow_html=True)
            st.markdown('<div class="card-header"><h2 class="card-title">👥 Lista de Agendamentos</h2></div>', unsafe_allow_html=True)
            
            # Botão de exportação
            st.markdown("---")
            col_export, col_info = st.columns([2, 3])
            
            
            if agendamentos:
                # Filtros avançados
                st.subheader("🔍 Filtros e Busca")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    filtro_data = st.selectbox(
                        "📅 Período:",
                        ["Todos", "Hoje", "Amanhã", "Esta Semana", "Próximos 7 dias", "Este Mês", "Próximo Mês", "Período Personalizado"],
                        help="Filtrar agendamentos por período"
                    )
                
                with col2:
                    filtro_status = st.selectbox(
                        "📊 Status:", 
                        ["Todos", "Pendentes", "Confirmados", "Atendidos", "Cancelados"],
                        help="Filtrar por status do agendamento"
                    )
                
                with col3:
                    busca_nome = st.text_input(
                        "👤 Buscar por nome:", 
                        placeholder="Digite o nome...",
                        help="Buscar agendamento por nome do cliente"
                    )
                
                with col4:
                    ordenacao = st.selectbox(
                        "📋 Ordenar por:",
                        ["Data (mais recente)", "Data (mais antiga)", "Nome (A-Z)", "Nome (Z-A)", "Status"],
                        help="Ordenar a lista de agendamentos"
                    )
                
                # Período personalizado
                if filtro_data == "Período Personalizado":
                    col1, col2 = st.columns(2)
                    with col1:
                        data_inicio_filtro = st.date_input("Data inicial:", value=datetime.today().date())
                    with col2:
                        data_fim_filtro = st.date_input("Data final:", value=datetime.today().date() + timedelta(days=30))
                
                # Aplicar filtros
                agendamentos_filtrados = agendamentos.copy()
                hoje = datetime.now().date()
                
                # Filtro por data
                if filtro_data == "Hoje":
                    agendamentos_filtrados = [a for a in agendamentos_filtrados if a[1] == hoje.strftime("%Y-%m-%d")]
                elif filtro_data == "Amanhã":
                    amanha = hoje + timedelta(days=1)
                    agendamentos_filtrados = [a for a in agendamentos_filtrados if a[1] == amanha.strftime("%Y-%m-%d")]
                elif filtro_data == "Esta Semana":
                    inicio_semana = hoje - timedelta(days=hoje.weekday())
                    fim_semana = inicio_semana + timedelta(days=6)
                    agendamentos_filtrados = [a for a in agendamentos_filtrados 
                                            if inicio_semana <= datetime.strptime(a[1], "%Y-%m-%d").date() <= fim_semana]
                elif filtro_data == "Próximos 7 dias":
                    proximos_7 = hoje + timedelta(days=7)
                    agendamentos_filtrados = [a for a in agendamentos_filtrados 
                                            if hoje <= datetime.strptime(a[1], "%Y-%m-%d").date() <= proximos_7]
                elif filtro_data == "Este Mês":
                    agendamentos_filtrados = [a for a in agendamentos_filtrados 
                                            if a[1].startswith(hoje.strftime("%Y-%m"))]
                elif filtro_data == "Próximo Mês":
                    proximo_mes = (hoje.replace(day=1) + timedelta(days=32)).replace(day=1)
                    agendamentos_filtrados = [a for a in agendamentos_filtrados 
                                            if a[1].startswith(proximo_mes.strftime("%Y-%m"))]
                elif filtro_data == "Período Personalizado":
                    agendamentos_filtrados = [a for a in agendamentos_filtrados 
                                            if data_inicio_filtro <= datetime.strptime(a[1], "%Y-%m-%d").date() <= data_fim_filtro]
                
                # Filtro por busca de nome
                if busca_nome:
                    agendamentos_filtrados = [a for a in agendamentos_filtrados 
                                            if busca_nome.lower() in a[3].lower()]
                
                # Filtro por status
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
                
                # Aplicar ordenação
                if ordenacao == "Data (mais recente)":
                    agendamentos_filtrados.sort(key=lambda x: (x[1], x[2]), reverse=True)
                elif ordenacao == "Data (mais antiga)":
                    agendamentos_filtrados.sort(key=lambda x: (x[1], x[2]))
                elif ordenacao == "Nome (A-Z)":
                    agendamentos_filtrados.sort(key=lambda x: x[3].lower())
                elif ordenacao == "Nome (Z-A)":
                    agendamentos_filtrados.sort(key=lambda x: x[3].lower(), reverse=True)
                elif ordenacao == "Status":
                    status_ordem = {"pendente": 1, "confirmado": 2, "atendido": 3, "cancelado": 4}
                    agendamentos_filtrados.sort(key=lambda x: status_ordem.get(x[6] if len(x) > 6 else "pendente", 5))
                
                # Estatísticas dos filtros
                st.markdown("---")
                col1, col2, col3, col4 = st.columns(4)
                
                pendentes = len([a for a in agendamentos_filtrados if len(a) > 6 and a[6] == "pendente"])
                confirmados = len([a for a in agendamentos_filtrados if len(a) > 6 and a[6] == "confirmado"])
                atendidos = len([a for a in agendamentos_filtrados if len(a) > 6 and a[6] == "atendido"])
                cancelados = len([a for a in agendamentos_filtrados if len(a) > 6 and a[6] == "cancelado"])
                
                with col1:
                    st.metric("⏳ Pendentes", pendentes)
                with col2:
                    st.metric("✅ Confirmados", confirmados)
                with col3:
                    st.metric("🎉 Atendidos", atendidos)
                with col4:
                    st.metric("❌ Cancelados", cancelados)
                
                st.markdown(f"**📊 Exibindo {len(agendamentos_filtrados)} de {len(agendamentos)} agendamento(s)**")
                
                # Lista de agendamentos com interface aprimorada
                st.markdown("---")
                st.subheader("📋 Agendamentos")
                
                if agendamentos_filtrados:
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
                        
                        # Definir configurações por status
                        status_config = {
                            'pendente': {
                                'icon': '⏳', 
                                'color': '#f59e0b', 
                                'bg_color': '#fef3c7',
                                'text': 'Aguardando Confirmação',
                                'actions': ['confirm', 'reject']
                            },
                            'confirmado': {
                                'icon': '✅', 
                                'color': '#3b82f6', 
                                'bg_color': '#dbeafe',
                                'text': 'Confirmado',
                                'actions': ['attend', 'cancel']
                            },
                            'atendido': {
                                'icon': '🎉', 
                                'color': '#10b981', 
                                'bg_color': '#d1fae5',
                                'text': 'Atendido',
                                'actions': ['delete']
                            },
                            'cancelado': {
                                'icon': '❌', 
                                'color': '#ef4444', 
                                'bg_color': '#fee2e2',
                                'text': 'Cancelado',
                                'actions': ['delete']
                            }
                        }
                        
                        config = status_config.get(status, status_config['pendente'])
                        
                        # Card do agendamento
                        col_info, col_actions = st.columns([4, 1])
                        
                        with col_info:
                            st.markdown(f"""
                            <div style="background: {config['bg_color']}; border-left: 4px solid {config['color']}; border-radius: 8px; padding: 1.5rem; margin: 1rem 0; transition: all 0.3s ease;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                                    <div style="font-size: 1.3rem; font-weight: 700; color: #1f2937;">
                                        {config['icon']} {nome}
                                    </div>
                                    <div style="color: {config['color']}; font-weight: 600; font-size: 1.1rem;">
                                        🕐 {horario}
                                    </div>
                                </div>
                                <div style="color: #374151; font-size: 1rem; line-height: 1.6;">
                                    📅 <strong>{data_formatada}</strong><br>
                                    📱 {telefone}<br>
                                    📧 {email}<br>
                                    <span style="background: {config['color']}; color: white; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; text-transform: uppercase; margin-top: 8px; display: inline-block;">
                                        {config['text']}
                                    </span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col_actions:
                            st.markdown("<br>", unsafe_allow_html=True)  # Espaçamento
                            
                            # Ações baseadas no status
                            if 'confirm' in config['actions']:
                                if st.button("✅ Confirmar", key=f"confirm_{agendamento_id}", help="Confirmar agendamento", use_container_width=True):
                                    atualizar_status_agendamento(agendamento_id, 'confirmado')
                                    st.success(f"✅ Agendamento de {nome} confirmado!")
                                    st.rerun()
                            
                            if 'reject' in config['actions']:
                                if st.button("❌ Recusar", key=f"reject_{agendamento_id}", help="Recusar agendamento", use_container_width=True):
                                    atualizar_status_agendamento(agendamento_id, 'cancelado')
                                    st.success(f"❌ Agendamento de {nome} recusado!")
                                    st.rerun()
                            
                            if 'attend' in config['actions']:
                                if st.button("🎉 Atender", key=f"attend_{agendamento_id}", help="Marcar como atendido", use_container_width=True):
                                    atualizar_status_agendamento(agendamento_id, 'atendido')
                                    st.success(f"🎉 {nome} marcado como atendido!")
                                    st.rerun()
                            
                            if 'cancel' in config['actions']:
                                if st.button("❌ Cancelar", key=f"cancel_{agendamento_id}", help="Cancelar agendamento", use_container_width=True):
                                    atualizar_status_agendamento(agendamento_id, 'cancelado')
                                    st.success(f"❌ Agendamento de {nome} cancelado!")
                                    st.rerun()
                            
                            if 'delete' in config['actions']:
                                if st.button("🗑️ Excluir", key=f"delete_{agendamento_id}", help="Excluir registro", use_container_width=True):
                                    if st.session_state.get(f"confirm_delete_{agendamento_id}", False):
                                        deletar_agendamento(agendamento_id)
                                        st.success(f"🗑️ Registro de {nome} excluído!")
                                        st.rerun()
                                    else:
                                        st.session_state[f"confirm_delete_{agendamento_id}"] = True
                                        st.warning("⚠️ Clique novamente para confirmar")
                else:
                    st.info("📅 Nenhum agendamento encontrado com os filtros aplicados.")
                
                # Ações em lote
                if agendamentos_filtrados:
                    st.markdown("---")
                    st.subheader("⚡ Ações em Lote")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("✅ Confirmar Todos os Pendentes", help="Confirma todos os agendamentos pendentes da lista filtrada"):
                            pendentes_ids = [a[0] for a in agendamentos_filtrados if len(a) > 6 and a[6] == "pendente"]
                            for agendamento_id in pendentes_ids:
                                atualizar_status_agendamento(agendamento_id, 'confirmado')
                            if pendentes_ids:
                                st.success(f"✅ {len(pendentes_ids)} agendamento(s) confirmado(s)!")
                                st.rerun()
                            else:
                                st.info("ℹ️ Nenhum agendamento pendente na lista atual.")
                    
                    with col2:
                        if st.button("🎉 Marcar Confirmados como Atendidos", help="Marca todos os confirmados como atendidos"):
                            confirmados_ids = [a[0] for a in agendamentos_filtrados if len(a) > 6 and a[6] == "confirmado"]
                            for agendamento_id in confirmados_ids:
                                atualizar_status_agendamento(agendamento_id, 'atendido')
                            if confirmados_ids:
                                st.success(f"🎉 {len(confirmados_ids)} agendamento(s) marcado(s) como atendido!")
                                st.rerun()
                            else:
                                st.info("ℹ️ Nenhum agendamento confirmado na lista atual.")
                    
                    with col3:
                        if st.button("🗑️ Limpar Cancelados Antigos", help="Remove registros cancelados com mais de 30 dias"):
                            data_limite = (hoje - timedelta(days=30)).strftime("%Y-%m-%d")
                            cancelados_antigos = [a[0] for a in agendamentos_filtrados 
                                                if len(a) > 6 and a[6] == "cancelado" and a[1] < data_limite]
                            for agendamento_id in cancelados_antigos:
                                deletar_agendamento(agendamento_id)
                            if cancelados_antigos:
                                st.success(f"🗑️ {len(cancelados_antigos)} registro(s) antigo(s) removido(s)!")
                                st.rerun()
                            else:
                                st.info("ℹ️ Nenhum cancelamento antigo para remover.")
                
            else:
                st.markdown("""
                <div style="background: #eff6ff; border: 1px solid #3b82f6; border-radius: 12px; padding: 2rem; text-align: center; margin: 2rem 0;">
                    <h3 style="color: #1d4ed8; margin-bottom: 1rem;">📅 Nenhum agendamento encontrado</h3>
                    <p style="color: #1e40af; margin-bottom: 1.5rem;">
                        Os agendamentos aparecerão aqui conforme forem sendo realizados pelos clientes.
                    </p>
                    <p style="color: #64748b; font-size: 0.9rem;">
                        💡 <strong>Dica:</strong> Compartilhe o link do sistema com seus clientes para começar a receber agendamentos!
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

        elif opcao == "💾 Backup & Restauração":
            st.markdown('<div class="main-card fade-in">', unsafe_allow_html=True)
            st.markdown('<div class="card-header"><h2 class="card-title">💾 Backup & Restauração</h2></div>', unsafe_allow_html=True)
            
            # Informações gerais
            st.info("""
            🛡️ **Centro de Backup e Restauração**
            
            Mantenha seus dados sempre seguros com nosso sistema completo de backup e restauração.
            Exporte seus agendamentos, configure backups automáticos e restaure dados quando necessário.
            """)
            
            # Separar em tabs para melhor organização
            tab_export, tab_import, tab_auto = st.tabs(["📤 Exportar Dados", "📥 Importar Dados", "🔄 Backup Automático"])

            # ============================================
            # ABA 1: EXPORTAR DADOS
            # ============================================
            
            with tab_export:
                st.subheader("📤 Exportar Agendamentos")
                
                col_info, col_action = st.columns([2, 1])
                
                with col_info:
                    st.markdown("""
                    **📋 O que será exportado:**
                    • Todos os agendamentos (confirmados, pendentes, atendidos, cancelados)
                    • Informações completas: nome, telefone, email, data, horário, status
                    • Formato CSV compatível com Excel e outras planilhas
                    • Dados organizados cronologicamente
                    """)
                
                with col_action:
                    if st.button("📥 Gerar Backup CSV", 
                                type="primary",
                                use_container_width=True,
                                help="Baixar todos os agendamentos em formato CSV"):
                        
                        csv_data = exportar_agendamentos_csv()
                        
                        if csv_data:
                            # Gerar nome do arquivo com data atual
                            from datetime import datetime
                            data_atual = datetime.now().strftime("%Y%m%d_%H%M%S")
                            nome_arquivo = f"agendamentos_backup_{data_atual}.csv"
                            
                            # Estatísticas
                            total_agendamentos = len(buscar_agendamentos())
                            tamanho_kb = len(csv_data.encode('utf-8')) / 1024
                            
                            st.success(f"✅ Backup gerado com sucesso!")
                            
                            # Métricas do backup
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("📊 Total de Registros", total_agendamentos)
                            with col2:
                                st.metric("📏 Tamanho", f"{tamanho_kb:.1f} KB")
                            with col3:
                                st.metric("📅 Data/Hora", datetime.now().strftime("%d/%m %H:%M"))
                            
                            # Botão de download
                            st.download_button(
                                label="⬇️ Baixar Arquivo de Backup",
                                data=csv_data,
                                file_name=nome_arquivo,
                                mime="text/csv",
                                use_container_width=True,
                                type="primary"
                            )
                            
                            st.info(f"💾 **Arquivo:** {nome_arquivo}")
                            
                        else:
                            st.warning("⚠️ Nenhum agendamento encontrado para exportar")
                
                # Instruções
                with st.expander("ℹ️ Como usar o arquivo de backup"):
                    st.markdown("""
                    **📖 Instruções de uso:**
                    
                    1. **💾 Salvar arquivo:** Guarde o arquivo CSV em local seguro
                    2. **📁 Organização:** Recomendamos criar uma pasta "Backups_Agendamento"
                    3. **📊 Abrir no Excel:** O arquivo abre diretamente no Excel ou Google Sheets
                    4. **🔄 Restaurar:** Use a aba "Importar Dados" para restaurar os agendamentos
                    5. **⏰ Frequência:** Recomendamos backup semanal ou antes de mudanças importantes
                    
                    **🔒 Segurança:**
                    • O arquivo contém dados pessoais dos clientes
                    • Mantenha-o em local seguro e protegido
                    • Não compartilhe sem necessidade
                    """)
            
            # ============================================
            # ABA 2: IMPORTAR DADOS
            # ============================================
            
            with tab_import:
                st.subheader("📥 Restaurar Agendamentos")
                
                col_info_import, col_upload = st.columns([2, 3])

                with col_info_import:
                    st.markdown("""
                    **📂 Restaurar Backup:**
                    
                    • Importe um arquivo CSV exportado anteriormente
                    • Formato deve ser idêntico ao exportado
                    • Duplicatas serão ignoradas automaticamente
                    • Colunas obrigatórias: ID, Data, Horário, Nome, Telefone
                    """)
                    
                    st.warning("""
                    ⚠️ **Atenção:**
                    Esta operação irá adicionar os agendamentos do arquivo ao sistema atual.
                    Agendamentos duplicados serão ignorados automaticamente.
                    """)

                with col_upload:
                    uploaded_file = st.file_uploader(
                        "Escolha um arquivo CSV de backup:",
                        type=['csv'],
                        help="Selecione um arquivo CSV exportado anteriormente do sistema"
                    )
                    
                    if uploaded_file is not None:
                        # Mostrar informações do arquivo
                        file_size = uploaded_file.size
                        st.info(f"📄 **Arquivo:** {uploaded_file.name} ({file_size} bytes)")
                        
                        if st.button("📤 Restaurar Dados do Backup", 
                                    type="primary", 
                                    use_container_width=True):
                            
                            # Ler conteúdo do arquivo
                            csv_content = uploaded_file.getvalue().decode('utf-8')
                            
                            # Importar dados
                            resultado = importar_agendamentos_csv(csv_content)
                            
                            if resultado['sucesso']:
                                st.success("🎉 Restauração realizada com sucesso!")
                                
                                # Mostrar estatísticas sem colunas aninhadas
                                if resultado['importados'] > 0:
                                    st.info(f"✅ **{resultado['importados']}** agendamento(s) restaurado(s)")
                                
                                if resultado['duplicados'] > 0:
                                    st.warning(f"⚠️ **{resultado['duplicados']}** registro(s) já existiam (ignorados)")
                                
                                if resultado['erros'] > 0:
                                    st.error(f"❌ **{resultado['erros']}** registro(s) com erro nos dados")
                                
                                # Atualizar a página para mostrar os novos dados
                                if resultado['importados'] > 0:
                                    st.balloons()
                                    st.rerun()
                                    
                            else:
                                st.error(f"❌ Erro na restauração: {resultado.get('erro', 'Erro desconhecido')}")
                
                # Formato esperado
                with st.expander("📋 Formato esperado do arquivo CSV"):
                    st.code("""
        ID,Data,Horário,Nome,Telefone,Email,Status
        1,2024-12-20,09:00,João Silva,(11) 99999-9999,joao@email.com,confirmado
        2,2024-12-20,10:00,Maria Santos,(11) 88888-8888,maria@email.com,pendente
        3,2024-12-21,14:00,Pedro Costa,(11) 77777-7777,pedro@email.com,atendido
                    """, language="csv")
                    
                    st.markdown("""
                    **📝 Observações importantes:**
                    - Use exatamente os mesmos cabeçalhos mostrados acima
                    - Formato de data: AAAA-MM-DD (ex: 2024-12-20)
                    - Formato de horário: HH:MM (ex: 09:00)
                    - Status válidos: pendente, confirmado, atendido, cancelado
                    - Email é opcional (pode ficar em branco)
                    - ID será ignorado (sistema gera automaticamente)
                    """)
            
            # ============================================
            # ABA 3: BACKUP AUTOMÁTICO (placeholder)
            # ============================================
            
            with tab_auto:
                interface_backup_email()

            st.markdown('</div>', unsafe_allow_html=True)

else:
    # INTERFACE DO CLIENTE
    # Obter configurações dinâmicas atualizadas
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

    st.markdown(f"""
    <div class="main-header">
        <h1>⏳ Agendamento Online</h1>
        <p>Agende seu horário com {nome_profissional} - {especialidade}</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        
        tab_agendar, tab_cancelar = st.tabs(["📅 Agendar Horário", "❌ Cancelar Agendamento"])
        
        with tab_agendar:
            # Obter configurações dinâmicas para agendamento
            hoje = datetime.today()
            dias_futuros_config = obter_configuracao("dias_futuros", 30)
            antecedencia_minima = obter_configuracao("antecedencia_minima", 2)
            horario_inicio = obter_configuracao("horario_inicio", "09:00")
            horario_fim = obter_configuracao("horario_fim", "18:00")
            intervalo_consultas = obter_configuracao("intervalo_consultas", 60)  # AGORA USA A CONFIGURAÇÃO!
            
            dias_uteis = obter_dias_uteis()
            datas_bloqueadas = obter_datas_bloqueadas()
            datas_bloqueadas_dt = [datetime.strptime(d, "%Y-%m-%d").date() for d in datas_bloqueadas]
            
            agora = datetime.now()
            data_limite_antecedencia = agora + timedelta(hours=antecedencia_minima)
            
            datas_validas = []
            for i in range(1, dias_futuros_config + 1):
                data = hoje + timedelta(days=i)
                dia_semana = data.strftime("%A")
                data_str = data.strftime("%Y-%m-%d")  # Formato para verificar períodos
                
                # Verificar todas as condições:
                # 1. Dia da semana permitido
                # 2. Não está na lista de bloqueios individuais  
                # 3. Não está em nenhum período bloqueado
                # 4. Respeita antecedência mínima
                if (dia_semana in dias_uteis and 
                    data.date() not in datas_bloqueadas_dt and 
                    not data_em_periodo_bloqueado(data_str) and  # NOVA VERIFICAÇÃO!
                    data.date() > data_limite_antecedencia.date()):
                    datas_validas.append(data.date())
            
            if not datas_validas:
                st.warning("⚠️ Nenhuma data disponível no momento.")
            else:
                st.subheader("📋 Dados do Cliente")
                
                nome = st.text_input("Nome completo *", placeholder="Digite seu nome")
                
                telefone = st.text_input("Telefone *", placeholder="(11) 99999-9999")
                
                email = st.text_input("E-mail *", placeholder="seu@email.com")
                
                st.subheader("📅 Escolha a Data")
                # Substitua a seção do calendário (a partir de "st.subheader("📅 Escolha a Data")") por este código:

                
                # Inicializar estado do calendário
                if 'data_selecionada_cal' not in st.session_state:
                    st.session_state.data_selecionada_cal = datas_validas[0] if datas_validas else None

                if 'mes_atual' not in st.session_state:
                    hoje = datetime.now()
                    st.session_state.mes_atual = hoje.month
                    st.session_state.ano_atual = hoje.year

                # Criar lista de meses disponíveis
                meses_disponiveis = {}
                for data in datas_validas:
                    chave_mes = f"{data.year}-{data.month:02d}"
                    nome_mes = f"{calendar.month_name[data.month]} {data.year}"
                    if chave_mes not in meses_disponiveis:
                        meses_disponiveis[chave_mes] = nome_mes

                # Navegação entre meses
                col_prev, col_mes, col_next = st.columns([1, 3, 1])

                with col_prev:
                    if st.button("◀️", key="prev_month", help="Mês anterior"):
                        chave_atual = f"{st.session_state.ano_atual}-{st.session_state.mes_atual:02d}"
                        chaves_ordenadas = sorted(meses_disponiveis.keys())
                        try:
                            indice_atual = chaves_ordenadas.index(chave_atual)
                            if indice_atual > 0:
                                nova_chave = chaves_ordenadas[indice_atual - 1]
                                ano, mes = nova_chave.split("-")
                                st.session_state.ano_atual = int(ano)
                                st.session_state.mes_atual = int(mes)
                                st.rerun()
                        except ValueError:
                            pass

                with col_mes:
                    st.markdown(f"""
                    <div style="text-align: center; font-size: 1.1rem; font-weight: 600; color: #1f2937; padding: 0.5rem;">
                        📅 {calendar.month_name[st.session_state.mes_atual]} {st.session_state.ano_atual}
                    </div>
                    """, unsafe_allow_html=True)

                with col_next:
                    if st.button("▶️", key="next_month", help="Próximo mês"):
                        chave_atual = f"{st.session_state.ano_atual}-{st.session_state.mes_atual:02d}"
                        chaves_ordenadas = sorted(meses_disponiveis.keys())
                        try:
                            indice_atual = chaves_ordenadas.index(chave_atual)
                            if indice_atual < len(chaves_ordenadas) - 1:
                                nova_chave = chaves_ordenadas[indice_atual + 1]
                                ano, mes = nova_chave.split("-")
                                st.session_state.ano_atual = int(ano)
                                st.session_state.mes_atual = int(mes)
                                st.rerun()
                        except ValueError:
                            pass

                # Forçar colunas a não empilhar usando CSS
                st.markdown("""
                <style>
                /* Forçar TODAS as colunas do Streamlit a ficarem lado a lado no calendário */
                div[data-testid="stHorizontalBlock"] {
                    display: flex !important;
                    flex-direction: row !important;
                    flex-wrap: nowrap !important;
                    gap: 2px !important;
                    width: 100% !important;
                }

                div[data-testid="stHorizontalBlock"] > div {
                    flex: 1 1 14.28% !important;
                    max-width: 14.28% !important;
                    min-width: 0 !important;
                    padding: 0 1px !important;
                }

                /* Forçar também pela classe */
                .row-widget.stColumns {
                    display: flex !important;
                    flex-direction: row !important;
                    flex-wrap: nowrap !important;
                    gap: 2px !important;
                    width: 100% !important;
                }

                .row-widget.stColumns > div {
                    flex: 1 1 14.28% !important;
                    max-width: 14.28% !important;
                    min-width: 0 !important;
                    padding: 0 1px !important;
                }

                /* Prevenir quebra em qualquer nível */
                div[data-testid="column"] {
                    flex: 1 1 14.28% !important;
                    max-width: 14.28% !important;
                    min-width: 0 !important;
                }

                /* Container do calendário */
                .calendar-container {
                    width: 100%;
                    max-width: 400px;
                    margin: 1rem auto;
                    background: white;
                    border-radius: 12px;
                    padding: 0.5rem;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }

                /* Ajustar botões para serem menores em mobile */
                .stButton > button {
                    width: 100% !important;
                    padding: 0.25rem !important;
                    min-height: 2rem !important;
                    font-size: 0.8rem !important;
                    margin: 1px 0 !important;
                }

                /* Em telas muito pequenas, ajustar ainda mais */
                @media (max-width: 400px) {
                    .stButton > button {
                        font-size: 0.75rem !important;
                        padding: 0.2rem !important;
                        min-height: 1.8rem !important;
                    }
                    
                    .calendar-container {
                        padding: 0.3rem;
                    }
                }

                /* Forçar layout horizontal mesmo em mobile */
                @media (max-width: 768px) {
                    div[data-testid="stHorizontalBlock"] {
                        display: flex !important;
                        flex-direction: row !important;
                    }
                    
                    div[data-testid="column"] {
                        flex: 1 1 14.28% !important;
                        max-width: 14.28% !important;
                    }
                }
                </style>
                """, unsafe_allow_html=True)

                # Container do calendário
                st.markdown('<div class="calendar-container">', unsafe_allow_html=True)

                # Gerar calendário do mês
                cal = calendar.monthcalendar(st.session_state.ano_atual, st.session_state.mes_atual)

                # Dias da semana - bem curtos para mobile
                st.markdown("""
                <div style="display: flex; gap: 2px; margin-bottom: 6px;">
                    <div style="flex: 1; text-align: center; font-size: 0.8rem; font-weight: 700; color: #374151; background: #f1f5f9; padding: 6px 3px; border-radius: 4px; border: 1px solid #e2e8f0;">SEG</div>
                    <div style="flex: 1; text-align: center; font-size: 0.8rem; font-weight: 700; color: #374151; background: #f1f5f9; padding: 6px 3px; border-radius: 4px; border: 1px solid #e2e8f0;">TER</div>
                    <div style="flex: 1; text-align: center; font-size: 0.8rem; font-weight: 700; color: #374151; background: #f1f5f9; padding: 6px 3px; border-radius: 4px; border: 1px solid #e2e8f0;">QUA</div>
                    <div style="flex: 1; text-align: center; font-size: 0.8rem; font-weight: 700; color: #374151; background: #f1f5f9; padding: 6px 3px; border-radius: 4px; border: 1px solid #e2e8f0;">QUI</div>
                    <div style="flex: 1; text-align: center; font-size: 0.8rem; font-weight: 700; color: #374151; background: #f1f5f9; padding: 6px 3px; border-radius: 4px; border: 1px solid #e2e8f0;">SEX</div>
                    <div style="flex: 1; text-align: center; font-size: 0.8rem; font-weight: 700; color: #374151; background: #f1f5f9; padding: 6px 3px; border-radius: 4px; border: 1px solid #e2e8f0;">SAB</div>
                    <div style="flex: 1; text-align: center; font-size: 0.8rem; font-weight: 700; color: #374151; background: #f1f5f9; padding: 6px 3px; border-radius: 4px; border: 1px solid #e2e8f0;">DOM</div>
                </div>
                """, unsafe_allow_html=True)

                # Gerar cada semana do calendário
                for semana_idx, semana in enumerate(cal):
                    cols = st.columns(7)
                    for dia_idx, dia in enumerate(semana):
                        with cols[dia_idx]:
                            if dia == 0:
                                # Célula vazia
                                st.markdown('<div style="height: 2rem;"></div>', unsafe_allow_html=True)
                            else:
                                # Verificar se data está disponível
                                try:
                                    data_atual = datetime(st.session_state.ano_atual, st.session_state.mes_atual, dia).date()
                                    data_disponivel = data_atual in datas_validas
                                    data_selecionada_atual = st.session_state.data_selecionada_cal == data_atual
                                    
                                    if data_disponivel:
                                        # Data disponível - botão clicável
                                        button_type = "primary" if data_selecionada_atual else "secondary"
                                        
                                        if st.button(
                                            str(dia),
                                            key=f"cal_{semana_idx}_{dia_idx}_{dia}",
                                            type=button_type,
                                            use_container_width=True
                                        ):
                                            st.session_state.data_selecionada_cal = data_atual
                                            st.rerun()
                                    else:
                                        # Data indisponível
                                        st.markdown(f"""
                                        <div style="
                                            height: 2rem; 
                                            display: flex; 
                                            align-items: center; 
                                            justify-content: center;
                                            color: #cbd5e1;
                                            font-size: 0.8rem;
                                        ">{dia}</div>
                                        """, unsafe_allow_html=True)
                                        
                                except ValueError:
                                    st.markdown('<div style="height: 2rem;"></div>', unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

                # Mostrar data selecionada
                if st.session_state.data_selecionada_cal:
                    data_formatada = st.session_state.data_selecionada_cal.strftime("%A, %d de %B de %Y").replace("Monday", "Segunda-feira")\
                        .replace("Tuesday", "Terça-feira").replace("Wednesday", "Quarta-feira")\
                        .replace("Thursday", "Quinta-feira").replace("Friday", "Sexta-feira")\
                        .replace("Saturday", "Sábado").replace("Sunday", "Domingo")\
                        .replace("January", "Janeiro").replace("February", "Fevereiro").replace("March", "Março")\
                        .replace("April", "Abril").replace("May", "Maio").replace("June", "Junho")\
                        .replace("July", "Julho").replace("August", "Agosto").replace("September", "Setembro")\
                        .replace("October", "Outubro").replace("November", "Novembro").replace("December", "Dezembro")
                    
                    st.success(f"📅 **Data selecionada:** {data_formatada}")

                # Definir data selecionada para o resto do código
                data_selecionada = st.session_state.data_selecionada_cal
                
                if data_selecionada:
                    st.subheader("⏰ Horários Disponíveis")
                    
                    data_str = data_selecionada.strftime("%Y-%m-%d")
                    
                    # Gerar horários baseados nas configurações ATUALIZADAS
                    try:
                        hora_inicio = datetime.strptime(horario_inicio, "%H:%M").time()
                        hora_fim = datetime.strptime(horario_fim, "%H:%M").time()
                        
                        inicio_min = hora_inicio.hour * 60 + hora_inicio.minute
                        fim_min = hora_fim.hour * 60 + hora_fim.minute
                        
                        horarios_possiveis = []
                        horario_atual = inicio_min
                        
                        # USAR O INTERVALO CONFIGURADO!
                        while horario_atual + intervalo_consultas <= fim_min:
                            h = horario_atual // 60
                            m = horario_atual % 60
                            horarios_possiveis.append(f"{str(h).zfill(2)}:{str(m).zfill(2)}")
                            horario_atual += intervalo_consultas
                            
                    except:
                        horarios_possiveis = [f"{str(h).zfill(2)}:00" for h in range(9, 18)]
                    
                    horarios_disponiveis = [h for h in horarios_possiveis if horario_disponivel(data_str, h)]
                    
                    if horarios_disponiveis:
                        horario = st.selectbox("Escolha o horário:", horarios_disponiveis)
                        
                        if horario and nome and telefone and email:
                            email_valido = "@" in email and "." in email.split("@")[-1]
                            
                            if not email_valido:
                                st.warning("⚠️ Digite um e-mail válido.")
                            else:
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
                                        <span>👨‍⚕️ Profissional:</span>
                                        <strong>{nome_profissional}</strong>
                                    </div>
                                    <div class="summary-item">
                                        <span>🏥 Local:</span>
                                        <strong>{nome_clinica}</strong>
                                    </div>
                                    <div class="summary-item">
                                        <span>📍 Endereço:</span>
                                        <strong>{endereco_completo}</strong>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Mostrar instruções se existirem
                                if instrucoes_chegada:
                                    st.markdown(f"""
                                    <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 1rem; margin: 1rem 0; border-radius: 8px;">
                                        <strong>📝 Instruções importantes:</strong><br>
                                        {instrucoes_chegada}
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                if st.button("✅ Confirmar Agendamento", type="primary", use_container_width=True):
                                    try:
                                        status_inicial = adicionar_agendamento(nome, telefone, email, data_str, horario)
                                        
                                        if status_inicial == "confirmado":
                                            st.success("✅ Agendamento confirmado automaticamente!")
                                        else:
                                            st.success("✅ Agendamento solicitado! Aguarde confirmação.")
                                        
                                        st.info(f"💡 Seu agendamento: {data_selecionada.strftime('%d/%m/%Y')} às {horario}")
                                        
                                        # Mostrar informações de contato
                                        st.markdown(f"""
                                        <div style="background: #ecfdf5; border-left: 4px solid #10b981; padding: 1rem; margin: 1rem 0; border-radius: 8px;">
                                            <strong>📞 Em caso de dúvidas:</strong><br>
                                            📱 Telefone: {telefone_contato}<br>
                                            💬 WhatsApp: {whatsapp}
                                        </div>
                                        """, unsafe_allow_html=True)
                                        
                                    except Exception as e:
                                        st.error(f"❌ Erro ao agendar: {str(e)}")
                        
                        elif nome or telefone or email:
                            campos_faltando = []
                            if not nome: campos_faltando.append("Nome")
                            if not telefone: campos_faltando.append("Telefone") 
                            if not email: campos_faltando.append("E-mail")
                            
                            if campos_faltando:
                                st.info(f"📝 Para continuar, preencha: {', '.join(campos_faltando)}")
                    else:
                        st.warning("⚠️ Nenhum horário disponível para esta data.")
        
        with tab_cancelar:
            st.subheader("❌ Cancelar Agendamento")
            
            st.info("ℹ️ Informe os mesmos dados utilizados no agendamento.")
            
            nome_cancel = st.text_input(
                "Nome cadastrado:",
                placeholder="Digite o nome usado no agendamento",
                help="Informe exatamente o mesmo nome usado no agendamento"
            )
            
            telefone_cancel = st.text_input(
                "Telefone cadastrado:",
                placeholder="(11) 99999-9999",
                help="Informe exatamente o mesmo telefone usado no agendamento"
            )
            
            data_cancel = st.date_input(
                "Data do agendamento:",
                min_value=datetime.today().date(),
                help="Selecione a data do agendamento que deseja cancelar"
            )
            
            if st.button("🗑️ Cancelar Agendamento", type="secondary", use_container_width=True):
                if nome_cancel and telefone_cancel and data_cancel:
                    data_str = data_cancel.strftime("%Y-%m-%d")
                    sucesso = cancelar_agendamento(nome_cancel, telefone_cancel, data_str)
                    
                    if sucesso:
                        st.success("✅ Agendamento cancelado com sucesso!")
                    else:
                        st.error("❌ Agendamento não encontrado! Verifique os dados.")
                else:
                    st.warning("⚠️ Preencha todos os campos.")
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Footer dinâmico com configurações atualizadas
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem; color: rgba(102, 126, 234, 0.8);">
        <h3 style="color: #1f2937; margin-bottom: 1rem;">{nome_profissional}</h3>
        <p style="color: #6b7280; margin-bottom: 0.5rem;"><strong>{especialidade}</strong></p>
        <p><strong>{nome_clinica}</strong></p>
        <p>📍 {endereco_completo}</p>
        <div style="margin: 1rem 0;">
            <p>📞 {telefone_contato} | 💬 WhatsApp: {whatsapp}</p>
        </div>
        <hr style="margin: 1.5rem 0; border: none; height: 1px; background: #e9ecef;">
        <p>💡 <strong>Dica:</strong> Mantenha seus dados atualizados</p>
        <p style="font-size: 0.9rem; opacity: 0.7;">Sistema de Agendamento Online</p>
    </div>
    """, unsafe_allow_html=True)
