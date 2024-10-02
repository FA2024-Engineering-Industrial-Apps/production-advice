# Production Advice

## Running the code

### Locally
`python -m streamlit run ./main.py`

### Docker
```docker compose up --build```

### Running together with the machine emulation:

1. Option $\longrightarrow$ running everything on Docker:

    ```shell
    docker compose up --build
    ```

2. Option $\longrightarrow$ running the MQTT server in docker, and the Streamlit apps locally:

    * Running the MQTT server in Docker:
        ```shell
        docker compose -f ./docker-compose-eclipse-mosquitto.yml up --build
        ```
    * Running the Streamlit Production optimization app:
        ```shell
        python -m streamlit run ./main.py --server.port 8501
        ```
    * Running the Streamlit Machine emulation app:
        ```shell
        python -m streamlit run ./machine_emulator/main.py --server.port 8502
        ```

## Some guides

### Installing Ollama

- download Ollama @ https://ollama.com/
- ~~in your terminal run ‚ollama pull llama3-groq-tool-use‘~~
- in your  terminal run ‚ollama serve‘
	

### Running Ollama server:

- set an `OLLAMA_HOST` environment variable to `0.0.0.0:11434`;

    - ```ps
      $env:OLLAMA_HOST = "0.0.0.0:11434"
      ```
- determine your local IP address
- use `ChatOllama(..., base_url="your_local_ip_address:11434")`
