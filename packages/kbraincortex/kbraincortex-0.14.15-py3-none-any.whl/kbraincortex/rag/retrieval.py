from kbraincortex.azure.search import rag_search
from kbraincortex.azure.cosmos import query_cosmos_db
from kbraincortex.taxonomy.categories import categorize_query
import logging 

def get_document_links(documents):
    for document in documents:
        datasource = document.get("datasource", None)
        query = {
            "query": f"SELECT * from c where c.id = @filename",
            "parameters": [{"name": "@filename", "value": document["filename"]}]
        }
        result, _ = query_cosmos_db(
            query,
            "metadata",
            datasource
        )

        if len(result) == 0:
            logging.error(f"Unable to find datasource {datasource} in metadata database")
            continue
        document["url"] = result[0]["url"]
        document["tags"] = []

    return documents

def select_content_by_category(query, datasets, topic, citations=1):
    logging.info("Choosing category")
    category, tokens = categorize_query(query, topic)
    logging.info(category)    
    logging.info(tokens)
    logging.info("Selecting documents in category...")
    #Make a call to azure semantic search to get the documents in the category
    resultset = []
    for dataset in datasets:
        try:
            logging.info(f"Searching dataset {dataset.get('id')}...")
            files = dataset["files"] if "files" in dataset else None
            result = rag_search(query, dataset.get('id'), citations, files=files)
            logging.info(result)
            resultset += result
        except Exception as e:
            logging.error(f"Error searching dataset {dataset.get('id')}: {e}")
            continue

    sorted_results = sorted(resultset, key=lambda x: x["@search.reranker_score"], reverse=True)[0:citations]
    sorted_results = get_document_links(sorted_results)
    logging.info(sorted_results)
    
    return sorted_results, category