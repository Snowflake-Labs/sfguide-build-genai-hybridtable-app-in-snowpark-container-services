# Use rapidsai image for GPU compute
FROM rapidsai/rapidsai:23.06-cuda11.8-runtime-ubuntu22.04-py3.10

RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --default-timeout=1000 -r requirements.txt
RUN pip install ipython --upgrade

COPY app.css .
COPY *.py ./
ADD pages ./pages
COPY *.ipynb ./
COPY entrypoint.sh .

RUN mkdir .streamlit
COPY .streamlit/config.toml .streamlit

# Expose Jupyter port
EXPOSE 4200
# Expose Streamlit port
EXPOSE 8080

RUN chmod +x ./entrypoint.sh
ENTRYPOINT [ "./entrypoint.sh" ]
