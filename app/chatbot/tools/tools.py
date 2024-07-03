from app.chatbot.tools.product import search_product
from app.chatbot.tools.promotion import query_promotion
from app.chatbot.tools.tool_schemas import search_product as search_product_schema
from app.chatbot.tools.tool_schemas import query_promotion as query_promotion_schema

external_tool_info = {
    "search_product": {
        "name": "search_product",
        "id": "/vdxxx",
        "type": "external",
        "schema": search_product_schema,
        "function": search_product
    },
    "query_promotion": {
        "name": "query_promotion",
        "id": "/vdyyy",
        "type": "external",
        "schema": query_promotion_schema,
        "function": query_promotion
    }
}