import logging
import requests
import msal
from typing import Optional
from kbraincortex.exceptions.collection import KBRaiNAuthenticationError
def on_behalf_of(client_id, client_secret, tenant_id, assertion_token, scope):
    AUTH_URL = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
    grant_type = "urn:ietf:params:oauth:grant-type:jwt-bearer"
    query_params = f"grant_type={grant_type}&client_id={client_id}&client_secret={client_secret}&assertion={assertion_token}&scope={scope}&requested_token_use=on_behalf_of"
    logging.info(client_id)
    logging.info(scope)
    response = requests.post(AUTH_URL, data=f"{query_params}", headers={"Content-Type": "application/x-www-form-urlencoded"})
    token_data = response.json()
    if 'access_token' not in token_data:
        raise ValueError(f"On Behalf of request failed: {token_data}")
    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]
    
    return access_token, refresh_token


def validate_app_credentials(client_id:str, tenant_id:str, client_secret:str, scopes:Optional[list]=["https://graph.microsoft.com/.default"]):
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    app = msal.ConfidentialClientApplication(
        client_id,
        authority=authority,
        client_credential=client_secret
    )
    
    # Attempt to acquire a token for a specific scope
    token_response = app.acquire_token_for_client(scopes=scopes)
    
    if "access_token" not in token_response:
        raise KBRaiNAuthenticationError("Failed to validate token for client.")
    
    return token_response