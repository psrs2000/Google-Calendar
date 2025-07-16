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

                # Navegação em linha única: Data [◀️] Mês Ano [▶️]
                col_data, col_prev, col_mes, col_next = st.columns([1, 1, 3, 1])

                with col_data:
                    st.markdown('<p style="font-size: 18px; font-weight: 600; margin: 0; padding-top: 0.3rem;">📅 Data</p>', unsafe_allow_html=True)

                with col_prev:
                    if st.button("◀️", key="prev_month", help="Mês anterior", use_container_width=True):
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
                    <div style="text-align: center; font-size: 1.1rem; font-weight: 600; color: #1f2937; padding-top: 0.3rem; margin: 0;">
                       {calendar.month_name[st.session_state.mes_atual]} {st.session_state.ano_atual}
                    </div>
                    """, unsafe_allow_html=True)

                with col_next:
                    if st.button("▶️", key="next_month", help="Próximo mês", use_container_width=True):
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
