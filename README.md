LINK PARA O VIDEO DEMONSTRANDO TODO O CODIGO

https://youtu.be/onrJng93ae4

🧠 API de Análise de Compatibilidade com IA + OracleDB

Este projeto integra Oracle Database, Flask (Python) e Gemini 2.0 Flash (IA Generativa) para analisar a compatibilidade entre candidatos e vagas.
A solução busca dados do banco, envia para a IA e retorna um JSON estruturado com a análise completa.

📌 oracle.py — Arquivo da Disciplina de Banco de Dados

O arquivo oracle.py foi criado especificamente para atender aos requisitos da disciplina de Banco de Dados.
Ele é responsável por:

Conectar ao OracleDB

Buscar usuários, vagas e competências

Organizar e estruturar os dados antes de enviar para a IA

🤖 Funcionamento da IA

A API envia todas as informações dos usuários e vagas para o modelo Gemini 2.0 Flash, que gera:

Compatibilidade entre cada candidato e todas as vagas

A melhor vaga para cada candidato

Um JSON final estruturado, pronto para uso no frontend ou mobile

🔗 Rota Principal

Retorna o JSON gerado pela IA:

http://127.0.0.1:5062/analise

⚙️ Tecnologias Utilizadas

Python + Flask

OracleDB (oracledb)

Google Gemini 2.0 Flash

dotenv (.env)

REST API

🚀 Como Rodar
1️⃣ Instalar dependências
pip install -r requirements.txt

2️⃣ Configurar o arquivo .env

Exemplo:

GOOGLE_API_KEY=??????
ORACLE_USER=??????
ORACLE_PASS=??????
ORACLE_DSN=??????

3️⃣ Executar a API
python app.py
