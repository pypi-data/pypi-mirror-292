from jamesql import JameSQL
from jamesql.index import GSI_INDEX_STRATEGIES
import json

with open("tests/fixtures/documents.json") as f:
    documents = json.load(f)

index = JameSQL()
# documents = [[]]

for i, document in enumerate(documents): # * 100000):
    document = document.copy()
    # document["listens"] = (i + 1) * 100
    # if "The" in document["title"]:
    #     document["categories"] = ["pop", "rock", "jazz"]
    # print(document)
    index.add(document)
# print(documents)
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
# index.create_gsi("lyric", strategy=GSI_INDEX_STRATEGIES.CONTAINS)
index.create_gsi("title", strategy=GSI_INDEX_STRATEGIES.PREFIX)
# index.create_gsi("listens", strategy=GSI_INDEX_STRATEGIES.NUMERIC)

# result = index.search(
#     {
#         "query": {
#             "and": [
#                 {"categories": {"contains": "jazz"}},
#             ]
#         },
#         "group_by": "categories",
#         "limit": 10,
#         "sort_by": "title",
#     }
# )

# result = index.search(
#     {
#         "query": {
#             "and": [
#                 {"listens": {"range": [200, 300]}},
#             ]
#         },
#         "metrics": ["aggregate"],
#         "limit": 10,
#         "sort_by": "title",
#     }
# )
print(index.gsis["title"]["gsi"].keys(prefix="tol"))
# result = index.search(
# query = {'limit': 10, 'query': {'lyric': {'boost': 56, 'contains': 'sky'}}, 'sort_by': 'title'}
# )


# print(result)
# print(response)

# query = "-started -with mural, ]["
# from pprint import pprint

# # exit()

# print(dict(result["groups"]))
# print(result["metrics"])

# print([i["_context"] for i in result["documents"]])

# # query = "St*rted"
# print(index._compute_string_query(query, query_keys=["title", "lyric"]))
# result = index.string_query_search(query)
# print(result)

# print("Showing search results for query: ", query)
# print(result)

print(result["documents"][0]["title"])
for r in result["documents"]:
    print(r["title"], " - ", r["_score"]) # , r["_context"])

print("results returned in ", result["query_time"] + "s")