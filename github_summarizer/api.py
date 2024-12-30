from urllib.parse import urljoin
from flask import Flask, request, jsonify
from repo import get_repo_algo

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze_repo():
    data = request.json
    if 'repo_url' not in data:
        return jsonify({"error": "repo_url is required"}), 400

    repo_url = data['repo_url']
    algo_description, directory_structure = get_repo_algo(repo_url)

    return jsonify({
        "directory_structure": directory_structure,
        "algorithm_description": algo_description
    })

