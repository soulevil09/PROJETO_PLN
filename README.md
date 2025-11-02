# Projeto: Django + Transformers (Hugging Face) + MongoDB Atlas

Aplicação web construída com Django que integra modelos de NLP via Transformers (Hugging Face) e persiste interações no MongoDB (Atlas). O projeto usa variáveis de ambiente (.env) para configuração e segue uma estrutura de pastas simples com serviços para NLP e banco de dados.
Sumário

## Sumário 
    Stack e requisitos
    Estrutura de pastas
    Configuração do ambiente
    Variáveis de ambiente
    Comandos úteis
    Fluxo de dados
    Troubleshooting
    Boas práticas
    Licença

## Visão geral

    Backend: Django 5.x
    NLP: transformers.pipeline (modelo padrão google/flan-t5-small, tarefa text2text-generation)
    Banco: MongoDB Atlas via PyMongo
    Configuração: django-environ com .env

## Stack e requisitos

    Python 3.11+ (testado em Windows)
    Pacotes principais:
        django
        django-environ
        pymongo
        transformers
        torch (CPU se não houver CUDA)
        accelerate (opcional)
    Outros: virtualenv/venv
    
## Configuração do ambiente
Instruções testadas e validadas (A4) no Windows.

## Pré-requisitos (Python)
Este projeto requer Python 3.10+. Ao instalar o Python no Windows, é altamente recomendado marcar a caixa de seleção "Add python.exe to PATH".

Se o comando python não for reconhecido, use py como alternativa (ex: py -m venv venv).

## Crie e Ative a Venv

No terminal, dentro da pasta do projeto (PROJETO_PLN), crie o ambiente virtual:

Você deve ativar o ambiente antes de instalar os pacotes. O comando muda dependendo do seu terminal:

**Para Command Prompt (CMD):**

.\venv\Scripts\activate.bat

**Para Windows PowerShell:**

.\venv\Scripts\Activate.ps1

    Atenção: Se este comando abrir o Bloco de Notas, sua política de segurança do PowerShell está bloqueando scripts. Você pode permitir temporariamente com o comando Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process e tentar novamente, ou simplesmente usar o terminal CMD. 

## Instale as Dependências

A instalação do torch (PyTorch) depende do seu ambiente.

 **Caso 1:** 
    
    Se você JÁ POSSUI o torch instalado no seu computador:

    Você (provavelmente) pode rodar o comando de instalação direta. Com o (venv) ativo, execute: **pip install -r requirements.txt**

    (O pip deve reconhecer sua instalação existente e pular o torch).

**Caso 2:** 

    Se você NÃO TEM o torch instalado (uma instalação limpa):
    
    O comando pip install -r requirements.txt vai falhar com o erro ERROR: Could not find a version....
    
    Neste caso, siga estes 3 passos:
    
    1. Abra o arquivo requirements.txt e APAGUE a linha torch==2.9.0+cpu. Salve o arquivo.
    
    2. Com o (venv) ativo, instale todas as outras dependências: **pip install -r requirements.txt**
    
    3. Instale o torch (CPU) separadamente com o comando correto: **pip install torch --index-url https://download.pytorch.org/whl/cpu**

## Configure o .env

Copie o arquivo de exemplo para criar seu arquivo de configuração local. O comando muda dependendo do seu terminal:

**CMD:** copy .env.example .env

**No PowerShell:** Copy-Item .env.example .env

Agora, abra o arquivo .env e preencha os valores reais (sem aspas e sem espaços no fim da linha):

SECRET_KEY: (Use este comando para gerar uma nova: py -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

MONGO_URI: (Preencha com a string de conexão do MongoDB Atlas fornecida pelo A1-Infra)

ALLOWED_HOSTS: 127.0.0.1,localhost

CSRF_TRUSTED_ORIGINS: http://127.0.0.1:8000,http://localhost:8000

## Migrações e Servidor

Com o (venv) ativo e o .env configurado:

Execute as migrações do banco de dados (para criar tabelas de admin, etc.): py manage.py migrate

Inicie o servidor de desenvolvimento: py manage.py runserver

O site estará disponível em http://127.0.0.1:8000/.

## Estrutura de pastas

projeto/  
  manage.py  
  .env                 # NÃO versionar  
  .env.example         # Template versionado  
  requirements.txt  
  django_hf_ml/  
    __init__.py  
    settings.py  
    urls.py  
    wsgi.py  
  app/  
    __init__.py  
    urls.py  
    views.py  
    templates/  
      # HTML templates  
    static/  
      # arquivos estáticos (css/js/img)  
    services/  
      __init__.py  
      mongo_repo.py  
      nlp_service.py  
  venv/  
  .gitignore  
  README.md  

Pontos importantes:

    WSGI_APPLICATION deve ser django_hf_ml.wsgi.application.
    Pastas app/ e app/services/ precisam de __init__.py.
    Evite imports no app/__init__.py para não criar ciclos.

# MongoDB Atlas  
MONGO_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/?appName=Cluster0  
MONGO_DB_NAME=django_hf_ml  
MONGO_COLLECTION=interactions  
  
# Hugging Face / Transformers  
HF_MODEL=google/flan-t5-large  
HF_TASK=text2text-generation  
HF_API_TOKEN=  
  
# CSRF  
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000  

Notas:

    Não use aspas nos valores.
    Evite espaços ao final das linhas.
    Se a MONGO_URI incluir o nome do DB, mantenha MONGO_DB_NAME coerente.
 

Fluxo de dados

    View recebe um prompt do usuário.
    NLPService usa transformers.pipeline(task=HF_TASK, model=HF_MODEL) para gerar saída.
    MongoRepo registra a interação em MONGO_COLLECTION no DB MONGO_DB_NAME (MongoDB Atlas via MONGO_URI).
    Resposta é renderizada no template e/ou API.


Boas práticas

    Versione .env.example, nunca .env.
    Atualize requirements.txt após instalar pacotes:

bash

Copy
pip freeze > requirements.txt  

    Crie índices no Mongo para campos consultados com frequência (ex.: created_at, session_id, model).
    Logue eventos chave (carregamento de pipeline, conexão com Mongo, exceções).


