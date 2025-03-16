from flask import Flask, request, jsonify
import subprocess as sp  # Keep subprocess as sp

app = Flask(__name__)

@app.route('/query', methods=['POST'])
def query_tgpt_normal():
    data = request.json  # Get JSON request data
    query = data.get("query", "").strip()  # Extract and sanitize query

    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        # Run 'tgpt' with query
        result = sp.run(['tgpt', '-q', query], capture_output=True, text=True)

        if result.returncode != 0:
            return jsonify({"error": result.stderr.strip()}), 500  # Return error if command fails

        response = result.stdout.strip()  # Extract output
        return jsonify({"response": response})  # Return JSON response

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/web_search/query', methods=['POST'])
def query_tgpt_web_search():
    data = request.json  # Get JSON request data
    query = data.get("query", "").strip()  # Extract and sanitize query

    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        # Run 'tgpt' with web search
        result = sp.run(['tgpt', '-q', f"@web_search {query}"], capture_output=True, text=True)

        if result.returncode != 0:
            return jsonify({"error": result.stderr.strip()}), 500  # Return error if command fails

        response = result.stdout.strip()  # Extract output
        return jsonify({"response": response})  # Return JSON response

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)  # Runs Flask on port 8080 with debugging enabled

