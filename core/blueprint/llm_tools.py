

import json
import re
from typing import Any, Dict, List, Union

import numpy as np
from sklearn.preprocessing import Normalizer, PolynomialFeatures

from ..embeddings.embedding_factory import EmbeddingFactory


class LLMTools:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMTools, cls).__new__(cls)
            cls._initialized = False
            cls._instance.__init__()
            
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
    
    def extract_json_from_text(self,text: str) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        json_match = re.search(r'(\[[\s\S]*\]|\{[\s\S]*\})', text)
        if json_match:
            json_str = json_match.group()
            return json.loads(json_str)
        raise json.JSONDecodeError("No valid JSON found in the text", text, 0)
    
    def extract_code(self, content: str) -> str:
        code_match = re.search(r'```python(.*?)```', content, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        else:
            return content.strip()
            
    def expand_features(self,embedding, target_length):  #使用了正则来归一向量
        poly = PolynomialFeatures(degree=2)
        expanded_embedding = poly.fit_transform(embedding.reshape(1, -1))
        expanded_embedding = expanded_embedding.flatten()
        if len(expanded_embedding) > target_length:
            expanded_embedding = expanded_embedding[:target_length]
        elif len(expanded_embedding) < target_length:
            expanded_embedding = np.pad(expanded_embedding, (0, target_length - len(expanded_embedding)))
        normalizer = Normalizer(norm='l2')
        expanded_embedding = normalizer.transform(expanded_embedding.reshape(1, -1)).flatten()
        return expanded_embedding
    
    def _all_embedding_dimensions(self):
        from core.utils.tsdata import check_proxy_running
        check_proxy_running("127.0.0.1", 1087, "http")
        factory = EmbeddingFactory()
        elist = factory.list_available_embeddings()
        for i in elist:
            e= factory.get_instance(i)
            embeds=e.convert_to_embedding(["中国"])
            lengrg = len(embeds[0])
            print(f"{i} has {lengrg} dimensions")