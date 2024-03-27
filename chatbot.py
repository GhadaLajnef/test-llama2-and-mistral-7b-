import streamlit as st
import anthropic
import requests
import json
import csv
import datetime
import pandas as pd



url = "http://localhost:11434/api/generate"
headers = {'Content-Type': 'application/json'}
context = []

def save_to_csv(input_output):
    """
    Saves the given input-output data as rows in a CSV file named 'output-{model_name}.csv'. Takes one argument `input_output`, which can be either an iterable (like a single list) or an iterable of iterables (like a list containing multiple sub-lists).

    Args:
    input_output (Iterable or Iterable of Iterables): The data to be saved in the CSV file.
    """
    with open('output-%s.csv' % model_name, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')

        row_data = ["---", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), *input_output]
        # Encode each element in the row_data to UTF-8 before writing
        row_data_utf8 = [item.encode('utf-8') if isinstance(item, str) else item for item in row_data]
        writer.writerow(row_data_utf8)

def generate_response(input):
    """
    Generates a response from an API using the given input and saves the input and output to a CSV file. Takes one argument, `input`, which can be any iterable data.
    Args:
    input (Any iterable): The data to be sent as an input to the API.
    Returns:
    The actual response from the API if it returns a status code 200 (success). Otherwise, it prints an error message and returns None.
    """
    global context
    data = {
        "model": model_name,
        "stream": False,
        "prompt": input,
        "context": context
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        response_text = response.text
        data = json.loads(response_text)
        actual_response = data["response"]
        context = data["context"]
        # Save input and output to CSV file
        save_to_csv([input, actual_response])
        return actual_response
    else:
        print("Error:", response.status_code, response.text)
        return None

def clear_history():
    """
    Clears conversation history.
    """
    global context
    context = []
    return None

def set_model_name(checked_values):
    global model_name
    if "mistral" in checked_values:
        model_name = "mistral"
    elif "llama2" in checked_values:
        model_name = "llama2"
    print("Selected model:", model_name)



with st.sidebar:
    
  st.title("📝 Ollama chatbot ")
  
  #st.write("Choose LLM")
  ollama_model = st.selectbox(
        "Choose Ollama Model",
        ["llama2", "mistral"]
    )
  st.button("Set Model", on_click=set_model_name(ollama_model))
  model_name = ollama_model
  st.write("### Clear Conversation History")
  if st.button("Clear History"):
        clear_history()
uploaded_file = st.file_uploader("Upload an article", type=("csv", "xlsx"))
question = st.chat_input(
    placeholder="Can you give me a short summary?",
    disabled=not uploaded_file,
)

if not uploaded_file and question :
    st.info("Please add a file to continue.")

if uploaded_file and question :
    file = uploaded_file.read().decode()
    response = generate_response(file + "\n" + question)
    st.write("### Answer")
    st.write(response)
    save_to_csv([file, response, question])
