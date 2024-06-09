
use role ACCOUNTADMIN;

create database DASH_DB;
create schema DASH_SCHEMA;
create warehouse DASH_WH_S WAREHOUSE_SIZE=SMALL;

use database DASH_DB;
use schema DASH_SCHEMA;
use warehouse DASH_WH_S;

create stage DASH_STAGE;
create image repository DASH_REPO;

create security integration if not exists SNOWSERVICES_INGRESS_OAUTH
  type=oauth
  oauth_client=snowservices_ingress
  enabled=true;

create compute pool DASH_GPU3
min_nodes = 1
max_nodes = 2
instance_family = GPU_NV_S
auto_suspend_secs = 7200;

create stage llm_workspace encryption = (type = 'SNOWFLAKE_SSE');

create or replace hybrid table cell_towers_ca (
  tower_id int unique primary key,
  tower_name varchar(255),
  lat float,
  lon float,
  status varchar(30),
  status_message varchar(256),
  last_comm datetime,
  maintenance_due datetime
);

create or alter table images (
    id int autoincrement,
    site_name string,
    city_name string,
    file_name string, 
    lat float,
    lon float,
    image_bytes string
);

create role DASH_SPCS;
grant usage on database DASH_DB to role DASH_SPCS;
grant all on schema DASH_SCHEMA to role DASH_SPCS;
grant create service on schema DASH_SCHEMA to role DASH_SPCS;
grant usage on warehouse DASH_WH_S to role DASH_SPCS;
grant READ,WRITE on stage DASH_STAGE to role DASH_SPCS;
grant READ,WRITE on image repository DASH_REPO to role DASH_SPCS;
grant all on compute pool DASH_GPU3 to role DASH_SPCS;
grant bind service endpoint on account to role DASH_SPCS;
grant monitor usage on account to role DASH_SPCS;
grant READ,WRITE on stage llm_workspace to role DASH_SPCS;
grant all on table cell_towers_ca to role DASH_SPCS;
grant all on table images to role DASH_SPCS;

CREATE OR REPLACE NETWORK RULE allow_all_rule
  TYPE = 'HOST_PORT'
  MODE= 'EGRESS'
  VALUE_LIST = ('0.0.0.0:443','0.0.0.0:80');

CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION ALLOW_ALL_ACCESS_INTEGRATION
  ALLOWED_NETWORK_RULES = (allow_all_rule)
  ENABLED = true;

GRANT USAGE ON INTEGRATION ALLOW_ALL_ACCESS_INTEGRATION TO ROLE DASH_SPCS;
