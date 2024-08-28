from typing import Optional, Dict, List, Tuple

from pydantic import BaseModel, ConfigDict


class Emb(BaseModel):
    """Base class for managing embedders"""

    dimensions: int = 1536

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def get_embedding(self, text: str) -> List[float]:
        raise NotImplementedError

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError