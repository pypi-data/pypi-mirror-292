from kbraincortex.microsoft.graph import on_behalf_of
from kbraincortex.azure.datafactory import trigger_pipeline
from kbraincortex.azure.cosmos import upsert_record
from kbrainsdk.ingest import Ingest 
import json

def trigger_sharepoint_ingest_scan(
        host:str, 
        site:str, 
        environment:str, 
        p_name:str,
        assertion_token:str|None=None, 
        on_behalf_of_token:str|None=None,
        tenant_id:str|None=None,
        client_id:str|None=None, 
        oauth_secret:str|None=None,         
        folder_id:str="",
        drive:str="",
        current_next_link:str="",
        cosmos_guid:str="",
        initial_run_id:str="",       
        next_link:str=""
    ) -> None:
    
    assert(assertion_token or on_behalf_of_token, "At least one of assertion_token or on_behalf_of_token must be provided")
    
    access_token = on_behalf_of_token

    if not access_token:
        scope = "https://graph.microsoft.com/AllSites.Read+offline_access"
        access_token, _ = on_behalf_of(client_id, oauth_secret, tenant_id, assertion_token, scope)

    optionals = {}

    if folder_id:
        optionals["folder_id"] = folder_id

    if current_next_link:
        optionals["current_next_link"] = current_next_link
    
    if cosmos_guid:
        optionals["cosmos_guid"] = cosmos_guid
    
    if initial_run_id:
        optionals["initial_run_id"] = initial_run_id

    if next_link:
        optionals["next_link"] = next_link

    if drive:
        optionals["drive"] = drive
    
    params = {
        "access_token":access_token,
        "host": host,
        "site": site,
        "environment": environment,
        "optionals": json.dumps(optionals) if optionals != {} else ""
    }

    run_id = trigger_pipeline(p_name, params, environment)

    return run_id