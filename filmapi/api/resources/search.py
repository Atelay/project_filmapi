from flask_restful import Resource, request
from filmapi.extensions import es


class SearchResource(Resource):
    """
    Search Resource

    ---
    get:
      tags:
        - search
      summary: Search for films by title or description
      description: Search for films by title or description using Elasticsearch.
      parameters:
        - in: query
          name: query
          schema:
            type: string
          required: true
          description: The search query string.
      responses:
        200:
          description: List of films matching the search query
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
                  properties:
                    title:
                      type: string
                    title_original:
                      type: string
                    description:
                      type: string
        404:
          description: Error, film not found
    """

    def get(self):
        query = request.args.get("query")
        if not query:
            return {"error": "Missing query parameter"}, 400
        try:
            results = es.search(
                index="films",
                body={
                    "query": {
                        "multi_match": {
                            "query": query,
                            "fields": ["title", "title_original", "description"],
                            "fuzziness": "AUTO",
                        }
                    }
                },
            )
        except Exception as ex:
            return f"Error, {ex}", 404
        return [hit["_source"] for hit in results["hits"]["hits"]], 200
