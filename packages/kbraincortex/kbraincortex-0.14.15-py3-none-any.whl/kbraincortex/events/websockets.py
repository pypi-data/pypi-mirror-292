from typing import Dict, Any
from kbraincortex.azure.cosmos import get_cosmos_item, query_cosmos_db, upsert_record, delete_record
from kbraincortex.microsoft.graph import get_entra_groups
from kbrainsdk.security.bearer import extract_claims
from kbraincortex.microsoft.msal import validate_app_credentials
from kbraincortex.exceptions.collection import KBRaiNAuthenticationError
import logging

def subscribe_to_group(token:str, group_name: str, subscription_id:str, client_id:str, client_secret:str, tenant_id:str) -> None:
    logging.info(f"Subscribing to group {group_name} with subscription_id {subscription_id}.")
    logging.info(f"Client ID: {client_id}, Tenant ID: {tenant_id}")
    email = authenticate_to_group(token=token, group_name=group_name, client_id=client_id, client_secret=client_secret, tenant_id=tenant_id)
    upsert_record(item={
        "id": subscription_id,
        "group": group_name,
        "email": email
    }, database_name="websockets", container_name="subscriptions")
    return email

def unsubscribe_from_group(token:str, group_name:str, subscription_id:str) -> None:
    authenticate_to_subscription(token, group_name, subscription_id)
    delete_record("websockets", "subscriptions", subscription_id)

def authenticate_to_group(token:str, group_name:str=None, client_id:str=None, client_secret:str=None, tenant_id:str=None) -> str:
    email = extract_claims(f"Bearer {token}").get("unique_name")
    if group_name == email:
        return email
    groups = get_entra_groups(client_id=client_id, oauth_secret=client_secret, tenant_id=tenant_id, token=token)    
    websocket_group = get_cosmos_item(database_name="websockets", container_name="groups", item_id=group_name)
    for group in groups:
        if group in websocket_group.get("allowed_groups"):
            return email
    raise KBRaiNAuthenticationError(f"User is not authorized for the group {group_name}.")

def app_authenticate_to_group(client_id:str, group_name:str) -> str:
    websocket_group = get_cosmos_item("websockets", "groups", group_name)
    if client_id not in websocket_group.get("allowed_apps"):    
        raise KBRaiNAuthenticationError(f"Application is not authorized for the group {group_name}.")

def authenticate_to_subscription(token:str, subscription_id:str) -> bool:
    email = authenticate_to_group(token)
    subscription = get_cosmos_item("websockets", "subscriptions", subscription_id)
    if subscription.get("email") != email:
        raise ValueError(f"User is not authorized for this subscription.")
    return True

def get_group_subscriptions(group_name:str,  client_id:str, tenant_id:str, client_secret:str, continuation_token:str|None=None) -> Dict[str, Any]:
    validate_app_credentials(client_id=client_id, tenant_id=tenant_id, client_secret=client_secret)
    app_authenticate_to_group(client_id=client_id, group_name=group_name)
    optional_args = {}
    if continuation_token:
        optional_args["continuation_token"] = continuation_token
    return query_cosmos_db(
        query={"query": f"SELECT * FROM c WHERE c['group']  = @group_name", "parameters": [{"name": "@group_name", "value": group_name}]},
        database_name="websockets",
        container_name="subscriptions",
        **optional_args
    )

def create_group(group_name:str, group_data:Dict[str, Any], client_id:str, tenant_id:str, client_secret:str) -> None:
    validate_app_credentials(client_id=client_id, tenant_id=tenant_id, client_secret=client_secret)
    upsert_record(
        container_name="groups",
        database_name="websockets",
        item = {
            "id": group_name,
            **group_data
        }
    )