# app/services/nlp_service.py
import logging
import time
from typing import Dict, Any
from django.conf import settings
from transformers import pipeline

logger = logging.getLogger('app')

class NLPService:
    _pipeline = None

    @classmethod
    def get_pipeline(cls):
        if cls._pipeline is None:
            task = settings.HF_TASK
            model = settings.HF_MODEL
            logger.info(f'Loading Transformers pipeline task={task} model={model}')
            # Para modelos baseados em T5/bart/Flan, use text2text-generation; para modelos causais, text-generation.
            cls._pipeline = pipeline(task=task, model=model)
        return cls._pipeline

    @classmethod
    def generate(cls, prompt: str, params: Dict[str, Any]) -> Dict[str, Any]:
        pl = cls.get_pipeline()
        start = time.time()
        # Parâmetros padrão razoáveis
        gen_kwargs = {
            'max_new_tokens': int(params.get('max_new_tokens', 128)),
            'temperature': float(params.get('temperature', 0.7)),
        }
        outputs = pl(prompt, **gen_kwargs)
        elapsed = time.time() - start

        # Normalização do retorno (para text2text-generation)
        if isinstance(outputs, list) and outputs and 'generated_text' in outputs[0]:
            text = outputs[0]['generated_text']
        elif isinstance(outputs, list) and outputs and 'summary_text' in outputs[0]:
            text = outputs[0]['summary_text']
        else:
            text = str(outputs)

        return {
            'response_text': text,
            'elapsed_seconds': elapsed,
            'used_params': gen_kwargs,
            'model': settings.HF_MODEL,
            'task': settings.HF_TASK,
        }