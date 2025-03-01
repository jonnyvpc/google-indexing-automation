import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def get_authenticated_service():
    """Get an authenticated service for the Google Indexing API with detailed logging."""
    try:
        logger.info("Starting authentication process")
        start_time = datetime.now()
        
        # Get credentials from Workload Identity Federation
        from google.auth.default import default
        credentials, project = default(scopes=["https://www.googleapis.com/auth/indexing"])
        
        logger.info(f"Using project: {project}")
        
        # Refresh credentials
        credentials.refresh(Request())
        
        # Build service
        service = build("indexing", "v3", credentials=credentials)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Authentication completed in {duration:.2f} seconds")
        logger.info("Successfully authenticated with Google Indexing API")
        
        return service
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        raise

def submit_url_to_google(url):
    """Submit URL to Google's Indexing API with enhanced logging."""
    try:
        logger.info(f"Submitting URL to Google Indexing API: {url}")
        start_time = datetime.now()
        
        service = get_authenticated_service()
        
        # Prepare the URL Notification
        url_notification = {
            "url": url,
            "type": "URL_UPDATED"
        }
        
        # Submit to Google's Indexing API
        response = service.urlNotifications().publish(
            body=url_notification
        ).execute()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"URL submission completed in {duration:.2f} seconds")
        logger.info(f"Google Indexing API response: {json.dumps(response)}")
        
        return response
    except Exception as e:
        logger.error(f"URL submission failed: {str(e)}")
        raise

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhooks from Webflow with comprehensive logging."""
    try:
        # Generate request ID
        request_id = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        logger.info(f"Request received - ID: {request_id}")
        
        # Log request details
        logger.info(f"Request headers: {json.dumps(dict(request.headers))}")
        
        # Validate request
        if not request.is_json:
            logger.warning("Invalid content type - expected application/json")
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.json
        logger.info(f"Request payload: {json.dumps(data)}")
        
        # Validate payload
        if not data or 'slug' not in data:
            logger.warning(f"Invalid payload received: {json.dumps(data)}")
            return jsonify({"error": "Invalid payload"}), 400
        
        # Construct the full URL
        item_slug = data["slug"]
        blog_url = f"https://jonnyvpc.com/news-posts/{item_slug}"
        logger.info(f"Constructed URL: {blog_url}")
        
        # Submit to Google
        response = submit_url_to_google(blog_url)
        
        # Return success response
        result = {
            "request_id": request_id,
            "response": response,
            "status": "success"
        }
        logger.info(f"Request {request_id} completed successfully")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        return jsonify({
            "error": str(e),
            "request_id": request_id if 'request_id' in locals() else None
        }), 500

@app.route('/webhook', methods=['GET'])
def webhook_status():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "Webhook endpoint is running. Use POST method to submit URLs."
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
