# app/views.py
import csv
import json
import logging
import uuid
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from .forms import ChatForm
from .services.mongo_repo import MongoRepo
from .services.nlp_service import NLPService

logger = logging.getLogger('app')
mongo = MongoRepo()

def _get_or_create_session_id(request: HttpRequest) -> str:
    sid = request.session.get('session_id')
    if not sid:
        sid = str(uuid.uuid4())
        request.session['session_id'] = sid
    return sid

@require_http_methods(["GET", "POST"])
def chat_view(request: HttpRequest):
    session_id = _get_or_create_session_id(request)
    context = {'session_id': session_id}

    if request.method == 'POST':
        form = ChatForm(request.POST)
        if form.is_valid():
            prompt = form.cleaned_data['prompt'].strip()
            params = {
                'max_new_tokens': form.cleaned_data.get('max_new_tokens') or 128,
                'temperature': form.cleaned_data.get('temperature') or 0.7,
            }
            try:
                nlp_result = NLPService.generate(prompt, params)
                response_text = nlp_result['response_text']
                elapsed = nlp_result['elapsed_seconds']
                # Registro no Mongo
                record = {
                    'session_id': session_id,
                    'prompt': prompt,
                    'response': response_text,
                    'model': nlp_result['model'],
                    'task': nlp_result['task'],
                    'params': nlp_result['used_params'],
                    'latency_seconds': elapsed,
                }
                mongo.insert_interaction(record)
                context.update({'form': ChatForm(), 'response_text': response_text, 'latency': elapsed})
                messages.success(request, 'Resposta gerada com sucesso.')
            except Exception as e:
                logger.exception('Erro ao gerar resposta')
                messages.error(request, 'Ocorreu um erro ao processar sua solicitação. Tente novamente.')
                context['form'] = form
        else:
            messages.error(request, 'Verifique os campos do formulário.')
            context['form'] = form
    else:
        context['form'] = ChatForm()

    return render(request, 'chat.html', context)

@require_http_methods(["GET"])
def history_view(request: HttpRequest):
    session_id = request.GET.get('session_id') or request.session.get('session_id')
    model = request.GET.get('model') or None
    q = request.GET.get('q') or None
    page = int(request.GET.get('page') or 1)
    page_size = int(request.GET.get('page_size') or 10)

    data = mongo.list_interactions(session_id=session_id, model=model, q=q, page=page, page_size=page_size)
    context = {
        'session_id': session_id,
        'model': model,
        'q': q,
        'page': data['page'],
        'page_size': data['page_size'],
        'total': data['total'],
        'items': data['items'],
    }
    return render(request, 'history.html', context)

@require_http_methods(["GET"])
def export_view(request: HttpRequest):
    fmt = request.GET.get('format', 'csv').lower()
    session_id = request.GET.get('session_id') or request.session.get('session_id')
    model = request.GET.get('model') or None
    q = request.GET.get('q') or None

    items = mongo.all_for_export(session_id=session_id, model=model, q=q)

    if fmt == 'json':
        response = HttpResponse(json.dumps(items, ensure_ascii=False, default=str), content_type='application/json; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="interactions.json"'
        return response
    else:
        # CSV padrão
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="interactions.csv"'
        writer = csv.writer(response)
        writer.writerow(['_id', 'created_at', 'session_id', 'model', 'task', 'prompt', 'response', 'latency_seconds', 'params'])
        for it in items:
            writer.writerow([
                it.get('_id', ''),
                it.get('created_at', ''),
                it.get('session_id', ''),
                it.get('model', ''),
                it.get('task', ''),
                it.get('prompt', '').replace('\n', ' ')[:10000],
                it.get('response', '').replace('\n', ' ')[:10000],
                it.get('latency_seconds', ''),
                json.dumps(it.get('params', {}), ensure_ascii=False),
            ])
        return response