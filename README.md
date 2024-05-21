# Gen AI and Hybrid Tables Application in Snowpark Container Services

## Overview

This repo contains instructions for building a Gen AI application running in Snowpark Container Sevices (SPCS) and it also demonstrates the use of Hybrid tables within the application. If you have any questions or feedback, reach out to [Dash](dash.desai@snowflake.com).

Here is the outline of what's covered:

* [Prerequisites](#prerequisites)
* [Setup Environment](#setup-environment)
  * [Clone Repository](#step-1-clone-repository)
  * [Create DB, Schema, Warehouse, Tables, Role And Other Objects](#step-2-create-db-schema-warehouse-tables-role-and-other-objects)
  * [Load Data](#step-3-load-data)
* [Docker Setup](#docker-setup)
  * [Build Docker Image](#step-1-build-docker-image)
  * [Push Docker Image to Snowflake Registry](#step-2-push-docker-image-to-snowflake-registry)
* [Snowpark Container Sevices (SPCS) Setup](#snowpark-container-sevices-spcs-setup)
  * [Update SPCS Specification File](#step-1-update-spcs-specification-file)
  * [Create Service](#step-2-create-service)
  * [Check Service Status](#step-3-check-service-status)
  * [Get Public Endpoint](#step-4-get-public-endpoint)
* [Run Application](#run-application)
  * [Gen AI Inpainting](#gen-ai-inpainting)
  * [Tower Uptime](#tower-uptime)

## Quick Demo

https://github.com/Snowflake-Labs/sfguide-build-genai-hybridtable-app-in-snowpark-container-services/assets/1723932/b724d02d-97e0-4fa7-be16-22cf8bbc9363

## Prerequisites

* Snowflake Account with SPCS (+ the ability to create GPU compute pool) and Hybrid Tables enabled. [Check SPCS availability](https://docs.snowflake.com/developer-guide/snowpark-container-services/overview#).
* Docker Desktop (https://docs.docker.com/desktop) 

## Setup Environment

### Step 1: Clone Repository
Clone this repo and browse to the cloned repo folder on your laptop.

### Step 2: Create DB, Schema, Warehouse, Tables, Role And Other Objects

Log into your Snowflake account and follow instructions in [setup.sql](setup.sql) to create necessary objcts such as database, schema, warehouse, tables.

### Step 3: Load Data

Log into your Snowflake account and use Snowsight to load data into newly created `cell_towers_ca` and `images` tables. For both of the tables, select the following in the UI:

* **Header**: 'Skip first line' 
* **Field optionally enclosed by**: 'Double quotes'

## Docker Setup

### Step 1: Build Docker Image

Make sure Docker is running and then in a terminal window, browse to the cloned folder and execute the following command to build the Docker image.

`DOCKER_BUILDKIT=0  docker build --platform linux/amd64 -t genai-spcs .`

**NOTE**: The first time you build the image it can take about ~45-60mins.

### Step 2: Push Docker Image to Snowflake Registry

* Execute the following command in the terminal window to tag the image

`docker tag genai-spcs:latest YOUR_IMAGE_URL_GOES_HERE`

For example, *docker tag genai-spcs:latest <org>-<account_alias>.registry.snowflakecomputing.com/dash_db/dash_schema/dash_repo/genai-spcs:latest*

* Execute the following command in the terminal to login to your Snowflake account that's enabled for SPCS

`docker login YOUR_ACCOUNT_REGISTRY_URL`

For example, *docker login <org>-<account_alias>*

* Execute the follwing command in the terminal to push the image to Snowflake registry

`docker push YOUR_IMAGE_URL_GOES_HERE`

For example, `docker push <org>-<account_alias>.registry.snowflakecomputing.com/dash_db/dash_schema/dash_repo/genai-spcs:latest`

## Snowpark Container Sevices (SPCS) Setup

Assuming you were able to successfully push the Docker image just fine, follow the steps below to deploy and run the application in SPCS.

### Step 1: Update SPCS Specification File

* Update the following attributes in [genai-spcs.yaml](genai-spcs.yaml)

  * Set `image` to your image URL. For example, `/dash_db/dash_schema/dash_repo/genai-spcs`.

* Upload **updated** [genai-spcs.yaml](genai-spcs.yaml) to YOUR_DB.YOUR_SCHEMA.YOUR_STAGE. For example, `DASH_DB.DASH_SCHEMA.DASH_STAGE`.

### Step 2: Create Service

In Snowsight, execute the following SQL statememts to create and launch the service.

```sql
use role DASH_SPCS;

-- Check compute pool status
show compute pools;
-- If compute pool is not ACTIVE or IDLE, uncomment and run the following alter command
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
```

### Step 3: Check Service Status

Execute the following SQL statement and check the status of the service to make sure it's in READY state before proceeding.

```sql
select 
  v.value:containerName::varchar container_name
  ,v.value:status::varchar status  
  ,v.value:message::varchar message
from (select parse_json(system$get_service_status('genai_service'))) t, 
lateral flatten(input => t.$1) v;

-- NOTE: Do not proceed unless the service is in READY state
```

### Step 4: Get Public Endpoint

Assuming compute pool is in IDLE or ACTIVE state and the service is in READY state, execute the following SQL statement to get the public endpoint of the application.

```sql
show endpoints in service genai_service;
```

If everything has gone well, you should see a service named `streamlit` with `ingress_url` of the application--something similar to `iapioai5-sfsenorthamerica-build-spcs.snowflakecomputing.app`

## Run Application

In a new browser window, copy-paste the `ingress_url` URL from **Step 4** above and you should see the login screen. To launch the application, enter your Snowflake credentials and you should see the application up and running!

#### Gen AI Inpainting

- On this page, use your mouse to paint the area white where you'd like a cell phone tower to be built.
- Then click on **Generate Image** button -- this will kickoff a inpainting process using open source Gen AI model. In a few seconds the generated image will be displayed on the right-hand side of the selected image!

#### Tower Uptime

- On this page, update status of one of the towers in the dataframe on the right. This will kickoff a process to updated the hybrid table and also update the map instantaneously.

## Quick Demo

https://github.com/Snowflake-Labs/sfguide-build-genai-hybridtable-app-in-snowpark-container-services/assets/1723932/b724d02d-97e0-4fa7-be16-22cf8bbc9363

## Questions or Feedback

If you have any questions or feedback, reach out to [Dash](dash.desai@snowflake.com).


