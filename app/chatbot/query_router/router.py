
import os
import sys
from semantic_router.encoders import OpenAIEncoder
from semantic_router.layer import RouteLayer
from semantic_router import Route
from semantic_router.encoders import BM25Encoder, TfidfEncoder
from semantic_router.hybrid_layer import HybridRouteLayer
from typing import List, TypeVar
from app.chatbot.query_router.routes import routes
from app.common.config import cfg


RouteChoice = TypeVar('RouteChoice')


class Router:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Router, cls).__new__(cls)
        return cls._instance

    def __init__(self, routes: List[Route]=routes, 
                top_k: int=cfg.top_k, 
                using_hybrid: bool=False, 
                sparse_encoder_name=None):
        if not hasattr(self, 'initialized'): # Prevent re-initialization
            self.initialized = True
            self.encoder = OpenAIEncoder() # default is text-embedding-ada-002
            
            if using_hybrid:
                if sparse_encoder_name == "BM25":
                    self.sparse_encoder = BM25Encoder()
                else:
                    self.sparse_encoder = TfidfEncoder()

                self.rl = HybridRouteLayer(
                    encoder=self.encoder, sparse_encoder=self.sparse_encoder, routes=routes
                )
            else:
                self.rl = RouteLayer(encoder=self.encoder, routes=routes)
            
            self.rl.top_k = top_k

    def predict(self, query: str) -> List[RouteChoice]:
        """
        This function takes a query and returns a list of RouteChoice objects.
        Args:
            query (str): The query to predict

        Returns:
            List[RouteChoice]: A list of RouteChoice objects
                            Ex: [RouteChoice(name='unclear_issue', function_call=None, similarity_score=0.8904590012)]
        """
        result = self.rl.retrieve_multiple_routes(query)
        return result
