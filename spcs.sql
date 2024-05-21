
use role DASH_SPCS;

-- Check compute pool status
show compute pools;
-- If compute pool is not ACTIVE or IDLE, uncomment and run the following command
-- alter compute pool DASH_GPU3 resume;

-- NOTE: Do not proceed unless the compute pool is in ACTIVE or IDLE state

-- Create GenAI service in SPCS
create service genai_service
IN COMPUTE POOL DASH_GPU3
FROM @dash_stage
SPECIFICATION_FILE = 'genai-spcs.yaml'
MIN_INSTANCES = 1
MAX_INSTANCES = 1
QUERY_WAREHOUSE = DASH_WH_S
EXTERNAL_ACCESS_INTEGRATIONS = (ALLOW_ALL_ACCESS_INTEGRATION);

-- Check GenAI service status
select 
  v.value:containerName::varchar container_name
  ,v.value:status::varchar status  
  ,v.value:message::varchar message
from (select parse_json(system$get_service_status('genai_service'))) t, 
lateral flatten(input => t.$1) v;

-- NOTE: Do not proceed unless the service is in READY state

-- Get Gen AI Streamlit application endpoint
show endpoints in service genai_service;

-- Check SPCS logs for debugging
CALL SYSTEM$GET_SERVICE_LOGS('DASH_DB.DASH_SCHEMA.genai_service', 0, 'genai-spcs', 1000);
