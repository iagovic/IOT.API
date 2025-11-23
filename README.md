🧠 API de Análise de Compatibilidade com IA + OracleDB

Este projeto integra Oracle Database, Flask (Python) e Gemini 2.0 Flash (IA Generativa) para analisar a compatibilidade entre candidatos e vagas.
A solução busca dados do banco, envia para a IA e retorna um JSON estruturado com a análise completa.

📌 oracle.py — Arquivo da disciplina de Banco de Dados

O arquivo oracle.py foi criado especificamente para atender a disciplina de Banco de Dados.
Ele é responsável por:

Conectar ao OracleDB

Buscar usuários, vagas e competências

Organizar os dados antes de enviar para a IA

🤖 Funcionamento da IA

A API envia todos os dados do usuário e da vaga para o Gemini 2.0 Flash, que gera:

Compatibilidade entre cada candidato e todas as vagas

Melhor vaga para cada candidato

JSON final estruturado

🔗 Rota principal (retorna o JSON gerado pela IA)
http://127.0.0.1:5062/analise

⚙️ Tecnologias usadas

Python + Flask

OracleDB (oracledb)

Google Gemini 2.0 Flash

Dotenv

REST API

🚀 Como rodar

Instale dependências

pip install -r requirements.txt


Configure o .env com as variáveis do Oracle e da Google, exemplo de como o .env deve ficar 
(
GOOGLE_API_KEY=??????
ORACLE_USER=??????
ORACLE_PASS=??????
ORACLE_DSN=??????
)

Execute:

python app.py
