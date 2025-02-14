import gradio as gr
from openai import OpenAI
from configuration import get_settings
import requests
import time

vllm_url = 'http://localhost:8000'

# We need to load initial settings
initial_settings = get_settings()
client = OpenAI(
    api_key=initial_settings.API_KEY,
    base_url='http://localhost:8000/v1',
)
admin_url = 'http://localhost:9000'
## 
DEFAULT_TEMP = 0.8
DEFAULT_SYSTEM = "Eres un asistente conversacional que busca ayudar. Solo hablas en español."
default_token_ids = ''

# Function to check the status of inference server
def get_with_retries(url, max_retries=20, delay=10):
    """
    Sends a GET request to the given URL, retrying until a 200 status code is received or
    until the maximum number of retries is reached.

    :param url: The URL to send the GET request to.
    :param max_retries: The maximum number of attempts (default is 20).
    :param delay: The delay in seconds between each retry (default is 1.5 seconds).
    :return: The response object if successful (status code 200), otherwise None.
    """
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"Attempt {attempt}: Success! Received 200 status code.")
                return response
            else:
                print(f"Attempt {attempt}: Received status code {response.status_code}. Retrying in {delay} seconds...")
        except Exception as e:
            print(f"Attempt {attempt}: Exception occurred: {e}. Retrying in {delay} seconds...")
        
        time.sleep(delay)

    print("Maximum retries exceeded. Failed to receive a 200 status code.")
    return None

# Function for fetching the config of inference server
def fetch_config():
    """
    Fetch the current configuration from the FastAPI Administrator app.
    """
    # Always load the settings to avoid race conditions
    app_settings = get_settings()
    try:
        headers = {
        "Content-Type":"application/json",
        "access_token": app_settings.API_KEY
        }
        response = requests.get(f"{admin_url}/config", headers=headers)
        response.raise_for_status()
        config = response.json()
        # Map the config to the Gradio input order:
        # MODEL_ID
        return config["MODEL_ID"]
    except Exception as _:
        return "Error"

# Function to update the config using administrator
def update_config_gradio(model_id):
    """
    Send a POST request to update the configuration.
    """
    app_settings = get_settings()
    headers = {
        "Content-Type":"application/json",
        "access_token": app_settings.API_KEY
        }
    payload = {
        "model_id": model_id
    }
    try:
        response = requests.post(f"{admin_url}/reload", 
                                 json=payload,
                                 headers=headers)
        response.raise_for_status()
        # Check the health of vllm server
        health_check = get_with_retries(f"{vllm_url}/health")
        if health_check is not None:
            return response.json()["message"]
        else:
            raise Exception("Maximum retries exceeded. Failed to receive a 200 status code.")
    except Exception as e:
        return f"Failed to update configuration: {e}"

# Function to set the global value of the temperature
def set_temperature_chat(temp_value:float):
    """
    Set a global value for temperature
    """
    global DEFAULT_TEMP
    DEFAULT_TEMP = temp_value
    return None

# Function to fetch the current system message
def fetch_system():
    return DEFAULT_SYSTEM

# Function to update the current system message
def update_system(message:str):
    global DEFAULT_SYSTEM
    
    DEFAULT_SYSTEM = message
    return None

# Main function for chat
def predict(message, history):
    global DEFAULT_TEMP
    global DEFAULT_SYSTEM
    
    app_settings = get_settings()
    # Convert chat history to OpenAI format
    history_openai_format = [{
        "role": "system",
        "content": DEFAULT_SYSTEM
    }]
    for human, assistant in history:
        history_openai_format.append({"role": "user", "content": human})
        history_openai_format.append({
            "role": "assistant",
            "content": assistant
        })
    history_openai_format.append({"role": "user", "content": message})

    # Create a chat completion request and send it to the API server
    stream = client.chat.completions.create(
        model=app_settings.MODEL_ID,  # Model name to use
        messages=history_openai_format,  # Chat history
        temperature=DEFAULT_TEMP,  # Temperature for text generation
        stream=True,  # Stream response
        extra_body={
            'repetition_penalty':
            1,
            'stop_token_ids': [
                int(id.strip()) for id in default_token_ids.split(',')
                if id.strip()
            ] if default_token_ids else []
        })

    # Read and return generated text from response stream
    partial_message = ""
    for chunk in stream:
        partial_message += (chunk.choices[0].delta.content or "")
        yield partial_message

# --- Build the Gradio Interface ---
with gr.Blocks() as demo:
    gr.Markdown("# VLLM Gradio Interface")
    
    gr.Markdown("## Update Model Configuration")
    
    
    with gr.Row():
        model_id = gr.Textbox(label="Model ID")
        output = gr.Textbox(label="Response")
    
    with gr.Row():
        refresh_button = gr.Button("Load Current Config")
        update_button = gr.Button("Update Configuration")
    
    # When the refresh button is clicked, fetch current config and fill the inputs.
    refresh_button.click(
        fetch_config,
        outputs=[model_id]
    )
    
    # When the update button is clicked, send the updated config.
    update_button.click(
        update_config_gradio,
        inputs=[model_id],
        outputs=output
    )
    
    # Include a slider for temperature
    temperature_slider = gr.Slider(
        minimum=0, maximum=2, step=0.01, value=0.8, label="Temperature",
        info="Temperature for responses: lower makes model deterministic"
    )
    # Set temperature value
    temperature_botton = gr.Button("Set Temperature")
    
    temperature_botton.click(
        fn=set_temperature_chat,
        inputs=[temperature_slider]
    )
    
    # Show the system message
    with gr.Row():
        system_message = gr.Textbox(label="Assistant System Message")
        
    with gr.Row():
        refresh_system_button = gr.Button("Load Current System Message")
        update_system_button = gr.Button("Update System message")
    
    # When the refresh button is clicked, fetch current message and fill the inputs.
    refresh_system_button.click(
        fetch_system,
        outputs=[system_message]
    )
    
    # When the update button is clicked, change the system message.
    update_system_button.click(
        update_system,
        inputs=[system_message]
    )
    
    gr.ChatInterface(fn=predict).queue()

if __name__ == "__main__":
    # Launch Gradio so that it listens on all interfaces (0.0.0.0) on port 7860.
    demo.launch(server_name="0.0.0.0", server_port=7860, share=True)