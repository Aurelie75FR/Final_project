# from flask import Flask 

# app = Flask(__name__)

# @app.route('/', methods=['GET'])

# def hello():
#     return '<h1>Hello !!</h1>'

# if __name__ == "__main__":
#     app.run(host =" 0.0.0.0", port = 8080)

from flask import Flask, request, jsonify
from google.cloud import bigquery
import os

app = Flask(__name__)

# Initialiser le client BigQuery
client = bigquery.Client()

@app.route('/recommend', methods=['GET'])
def recommend():
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({"error": "user_id parameter is required"}), 400

    # Exemple de requête SQL pour obtenir des recommandations basées sur les évaluations
    query = f"""
    SELECT product_id, AVG(rating) AS avg_rating, COUNT(*) AS review_count
    FROM `votre_projet.amazon_data.combined_data`
    WHERE product_id IN (
        SELECT product_id
        FROM `votre_projet.amazon_data.combined_data`
        WHERE user_id = @user_id
    )
    GROUP BY product_id
    ORDER BY avg_rating DESC
    LIMIT 10
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]
    )

    query_job = client.query(query, job_config=job_config)
    results = query_job.result()

    recommendations = [
        {"product_id": row.product_id, "avg_rating": row.avg_rating, "review_count": row.review_count}
        for row in results
    ]

    return jsonify(recommendations)

if __name__ == '__main__':
    # Assurez-vous de configurer le port si nécessaire
    app.run(host='0.0.0.0', port=5000, debug=True)
