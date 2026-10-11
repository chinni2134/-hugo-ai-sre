# pyrefly: ignore [missing-import]
from sentence_transformers import SentenceTransformer


class EmbeddingService:

    def __init__(self):
        self.model_name = "all-MiniLM-L6-v2" 

        self.device = "mps"

        self.model = SentenceTransformer(
            self.model_name,
            device=self.device,
        )

    def embed_text(self, text: str) -> list[float]:
        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()

    def embed_texts(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
        )

        return embeddings.tolist()


embedding_service = EmbeddingService()