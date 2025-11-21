from flask import Flask, jsonify
import json
import oracledb
from openai import OpenAI
from dotenv import load_dotenv
import os

# ------------------------------
# CARREGAR VARIÁVEIS DE AMBIENTE
# ------------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASS = os.getenv("ORACLE_PASS")
ORACLE_DSN  = os.getenv("ORACLE_DSN")

client = OpenAI(api_key=OPENAI_API_KEY)
app = Flask(__name__)

# ------------------------------
# CONEXÃO ORACLE
# ------------------------------
def connect_oracle():
    if not ORACLE_USER or not ORACLE_PASS or not ORACLE_DSN:
        raise ValueError("Credenciais do Oracle não definidas. Verifique o .env")
    return oracledb.connect(
        user=ORACLE_USER,
        password=ORACLE_PASS,
        dsn=ORACLE_DSN
    )

# ------------------------------
# BUSCAR CANDIDATOS
# ------------------------------
def get_candidatos(conn):
    cursor = conn.cursor()
    query = """
        SELECT 
            U.USUARIO_ID AS CANDIDATO_ID,
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

# ------------------------------
# BUSCAR VAGAS
# ------------------------------
def get_vagas(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT VAGA_ID, TITULO, DESCRICAO, REQUISITOS FROM VAGAS")
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

# ------------------------------
# ANÁLISE OPENAI
# ------------------------------
def analisar_compatibilidade(candidatos, vagas):

    # Prompt em string normal (sem f-string)
    prompt = """
Você receberá uma lista de candidatos e uma lista de vagas.
Compare cada candidato com todas as vagas e produza um JSON válido com o seguinte formato exato:

{
  "candidatos": [
    {
      "id": <id_do_candidato>,
      "nome": "<nome_do_candidato>",
      "melhor_vaga": {
        "vaga_id": <id_da_vaga_com_maior_compatibilidade>,
        "vaga_nome": "<titulo_da_vaga>",
        "compatibilidade": <score_de_0_a_100>
      },
      "todas_as_vagas": [
        {
          "vaga_id": <id_da_vaga>,
          "vaga_nome": "<titulo_da_vaga>",
          "compatibilidade": <score>
        }
      ]
    }
  ]
}

Regras:
- O JSON deve ser 100% válido.
- Não inclua comentários, explicações ou texto fora do JSON.
- Calcule compatibilidade analisando descrição, habilidades, experiência e requisitos.
- Use exatamente os nomes "nome" para o nome do candidato e "vaga_nome" para o nome da vaga.

Candidatos:
"""

    # Adiciona os dados reais no final do prompt
    prompt += json.dumps(candidatos, ensure_ascii=False)
    prompt += "\n\nVagas:\n"
    prompt += json.dumps(vagas, ensure_ascii=False)

    # Chamada a OpenAI
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    conteudo = response.choices[0].message.content.strip()

    if not (conteudo.startswith("{") or conteudo.startswith("[")):
        raise ValueError("⚠ A OpenAI não retornou JSON válido.")

    return json.loads(conteudo)

# ------------------------------
# ROTA DA API
# ------------------------------
@app.get("/analise")
def analise():
    conn = connect_oracle()
    candidatos = get_candidatos(conn)
    vagas = get_vagas(conn)
    resultado = analisar_compatibilidade(candidatos, vagas)
    return jsonify(resultado)

# ------------------------------
# RUN
# ------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5062, debug=True)
