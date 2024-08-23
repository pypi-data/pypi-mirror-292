from kbraincortex.azure.datafactory import trigger_pipeline
from kbraincortex.azure.cosmos import upsert_record
import json 

def trigger_rfp_response_generation(proposal_id, email, assertion_token, environment, client_id, oauth_secret, tenant_id, datasets = []):

    p_name = "RFPResponses"
    params = {
        "proposal_id": proposal_id,
        "email":email,
        "client_id": client_id,
        "tenant_id": tenant_id,        
        "token":assertion_token,
        "oauth_secret": oauth_secret,
        "environment": environment,
        "datasets": json.dumps(datasets)
    }

    run_id = trigger_pipeline(p_name, params, environment)

    upsert_record(
        database_name="status", 
        container_name="ingest",
        item={
            "id": proposal_id,
            "type": "RFP",
            "status": f"Response Generation initiated for proposal. Waiting for cluster..",
            "run_id": run_id
        }
    )

    return run_id
