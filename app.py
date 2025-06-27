from flask import Flask, render_template, request
from data_processor import get_financial_news, process_news_data, init_db

print("app.py: Starting Flask application setup...")

app = Flask(__name__)

# Initialize the database and create tables on application startup
# This will run once when the app container starts
init_db()
print("app.py: Database initialization complete.")

@app.route('/', methods=['GET', 'POST'])
def index():
    print("app.py: Route '/' accessed.")
    query = "economy" # Default news query
    processed_news = []
    error_message = None

    if request.method == 'POST':
        query = request.form.get('query', query)

    raw_news = get_financial_news(query)
    if raw_news:
        processed_news = process_news_data(raw_news)
    else:
        error_message = f"Could not retrieve news for '{query}'. Please check the query or API limits."
    
    # Render_template expects 'templates/dashboard.html'
    return render_template(
        'dashboard.html',
        news=processed_news,
        current_query=query,
        error=error_message
    )

# --- CRITICAL: Remove the if __name__ == '__main__': block ENTIRELY ---
# When Docker runs `python app.py`, it directly executes the script.
# We need app.run() to be called directly.
print("app.py: Attempting to run Flask app...")
app.run(host='0.0.0.0', port=5000, debug=True) # Explicitly set host/port/debug
print("app.py: Flask app.run() initiated (should not be reached if server starts).")