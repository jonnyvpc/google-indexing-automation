from google.auth import impersonated_credentials
from google.auth.transport.requests import Request
import google.auth

# Define the correct Google Indexing API scope
SCOPES = ["https://www.googleapis.com/auth/indexing"]

# Service account to impersonate for WIF
SERVICE_ACCOUNT = "jonnyvpc-indexing@jonnyvpc-indexing.iam.gserviceaccount.com"

try:
    # Get default credentials (typically from ADC or environment)
    source_credentials, project = google.auth.default(scopes=SCOPES)

    # Impersonate the service account for WIF
    target_credentials = impersonated_credentials.Credentials(
        source_credentials=source_credentials,
        target_principal=SERVICE_ACCOUNT,
        target_scopes=SCOPES,
        lifetime=300  # Token lifetime in seconds (5 minutes)
    )

    # Refresh the credentials to get a fresh token
    target_credentials.refresh(Request())

    # Print the access token to verify WIF is working
    print(f"Access Token: {target_credentials.token}")

    # Optional: Verify the token's scopes
    token_info = google.auth.transport.requests.Request().get(
        url=f"https://www.googleapis.com/oauth2/v3/tokeninfo?access_token={target_credentials.token}"
    ).json()
    print(f"Token Info: {token_info}")

except Exception as e:
    print(f"Error: {e}")