import requests
import json
from kbrainsdk.security.bearer import extract_claims 
from kbraincortex.microsoft.msal import on_behalf_of
import logging

GRAPH_URL = "https://graph.microsoft.com/v1.0/"

def list_site_contents(access_token, site, host):
    HEADERS = {'Authorization': f"Bearer {access_token}" }        
    response = requests.get(f"{GRAPH_URL}sites/{host}:/sites/{site}:/drives", headers=HEADERS) 
    return json.loads(response.text)

def get_entra_groups(client_id, oauth_secret, tenant_id, token, next_link=None):
    
    claims = extract_claims(f"Bearer {token}")
    oid = claims["oid"]
        
    scope = "https://graph.microsoft.com/GroupMember.Read.All"
    access_token, _ = on_behalf_of(client_id, oauth_secret, tenant_id, token, scope)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    groups = []
    
    try:
        link = next_link if next_link else f"https://graph.microsoft.com/v1.0/users/{oid}/memberOf"
        response = requests.get(link, headers=headers)
        response.raise_for_status()
        logging.info("Graph response:")
        logging.info(response.json())
        #Get next page if there is one
        response_json = response.json()
        group_objects = response_json.get("value", [])
        for group in group_objects:
            groups.append(group["id"])
        if "@odata.nextLink" in response_json:
            next_link = response_json["@odata.nextLink"]
            logging.info(f"Next link: {next_link}")
            groups += get_entra_groups(client_id, oauth_secret, tenant_id, token, next_link = next_link)
        else:
            logging.info("No more pages.")
    except Exception as ex:
        logging.error(f"Error getting groups: {ex}")
        #groups += claims["groups"]
    logging.info(groups)
    return groups

def get_group_members(group_id, client_id, client_secret, tenant_id, token, scope = None, continuation_token = None):

    scope = "https://graph.microsoft.com/GroupMember.Read.All" if scope == None else scope
    impersonation_token, _ = on_behalf_of(client_id, client_secret, tenant_id, token, scope)    
    # Call Microsoft Graph to get group members
    graph_url = f"https://graph.microsoft.com/v1.0/groups/{group_id}/members"
    if continuation_token:
        graph_url = continuation_token    
    headers = {'Authorization': f'Bearer {impersonation_token}'}
    response = requests.get(graph_url, headers=headers)
    members = response.json()

    logging.info(members)

    next_link = members.get('@odata.nextLink', None)
    # Retrieve member details including profile picture URLs
    member_details = []
    for member in members['value']:
        member_info = {
            'id': member['id'],
            'displayName': member.get('displayName', 'N/A'),
            'userPrincipalName': member.get('userPrincipalName', 'N/A'),
            'jobTitle': member.get('jobTitle', 'N/A'),
            'mail': member.get('mail', 'N/A'),
            'photoUrl': f"https://graph.microsoft.com/v1.0/users/{member['id']}/photo/$value"
        }
        member_details.append(member_info)
    
    return member_details, next_link

