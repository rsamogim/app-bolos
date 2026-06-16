import streamlit as st
import sqlite3
import os
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Vanessa Felicio Confeitaria", page_icon="🎂", layout="centered")

# --- CARDÁPIO COMPLETO ---
CARDÁPIO = {
    "Tradicional": {
        "preco_kg": 65,
        "sabores": [
            "Brigadeiro Chocolate ao Leite",
            "Brigadeiro Branco",
            "Brigadeiro Meio Amargo",
            "Dois Amores",
            "Prestígio"
        ]
    },
    "Gourmet": {
        "preco_kg": 75,
        "sabores": [
            "Abacaxi",
            "Maracujá com Leite Ninho",
            "Maracujá com Chocolate ao Leite",
            "Doce de Leite com Ameixa",
            "Ninho com Geleia de Morango",
            "4 Leites"
        ]
    },
    "Premium": {
        "preco_kg": 85,
        "sabores": [
            "Doce de Leite com Nozes",
            "Ninho com Nutella",
            "Floresta Negra",
            "Kit Kat",
            "Kinder Bueno",
            "Oreo",
            "Pudim (mínimo 5kg)",
            "Sensação",
            "Mil Folhas",
            "Brownie com Nutella, Ninho e Ouro Branco",
            "Mousse de Ninho com Morango e Suspiro"
        ]
    }
}

# --- BANCO DE DADOS (CORRIGIDO) ---
def init_db():
    conn = sqlite3.connect('bolos.db')
    c = conn.cursor()
    # Cria a tabela apenas se ela NÃO existir
    c.execute('''
        CREATE TABLE IF NOT EXISTS encomendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            telefone TEXT,
            endereco TEXT,
            linha TEXT,
            sabor TEXT,
            massa TEXT,
            peso_kg REAL,
            valor_kg REAL,
            taxa_entrega REAL,
            valor_total REAL,
            data_entrega TEXT,
            horario_entrega TEXT,
            tipo_entrega TEXT,
            status_pagamento TEXT,
            status_pedido TEXT,
            observacoes TEXT,
            alerta_3dias INTEGER DEFAULT 0,
            alerta_2dias INTEGER DEFAULT 0,
            alerta_1dia INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def salvar_encomenda(dados):
    conn = sqlite3.connect('bolos.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO encomendas 
        (cliente, telefone, endereco, linha, sabor, massa, peso_kg, valor_kg, taxa_entrega, 
         valor_total, data_entrega, horario_entrega, tipo_entrega, status_pagamento, 
         status_pedido, observacoes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (dados['cliente'], dados['telefone'], dados['endereco'], dados['linha'], 
          dados['sabor'], dados['massa'], dados['peso_kg'], dados['valor_kg'], 
          dados['taxa_entrega'], dados['valor_total'], dados['data_entrega'], 
          dados['horario_entrega'], dados['tipo_entrega'], dados['status_pagamento'],
          dados['status_pedido'], dados['observacoes']))
    conn.commit()
    conn.close()

def listar_encomendas():
    conn = sqlite3.connect('bolos.db')
    c = conn.cursor()
    c.execute('SELECT * FROM encomendas ORDER BY data_entrega ASC, horario_entrega ASC')
    encomendas = c.fetchall()
    conn.close()
    return encomendas

def atualizar_encomenda(id_pedido, campo, valor):
    conn = sqlite3.connect('bolos.db')
    c = conn.cursor()
    c.execute(f'UPDATE encomendas SET {campo} = ? WHERE id = ?', (valor, id_pedido))
    conn.commit()
    conn.close()

def deletar_encomenda(id_pedido):
    conn = sqlite3.connect('bolos.db')
    c = conn.cursor()
    c.execute('DELETE FROM encomendas WHERE id = ?', (id_pedido,))
    conn.commit()
    conn.close()

# Inicializa banco apenas uma vez
init_db()

# --- MENU LATERAL ---
st.sidebar.title("🎂 Menu")
menu = st.sidebar.radio("Navegar", ["📝 Nova Encomenda", " Agenda de Pedidos", "📊 Resumo"])

# --- TELA PRINCIPAL ---
if menu == "📝 Nova Encomenda":
    st.title("📝 Cadastrar Nova Encomenda")
    
    # Dados do cliente
    st.subheader("Dados do Cliente")
    col1, col2 = st.columns(2)
    cliente = col1.text_input("Nome do Cliente *")
    telefone = col2.text_input("Telefone/WhatsApp")
    
    # Tipo de entrega
    tipo_entrega = st.radio("Tipo de Entrega", ["Retirada", "Entrega"], horizontal=True)
    
    endereco = ""
    taxa_entrega = 0.0
    if tipo_entrega == "Entrega":
        endereco = st.text_input("📍 Endereço Completo para Entrega")
        taxa_entrega = st.number_input("Taxa de Entrega (R$)", min_value=0.0, value=5.0, step=0.5)
    
    # Detalhes do bolo
    st.subheader("Detalhes do Bolo")
    col3, col4 = st.columns(2)
    linha = col3.selectbox("Linha", ["Tradicional", "Gourmet", "Premium"])
    sabores_disponiveis = CARDÁPIO[linha]["sabores"]
    sabor = col3.selectbox("Sabor", sabores_disponiveis)
    
    massa = col4.radio("Massa do Bolo", ["Branca", "Chocolate"])
    peso_kg = col4.number_input("Peso (kg)", min_value=0.5, max_value=10.0, value=1.0, step=0.5)
    
    # Cálculo
    valor_kg = CARDÁPIO[linha]["preco_kg"]
    valor_bolo = peso_kg * valor_kg
    valor_total = valor_bolo + taxa_entrega
    
    st.success(f"💰 **Valor Total: R$ {valor_total:.2f}** ({peso_kg}kg x R$ {valor_kg:.2f} + R$ {taxa_entrega:.2f} entrega)")
    
    # Data e hora
    st.subheader("Entrega/Retirada")
    col5, col6 = st.columns(2)
    data_entrega = col5.date_input("Data de Entrega")
    horario_entrega = col6.time_input("Horário da Entrega")
    
    # Status
    col7, col8 = st.columns(2)
    status_pagamento = col7.selectbox("Pagamento", ["Pendente", "Sinal Pago", "Pago"])
    status_pedido = col8.selectbox("Status", ["Novo", "Em Preparo", "Pronto", "Entregue"])
    
    observacoes = st.text_area("Observações")
    
    # Botão salvar
    if st.button("💾 Salvar Encomenda", type="primary", use_container_width=True):
        if cliente:
            dados = {
                'cliente': cliente,
                'telefone': telefone,
                'endereco': endereco,
                'linha': linha,
                'sabor': sabor,
                'massa': massa,
                'peso_kg': peso_kg,
                'valor_kg': valor_kg,
                'taxa_entrega': taxa_entrega,
                'valor_total': valor_total,
                'data_entrega': data_entrega.strftime("%d/%m/%Y"),
                'horario_entrega': horario_entrega.strftime("%H:%M"),
                'tipo_entrega': tipo_entrega,
                'status_pagamento': status_pagamento,
                'status_pedido': status_pedido,
                'observacoes': observacoes
            }
            salvar_encomenda(dados)
            st.success(f"✅ Encomenda de {cliente} salva com sucesso!")
            st.balloons()
            st.rerun()
        else:
            st.error("⚠️ Por favor, preencha o nome do cliente.")

elif menu == "📋 Agenda de Pedidos":
    st.title("📋 Agenda de Pedidos")
    
    encomendas = listar_encomendas()
    hoje = datetime.now().date()
    
    if encomendas:
        pendentes = [e for e in encomendas if e[15] != "Entregue"]
        entregues = [e for e in encomendas if e[15] == "Entregue"]
        
        if pendentes:
            st.subheader(f"🔴 Pedidos Pendentes ({len(pendentes)})")
            for encomenda in pendentes:
                id_pedido, cliente, telefone, endereco, linha, sabor, massa, peso_kg, valor_kg, taxa_entrega, valor_total, data_entrega, horario_entrega, tipo_entrega, status_pagamento, status_pedido, observacoes, a3, a2, a1 = encomenda
                
                data_obj = datetime.strptime(data_entrega, "%d/%m/%Y").date()
                dias_restantes = (data_obj - hoje).days
                
                alertas = []
                if dias_restantes == 3 and a3 == 0:
                    alertas.append("⚠️ Faltam 3 dias!")
                    atualizar_encomenda(id_pedido, "alerta_3dias", 1)
                elif dias_restantes == 2 and a2 == 0:
                    alertas.append("⚠️ Faltam 2 dias!")
                    atualizar_encomenda(id_pedido, "alerta_2dias", 1)
                elif dias_restantes == 1 and a1 == 0:
                    alertas.append("🚨 Faltam 1 dia!")
                    atualizar_encomenda(id_pedido, "alerta_1dia", 1)
                elif dias_restantes == 0:
                    alertas.append("🔥 ENTREGA HOJE!")
                elif dias_restantes < 0:
                    alertas.append("📅 Atrasado!")
                
                if status_pedido == "Novo":
                    cor_status = "🔵"
                elif status_pedido == "Em Preparo":
                    cor_status = "🟡"
                elif status_pedido == "Pronto":
                    cor_status = "🟢"
                else:
                    cor_status = ""
                
                with st.expander(f"{cor_status} {cliente} - {data_entrega} às {horario_entrega}"):
                    if alertas:
                        for alerta in alertas:
                            st.warning(alerta)
                    
                    st.write(f"**Linha:** {linha} | **Sabor:** {sabor}")
                    st.write(f"**Massa:** {massa} | **Peso:** {peso_kg}kg")
                    st.write(f"**Valor:** R$ {valor_total:.2f} ({tipo_entrega})")
                    if tipo_entrega == "Entrega" and endereco:
                        st.info(f" **Endereço:** {endereco}")
                    st.write(f"**Pagamento:** {status_pagamento}")
                    if telefone:
                        st.write(f"**Telefone:** {telefone}")
                    if observacoes:
                        st.write(f"**Obs:** {observacoes}")
                    
                    st.divider()
                    
                    novo_status = st.selectbox(
                        "Status:",
                        ["Novo", "Em Preparo", "Pronto", "Entregue"],
                        index=["Novo", "Em Preparo", "Pronto", "Entregue"].index(status_pedido),
                        key=f"status_{id_pedido}"
                    )
                    if st.button("💾 Atualizar", key=f"btn_{id_pedido}"):
                        atualizar_encomenda(id_pedido, "status_pedido", novo_status)
                        st.success("Status atualizado!")
                        st.rerun()
                    
                    if st.button("🗑️ Excluir", key=f"del_{id_pedido}"):
                        deletar_encomenda(id_pedido)
                        st.success("Excluído!")
                        st.rerun()
        
        if entregues:
            with st.expander(f"📦 Pedidos Entregues ({len(entregues)})"):
                for encomenda in entregues:
                    id_pedido, cliente, telefone, endereco, linha, sabor, massa, peso_kg, valor_kg, taxa_entrega, valor_total, data_entrega, horario_entrega, tipo_entrega, status_pagamento, status_pedido, observacoes, a3, a2, a1 = encomenda
                    st.write(f"✅ {cliente} - {data_entrega} - R$ {valor_total:.2f}")
    else:
        st.info("Nenhuma encomenda cadastrada.")

elif menu == "📊 Resumo":
    st.title(" Resumo Geral")
    
    encomendas = listar_encomendas()
    
    if encomendas:
        total_pedidos = len(encomendas)
        pendentes = len([e for e in encomendas if e[15] != "Entregue"])
        entregues = len([e for e in encomendas if e[15] == "Entregue"])
        faturamento = sum([e[10] for e in encomendas if e[15] != "Entregue"])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Pedidos", total_pedidos)
        col2.metric("Pendentes", pendentes)
        col3.metric("Entregues", entregues)
        
        st.divider()
        st.metric("Faturamento Pendente", f"R$ {faturamento:.2f}")
    else:
        st.info("Sem dados.")