import json
import logging
from opensearchpy import RequestError

logger = logging.getLogger(__name__)
def configure_opensearch_index(os_client,index_name):
  logger.info('Configure opensearch index')
  index_body = """
{
  "settings": {
    "index.knn": true
  },
  "mappings": {
    "properties": {
      "vector_embedding": {
        "type": "knn_vector",
        "dimension": 1024,
        "method": {
          "name": "hnsw",
          "engine": "nmslib",
          "space_type": "cosinesimil",
          "parameters": {}
        }
      },
       "metadata": { 
        "properties" :
          {
            "context_index_id" : {
              "type" : "text"
            },
            "image_path" : {
              "type" : "text"
            }
          }
      }
    }
  }
}
"""

  # We would get an index already exists exception if the index already exists, and that is fine.
  index_body = json.loads(index_body)
  try:
    response = os_client.indices.create(index_name, body=index_body)
    logger.info(f"response received for the create index -> {response}")
  except RequestError as e:
    if e.error == 'resource_already_exists_exception':
      logger.warning(f"Index '{index_name}' already exists. Skipping creation.")
    else:
      logger.error(f"Failed to create index '{index_name}': {str(e)}")
  except Exception as e:
    logger.error(f"Exception Occured : {str(e)}")
