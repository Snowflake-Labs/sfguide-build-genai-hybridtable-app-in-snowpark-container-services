#!/bin/bash

jupyter lab --port 4200 --allow-root --no-browser --NotebookApp.token='' --NotebookApp.password='' --ip=0.0.0.0 2>&1 & ## DEBUG

python3 -m streamlit run --logger.level=debug --server.port=8080 --server.address=0.0.0.0 --server.runOnSave=true --server.fileWatcherType=poll app_main.py 2>&1
