import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Verificar se é modo admin através do parâmetro da URL
# Compatibilidade com Streamlit Cloud e versões locais
try:
    # Streamlit versão mais nova (local)
    query_params = st.query_params
    admin_param = query_params.get("admin", "")
    is_admin = admin_param == "Rota@717"
except:
    try:
        # Streamlit Cloud (versão mais antiga)
        query_params = st.experimental_get_query_params()
        admin_param = query_params.get("admin", [""])[0]
        is_admin = admin_param == "Rota@717"
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
try:
    SENHA_CORRETA = st.secrets["ADMIN_PASSWORD"]
except:
    SENHA_CORRETA = "admin123"

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
                    st.error("❌ Senha incorreta!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Interface administrativa autenticada
        with st.sidebar:
            st.markdown("### 🔧 Menu Administrativo")
            if st.button("🚪 Sair", use_container_width=True):
                st.session_state.authenticated = False
                st.rerun()
            
            st.markdown("---")
            opcao = st.selectbox(
                "Escolha uma opção:",
                ["⚙️ Configurações Gerais", "📅 Configurar Agenda", "🗓️ Gerenciar Bloqueios", "👥 Lista de Agendamentos"]
            )
        
        # Instrução simples para reabrir menu (sem botão problemático)
        st.markdown("""
        <div style="position: fixed; top: 10px; left: 10px; background: rgba(102, 126, 234, 0.9); color: white; padding: 5px 10px; border-radius: 5px; font-size: 12px; z-index: 1000;">
            💡 Menu sumiu? Tecle <strong>Ctrl+Shift+M</strong> (ou Cmd+Shift+M no Mac)
        </div>
        """, unsafe_allow_html=True)
        
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
                        help="Tempo mínimo necessário entre o agendamento e a consulta"
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
                
                # Configurações de limite
                st.markdown("---")
                st.markdown("**⚠️ Limites e Restrições**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    max_agendamentos_dia = st.number_input(
                        "Máximo de agendamentos por dia:",
                        min_value=1,
                        max_value=50,
                        value=obter_configuracao("max_agendamentos_dia", 20),
                        help="Limite máximo de agendamentos aceitos por dia"
                    )
                
                with col2:
                    permitir_feriados = st.checkbox(
                        "Permitir agendamentos em feriados",
                        value=obter_configuracao("permitir_feriados", False),
                        help="Se desativado, feriados nacionais serão automaticamente bloqueados"
                    )
            
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
                        
                        porta_smtp = st.number_input(
                            "Porta SMTP:",
                            value=obter_configuracao("porta_smtp", 587),
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
                        
                        enviar_lembrete = st.checkbox(
                            "Enviar lembrete 24h antes",
                            value=obter_configuracao("enviar_lembrete", False),
                            help="Envia lembrete automático um dia antes do agendamento"
                        )
                    
                    with col2:
                        enviar_cancelamento = st.checkbox(
                            "Enviar email de cancelamento",
                            value=obter_configuracao("enviar_cancelamento", True),
                            help="Envia email quando agendamento é cancelado"
                        )
                        
                        enviar_reagendamento = st.checkbox(
                            "Enviar email de reagendamento",
                            value=obter_configuracao("enviar_reagendamento", False),
                            help="Envia email quando agendamento é alterado"
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
                salvar_configuracao("max_agendamentos_dia", max_agendamentos_dia)
                salvar_configuracao("permitir_feriados", permitir_feriados)
                
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
                salvar_configuracao("email_teste", email_teste if envio_automatico else "")
                if envio_automatico:
                    salvar_configuracao("email_sistema", email_sistema)
                    salvar_configuracao("senha_email", senha_email)
                    salvar_configuracao("servidor_smtp", servidor_smtp)
                    salvar_configuracao("porta_smtp", porta_smtp)
                    salvar_configuracao("enviar_confirmacao", enviar_confirmacao)
                    salvar_configuracao("enviar_lembrete", enviar_lembrete)
                    salvar_configuracao("enviar_cancelamento", enviar_cancelamento)
                    salvar_configuracao("enviar_reagendamento", enviar_reagendamento)
                    salvar_configuracao("template_confirmacao", template_confirmacao)
                
                st.success("✅ Todas as configurações foram salvas com sucesso!")
                
                # Mostrar resumo
                st.markdown("**📋 Resumo das configurações salvas:**")
                st.info(f"""
                📅 **Agendamento:** {intervalo_selecionado} de {horario_inicio.strftime('%H:%M')} às {horario_fim.strftime('%H:%M')}
                ⏰ **Antecedência:** {antecedencia_selecionada}
                🔄 **Confirmação:** {'Automática' if confirmacao_automatica else 'Manual'}
                📧 **Email:** {'Ativado' if envio_automatico else 'Desativado'}
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
            tab1, tab2, tab3 = st.tabs(["📅 Bloquear Dias Inteiros", "🕐 Bloquear Horários Específicos", "⏰ Bloqueios Permanentes"])
            
            with tab1:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📌 Bloquear Data")
                    data_bloqueio = st.date_input("Data para bloquear:", min_value=datetime.today())
                    
                    if st.button("🚫 Bloquear Dia Inteiro", type="primary", key="btn_bloquear_dia"):
                        if adicionar_bloqueio(data_bloqueio.strftime("%Y-%m-%d")):
                            st.success("✅ Dia bloqueado!")
                            st.rerun()
                        else:
                            st.warning("⚠️ Data já bloqueada.")
                
                with col2:
                    st.subheader("📋 Bloquear Período")
                    data_inicio = st.date_input("Data inicial:", min_value=datetime.today(), key="data_inicio_periodo")
                    data_fim = st.date_input("Data final:", min_value=data_inicio, key="data_fim_periodo")
                    
                    if st.button("🚫 Bloquear Período", type="primary", key="btn_bloquear_periodo"):
                        if data_fim >= data_inicio:
                            dias_bloqueados = 0
                            for i in range((data_fim - data_inicio).days + 1):
                                data = (data_inicio + timedelta(days=i)).strftime("%Y-%m-%d")
                                if adicionar_bloqueio(data):
                                    dias_bloqueados += 1
                            
                            st.success(f"✅ {dias_bloqueados} dias foram bloqueados!")
                            st.rerun()
                        else:
                            st.error("❌ Data final deve ser posterior à data inicial.")
                
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
                    st.info("📅 Nenhum dia inteiro bloqueado atualmente.")
            
            with tab2:
                st.subheader("🕐 Bloquear Horários Específicos")
                
                # Seleção de data
                data_horario = st.date_input("Selecionar data:", min_value=datetime.today(), key="data_horario_especifico")
                data_horario_str = data_horario.strftime("%Y-%m-%d")
                
                # Obter configurações de horários
                horario_inicio_config = obter_configuracao("horario_inicio", "09:00")
                horario_fim_config = obter_configuracao("horario_fim", "18:00")
                
                # Gerar horários possíveis
                try:
                    hora_inicio = datetime.strptime(horario_inicio_config, "%H:%M").time()
                    hora_fim = datetime.strptime(horario_fim_config, "%H:%M").time()
                    
                    inicio_min = hora_inicio.hour * 60 + hora_inicio.minute
                    fim_min = hora_fim.hour * 60 + hora_fim.minute
                    
                    horarios_possiveis = []
                    horario_atual = inicio_min
                    
                    while horario_atual + 60 <= fim_min:
                        h = horario_atual // 60
                        m = horario_atual % 60
                        horarios_possiveis.append(f"{str(h).zfill(2)}:{str(m).zfill(2)}")
                        horario_atual += 60
                        
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
                    if st.button("🚫 Bloquear Horários Selecionados", type="primary", key="btn_bloquear_horarios"):
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
                    if st.button("🔓 Desbloquear Todos os Horários do Dia", type="secondary", key="btn_desbloquear_dia"):
                        if horarios_bloqueados_dia:
                            for horario in horarios_bloqueados_dia:
                                remover_bloqueio_horario(data_horario_str, horario)
                            
                            st.success(f"✅ Todos os horários do dia {data_horario.strftime('%d/%m/%Y')} foram desbloqueados!")
                            st.rerun()
                        else:
                            st.info("ℹ️ Nenhum horário bloqueado neste dia.")
                
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
                
                if dia_semana in dias_uteis and data.date() not in datas_bloqueadas_dt:
                    if data.date() > data_limite_antecedencia.date():
                        datas_validas.append(data.date())
            
            if not datas_validas:
                st.warning("⚠️ Nenhuma data disponível no momento.")
            else:
                st.subheader("📋 Dados do Cliente")
                
                col1, col2 = st.columns(2)
                with col1:
                    nome = st.text_input("Nome completo *", placeholder="Digite seu nome")
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
            
            col1, col2 = st.columns(2)
            with col1:
                nome_cancel = st.text_input("Nome cadastrado:", placeholder="Nome usado no agendamento")
            with col2:
                telefone_cancel = st.text_input("Telefone cadastrado:", placeholder="(11) 99999-9999")
            
            data_cancel = st.date_input("Data do agendamento:", min_value=datetime.today().date())
            
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
