import streamlit as st
import sqlite3

# Configuração da página
st.set_page_config(page_title="Encomendas de Bolos", page_icon="🎂", layout="centered")

# --- 1. Funções do Banco de Dados ---
def init_db():
    conn = sqlite3.connect('bolos.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS encomendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT, sabor TEXT, recheio TEXT, tamanho TEXT,
            data_entrega TEXT, valor REAL, status_pagamento TEXT,
            status_pedido TEXT, observacoes TEXT
        )
    ''')
    conn.commit()
    conn.close()

def salvar_encomenda(cliente, sabor, recheio, tamanho, data_entrega, valor, status_pagamento, status_pedido, observacoes):
    conn = sqlite3.connect('bolos.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO encomendas (cliente, sabor, recheio, tamanho, data_entrega, valor, status_pagamento, status_pedido, observacoes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (cliente, sabor, recheio, tamanho, data_entrega, valor, status_pagamento, status_pedido, observacoes))
    conn.commit()
    conn.close()

def listar_encomendas():
    conn = sqlite3.connect('bolos.db')
    c = conn.cursor()
    # Ordena pela data de entrega (as mais próximas aparecem primeiro)
    c.execute('SELECT * FROM encomendas ORDER BY data_entrega ASC')
    encomendas = c.fetchall()
    conn.close()
    return encomendas

def deletar_encomenda(id_pedido):
    conn = sqlite3.connect('bolos.db')
    c = conn.cursor()
    c.execute('DELETE FROM encomendas WHERE id = ?', (id_pedido,))
    conn.commit()
    conn.close()

def atualizar_status(id_pedido, novo_status):
    conn = sqlite3.connect('bolos.db')
    c = conn.cursor()
    c.execute('UPDATE encomendas SET status_pedido = ? WHERE id = ?', (novo_status, id_pedido))
    conn.commit()
    conn.close()

# Inicia o banco de dados
init_db()

# --- 2. Interface do App (Com Abas) ---
st.title("🎂 Gestão de Encomendas")

# Cria as duas abas no topo
tab1, tab2 = st.tabs(["📝 Novo Pedido", "📋 Meus Pedidos"])

# --- ABA 1: Cadastrar ---
with tab1:
    st.subheader("Cadastrar Nova Encomenda")
    with st.form("nova_encomenda"):
        cliente = st.text_input("Nome do Cliente *")
        sabor = st.text_input("Sabor do Bolo")
        recheio = st.text_input("Recheio")
        tamanho = st.text_input("Tamanho (ex: 2kg, 20 fatias)")
        data_entrega = st.date_input("Data de Entrega")
        valor = st.number_input("Valor Total (R$)", min_value=0.0, format="%.2f")
        status_pagamento = st.selectbox("Status do Pagamento", ["Pendente", "Sinal Pago", "Pago"])
        status_pedido = st.selectbox("Status do Pedido", ["Novo", "Em Preparo", "Pronto", "Entregue"])
        observacoes = st.text_area("Observações (ex: escrever 'Parabéns Ana')")
        
        submitted = st.form_submit_button("💾 Salvar Encomenda")
        
        if submitted:
            if cliente:
                salvar_encomenda(cliente, sabor, recheio, tamanho, data_entrega, valor, status_pagamento, status_pedido, observacoes)
                st.success(f"✅ Encomenda de {cliente} salva com sucesso!")
                st.rerun() # Atualiza a tela automaticamente
            else:
                st.error("⚠️ Por favor, preencha o nome do cliente.")

# --- ABA 2: Ver e Gerenciar ---
with tab2:
    st.subheader("📋 Encomendas Cadastradas")
    encomendas = listar_encomendas()
    
    if encomendas:
        for encomenda in encomendas:
            id_pedido, cliente, sabor, recheio, tamanho, data_entrega, valor, status_pagamento, status_pedido, observacoes = encomenda
            
            # Cria um cartão expansível para cada pedido
            with st.expander(f"🎂 {cliente} - Entrega: {data_entrega}"):
                st.write(f"**Sabor:** {sabor} | **Recheio:** {recheio}")
                st.write(f"**Tamanho:** {tamanho} | **Valor:** R$ {valor:.2f}")
                st.write(f"**Pagamento:** {status_pagamento}")
                if observacoes:
                    st.write(f"** Obs:** {observacoes}")
                
                st.divider()
                
                # Botão para mudar o status
                novo_status = st.selectbox(
                    "Alterar Status:",
                    ["Novo", "Em Preparo", "Pronto", "Entregue"],
                    index=["Novo", "Em Preparo", "Pronto", "Entregue"].index(status_pedido),
                    key=f"status_{id_pedido}"
                )
                if novo_status != status_pedido:
                    if st.button("Salvar Novo Status", key=f"btn_status_{id_pedido}"):
                        atualizar_status(id_pedido, novo_status)
                        st.success("Status atualizado!")
                        st.rerun()
                
                st.divider()
                
                # Botão para excluir
                if st.button("🗑️ Excluir Encomenda", key=f"btn_del_{id_pedido}"):
                    deletar_encomenda(id_pedido)
                    st.success("Encomenda excluída!")
                    st.rerun()
    else:
        st.info("Nenhuma encomenda cadastrada ainda.")