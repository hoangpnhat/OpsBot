import os
from typing import Literal
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.core import SimpleDirectoryReader, PropertyGraphIndex
from llama_index.core.indices.property_graph import ImplicitPathExtractor, SchemaLLMPathExtractor
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from neo4j import GraphDatabase
import sys
import os
if os.getcwd() not in sys.path: sys.path.append(os.getcwd())
from app.utils.graph.schema_llm import CustomSchemaLLMPathExtractor
def delete_all(tx):
    tx.run("MATCH (n) DETACH DELETE n")

def get_driver():
    return GraphDatabase.driver(os.getenv("NEO4J_URL"), auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")))
def get_graph_store():
    return Neo4jPropertyGraphStore(
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD"),
        url=os.getenv("NEO4J_URL"),
    )
    # print(os.getenv("NEO4J_URL"))
    # return Neo4jPropertyGraphStore(
    #     username="neo4j",
    #     password="Q9XbcdaBhQqGXSn",
    #     url="bolt://34.142.247.255:7687",
    # )

def embed_documents(documents_path, entities, relations, validation_schema, graph_store):
    api_key = os.getenv("OPENAI_API_KEY")
    documents = SimpleDirectoryReader(documents_path).load_data()
    index = PropertyGraphIndex.from_documents(
        documents,
        embed_model=OpenAIEmbedding(model_name=os.environ.get("GRAPH_EMBEDDING"),api_key=api_key),
        kg_extractors=[
            ImplicitPathExtractor(),
            CustomSchemaLLMPathExtractor(
                llm=OpenAI(model=os.environ.get("LLM_GRAPH"), temperature=0.1, api_key=api_key),
                possible_entities=entities,
                possible_relations=relations,
                kg_validation_schema=validation_schema,
                strict=False,
            ),
        ],
        property_graph_store=graph_store,
        show_progress=True,
    )
    return index

def main():
    # Neo4j connection setup
    graph_store = get_graph_store()
    driver = get_driver()
    # Delete all nodes and relationships
    with driver.session() as session:
        session.execute_write(delete_all)
    # Paths from environment variables
    promotion_documents_path = os.getenv("PROMOTION_DOCUMENTS_PATH")

    # Embedding promotion documents
    promotion_entities = Literal["PROMOTION_PROGRAM", "ORDER", "CUSTOMER", "INVOICE", "STORE", "DATE", "LINK", "VOUCHER"]
    promotion_relations = Literal[
        "HAS", "HAS_CONTENT", "HAS_LINK", "HAS_CONDITIONS", "HAS_SCOPE", "HAS_REDUCTION", "HAS_VOUCHER",
        "FOR", "MINIMUM_REQUIRED", "BELONG_TO", "EXPIRY", "START_DATE", "END_DATE"
    ]
    promotion_validation_schema = {
        "PROMOTION_PROGRAM": [
            "HAS", "HAS_CONTENT", "HAS_LINK", "HAS_CONDITIONS", "HAS_SCOPE", "HAS_REDUCTION",
            "FOR", "MINIMUM_REQUIRED", "START_DATE", "END_DATE"
        ],
        "CUSTOMER": ["FOR"],
        "STORE": ["SCOPE"],
    }
    embed_documents(promotion_documents_path, promotion_entities, promotion_relations, promotion_validation_schema, graph_store)
     # Embedding voucher documents
    voucher_documents_path = os.getenv("VOUCHER_DOCUMENTS_PATH")
    voucher_entities = Literal["PROMOTION_PROGRAM", "SCOPE", "DATE", "VOUCHER"]
    voucher_relations = Literal[
        "HAS", "HAS_CONTENT", "HAS_SCOPE", "BELONG_TO", "START_DATE", "END_DATE"
    ]
    voucher_validation_schema = {
        "VOUCHER": ["HAS", "HAS_CONTENT", "HAS_SCOPE", "START_DATE", "END_DATE", "BELONG_TO"],
    }
    embed_documents(voucher_documents_path, voucher_entities, voucher_relations, voucher_validation_schema, graph_store)
if __name__ == "__main__":
    main()
