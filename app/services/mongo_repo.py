# app/services/mongo_repo.py
import os
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pymongo import MongoClient, DESCENDING
from django.conf import settings

logger = logging.getLogger('app')

class MongoRepo:
    def __init__(self):
        uri = settings.MONGO_URI
        db_name = settings.MONGO_DB_NAME
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[settings.MONGO_COLLECTION]
        # Índices úteis para filtros
        self.collection.create_index([('session_id', DESCENDING)])
        self.collection.create_index([('created_at', DESCENDING)])
        self.collection.create_index([('model', DESCENDING)])

    def insert_interaction(self, data: Dict[str, Any]) -> str:
        data['created_at'] = data.get('created_at') or datetime.utcnow()
        res = self.collection.insert_one(data)
        return str(res.inserted_id)

    def list_interactions(
        self,
        session_id: Optional[str] = None,
        model: Optional[str] = None,
        q: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        sort_field: str = 'created_at',
        sort_dir: int = -1
    ) -> Dict[str, Any]:
        query: Dict[str, Any] = {}
        if session_id:
            query['session_id'] = session_id
        if model:
            query['model'] = model
        if q:
            # Busca simples em prompt/resposta
            query['$or'] = [
                {'prompt': {'$regex': q, '$options': 'i'}},
                {'response': {'$regex': q, '$options': 'i'}}
            ]

        total = self.collection.count_documents(query)
        skip = (page - 1) * page_size
        cursor = self.collection.find(query).sort(sort_field, sort_dir).skip(skip).limit(page_size)
        items = []
        for doc in cursor:
            doc['_id'] = str(doc['_id'])
            items.append(doc)

        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'items': items,
        }

    def all_for_export(
        self,
        session_id: Optional[str] = None,
        model: Optional[str] = None,
        q: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        data = self.list_interactions(session_id=session_id, model=model, q=q, page=1, page_size=1000000)
        return data['items']