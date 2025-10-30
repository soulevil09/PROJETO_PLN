import logging
import time
from typing import Dict, Any
from django.conf import settings
from transformers import pipeline, AutoTokenizer
import torch

logger = logging.getLogger('app')

class NLPService:
    _pipeline = None
    _tokenizer = None

    @classmethod
    def get_pipeline(cls):
        """
        Carrega o pipeline com otimização de memória.
        """
        if cls._pipeline is None:
            try:
                task = settings.HF_TASK
                model_name = settings.HF_MODEL
                logger.info(f'Carregando pipeline Transformers task={task} model={model_name}')
                
                # --- CORREÇÃO DE MEMÓRIA (QUE FUNCIONOU) ---
                cls._tokenizer = AutoTokenizer.from_pretrained(model_name)
                
                model_args = {
                    "device_map": "auto",
                    "offload_folder": "offload_cache"
                }

                cls._pipeline = pipeline(
                    task=task, 
                    model=model_name, 
                    tokenizer=cls._tokenizer,
                    model_kwargs=model_args 
                )
                
                # Lógica de padding do professor
                if task == "text-generation":
                    if cls._pipeline.tokenizer.pad_token_id is None:
                        logger.warning("pad_token_id não definido. Usando eos_token_id como pad_token_id.")
                        cls._pipeline.tokenizer.pad_token_id = cls._pipeline.tokenizer.eos_token_id
                
                logger.info("Pipeline carregado com sucesso.")

            except Exception as e:
                logger.error(f"Erro CRÍTICO ao carregar o pipeline: {e}")
                raise e # Lança o erro para a view

        return cls._pipeline

    @classmethod
    def generate(cls, prompt: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera uma resposta e RETORNA UM DICIONÁRIO,
        corrigindo o 'TypeError' na views.py.
        """
        start = time.time()
        gen_kwargs = {}
        task = ""
        try:
            pl = cls.get_pipeline() # Pode lançar um erro
            task = settings.HF_TASK
            
            gen_kwargs = {
                # 'max_new_tokens' estava causando o warning, vamos usar o padrão
                'max_length': int(params.get('max_length', 150)), 
            }
            
            if task == "text-generation":
                if pl.tokenizer.pad_token_id is not None:
                    gen_kwargs['pad_token_id'] = pl.tokenizer.pad_token_id
                else:
                    gen_kwargs['pad_token_id'] = pl.tokenizer.eos_token_id
            
            logger.info(f"Gerando resposta para o prompt: '{prompt[:50]}...'")
            outputs = pl(prompt, **gen_kwargs)
            
            elapsed = time.time() - start

            # --- TRATAMENTO DE RESPOSTA ---
            text = ""
            if isinstance(outputs, list) and outputs:
                text_bruto = outputs[0]['generated_text']
                
                if task == "text-generation": # Limpa o prompt
                    if text_bruto.startswith(prompt):
                        text = text_bruto[len(prompt):].strip()
                    else:
                        text = text_bruto.strip()
                else: # Resposta direta (ex: flan-t5)
                    text = text_bruto.strip()
                
                if not text:
                     text = "[O modelo gerou uma resposta vazia]"
            else:
                text = "Erro: O modelo não gerou resposta."
            
            logger.info("Resposta gerada e tratada com sucesso.")
            
            return {
                'response_text': text,
                'elapsed_seconds': elapsed,
                'used_params': gen_kwargs,
                'model': settings.HF_MODEL,
                'task': task,
            }
        
        except Exception as e:
            # --- CORREÇÃO DO TypeError ---
            # Se der erro (ex: no get_pipeline), retorna um 
            # dicionário de erro, e não uma string.
            logger.error(f"Erro na função generate: {e}")
            return {
                'response_text': f"Erro ao gerar resposta: {e}",
                'elapsed_seconds': time.time() - start,
                'used_params': gen_kwargs,
                'model': settings.HF_MODEL,
                'task': task or 'unknown',
            }

