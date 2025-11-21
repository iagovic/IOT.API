from flask import Flask, jsonify
import json
import oracledb
from dotenv import load_dotenv
import google.generativeai as genai
import os

# ============================
# Carregar variáveis do .env
# ============================
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASS = os.getenv("ORACLE_PASS")
ORACLE_DSN = os.getenv("ORACLE_DSN")

# ============================
# Configurar Gemini
# ============================
if not GOOGLE_API_KEY:
    raise ValueError("❌ GOOGLE_API_KEY ausente no arquivo .env")

genai.configure(api_key=GOOGLE_API_KEY)
MODEL = "gemini-2.0-flash"

app = Flask(__name__)

# ============================
# Conexão Oracle
# ============================
def connect_oracle():
    if not ORACLE_USER or not ORACLE_PASS or not ORACLE_DSN:
        raise ValueError("❌ Dados do Oracle ausentes no .env")

    return oracledb.connect(
        user=ORACLE_USER,
        password=ORACLE_PASS,
        dsn=ORACLE_DSN
    )

# ============================
# Buscar Candidatos
# ============================
def get_candidatos(conn):
    cursor = conn.cursor()

    query = """
        SELECT 
            U.USUARIO_ID AS ID,
            U.NOME,
            COALESCE(LISTAGG(C.NOME, ', ') WITHIN GROUP (ORDER BY C.NOME), '') AS COMPETENCIAS
        FROM USUARIOS U
        LEFT JOIN USUARIO_COMPETENCIAS UC ON UC.USUARIO_ID = U.USUARIO_ID
        LEFT JOIN COMPETENCIAS C ON C.COMPETENCIA_ID = UC.COMPETENCIA_ID
        GROUP BY U.USUARIO_ID, U.NOME
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    candidatos = []
    for r in rows:
        candidatos.append({
            "id": r[0],
            "nome": r[1],
            "competencias": r[2]
        })

    return candidatos

# ============================
# Buscar Vagas
# ============================
def get_vagas(conn):
    cursor = conn.cursor()

    query = """
        SELECT 
            VAGA_ID,
            TITULO,
            DESCRICAO,
            REQUISITOS
        FROM VAGAS
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    vagas = []
    for r in rows:
        descricao = r[2]
        if hasattr(descricao, "read"):
            descricao = descricao.read()

        vagas.append({
            "id": r[0],
            "titulo": r[1],
            "descricao": descricao,
            "requisitos": r[3]
        })

    return vagas

# ============================
# Análise via Gemini
# ============================
def analisar_compatibilidade(candidatos, vagas):

    prompt = f"""
Gere SOMENTE um JSON 100% válido seguindo exatamente esta estrutura:

{{
  "candidatos": [
    {{
      "id": <id>,
      "nome": "<nome>",
      "melhor_vaga": {{
        "vaga_id": <id>,
        "vaga_nome": "<titulo>",
        "compatibilidade": <0-100>
      }},
      "todas_as_vagas": [
        {{
          "vaga_id": <id>,
          "vaga_nome": "<titulo>",
          "compatibilidade": <0-100>
        }}
      ]
    }}
  ]
}}

Candidatos:
{json.dumps(candidatos, ensure_ascii=False)}

Vagas:
{json.dumps(vagas, ensure_ascii=False)}
"""

    response = genai.GenerativeModel(MODEL).generate_content(prompt)
    raw = response.text.strip()

    # 1. Tentativa direta
    try:
        return json.loads(raw)
    except:
        pass

    # 2. Tentar extrair JSON isolado
    try:
        extract = raw[raw.find("{"): raw.rfind("}") + 1]
        return json.loads(extract)
    except:
        raise ValueError("❌ JSON inválido retornado pelo Gemini:\n" + raw)


# ============================
# Rotas
# ============================

@app.get("/")
def home():
    return {"status": "API rodando com Gemini 2.0 + Oracle!"}

@app.get("/test-db")
def test_db():
    try:
        conn = connect_oracle()
        cur = conn.cursor()
        cur.execute("SELECT 'ORACLE OK' FROM dual")
        result = cur.fetchone()
        return {"oracle": result[0]}
    except Exception as e:
        return {"erro": str(e)}, 500

@app.get("/analise")
def analise():
    try:
        conn = connect_oracle()
        candidatos = get_candidatos(conn)
        vagas = get_vagas(conn)

        resultado = analisar_compatibilidade(candidatos, vagas)
        return jsonify(resultado)

    except Exception as e:
        return {"erro": str(e)}, 500


# ============================
# Executar servidor
# ============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5062, debug=True)
