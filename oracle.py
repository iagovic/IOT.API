import oracledb
import json
import os
from dotenv import load_dotenv

# =======================================================
# 1. CARREGAR VARIÁVEIS DO .env
# =======================================================
load_dotenv()

ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASS = os.getenv("ORACLE_PASS")
ORACLE_DSN = os.getenv("ORACLE_DSN")

# =======================================================
# 2. CONEXÃO ORACLE
# =======================================================
def conectar():
    try:
        print("\n🔄 Conectando ao Oracle...")
        conn = oracledb.connect(
            user=ORACLE_USER,
            password=ORACLE_PASS,
            dsn=ORACLE_DSN
        )
        print("✅ Conectado com sucesso!")
        return conn

    except Exception as e:
        print("❌ Erro ao conectar:", e)
        return None


# =======================================================
# 3. EXECUTAR PROCEDURE inserir_usuario
# =======================================================
def inserir_usuario(nome, email, senha_hash):
    conn = conectar()
    cur = conn.cursor()

    try:
        print("\n➡️ Executando inserir_usuario...")

        cur.callproc("FUTURO_TRABALHO_PKG.inserir_usuario", [
            nome,
            email,
            senha_hash
        ])

        conn.commit()
        print("✅ Usuário inserido com sucesso!")

    except Exception as e:
        print("❌ Erro:", e)

    finally:
        cur.close()
        conn.close()


# =======================================================
# 4. EXECUTAR inserir_competencia_usuario
# =======================================================
def inserir_competencia(email, competencia, nivel):
    conn = conectar()
    cur = conn.cursor()

    try:
        print("\n➡️ Executando inserir_competencia_usuario...")

        # ================================
        # Validar nível conforme Oracle (1.0 a 5.0)
        # ================================
        try:
            nivel = float(nivel)
        except:
            print("❌ O nível deve ser um número válido (ex: 3.5)")
            return

        if not (1.0 <= nivel <= 5.0):
            print("❌ O nível deve estar entre 1.0 e 5.0")
            return

        # ================================
        # Chamar a procedure direto
        # ================================
        cur.callproc(
            "FUTURO_TRABALHO_PKG.inserir_competencia_usuario",
            [email, competencia, nivel]
        )

        conn.commit()
        print("✅ Competência inserida com sucesso!")

    except Exception as e:
        print("❌ Erro ao inserir competência:", e)

    finally:
        cur.close()
        conn.close()


# =======================================================
# 5. EXECUTAR Função calcular_compatibilidade_vaga
# =======================================================
def calcular_compatibilidade(email, vaga):
    conn = conectar()
    cur = conn.cursor()

    try:
        print("\n➡️ Executando calcular_compatibilidade_vaga...")

        retorno = cur.callfunc(
            "FUTURO_TRABALHO_PKG.calcular_compatibilidade_vaga",
            oracledb.STRING,
            [email, vaga]
        )

        print("📄 JSON retornado:")
        print(retorno)

    except Exception as e:
        print("❌ Erro:", e)

    finally:
        cur.close()
        conn.close()


# =======================================================
# 6. EXECUTAR Função gerar_perfil_json_manual
# =======================================================
def gerar_json_usuario(email):
    conn = conectar()
    cur = conn.cursor()

    try:
        print("\n➡️ Executando gerar_perfil_json_manual...")

        retorno = cur.callfunc(
            "FUTURO_TRABALHO_PKG.gerar_perfil_json_manual",
            oracledb.CLOB,
            [email]
        )

        print("📄 JSON do usuário:")
        print(retorno.read())

    except Exception as e:
        print("❌ Erro:", e)

    finally:
        cur.close()
        conn.close()


# =======================================================
# 7. EXPORTAÇÃO LOCAL PARA JSON (SEM UTL_FILE)
# =======================================================
def exportar_json_local():
    conn = conectar()
    cur = conn.cursor()

    print("\n📥 Coletando dados...")

    # USUARIOS
    cur.execute("SELECT USUARIO_ID, NOME, EMAIL FROM USUARIOS")
    usuarios = [
        {"id": u[0], "nome": u[1], "email": u[2]}
        for u in cur.fetchall()
    ]

    # COMPETENCIAS
    cur.execute("""
        SELECT U.EMAIL, C.NOME, UC.NIVEL_PONTUACAO
        FROM USUARIO_COMPETENCIAS UC
        JOIN USUARIOS U ON UC.USUARIO_ID = U.USUARIO_ID
        JOIN COMPETENCIAS C ON UC.COMPETENCIA_ID = C.COMPETENCIA_ID
    """)
    competencias = [
        {"email": c[0], "competencia": c[1], "nivel": c[2]}
        for c in cur.fetchall()
    ]

    # CURSOS
    cur.execute("""
        SELECT U.EMAIL, C.TITULO, I.STATUS
        FROM INSCRICOES I
        JOIN USUARIOS U ON I.USUARIO_ID = U.USUARIO_ID
        JOIN CURSOS C ON I.CURSO_ID = C.CURSO_ID
    """)
    cursos = [
        {"email": c[0], "curso": c[1], "status": c[2]}
        for c in cur.fetchall()
    ]

    final_json = {
        "usuarios": usuarios,
        "competencias": competencias,
        "cursos": cursos
    }

    with open("backup_completo.json", "w", encoding="utf-8") as f:
        json.dump(final_json, f, indent=4, ensure_ascii=False)

    print("📦 Backup criado: backup_completo.json")

    conn.close()


# =======================================================
# 8. MENU DE TESTES NO CONSOLE
# =======================================================
def menu():
    while True:
        print("""
============================
  🔧 MENU ORACLE CONSOLE
============================
1 - Inserir Usuário
2 - Inserir Competência em Usuário
3 - Calcular Compatibilidade
4 - Gerar JSON do Usuário
5 - Exportar JSON Local (backup)
0 - Sair
""")

        op = input("Escolha uma opção: ")

        if op == "1":
            nome = input("Nome: ")
            email = input("Email: ")
            senha = input("Senha (hash): ")
            inserir_usuario(nome, email, senha)

        elif op == "2":
            email = input("Email do usuário: ")
            comp = input("Competência: ")
            nivel = input("Nível (0-100): ")
            inserir_competencia(email, comp, nivel)

        elif op == "3":
            email = input("Email do usuário: ")
            vaga = input("Título da vaga: ")
            calcular_compatibilidade(email, vaga)

        elif op == "4":
            email = input("Email: ")
            gerar_json_usuario(email)

        elif op == "5":
            exportar_json_local()

        elif op == "0":
            print("Finalizado.")
            break

        else:
            print("Opção inválida!")


# =======================================================
# 9. RODAR O PROGRAMA
# =======================================================
if __name__ == "__main__":
    menu()
