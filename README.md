Projeto: Django + Transformers (Hugging Face) + MongoDB Atlas

Aplicação web construída com Django que integra modelos de NLP via Transformers (Hugging Face) e persiste interações no MongoDB (Atlas). O projeto usa variáveis de ambiente (.env) para configuração e segue uma estrutura de pastas simples com serviços para NLP e banco de dados.
Sumário

    Visão geral
    Stack e requisitos
    Estrutura de pastas
    Configuração do ambiente
    Variáveis de ambiente
    Comandos úteis
    Fluxo de dados
    Troubleshooting
    Boas práticas
    Licença

Visão geral

    Backend: Django 5.x
    NLP: transformers.pipeline (modelo padrão google/flan-t5-small, tarefa text2text-generation)
    Banco: MongoDB Atlas via PyMongo
    Configuração: django-environ com .env

Stack e requisitos

    Python 3.11+ (testado em Windows)
    Pacotes principais:
        django
        django-environ
        pymongo
        transformers
        torch (CPU se não houver CUDA)
        accelerate (opcional)
    Outros: virtualenv/venv

Instalação típica:

bash

Copy
# Windows PowerShell  
.\venv\Scripts\Activate.ps1  
pip install -r requirements.txt  

Se precisar instalar do zero:

bash

Copy
pip install django django-environ pymongo transformers accelerate  
# Torch (CPU)  
pip install torch --index-url https://download.pytorch.org/whl/cpu  

Estrutura de pastas

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

Configuração do ambiente

    Crie e ative a venv

bash

Copy
python -m venv venv  
# PowerShell  
.\venv\Scripts\Activate.ps1  

    Instale dependências

bash

Copy
pip install -r requirements.txt  
# ou conforme a seção de requisitos  

    Configure o .env

    Copie .env.example para .env:

bash

Copy
copy .env.example .env  

    Edite os valores reais (sem aspas e sem espaços no fim da linha).

    Migrações e servidor

bash

Copy
python manage.py migrate  
python manage.py runserver  

Variáveis de ambiente

Exemplo (veja .env.example):

DEBUG=True  
SECRET_KEY=your-secret-key-here-generate-a-new-one  
ALLOWED_HOSTS=127.0.0.1,localhost  
  
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

Comandos úteis

    Verificar configurações:

bash

Copy
python manage.py check  

    Aplicar migrações:

bash

Copy
python manage.py migrate  

    Rodar servidor:

bash

Copy
python manage.py runserver  

    Gerar SECRET_KEY:

bash

Copy
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"  

Fluxo de dados

    View recebe um prompt do usuário.
    NLPService usa transformers.pipeline(task=HF_TASK, model=HF_MODEL) para gerar saída.
    MongoRepo registra a interação em MONGO_COLLECTION no DB MONGO_DB_NAME (MongoDB Atlas via MONGO_URI).
    Resposta é renderizada no template e/ou API.

Troubleshooting

    ModuleNotFoundError (services):
        Confirme app/services/nlp_service.py e app/services/mongo_repo.py.
        Garanta __init__.py em app/ e app/services/.
        Ajuste imports: from .services.nlp_service import NLPService.
    WSGI_APPLICATION inválido:
        Use django_hf_ml.wsgi.application.
    .env inválido:
        Remova aspas e espaços no final das linhas.
        Para robustez no settings.py, use .strip() nos valores críticos.
    MongoDB InvalidName:
        MONGO_DB_NAME não pode conter espaços, /, \, " etc.
    Torch/Transformers:
        Se não tiver CUDA, instale Torch CPU via index da PyTorch.

Boas práticas

    Versione .env.example, nunca .env.
    Atualize requirements.txt após instalar pacotes:

bash

Copy
pip freeze > requirements.txt  

    Crie índices no Mongo para campos consultados com frequência (ex.: created_at, session_id, model).
    Logue eventos chave (carregamento de pipeline, conexão com Mongo, exceções).

Licença

    Defina a licença do projeto aqui (por exemplo, MIT). Se não definida ainda, não sei.
