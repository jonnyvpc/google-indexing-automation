from google.auth import default
from googleapiclient.discovery import build

# Define API scopes
SCOPES = ["https://www.googleapis.com/auth/indexing"]

# Authenticate using Workload Identity Federation
credentials, project = default(scopes=SCOPES)

# Build the Indexing API service
service = build("indexing", "v3", credentials=credentials)

# URLs to index (Replace with actual blog post URLs)
urls = [
    "https://jonnyvpc.com/news-posts/cloudflares-intelligence-revolution-in-cybersecurity",
    "https://jonnyvpc.com/news-posts/test-article",
    "https://jonnyvpc.com/blog/example-article",
    "https://jonnyvpc.com/blog/new-ai-strategy"
]

for url in urls:
    request_body = {"url": url, "type": "URL_UPDATED"}
    response = service.urlNotifications().publish(body=request_body).execute()
    print(f"Indexed: {response}")
