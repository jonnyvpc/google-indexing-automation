from flask import Flask, request, jsonify
from google.auth import default, transport
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import logging
import json
import time
import os
import google.auth.transport.requests
from datetime import datetime

# Configure logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
SCOPES = [
    "https://www.googleapis.com/auth/indexing",
    "https://www.googleapis.com/auth/cloud-platform"
]

def get_authenticated_service():
    try:
        start_time = time.time()
        logger.info("Starting authentication process")
        
        # Use Workload Identity Federation to get credentials
        credentials, project = default(scopes=SCOPES)
        
        # Ensure we have a valid token
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        
        auth_time = time.time() - start_time
        logger.info(f"Authentication completed in {auth_time:.2f} seconds")
        logger.info(f"Using project: {project}")
        
        # Build and return the service
        return build("indexing", "v3", credentials=credentials)
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}", exc_info=True)
        raise

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        start_time = time.time()
        request_id = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        logger.info(f"Request received - ID: {request_id}")
        
        # Log request details
        headers = dict(request.headers)
        safe_headers = {k: v for k, v in headers.items() if 'auth' not in k.lower()}
        logger.info(f"Request headers: {json.dumps(safe_headers)}")
        
        data = request.json
        if not data or "slug" not in data:
            logger.warning(f"Invalid payload received: {json.dumps(data)}")
            return jsonify({"error": "Invalid payload"}), 400

        item_slug = data["slug"]
        blog_url = f"https://jonnyvpc.com/news-posts/{item_slug}"
        logger.info(f"Processing webhook for URL: {blog_url} - Request ID: {request_id}")

        # Get fresh authenticated service
        service = get_authenticated_service()
        
        # Submit URL to Google Indexing API
        request_body = {"url": blog_url, "type": "URL_UPDATED"}
        response = service.urlNotifications().publish(body=request_body).execute()
        
        process_time = time.time() - start_time
        logger.info(f"Request {request_id} completed in {process_time:.2f} seconds")
        logger.info(f"Indexing response for {blog_url}: {json.dumps(response)}")
        
        return jsonify({"status": "success", "response": response, "request_id": request_id}), 200

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        return jsonify({
            "error": str(e),
            "request_id": request_id if 'request_id' in locals() else None
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Cloud Run"""
    try:
        # Include basic service stats
        uptime = time.time() - app.start_time if hasattr(app, 'start_time') else 0
        return jsonify({
            "status": "healthy",
            "uptime_seconds": uptime,
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

if __name__ == "__main__":
    # Record start time for uptime tracking
    app.start_time = time.time()
    
    # Verify authentication works on startup
    try:
        get_authenticated_service()
        logger.info("Successfully authenticated with Google Indexing API")
    except Exception as e:
        logger.error(f"Failed to authenticate on startup: {str(e)}", exc_info=True)
        
    # Use port from environment variable for Cloud Run compatibility
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
