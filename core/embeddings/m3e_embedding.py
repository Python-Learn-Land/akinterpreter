from sentence_transformers import SentenceTransformer
from typing import List
from ._embedding import Embedding

class M3EEmbedding(Embedding):
    def __init__(self):
        from ..utils.get_sentence_device import get_sentence_transformer_device
        device = get_sentence_transformer_device()
        self.model = SentenceTransformer('moka-ai/m3e-base',device=device)

    def convert_to_embedding(self, input_strings: List[str]) -> List[List[float]]:
        return self.model.encode(input_strings).tolist()
    
    @property
    def vector_size(self) -> int:
        return 768