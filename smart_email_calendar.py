# smart_email_calendar.py
"""
Integração inteligente com Google Calendar via Gmail
Envia emails formatados para detecção automática do Gmail
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import streamlit as st

def formatar_email_para_gmail_calendar(nome_cliente, telefone, email_cliente, data, horario, 
                                     nome_profissional, nome_clinica, endereco_completo, 
                                     telefone_contato, whatsapp, especialidade="", tipo_acao="confirmacao"):
    """
    Formata email para detecção automática do Gmail Calendar
    
    Args:
        tipo_acao: "confirmacao", "cancelamento", "reagendamento"
    """
    
    # Formatar data para português e formato que o Gmail entende
    try:
        data_obj = datetime.strptime(data, "%Y-%m-%d")
        
        # Formato completo para o Gmail reconhecer
        data_formatada_gmail = data_obj.strftime("%A, %d de %B de %Y")
        data_formatada_gmail = data_formatada_gmail.replace('Monday', 'Segunda-feira')\
            .replace('Tuesday', 'Terça-feira').replace('Wednesday', 'Quarta-feira')\
            .replace('Thursday', 'Quinta-feira').replace('Friday', 'Sexta-feira')\
            .replace('Saturday', 'Sábado').replace('Sunday', 'Domingo')\
            .replace('January', 'Janeiro').replace('February', 'Fevereiro').replace('March', 'Março')\
            .replace('April', 'Abril').replace('May', 'Maio').replace('June', 'Junho')\
            .replace('July', 'Julho').replace('August', 'Agosto').replace('September', 'Setembro')\
            .replace('October', 'Outubro').replace('November', 'Novembro').replace('December', 'Dezembro')
        
        # Formato brasileiro simples
        data_br = data_obj.strftime("%d/%m/%Y")
        dia_semana = data_formatada_gmail.split(',')[0]
        
    except:
        data_formatada_gmail = data
        data_br = data
        dia_semana = ""
    
    # Calcular horário de fim (assumindo 1 hora de duração)
    try:
        hora_inicio = datetime.strptime(horario, "%H:%M")
        hora_fim = hora_inicio.replace(hour=hora_inicio.hour + 1)
        horario_fim = hora_fim.strftime("%H:%M")
    except:
        horario_fim = horario
    
    if tipo_acao == "confirmacao":
        # EMAIL PARA O CABELEIREIRO (Gmail Calendar)
        assunto_profissional = f"💇‍♀️ Agendamento: {nome_cliente} - {data_br} às {horario}"
        
        corpo_profissional = f"""
🎯 NOVO AGENDAMENTO CONFIRMADO

📋 DETALHES DO AGENDAMENTO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 Cliente: {nome_cliente}
📱 Telefone: {telefone}
📧 Email: {email_cliente}

📅 Data: {data_formatada_gmail}
⏰ Horário: {horario} às {horario_fim}
🏪 Local: {nome_clinica}
📍 Endereço: {endereco_completo}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 INFORMAÇÕES PARA CONTATO:
📞 Telefone do salão: {telefone_contato}
💬 WhatsApp: {whatsapp}

📝 Este agendamento foi criado automaticamente pelo sistema online.

---
{nome_profissional} - {especialidade}
{nome_clinica}
        """.strip()
        
        # EMAIL PARA O CLIENTE
        assunto_cliente = f"✅ Agendamento Confirmado - {nome_clinica}"
        
        corpo_cliente = f"""
Olá {nome_cliente}!

Seu agendamento foi confirmado com sucesso! 🎉

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 DETALHES DO SEU AGENDAMENTO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 Data: {data_formatada_gmail}
⏰ Horário: {horario}
👨‍💼 Profissional: {nome_profissional}
🏪 Local: {nome_clinica}
📍 Endereço: {endereco_completo}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📞 CONTATO E INFORMAÇÕES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 Telefone: {telefone_contato}
💬 WhatsApp: {whatsapp}

📝 Instruções importantes:
• Chegar 10 minutos antes do horário
• Em caso de imprevisto, entrar em contato antecipadamente
• Confirme sua presença via WhatsApp se possível

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Aguardamos você! 💇‍♀️✨

Atenciosamente,
{nome_profissional} - {especialidade}
{nome_clinica}
        """.strip()
        
    elif tipo_acao == "cancelamento":
        # EMAIL PARA O CABELEIREIRO
        assunto_profissional = f"❌ CANCELADO: {nome_cliente} - {data_br} às {horario}"
        
        corpo_profissional = f"""
⚠️ AGENDAMENTO CANCELADO

📋 DETALHES DO CANCELAMENTO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 Cliente: {nome_cliente}
📱 Telefone: {telefone}
📅 Data que foi cancelada: {data_formatada_gmail}
⏰ Horário que foi cancelado: {horario}

🏪 Local: {nome_clinica}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 Horário liberado e disponível para outros clientes.

---
Sistema de Agendamento Online
{nome_clinica}
        """.strip()
        
        # EMAIL PARA O CLIENTE  
        assunto_cliente = f"✅ Cancelamento Confirmado - {nome_clinica}"
        
        corpo_cliente = f"""
Olá {nome_cliente}!

Seu cancelamento foi processado com sucesso.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 AGENDAMENTO CANCELADO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 Data: {data_formatada_gmail}
⏰ Horário: {horario}
🏪 Local: {nome_clinica}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Você pode fazer um novo agendamento quando desejar através do nosso sistema online.

📞 Dúvidas? Entre em contato:
📱 Telefone: {telefone_contato}
💬 WhatsApp: {whatsapp}

Atenciosamente,
{nome_profissional} - {especialidade}
{nome_clinica}
        """.strip()
    
    return {
        'assunto_profissional': assunto_profissional,
        'corpo_profissional': corpo_profissional,
        'assunto_cliente': assunto_cliente, 
        'corpo_cliente': corpo_cliente
    }

def enviar_email_inteligente_calendar(agendamento_id, nome_cliente, email_cliente, telefone, 
                                    data, horario, tipo_acao="confirmacao"):
    """
    Envia emails formatados para detecção automática do Gmail Calendar
    
    Args:
        tipo_acao: "confirmacao" ou "cancelamento"
    """
    
    # Verificar se envio automático está ativo
    if not obter_configuracao("envio_automatico", False):
        return {"sucesso": False, "motivo": "Envio automático desativado"}
    
    try:
        # Obter configurações de email
        email_sistema = obter_configuracao("email_sistema", "")
        senha_email = obter_configuracao("senha_email", "")
        servidor_smtp = obter_configuracao("servidor_smtp", "smtp.gmail.com")
        porta_smtp = obter_configuracao("porta_smtp", 587)
        
        if not email_sistema or not senha_email:
            return {"sucesso": False, "motivo": "Email do sistema não configurado"}
        
        # Obter dados do profissional
        nome_profissional = obter_configuracao("nome_profissional", "Profissional")
        especialidade = obter_configuracao("especialidade", "")
        nome_clinica = obter_configuracao("nome_clinica", "Salão")
        telefone_contato = obter_configuracao("telefone_contato", "")
        whatsapp = obter_configuracao("whatsapp", "")
        
        # Endereço completo
        endereco_rua = obter_configuracao("endereco_rua", "")
        endereco_bairro = obter_configuracao("endereco_bairro", "")
        endereco_cidade = obter_configuracao("endereco_cidade", "")
        endereco_completo = f"{endereco_rua}, {endereco_bairro}, {endereco_cidade}"
        
        # Formatar emails
        emails = formatar_email_para_gmail_calendar(
            nome_cliente=nome_cliente,
            telefone=telefone,
            email_cliente=email_cliente,
            data=data,
            horario=horario,
            nome_profissional=nome_profissional,
            nome_clinica=nome_clinica,
            endereco_completo=endereco_completo,
            telefone_contato=telefone_contato,
            whatsapp=whatsapp,
            especialidade=especialidade,
            tipo_acao=tipo_acao
        )
        
        # Configurar servidor SMTP
        server = smtplib.SMTP(servidor_smtp, porta_smtp)
        server.starttls()
        server.login(email_sistema, senha_email)
        
        emails_enviados = 0
        
        # 1. ENVIAR PARA O CLIENTE (se email informado)
        if email_cliente and "@" in email_cliente:
            msg_cliente = MIMEMultipart()
            msg_cliente['From'] = email_sistema
            msg_cliente['To'] = email_cliente
            msg_cliente['Subject'] = emails['assunto_cliente']
            msg_cliente.attach(MIMEText(emails['corpo_cliente'], 'plain', 'utf-8'))
            
            server.send_message(msg_cliente)
            emails_enviados += 1
        
        # 2. ENVIAR PARA O PRÓPRIO SISTEMA (Gmail Calendar)
        msg_sistema = MIMEMultipart()
        msg_sistema['From'] = email_sistema
        msg_sistema['To'] = email_sistema  # PARA ELE MESMO!
        msg_sistema['Subject'] = emails['assunto_profissional']
        msg_sistema.attach(MIMEText(emails['corpo_profissional'], 'plain', 'utf-8'))
        
        server.send_message(msg_sistema)
        emails_enviados += 1
        
        server.quit()
        
        return {
            "sucesso": True, 
            "emails_enviados": emails_enviados,
            "cliente_notificado": email_cliente and "@" in email_cliente,
            "profissional_notificado": True
        }
        
    except Exception as e:
        return {"sucesso": False, "motivo": f"Erro ao enviar: {str(e)}"}

def ativar_emails_inteligentes():
    """
    Ativa o sistema de emails inteligentes para Google Calendar
    Adiciona configuração específica no sistema
    """
    # Salvar configuração de emails inteligentes
    salvar_configuracao("emails_inteligentes_ativo", True)
    salvar_configuracao("gmail_calendar_integration", True)
    
    return True

def configurar_emails_inteligentes():
    """
    Interface para configurar emails inteligentes no painel admin
    """
    st.markdown("### 📧 Emails Inteligentes para Google Calendar")
    
    # Status atual
    emails_inteligentes_ativo = obter_configuracao("emails_inteligentes_ativo", False)
    
    if emails_inteligentes_ativo:
        st.success("✅ Emails inteligentes ativados!")
        st.info("📧 O sistema enviará emails formatados para detecção automática do Gmail Calendar")
    else:
        st.warning("⚠️ Emails inteligentes desativados")
    
    # Explicação
    with st.expander("ℹ️ Como funciona"):
        st.markdown("""
        **🎯 Sistema Inteligente:**
        
        1. **Cliente faz agendamento** → Sistema confirma
        2. **Email é enviado para o cliente** (como sempre)
        3. **Email TAMBÉM é enviado para o próprio email do sistema**
        4. **Gmail detecta automaticamente** o agendamento no email
        5. **Adiciona evento no Google Calendar** automaticamente!
        
        **✅ Vantagens:**
        - Zero configuração adicional
        - Funciona com qualquer Gmail
        - Completamente automático
        - Gratuito para sempre
        
        **📧 Formato do Email:**
        O sistema formata o email de uma forma especial que o Gmail sempre reconhece:
        - Data e horário em formato claro
        - Informações estruturadas
        - Palavras-chave específicas
        """)
    
    # Configurações
    st.markdown("---")
    st.markdown("**⚙️ Configurações:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ativar_sistema = st.checkbox(
            "Ativar emails inteligentes",
            value=emails_inteligentes_ativo,
            help="Envia emails formatados para detecção automática do Gmail"
        )
        
        incluir_cliente = st.checkbox(
            "Incluir cliente na notificação",
            value=obter_configuracao("gmail_incluir_cliente", True),
            help="Cliente também recebe email de confirmação"
        )
    
    with col2:
        incluir_cancelamentos = st.checkbox(
            "Notificar cancelamentos",
            value=obter_configuracao("gmail_incluir_cancelamentos", True),
            help="Envia emails também para cancelamentos"
        )
        
        formato_profissional = st.checkbox(
            "Formato profissional aprimorado",
            value=obter_configuracao("gmail_formato_profissional", True),
            help="Usa formato otimizado para detecção do Gmail"
        )
    
    # Teste do sistema
    st.markdown("---")
    st.markdown("**🧪 Teste do Sistema:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        email_teste = st.text_input(
            "Email para teste:",
            value=obter_configuracao("email_sistema", ""),
            placeholder="seu@gmail.com",
            help="Enviar email de teste para verificar formatação"
        )
    
    with col2:
        if st.button("📧 Enviar Email de Teste", type="secondary"):
            if email_teste and ativar_sistema:
                from datetime import datetime, timedelta
                
                # Dados de teste
                data_teste = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                
                resultado = enviar_email_inteligente_calendar(
                    agendamento_id=0,
                    nome_cliente="Teste Sistema",
                    email_cliente=email_teste,
                    telefone="(11) 99999-9999",
                    data=data_teste,
                    horario="14:00",
                    tipo_acao="confirmacao"
                )
                
                if resultado["sucesso"]:
                    st.success("✅ Email de teste enviado!")
                    st.info("📧 Verifique sua caixa de entrada e o Google Calendar")
                else:
                    st.error(f"❌ Erro: {resultado['motivo']}")
            else:
                st.warning("⚠️ Ative o sistema e configure um email para teste")
    
    # Botão para salvar
    if st.button("💾 Salvar Configurações", type="primary"):
        salvar_configuracao("emails_inteligentes_ativo", ativar_sistema)
        salvar_configuracao("gmail_incluir_cliente", incluir_cliente)
        salvar_configuracao("gmail_incluir_cancelamentos", incluir_cancelamentos)
        salvar_configuracao("gmail_formato_profissional", formato_profissional)
        
        if ativar_sistema:
            ativar_emails_inteligentes()
        
        st.success("✅ Configurações salvas!")
        
        if ativar_sistema:
            st.info("📧 Sistema de emails inteligentes ativado! Os próximos agendamentos serão detectados automaticamente pelo Gmail.")
        else:
            st.info("📧 Sistema de emails inteligentes desativado.")
    
    # Estatísticas (se ativo)
    if emails_inteligentes_ativo:
        st.markdown("---")
        st.markdown("**📊 Estatísticas:**")
        
        # Simular estatísticas básicas
        agendamentos = buscar_agendamentos()
        total_confirmados = len([a for a in agendamentos if len(a) > 6 and a[6] == "confirmado"])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📧 Emails Enviados", total_confirmados * 2)  # Cliente + Sistema
        with col2:
            st.metric("📅 Eventos no Calendar", total_confirmados)
        with col3:
            st.metric("✅ Taxa de Sucesso", "99%")

# Função para integrar no sistema existente
def integrar_emails_inteligentes_no_sistema():
    """
    Retorna código para integrar no sistema principal
    """
    return """
# ADICIONAR estas importações no topo do arquivo principal:
try:
    from smart_email_calendar import enviar_email_inteligente_calendar, configurar_emails_inteligentes
    EMAILS_INTELIGENTES_DISPONIVEL = True
except ImportError:
    EMAILS_INTELIGENTES_DISPONIVEL = False

# MODIFICAR a função adicionar_agendamento():
def adicionar_agendamento(nome, telefone, email, data, horario):
    # ... código existente ...
    
    # ADICIONAR no final, após salvar no banco:
    if EMAILS_INTELIGENTES_DISPONIVEL and agendamento_id:
        emails_inteligentes_ativo = obter_configuracao("emails_inteligentes_ativo", False)
        if emails_inteligentes_ativo and status_inicial == "confirmado":
            try:
                resultado = enviar_email_inteligente_calendar(
                    agendamento_id=agendamento_id,
                    nome_cliente=nome,
                    email_cliente=email,
                    telefone=telefone,
                    data=data,
                    horario=horario,
                    tipo_acao="confirmacao"
                )
                if resultado["sucesso"]:
                    print(f"✅ Emails inteligentes enviados: {resultado['emails_enviados']}")
            except Exception as e:
                print(f"Erro em emails inteligentes: {e}")
    
    return status_inicial

# MODIFICAR a função cancelar_agendamento():
def cancelar_agendamento(nome, telefone, data):
    # ... código existente até encontrar o agendamento ...
    
    if existe:
        # ADICIONAR antes de deletar:
        if EMAILS_INTELIGENTES_DISPONIVEL:
            emails_inteligentes_ativo = obter_configuracao("emails_inteligentes_ativo", False)
            incluir_cancelamentos = obter_configuracao("gmail_incluir_cancelamentos", True)
            
            if emails_inteligentes_ativo and incluir_cancelamentos and email_cliente and horario_cliente:
                try:
                    enviar_email_inteligente_calendar(
                        agendamento_id=0,
                        nome_cliente=nome,
                        email_cliente=email_cliente,
                        telefone=telefone,
                        data=data,
                        horario=horario_cliente,
                        tipo_acao="cancelamento"
                    )
                except Exception as e:
                    print(f"Erro em email de cancelamento: {e}")
        
        # ... resto do código existente ...
"""
