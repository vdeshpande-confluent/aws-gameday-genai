from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
import boto3
import numpy as np
import json
from typing import List, Dict
import os



class VectorSearchClient:

    def __init__(self,os_client):
        self.os_client = os_client
    
    def query_vector_search(self,embeddings: np.ndarray,num_neighbors) -> Dict:

        query_text = {
            "size": num_neighbors,
            "query": {
                "knn": {
                    "vector_embedding": {
                        "vector": embeddings['text_embedding'][0].tolist(),
                        "k": num_neighbors
                    }
                    
                }
            }
            
        }
        query_image = {
            "size": num_neighbors,
            "query": {
                "knn": {
                    "vector_embedding": {
                        "vector": embeddings['image_embedding'][0].tolist(),
                        "k": num_neighbors
                    }
                    
                }
            }
            
        }
        try:
            # Perform the image and text based searches
            image_based_search_response = self.os_client.search(body=query_image, index='rag-index')
            text_based_search_response = self.os_client.search(body=query_text, index='rag-index')

            # Remove vector embeddings from the responses
            text_hits = text_based_search_response['hits']['hits']
            image_hits = image_based_search_response['hits']['hits']

            for hit in text_hits:
                hit['_source'].pop('vector_embedding', None)

            for hit in image_hits:
                hit['_source'].pop('vector_embedding', None)

            # Print the responses
            print(f"text_based_search_response: {text_based_search_response}")
            print(f"image_based_search_response: {image_based_search_response}")

            # Combining the hits
            combined_hits = text_hits + image_hits

            # Sort the combined hits by score in descending order
            combined_hits_sorted = sorted(combined_hits, key=lambda x: x['_score'], reverse=True)

            # Take the top 5 results
            top_5_hits = combined_hits_sorted[:num_neighbors]
            

        except Exception as e:
            print(f"error occured while querying OpenSearch index={'rag-index'}, exception={e}")
            
        return [hit['_source']['context_index_id'] for hit in top_5_hits]
 