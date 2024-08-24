from enum import Enum
from llama_index.embeddings.openai import OpenAIEmbedding

class OpenAIEmbedModel(str, Enum):
    TEXT_EMBED_ADA_002 = "text-embedding-ada-002"
    TEXT_EMBED_3_LARGE = "text-embedding-3-large"
    TEXT_EMBED_3_SMALL = "text-embedding-3-small"

class OpenAIEmbedClient(OpenAIEmbedding):
    
    def __init__(self, model=OpenAIEmbedModel.TEXT_EMBED_3_SMALL):
        super().__init__(
            model=model
        )

    def embed(self, text):
        print("Embedding text", text)
        return self.get_text_embedding(text)
