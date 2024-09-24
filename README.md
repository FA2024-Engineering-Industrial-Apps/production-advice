# Some guides

## Installing Ollama

- download Ollama @ https://ollama.com/
- in your terminal run ‚ollama pull llama3-groq-tool-use‘
- in your  terminal run ‚ollama serve‘
	

## Running Ollama server:

- set an `OLLAMA_HOST` environment variable to `0.0.0.0:11434`;
- determine your local IP address
- use `ChatOllama(..., base_url="your_local_ip_address::11434")`