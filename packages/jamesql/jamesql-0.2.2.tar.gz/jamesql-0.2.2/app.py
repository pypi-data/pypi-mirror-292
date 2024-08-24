from jamesql import JameSQL
from jamesql.index import GSI_INDEX_STRATEGIES
import json

with open("tests/fixtures/documents.json") as f:
    documents = json.load(f)

index = JameSQL()

for document in documents:
    index.add(document)

# query = {
#     "query": {
#         "close_to": [
#             {"lyric": "made"},
#             {"lyric": "temple,"},
#             {"lyric": "my"},
#         ],
#         "distance": 7
#     },
#     "limit": 2,
#     "query_score": "(_score + 2)",
# }

# print(query)
index.create_gsi("lyric", strategy=GSI_INDEX_STRATEGIES.CONTAINS)
index.create_gsi("title", strategy=GSI_INDEX_STRATEGIES.CONTAINS)
# index.add({"title": "shake it off", "lyric": "I stay out too late", "category": "coffee"})


# response = index.search(
#     {
#         "query": {"title": {"equals": "shake it off"}},
#         "limit": 10,
#         "sort_by": "title",
#     }
# )

# print(response)

query = "-started -with mural, ]["
from pprint import pprint

# exit()

# query = "St*rted"
print(index._compute_string_query(query, query_keys=["title", "lyric"]))
result = index.string_query_search(query)
# print(result)

# print("Showing search results for query: ", query)

for r in result["documents"]:
    print(r["title"], " - ", r["_score"])

print("results returned in ", result["query_time"] + "s")