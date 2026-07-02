import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
import os

# ---------------------- CONFIGURAÇÕES DA EMPRESA ----------------------
PASTA_PROGRAMA = os.path.dirname(os.path.abspath(__file__))
CAMINHO_LOGO = os.path.join(PASTA_PROGRAMA, "logo_empresa.png")

DADOS_EMPRESA = {
    "nome": "VR Reservatórios",
    "cnpj": "13.343.741/0001-90",
    "endereco": "R. João Ifanger Júnior, 138 - Indaiatuba/SP",
    "telefone": "(19) 98986-9948",
    "logo": CAMINHO_LOGO
}
# -----------------------------------------------------------------------

usuario_logado = ""

# ---------------------- FUNÇÃO PARA VOLTAR À TELA DE LOGIN ----------------------
def voltar_para_login(janela_atual):
    janela_atual.destroy()   # Fecha a tela atual
    tela_login()             # Abre novamente a tela de login
# -----------------------------------------------------------------------


# ---------------------- FUNÇÃO DE FORMATAÇÃO DE VALORES ----------------------
def formatar_valor(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
# -----------------------------------------------------------------------

# ---------------------- BANCO DE DADOS COM TABELA DE ITENS ----------------------
def conectar_db():
    conn = sqlite3.connect("orcamentos.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario TEXT UNIQUE NOT NULL,
                        senha TEXT NOT NULL
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        razao_social TEXT NOT NULL,
                        cnpj_cpf TEXT,
                        ie_rg TEXT,
                        endereco TEXT,
                        numero TEXT,
                        bairro TEXT,
                        cidade TEXT,
                        uf TEXT,
                        cep TEXT,
                        contato TEXT
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS servicos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        codigo TEXT UNIQUE,
                        descricao TEXT NOT NULL,
                        valor_unitario REAL NOT NULL
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS orcamentos (
                        numero_orcamento TEXT PRIMARY KEY,
                        data_orcamento TEXT,
                        id_cliente INTEGER,
                        vendedor TEXT,
                        profundidade TEXT,
                        total_servicos REAL,
                        desconto REAL,
                        imposto REAL,
                        total_final REAL,
                        vencimento TEXT,
                        FOREIGN KEY (id_cliente) REFERENCES clientes(id)
                    )''')
    # NOVA TABELA: Itens dos orçamentos
    cursor.execute('''CREATE TABLE IF NOT EXISTS itens_orcamento (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        numero_orcamento TEXT,
                        codigo_servico TEXT,
                        descricao TEXT,
                        valor_unitario REAL,
                        quantidade INTEGER,
                        valor_total REAL,
                        FOREIGN KEY (numero_orcamento) REFERENCES orcamentos(numero_orcamento) ON DELETE CASCADE
                    )''')
    # Usuário padrão
    cursor.execute("SELECT * FROM usuarios WHERE usuario = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", ("admin", "123456"))
    conn.commit()
    return conn

conn = conectar_db()

# ---------------------- TELA ADICIONAR USUÁRIO ----------------------
def tela_adicionar_usuario():
    janela = tk.Toplevel()
    janela.title("Cadastrar Novo Usuário")
    janela.geometry("400x220")
    janela.resizable(False, False)
    janela.grab_set()

    frame = ttk.LabelFrame(janela, text="Dados do Usuário", padding=20)
    frame.pack(fill="both", expand=True, padx=15, pady=15)

    ttk.Label(frame, text="Nome de Usuário:").grid(row=0, column=0, sticky="w", pady=8)
    entrada_usuario = ttk.Entry(frame, width=30)
    entrada_usuario.grid(row=0, column=1, padx=10)

    ttk.Label(frame, text="Senha:").grid(row=1, column=0, sticky="w", pady=8)
    entrada_senha = ttk.Entry(frame, width=30, show="*")
    entrada_senha.grid(row=1, column=1, padx=10)

    def salvar():
        usuario = entrada_usuario.get().strip()
        senha = entrada_senha.get().strip()
        if not usuario or not senha:
            messagebox.showwarning("Aviso", "Preencha todos os campos!")
            return
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", (usuario, senha))
            conn.commit()
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
            janela.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Esse nome de usuário já existe!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao cadastrar: {e}")

    frame_botoes = ttk.Frame(frame)
    frame_botoes.grid(row=2, column=0, columnspan=2, pady=15)
    ttk.Button(frame_botoes, text="Salvar", command=salvar).pack(side="left", padx=10)
    ttk.Button(frame_botoes, text="Cancelar", command=janela.destroy).pack(side="right", padx=10)

# ---------------------- TELA DE LOGIN - MODO JANELA MAXIMIZADA ----------------------
def tela_login():
    global usuario_logado
    janela_login = tk.Tk()
    janela_login.title("Acesso ao Sistema de Orçamentos")
    janela_login.state("zoomed")  # Abre maximizada, não tela cheia
    janela_login.config(bg="#f0f0f0")

    frame_central = ttk.Frame(janela_login, padding=30)
    frame_central.place(relx=0.5, rely=0.5, anchor="center")

    ttk.Label(frame_central, text="SISTEMA DE ORÇAMENTOS", font=("Arial", 20, "bold")).pack(pady=20)
    ttk.Label(frame_central, text="Acesso ao Sistema", font=("Arial", 14)).pack(pady=10)

    frame = ttk.Frame(frame_central, padding=20)
    frame.pack()

    ttk.Label(frame, text="Usuário:", font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=10)
    entrada_usuario = ttk.Entry(frame, width=35, font=("Arial", 12))
    entrada_usuario.grid(row=0, column=1, pady=10, padx=10)

    ttk.Label(frame, text="Senha:", font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=10)
    entrada_senha = ttk.Entry(frame, width=35, show="*", font=("Arial", 12))
    entrada_senha.grid(row=1, column=1, pady=10, padx=10)

    def validar_login():
        global usuario_logado
        usuario = entrada_usuario.get().strip()
        senha = entrada_senha.get().strip()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha))
        if cursor.fetchone():
            usuario_logado = usuario
            janela_login.destroy()
            tela_principal()
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos!")

    frame_botoes = ttk.Frame(frame_central)
    frame_botoes.pack(pady=20)

    ttk.Button(frame_botoes, text="Entrar", command=validar_login, width=15).grid(row=0, column=0, padx=10)
    ttk.Button(frame_botoes, text="Adicionar Novo Usuário", command=tela_adicionar_usuario, width=20).grid(row=0, column=1, padx=10)
    ttk.Button(frame_botoes, text="Sair", command=janela_login.quit, width=10).grid(row=0, column=2, padx=10)

    janela_login.mainloop()

# ---------------------- TELA PRINCIPAL - MAXIMIZADA ----------------------
def tela_principal():
    janela = tk.Tk()
    janela.title(f"Sistema de Orçamentos - VR Reservatórios | Usuário: {usuario_logado}")
    janela.state("zoomed")  # Janela aberta no tamanho total da tela
    menu_bar = tk.Menu(janela)
    janela.config(menu=menu_bar)

    menu_cadastros = tk.Menu(menu_bar, tearoff=0)
    menu_cadastros.add_command(label="Clientes", command=tela_cadastro_clientes)
    menu_cadastros.add_command(label="Serviços", command=tela_cadastro_servicos)
    menu_cadastros.add_command(label="Gerenciar Usuários", command=tela_gerenciar_usuarios)
    menu_bar.add_cascade(label="Cadastros", menu=menu_cadastros)

    menu_orcamentos = tk.Menu(menu_bar, tearoff=0)
    menu_orcamentos.add_command(label="Novo Orçamento", command=tela_novo_orcamento)
    menu_orcamentos.add_command(label="Histórico / Reimprimir", command=tela_historico_orcamentos)
    menu_bar.add_cascade(label="Orçamentos", menu=menu_orcamentos)

    ttk.Label(janela, text="Sistema de Gestão de Orçamentos", font=("Arial", 22, "bold")).pack(pady=60)
    ttk.Label(janela, text=f"Usuário logado: {usuario_logado}", font=("Arial", 14, "italic")).pack(pady=10)
    ttk.Label(janela, text="Selecione uma opção no menu acima para começar", font=("Arial", 14)).pack(pady=30)
    
    # Botão alterado para voltar ao login ao invés de fechar o programa
    ttk.Button(janela, text="Sair do Sistema", command=lambda: voltar_para_login(janela)).pack(pady=20)

    janela.mainloop()

# ---------------------- GERENCIAR USUÁRIOS ----------------------
def tela_gerenciar_usuarios():
    janela = tk.Toplevel()
    janela.title("Gerenciar Usuários do Sistema")
    janela.geometry("600x450")
    janela.resizable(False, False)

    frame_form = ttk.LabelFrame(janela, text="Dados do Usuário", padding=15)
    frame_form.pack(fill="x", padx=10, pady=5)

    id_usuario_selecionado = None

    ttk.Label(frame_form, text="Usuário:").grid(row=0, column=0, sticky="w", pady=8, padx=5)
    entrada_usuario = ttk.Entry(frame_form, width=30)
    entrada_usuario.grid(row=0, column=1, padx=5)

    ttk.Label(frame_form, text="Senha:").grid(row=0, column=2, sticky="w", pady=8, padx=15)
    entrada_senha = ttk.Entry(frame_form, width=30, show="*")
    entrada_senha.grid(row=0, column=3, padx=5)

    def limpar_campos():
        nonlocal id_usuario_selecionado
        id_usuario_selecionado = None
        entrada_usuario.delete(0, tk.END)
        entrada_senha.delete(0, tk.END)

    def carregar_usuarios():
        for item in tree.get_children():
            tree.delete(item)
        cursor = conn.cursor()
        cursor.execute("SELECT id, usuario FROM usuarios ORDER BY usuario")
        for linha in cursor.fetchall():
            tree.insert("", "end", values=linha)

    def selecionar_usuario(event):
        nonlocal id_usuario_selecionado
        selecionado = tree.selection()
        if not selecionado:
            return
        valores = tree.item(selecionado[0], "values")
        id_usuario_selecionado = valores[0]
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (id_usuario_selecionado,))
        dados = cursor.fetchone()
        if dados:
            entrada_usuario.delete(0, tk.END)
            entrada_usuario.insert(0, dados[1])
            entrada_senha.delete(0, tk.END)
            entrada_senha.insert(0, dados[2])

    def salvar_usuario():
        usuario = entrada_usuario.get().strip()
        senha = entrada_senha.get().strip()
        if not usuario or not senha:
            messagebox.showwarning("Aviso", "Preencha o nome de usuário e a senha!")
            return
        try:
            cursor = conn.cursor()
            if id_usuario_selecionado:
                cursor.execute('''UPDATE usuarios SET usuario=?, senha=? WHERE id=?''',
                               (usuario, senha, id_usuario_selecionado))
                mensagem = "Usuário alterado com sucesso!"
            else:
                cursor.execute('''INSERT INTO usuarios (usuario, senha) VALUES (?, ?)''',
                               (usuario, senha))
                mensagem = "Usuário cadastrado com sucesso!"
            conn.commit()
            messagebox.showinfo("Sucesso", mensagem)
            limpar_campos()
            carregar_usuarios()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Esse nome de usuário já existe!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar: {e}")

    def excluir_usuario():
        if not id_usuario_selecionado:
            messagebox.showwarning("Aviso", "Selecione um usuário primeiro!")
            return
        if entrada_usuario.get().strip() == "admin":
            messagebox.showwarning("Aviso", "Não é possível excluir o administrador!")
            return
        if entrada_usuario.get().strip() == usuario_logado:
            messagebox.showwarning("Aviso", "Não pode excluir seu próprio usuário!")
            return
        confirma = messagebox.askyesno("Confirmar Exclusão", "Deseja excluir este usuário?")
        if not confirma:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuarios WHERE id = ?", (id_usuario_selecionado,))
            conn.commit()
            messagebox.showinfo("Sucesso", "Usuário excluído!")
            limpar_campos()
            carregar_usuarios()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha: {e}")

    frame_botoes = ttk.Frame(janela, padding=10)
    frame_botoes.pack(fill="x")
    ttk.Button(frame_botoes, text="Salvar / Atualizar", command=salvar_usuario).pack(side="left", padx=5)
    ttk.Button(frame_botoes, text="Limpar Campos", command=limpar_campos).pack(side="left", padx=5)
    ttk.Button(frame_botoes, text="Excluir Usuário", command=excluir_usuario).pack(side="right", padx=5)

    frame_lista = ttk.LabelFrame(janela, text="Lista de Usuários", padding=10)
    frame_lista.pack(fill="both", expand=True, padx=10, pady=5)

    colunas = ("id", "usuario")
    tree = ttk.Treeview(frame_lista, columns=colunas, show="headings", height=8)
    tree.heading("id", text="ID")
    tree.heading("usuario", text="Nome de Usuário")
    tree.column("id", width=60, anchor="center")
    tree.column("usuario", width=450)
    tree.pack(fill="both", expand=True)
    tree.bind("<<TreeviewSelect>>", selecionar_usuario)

    carregar_usuarios()

# ---------------------- CADASTRO DE CLIENTES ----------------------
def tela_cadastro_clientes():
    janela = tk.Toplevel()
    janela.title("Gerenciar Clientes")
    janela.geometry("750x550")
    frame_form = ttk.LabelFrame(janela, text="Dados do Cliente", padding=15)
    frame_form.pack(fill="x", padx=10, pady=5)
    campos = {}
    labels = [
        ("Razão Social:", "razao"), ("CNPJ/CPF:", "cnpj"), ("IE/RG:", "ie"),
        ("Endereço:", "end"), ("Número:", "num"), ("Bairro:", "bairro"),
        ("Cidade:", "cidade"), ("UF:", "uf"), ("CEP:", "cep"), ("Contato:", "contato")
    ]
    for i, (texto, chave) in enumerate(labels):
        linha = i // 2
        coluna = (i % 2) * 2
        ttk.Label(frame_form, text=texto).grid(row=linha, column=coluna, sticky="w", pady=5, padx=5)
        campos[chave] = ttk.Entry(frame_form, width=35)
        campos[chave].grid(row=linha, column=coluna + 1, padx=5, pady=5)
    id_cliente_selecionado = None

    def limpar_campos():
        nonlocal id_cliente_selecionado
        id_cliente_selecionado = None
        for entrada in campos.values():
            entrada.delete(0, tk.END)

    def carregar_clientes():
        for item in tree.get_children():
            tree.delete(item)
        cursor = conn.cursor()
        cursor.execute("SELECT id, razao_social, cnpj_cpf, cidade, uf FROM clientes ORDER BY razao_social")
        for linha in cursor.fetchall():
            tree.insert("", "end", values=linha)

    def selecionar_cliente(event):
        nonlocal id_cliente_selecionado
        selecionado = tree.selection()
        if not selecionado:
            return
        valores = tree.item(selecionado[0], "values")
        id_cliente_selecionado = valores[0]
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes WHERE id = ?", (id_cliente_selecionado,))
        dados = cursor.fetchone()
        if dados:
            campos["razao"].delete(0, tk.END)
            campos["razao"].insert(0, dados[1])
            campos["cnpj"].delete(0, tk.END)
            campos["cnpj"].insert(0, dados[2] or "")
            campos["ie"].delete(0, tk.END)
            campos["ie"].insert(0, dados[3] or "")
            campos["end"].delete(0, tk.END)
            campos["end"].insert(0, dados[4] or "")
            campos["num"].delete(0, tk.END)
            campos["num"].insert(0, dados[5] or "")
            campos["bairro"].delete(0, tk.END)
            campos["bairro"].insert(0, dados[6] or "")
            campos["cidade"].delete(0, tk.END)
            campos["cidade"].insert(0, dados[7] or "")
            campos["uf"].delete(0, tk.END)
            campos["uf"].insert(0, dados[8] or "")
            campos["cep"].delete(0, tk.END)
            campos["cep"].insert(0, dados[9] or "")
            campos["contato"].delete(0, tk.END)
            campos["contato"].insert(0, dados[10] or "")

    def salvar_cliente():
        dados = {k: v.get().strip() for k, v in campos.items()}
        if not dados["razao"]:
            messagebox.showwarning("Aviso", "Razão Social é obrigatória!")
            return
        try:
            cursor = conn.cursor()
            if id_cliente_selecionado:
                cursor.execute('''UPDATE clientes SET razao_social=?, cnpj_cpf=?, ie_rg=?, endereco=?, numero=?, bairro=?, cidade=?, uf=?, cep=?, contato=?
                                  WHERE id=?''',
                               (dados["razao"], dados["cnpj"], dados["ie"], dados["end"], dados["num"], dados["bairro"], dados["cidade"], dados["uf"], dados["cep"], dados["contato"], id_cliente_selecionado))
                mensagem = "Cliente alterado com sucesso!"
            else:
                cursor.execute('''INSERT INTO clientes (razao_social, cnpj_cpf, ie_rg, endereco, numero, bairro, cidade, uf, cep, contato)
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                               (dados["razao"], dados["cnpj"], dados["ie"], dados["end"], dados["num"], dados["bairro"], dados["cidade"], dados["uf"], dados["cep"], dados["contato"]))
                mensagem = "Cliente cadastrado com sucesso!"
            conn.commit()
            messagebox.showinfo("Sucesso", mensagem)
            limpar_campos()
            carregar_clientes()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar: {e}")

    def excluir_cliente():
        if not id_cliente_selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente primeiro!")
            return
        confirma = messagebox.askyesno("Confirmar Exclusão", "Deseja realmente excluir este cliente?\nTodos os orçamentos vinculados também serão apagados!")
        if not confirma:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM orcamentos WHERE id_cliente = ?", (id_cliente_selecionado,))
            cursor.execute("DELETE FROM clientes WHERE id = ?", (id_cliente_selecionado,))
            conn.commit()
            messagebox.showinfo("Sucesso", "Cliente excluído!")
            limpar_campos()
            carregar_clientes()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao excluir: {e}")

    frame_botoes = ttk.Frame(janela, padding=10)
    frame_botoes.pack(fill="x")
    ttk.Button(frame_botoes, text="Salvar / Atualizar", command=salvar_cliente).pack(side="left", padx=5)
    ttk.Button(frame_botoes, text="Limpar Campos", command=limpar_campos).pack(side="left", padx=5)
    ttk.Button(frame_botoes, text="Excluir Cliente", command=excluir_cliente).pack(side="right", padx=5)

    frame_lista = ttk.LabelFrame(janela, text="Lista de Clientes", padding=10)
    frame_lista.pack(fill="both", expand=True, padx=10, pady=5)
    colunas = ("id", "razao", "cnpj", "cidade", "uf")
    tree = ttk.Treeview(frame_lista, columns=colunas, show="headings", height=10)
    tree.heading("id", text="ID")
    tree.heading("razao", text="Razão Social")
    tree.heading("cnpj", text="CNPJ/CPF")
    tree.heading("cidade", text="Cidade")
    tree.heading("uf", text="UF")
    tree.column("id", width=50, anchor="center")
    tree.column("razao", width=280)
    tree.column("cnpj", width=150)
    tree.column("cidade", width=150)
    tree.column("uf", width=50, anchor="center")
    tree.pack(fill="both", expand=True)
    tree.bind("<<TreeviewSelect>>", selecionar_cliente)
    carregar_clientes()

# ---------------------- CADASTRO DE SERVIÇOS ----------------------
def tela_cadastro_servicos():
    janela = tk.Toplevel()
    janela.title("Gerenciar Serviços")
    janela.geometry("700x450")
    frame_form = ttk.LabelFrame(janela, text="Dados do Serviço", padding=15)
    frame_form.pack(fill="x", padx=10, pady=5)
    id_servico_selecionado = None
    ttk.Label(frame_form, text="Código:").grid(row=0, column=0, sticky="w", pady=8, padx=5)
    entrada_cod = ttk.Entry(frame_form, width=20)
    entrada_cod.grid(row=0, column=1, padx=5)
    ttk.Label(frame_form, text="Descrição do Serviço:").grid(row=0, column=2, sticky="w", pady=8, padx=15)
    entrada_desc = ttk.Entry(frame_form, width=45)
    entrada_desc.grid(row=0, column=3, padx=5)
    ttk.Label(frame_form, text="Valor Unitário R$:").grid(row=1, column=0, sticky="w", pady=8, padx=5)
    entrada_valor = ttk.Entry(frame_form, width=20)
    entrada_valor.grid(row=1, column=1, padx=5)

    def limpar_campos():
        nonlocal id_servico_selecionado
        id_servico_selecionado = None
        entrada_cod.delete(0, tk.END)
        entrada_desc.delete(0, tk.END)
        entrada_valor.delete(0, tk.END)

    def carregar_servicos():
        for item in tree.get_children():
            tree.delete(item)
        cursor = conn.cursor()
        cursor.execute("SELECT id, codigo, descricao, valor_unitario FROM servicos ORDER BY descricao")
        for linha in cursor.fetchall():
            tree.insert("", "end", values=(linha[0], linha[1], linha[2], formatar_valor(linha[3])))

    def selecionar_servico(event):
        nonlocal id_servico_selecionado
        selecionado = tree.selection()
        if not selecionado:
            return
        valores = tree.item(selecionado[0], "values")
        id_servico_selecionado = valores[0]
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM servicos WHERE id = ?", (id_servico_selecionado,))
        dados = cursor.fetchone()
        if dados:
            entrada_cod.delete(0, tk.END)
            entrada_cod.insert(0, dados[2] or "")
            entrada_desc.delete(0, tk.END)
            entrada_desc.insert(0, dados[3])
            entrada_valor.delete(0, tk.END)
            entrada_valor.insert(0, f"{dados[4]:.2f}")

    def salvar_servico():
        cod = entrada_cod.get().strip()
        desc = entrada_desc.get().strip()
        try:
            valor = float(entrada_valor.get().strip().replace(",", "."))
            if valor <= 0 or not desc:
                raise ValueError
        except:
            messagebox.showwarning("Aviso", "Preencha todos os campos corretamente! Valor deve ser maior que zero.")
            return
        try:
            cursor = conn.cursor()
            if id_servico_selecionado:
                cursor.execute('''UPDATE servicos SET codigo=?, descricao=?, valor_unitario=? WHERE id=?''',
                               (cod, desc, valor, id_servico_selecionado))
                mensagem = "Serviço alterado com sucesso!"
            else:
                cursor.execute('''INSERT INTO servicos (codigo, descricao, valor_unitario) VALUES (?, ?, ?)''',
                               (cod, desc, valor))
                mensagem = "Serviço cadastrado com sucesso!"
            conn.commit()
            messagebox.showinfo("Sucesso", mensagem)
            limpar_campos()
            carregar_servicos()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha: {e}")

    def excluir_servico():
        if not id_servico_selecionado:
            messagebox.showwarning("Aviso", "Selecione um serviço primeiro!")
            return
        confirma = messagebox.askyesno("Confirmar Exclusão", "Deseja realmente excluir este serviço?")
        if not confirma:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM servicos WHERE id = ?", (id_servico_selecionado,))
            conn.commit()
            messagebox.showinfo("Sucesso", "Serviço excluído!")
            limpar_campos()
            carregar_servicos()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao excluir: {e}")

    frame_botoes = ttk.Frame(janela, padding=10)
    frame_botoes.pack(fill="x")
    ttk.Button(frame_botoes, text="Salvar / Atualizar", command=salvar_servico).pack(side="left", padx=5)
    ttk.Button(frame_botoes, text="Limpar Campos", command=limpar_campos).pack(side="left", padx=5)
    ttk.Button(frame_botoes, text="Excluir Serviço", command=excluir_servico).pack(side="right", padx=5)

    frame_lista = ttk.LabelFrame(janela, text="Lista de Serviços", padding=10)
    frame_lista.pack(fill="both", expand=True, padx=10, pady=5)
    colunas = ("id", "codigo", "descricao", "valor")
    tree = ttk.Treeview(frame_lista, columns=colunas, show="headings", height=8)
    tree.heading("id", text="ID")
    tree.heading("codigo", text="Código")
    tree.heading("descricao", text="Descrição")
    tree.heading("valor", text="Valor Unitário")
    tree.column("id", width=50, anchor="center")
    tree.column("codigo", width=80, anchor="center")
    tree.column("descricao", width=420)
    tree.column("valor", width=120, anchor="e")
    tree.pack(fill="both", expand=True)
    tree.bind("<<TreeviewSelect>>", selecionar_servico)
    carregar_servicos()

# ---------------------- GERAR PDF ----------------------
def gerar_pdf(dados_orcamento, itens):
    nome_sugerido = f"Orcamento_{dados_orcamento['numero']}_{datetime.now().strftime('%Y%m%d%H%M')}.pdf"
    caminho_arquivo = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("Arquivo PDF", "*.pdf")],
        initialfile=nome_sugerido,
        title="Salvar Orçamento em PDF"
    )

    if not caminho_arquivo:
        messagebox.showinfo("Aviso", "Geração de PDF cancelada.")
        return

    c = canvas.Canvas(caminho_arquivo, pagesize=A4)
    largura, altura = A4

    if os.path.exists(DADOS_EMPRESA["logo"]):
        try:
            c.drawImage(DADOS_EMPRESA["logo"], 2*cm, altura - 5*cm, width=4*cm, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            print(f"Aviso: Não foi possível carregar a imagem. Erro: {e}")
    else:
        print(f"Aviso: Imagem não encontrada em: {DADOS_EMPRESA['logo']}")

    c.setFont("Helvetica-Bold", 16)
    c.drawString(7*cm, altura - 2*cm, DADOS_EMPRESA["nome"])
    c.setFont("Helvetica", 10)
    c.drawString(7*cm, altura - 2.8*cm, f"CNPJ: {DADOS_EMPRESA['cnpj']}")
    c.drawString(7*cm, altura - 3.4*cm, f"Endereço: {DADOS_EMPRESA['endereco']}")
    c.drawString(7*cm, altura - 4*cm, f"Telefone: {DADOS_EMPRESA['telefone']}")

    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(largura - 2*cm, altura - 2*cm, f"Pedido de Venda Nº {dados_orcamento['numero']}")
    c.drawRightString(largura - 2*cm, altura - 2.8*cm, f"Data: {dados_orcamento['data']}")

    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, altura - 6*cm, "Cliente/Destinatário")
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, altura - 6.8*cm, f"Razão Social: {dados_orcamento['cliente']['razao']}")
    c.drawString(2*cm, altura - 7.4*cm, f"CNPJ/CPF: {dados_orcamento['cliente']['cnpj']}")
    c.drawString(2*cm, altura - 8*cm, f"Endereço: {dados_orcamento['cliente']['end']}, Nº {dados_orcamento['cliente']['num']} - {dados_orcamento['cliente']['bairro']}")
    c.drawString(2*cm, altura - 8.6*cm, f"Cidade: {dados_orcamento['cliente']['cidade']}/{dados_orcamento['cliente']['uf']} - CEP: {dados_orcamento['cliente']['cep']}")

    c.drawString(2*cm, altura - 10*cm, f"Vendedor: {dados_orcamento['vendedor']}")
    c.drawRightString(largura - 2*cm, altura - 10*cm, f"Profundidade: {dados_orcamento['profundidade']} mts")

    c.setFont("Helvetica-Bold", 10)
    c.drawString(2*cm, altura - 11.5*cm, "Código")
    c.drawString(5*cm, altura - 11.5*cm, "Descrição")
    c.drawRightString(13*cm, altura - 11.5*cm, "Unid.")
    c.drawRightString(15*cm, altura - 11.5*cm, "Valor Un.")
    c.drawRightString(17*cm, altura - 11.5*cm, "Qtde")
    c.drawRightString(19*cm, altura - 11.5*cm, "Total")

    y_pos = altura - 12.5*cm
    c.setFont("Helvetica", 9)
    for item in itens:
        c.drawString(2*cm, y_pos, item["codigo"])
        c.drawString(5*cm, y_pos, item["descricao"])
        c.drawRightString(13*cm, y_pos, "UN")
        c.drawRightString(15*cm, y_pos, formatar_valor(item["valor"]))
        c.drawRightString(17*cm, y_pos, str(item["qtd"]))
        c.drawRightString(19*cm, y_pos, formatar_valor(item["total"]))
        y_pos -= 0.7*cm

    y_pos -= 1*cm
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(largura - 2*cm, y_pos, f"Total dos Serviços: {formatar_valor(dados_orcamento['total'])}")
    y_pos -= 0.6*cm
    c.drawRightString(largura - 2*cm, y_pos, f"Desconto: {formatar_valor(dados_orcamento['desconto'])}")
    y_pos -= 0.6*cm
    c.drawRightString(largura - 2*cm, y_pos, f"Imposto: {formatar_valor(dados_orcamento['imposto'])}")
    y_pos -= 0.6*cm
    c.drawRightString(largura - 2*cm, y_pos, f"Total do Pedido: {formatar_valor(dados_orcamento['total_final'])}")

    y_pos -= 1*cm
    c.drawString(2*cm, y_pos, f"Vencimento: {dados_orcamento['vencimento']}")

    c.save()
    messagebox.showinfo("PDF Salvo", f"Orçamento salvo com sucesso em:\n{caminho_arquivo}")

# ---------------------- NOVO ORÇAMENTO - SALVA ITENS NO BANCO ----------------------
def tela_novo_orcamento():
    janela = tk.Toplevel()
    janela.title("Novo Orçamento")
    janela.geometry("800x600")
    frame_dados = ttk.LabelFrame(janela, text="Dados do Orçamento", padding=10)
    frame_dados.pack(fill="x", padx=10, pady=5)

    ttk.Label(frame_dados, text="Número:").grid(row=0, column=0, sticky="w", padx=5)
    entrada_num = ttk.Entry(frame_dados, width=15)
    entrada_num.grid(row=0, column=1)
    entrada_num.insert(0, f"{datetime.now().strftime('%Y%m%d%H%M')}")

    ttk.Label(frame_dados, text="Cliente:").grid(row=0, column=2, sticky="w", padx=15)
    combo_cliente = ttk.Combobox(frame_dados, width=45, state="readonly")
    combo_cliente.grid(row=0, column=3)
    cursor = conn.cursor()
    cursor.execute("SELECT id, razao_social FROM clientes ORDER BY razao_social")
    lista_clientes = cursor.fetchall()
    combo_cliente["values"] = [f"{c[0]} - {c[1]}" for c in lista_clientes]

    ttk.Label(frame_dados, text="Vendedor:").grid(row=1, column=0, sticky="w", padx=5, pady=8)
    entrada_vend = ttk.Entry(frame_dados, width=25)
    entrada_vend.grid(row=1, column=1)
    entrada_vend.insert(0, usuario_logado)
    entrada_vend.config(state="readonly")

    ttk.Label(frame_dados, text="Profundidade (mts):").grid(row=1, column=2, sticky="w", padx=15)
    entrada_prof = ttk.Entry(frame_dados, width=15)
    entrada_prof.grid(row=1, column=3)

    ttk.Label(frame_dados, text="Vencimento:").grid(row=2, column=0, sticky="w", padx=5, pady=8)
    entrada_venc = ttk.Entry(frame_dados, width=15)
    entrada_venc.grid(row=2, column=1)
    entrada_venc.insert(0, "28 dias")

    frame_itens = ttk.LabelFrame(janela, text="Serviços", padding=10)
    frame_itens.pack(fill="both", expand=True, padx=10, pady=5)

    ttk.Label(frame_itens, text="Serviço:").grid(row=0, column=0, sticky="w")
    combo_servico = ttk.Combobox(frame_itens, width=55, state="readonly")
    combo_servico.grid(row=0, column=1, padx=5)
    cursor.execute("SELECT id, codigo, descricao, valor_unitario FROM servicos ORDER BY descricao")
    lista_servicos = cursor.fetchall()
    combo_servico["values"] = [f"{s[1]} - {s[2]} | {formatar_valor(s[3])}" for s in lista_servicos]

    ttk.Label(frame_itens, text="Quantidade:").grid(row=0, column=2, sticky="w", padx=10)
    entrada_qtd = ttk.Entry(frame_itens, width=8)
    entrada_qtd.insert(0, "1")
    entrada_qtd.grid(row=0, column=3)

    # ---------------------- CAMPOS DE PARCELAMENTO ----------------------
    ttk.Label(frame_dados, text="Número de Parcelas:").grid(row=3, column=0, sticky="w", padx=5, pady=8)
    entrada_parcelas = ttk.Entry(frame_dados, width=15)
    entrada_parcelas.insert(0, "1")  # Padrão: à vista
    entrada_parcelas.grid(row=3, column=1)

    ttk.Label(frame_dados, text="Valor por Parcela:").grid(row=3, column=2, sticky="w", padx=15)
    label_valor_parcela = ttk.Label(frame_dados, text="R$ 0,00", font=("Arial", 10, "bold"))
    label_valor_parcela.grid(row=3, column=3)
    # ----------------------------------------------------------------------
    lista_itens = []
    colunas = ("codigo", "descricao", "valor", "qtd", "total")
    tree = ttk.Treeview(frame_itens, columns=colunas, show="headings", height=7)
    tree.heading("codigo", text="Código")
    tree.heading("descricao", text="Descrição")
    tree.heading("valor", text="Valor Un.")
    tree.heading("qtd", text="Qtde")
    tree.heading("total", text="Total")
    tree.column("codigo", width=80, anchor="center")
    tree.column("descricao", width=380)
    tree.column("valor", width=100, anchor="e")
    tree.column("qtd", width=70, anchor="e")
    tree.column("total", width=100, anchor="e")
    tree.grid(row=1, column=0, columnspan=5, pady=15, sticky="nsew")

    def adicionar_item():
        if not combo_servico.get():
            messagebox.showwarning("Aviso", "Selecione um serviço!")
            return
        try:
            qtd = int(entrada_qtd.get())
            if qtd <= 0:
                raise ValueError
        except:
            messagebox.showwarning("Aviso", "Quantidade inválida! Digite um número maior que zero.")
            return
        idx = combo_servico.current()
        cod = lista_servicos[idx][1]
        desc = lista_servicos[idx][2]
        val = lista_servicos[idx][3]
        total = val * qtd
        item = {"codigo": cod, "descricao": desc, "valor": val, "qtd": qtd, "total": total}
        lista_itens.append(item)
        tree.insert("", "end", values=(cod, desc, formatar_valor(val), qtd, formatar_valor(total)))

    def remover_item():
        selecionado = tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um item para remover!")
            return
        indice = tree.index(selecionado[0])
        tree.delete(selecionado[0])
        del lista_itens[indice]

    frame_botoes_item = ttk.Frame(frame_itens)
    frame_botoes_item.grid(row=0, column=4, padx=10)
    ttk.Button(frame_botoes_item, text="Adicionar", command=adicionar_item).pack(pady=2)
    ttk.Button(frame_botoes_item, text="Remover", command=remover_item).pack(pady=2)

    frame_totais = ttk.Frame(janela, padding=10)
    frame_totais.pack(fill="x", padx=10)
    ttk.Label(frame_totais, text="Desconto R$:").grid(row=0, column=0, sticky="w", padx=5)
    entrada_desc = ttk.Entry(frame_totais, width=12)
    entrada_desc.insert(0, "0,00")
    entrada_desc.grid(row=0, column=1)
    ttk.Label(frame_totais, text="Imposto R$:").grid(row=0, column=2, sticky="w", padx=15)
    entrada_imp = ttk.Entry(frame_totais, width=12)
    entrada_imp.insert(0, "0,00")
    entrada_imp.grid(row=0, column=3)

    

    def finalizar_orcamento():
        if not lista_itens or not combo_cliente.get():
            messagebox.showwarning("Aviso", "Selecione o cliente e adicione pelo menos um serviço!")
            return
        try:
            desc = float(entrada_desc.get().replace(",", "."))
            imp = float(entrada_imp.get().replace(",", "."))
            if desc < 0 or imp < 0:
                raise ValueError
        except:
            messagebox.showwarning("Aviso", "Valores de desconto e imposto devem ser números positivos!")
            return
        total_bruto = sum(i["total"] for i in lista_itens)
        total_final = total_bruto - desc + imp
        id_cliente = int(combo_cliente.get().split(" - ")[0])
        cursor.execute("SELECT * FROM clientes WHERE id = ?", (id_cliente,))
        dados_cli = cursor.fetchone()
        dados_pdf = {
            "numero": entrada_num.get(),
            "data": datetime.now().strftime("%d/%m/%Y"),
            "cliente": {
                "razao": dados_cli[1], "cnpj": dados_cli[2] or "Não informado", "end": dados_cli[4] or "",
                "num": dados_cli[5] or "", "bairro": dados_cli[6] or "", "cidade": dados_cli[7] or "",
                "uf": dados_cli[8] or "", "cep": dados_cli[9] or ""
            },
            "vendedor": entrada_vend.get(),
            "profundidade": entrada_prof.get() or "0",
            "total": total_bruto,
            "desconto": desc,
            "imposto": imp,
            "total_final": total_final,
            "vencimento": entrada_venc.get()
        }
        gerar_pdf(dados_pdf, lista_itens)
        try:
            # Salva dados do orçamento
            cursor.execute('''INSERT INTO orcamentos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (entrada_num.get(), dados_pdf["data"], id_cliente, entrada_vend.get(), entrada_prof.get(),
                            total_bruto, desc, imp, total_final, entrada_venc.get()))
            # Salva cada item do orçamento
            for item in lista_itens:
                cursor.execute('''INSERT INTO itens_orcamento 
                                  (numero_orcamento, codigo_servico, descricao, valor_unitario, quantidade, valor_total)
                                  VALUES (?, ?, ?, ?, ?, ?)''',
                               (entrada_num.get(), item["codigo"], item["descricao"], item["valor"], item["qtd"], item["total"]))
            conn.commit()
            janela.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar orçamento: {e}")

    ttk.Button(frame_totais, text="Gerar Orçamento e Salvar", command=finalizar_orcamento).grid(row=0, column=4, padx=30)

# ---------------------- HISTÓRICO - CARREGA ITENS AUTOMATICAMENTE ----------------------
def tela_historico_orcamentos():
    janela = tk.Toplevel()
    janela.title("Histórico e Gerenciamento de Orçamentos")
    janela.geometry("900x500")
    frame_lista = ttk.LabelFrame(janela, text="Orçamentos Cadastrados", padding=10)
    frame_lista.pack(fill="both", expand=True, padx=10, pady=10)
    
    colunas = ("numero", "data", "cliente", "vendedor", "total")
    tree = ttk.Treeview(frame_lista, columns=colunas, show="headings", height=12)
    tree.heading("numero", text="Número")
    tree.heading("data", text="Data")
    tree.heading("cliente", text="Cliente")
    tree.heading("vendedor", text="Vendedor")
    tree.heading("total", text="Total R$")
    tree.column("numero", width=120, anchor="center")
    tree.column("data", width=100, anchor="center")
    tree.column("cliente", width=320)
    tree.column("vendedor", width=180)
    tree.column("total", width=120, anchor="e")
    tree.pack(fill="both", expand=True)

    def carregar_orcamentos():
        for item in tree.get_children():
            tree.delete(item)
        cursor = conn.cursor()
        cursor.execute('''SELECT o.numero_orcamento, o.data_orcamento, c.razao_social, o.vendedor, o.total_final
                          FROM orcamentos o JOIN clientes c ON o.id_cliente = c.id
                          ORDER BY o.data_orcamento DESC, o.numero_orcamento DESC''')
        for linha in cursor.fetchall():
           tree.insert("", "end", values=(linha[0], linha[1], linha[2], linha[3], formatar_valor(linha[4])))

    def excluir_orcamento():
        selecionado = tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um orçamento primeiro!")
            return
        numero_orc = tree.item(selecionado[0], "values")[0]
        confirma = messagebox.askyesno("Confirmar Exclusão", f"Deseja excluir o orçamento Nº {numero_orc}?\nEssa ação não pode ser desfeita!")
        if not confirma:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM itens_orcamento WHERE numero_orcamento = ?", (numero_orc,))
            cursor.execute("DELETE FROM orcamentos WHERE numero_orcamento = ?", (numero_orc,))
            conn.commit()
            messagebox.showinfo("Sucesso", "Orçamento excluído com sucesso!")
            carregar_orcamentos()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao excluir: {e}")

    def reimprimir_orcamento():
        selecionado = tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um orçamento primeiro!")
            return
        numero_orc = tree.item(selecionado[0], "values")[0]
        try:
            cursor = conn.cursor()
            # Busca dados completos do orçamento e cliente
            cursor.execute('''SELECT o.*, c.* FROM orcamentos o
                              JOIN clientes c ON o.id_cliente = c.id
                              WHERE o.numero_orcamento = ?''', (numero_orc,))
            dados = cursor.fetchone()
            if not dados:
                messagebox.showerror("Erro", "Orçamento não encontrado!")
                return

            # Busca todos os itens do orçamento
            cursor.execute('''SELECT codigo_servico, descricao, valor_unitario, quantidade, valor_total
                              FROM itens_orcamento WHERE numero_orcamento = ?''', (numero_orc,))
            itens_banco = cursor.fetchall()
            lista_itens = []
            for linha in itens_banco:
                lista_itens.append({
                    "codigo": linha[0],
                    "descricao": linha[1],
                    "valor": linha[2],
                    "qtd": linha[3],
                    "total": linha[4]
                })

            # Monta dados para o PDF
            dados_pdf = {
                "numero": dados[0],
                "data": dados[1],
                "cliente": {
                    "razao": dados[11],
                    "cnpj": dados[12] or "Não informado",
                    "end": dados[14] or "",
                    "num": dados[15] or "",
                    "bairro": dados[16] or "",
                    "cidade": dados[17] or "",
                    "uf": dados[18] or "",
                    "cep": dados[19] or ""
                },
                "vendedor": dados[3],
                "profundidade": dados[4] or "0",
                "total": dados[5],
                "desconto": dados[6],
                "imposto": dados[7],
                "total_final": dados[8],
                "vencimento": dados[9]
            }

            # Gera o PDF diretamente com todos os dados salvos
            gerar_pdf(dados_pdf, lista_itens)

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar orçamento: {e}")

    # Botões de ação
    frame_botoes = ttk.Frame(janela, padding=10)
    frame_botoes.pack(fill="x")
    ttk.Button(frame_botoes, text="Atualizar Lista", command=carregar_orcamentos).pack(side="left", padx=5)
    ttk.Button(frame_botoes, text="Reimprimir Orçamento", command=reimprimir_orcamento).pack(side="left", padx=5)
    ttk.Button(frame_botoes, text="Excluir Orçamento", command=excluir_orcamento).pack(side="right", padx=5)

    carregar_orcamentos()

# ---------------------- INICIO DO SISTEMA ----------------------
if __name__ == "__main__":
    # Inicia o sistema chamando a tela de login
    tela_login()