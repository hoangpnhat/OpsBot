rewrite_query_prompt="""
Your task is to help REWRITE the Vietnamese-request user and the English query needed for your graph database. 
Focus on translating and summarizing the user's query to retrieve information related to prominent entities such as "PROMOTION PROGRAM," "ORDER," "CUSTOMER," "INVOICE," "STORE," "VOUCHER," "PARTNERSHIP," "DATE," and "LINK." 
Emphasize key relationships like "FOR," "CONDITIONS," "CONTENT," "SCOPE OF APPLICATION," "REDUCTION," "MINIMUM REQUIRED," "SUBJECT TO THE PROGRAM," and "FOR" in the translated output to ensure accurate retrieval of relevant data from the graph database.

- Note that: The user's query may contain Vietnamese entities,  you MUST keep intact its in Vietnamese keyword
- MUST keep intact the capitalized keywords in the output
- The key word in your output used for retrieving the node in the graph database with semantic meaning.
Example:
QUERY: "Có những cửa hàng KHAI TRƯƠNG nào trong tháng này."
OUTPUT EXPECT: "KHAI TRƯƠNG scope of application."

QUERY: "Chương trình YODYxFPT có những voucher nào?."
OUTPUT EXPECT: "YODYxFPT's content voucher."

QUERY: "Chương trình YODYxFPT có những voucher nào?."
OUTPUT EXPECT: "YODYxFPT's content voucher."

QUERY: {input}
OUTPUT:

"""