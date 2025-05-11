# %%
import ollama
import json

# Nome do modelo Gemma que você baixou (por exemplo, gemma:2b)
# Certifique-se de que este nome corresponde ao modelo que você tem localmente via ollama list

def LLM_request(prompt):
    # model_name = "gemma3"
    model_name = "deepseek-r1:8b"
    try:
        # Conecta ao cliente Ollama local
        client = ollama.Client()

        print(f"Enviando prompt para o modelo {model_name}...")

        # Envia o prompt para o modelo e obtém a resposta
        # Usamos client.generate para uma interação simples de pergunta/resposta
        response = client.generate(model=model_name, prompt=prompt, keep_alive=1)

        # A resposta do modelo está na chave 'response' do dicionário retornado
        generated_text = response['response']

        return generated_text.strip()

    except ollama.ResponseError as e:
        print(f"Erro ao se comunicar com o Ollama: {e}")
        print("Certifique-se de que o serviço Ollama está rodando e que o modelo especificado existe.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

def translate_to_english(text_to_translate: str) -> str:
    """
    Translate the user text to english, using the LLMs.
    """
    suitable_prompt = fr'''
You are an intelligent assistant that helps a user by translating the user input to english. The source language is portuguese.
Your ONLY output MUST be a single, valid JSON object. Do NOT include any other text, explanations, apologies, or introductory phrases before or after the JSON object.

The JSON object must have exactly one key: "translation".

The user text to translate is:

{text_to_translate}

---
Here are some examples of user prompts and the corresponding desired JSON output:

User Prompt: "Mostre-me a figura que eu estava olhando antes dessa."
Desired JSON Output:
```json
{{
    "translation":": "Show me the picture I was looking at before this one."
}}
'''

    LLM_response = LLM_request(suitable_prompt)

    ## parsing translation

    translation = parse_json(LLM_response, "translation")
    print(translation)

    return translation

def parse_json(llm_response_str: str, key : str):
    """
    Parses the LLM response string to find a JSON block and extract the 'function_name'.
    """
    try:
        # Attempt to find the JSON block enclosed in ```json ... ```
        json_block_start_marker = "```json"
        json_block_end_marker = "```"

        start_marker_index = llm_response_str.find(json_block_start_marker)

        json_str_to_parse = None

        if start_marker_index != -1:
            # Found the start marker, now find the end marker after it
            end_marker_index = llm_response_str.find(json_block_end_marker, start_marker_index + len(json_block_start_marker))
            if end_marker_index != -1:
                # Extract the content between ```json and ```
                json_content_start = start_marker_index + len(json_block_start_marker)
                json_str_to_parse = llm_response_str[json_content_start:end_marker_index].strip()

        if json_str_to_parse is None:
            # Fallback: If ```json block not found or incomplete, try to find a raw JSON object
            # This looks for the first '{' and the last '}' in the string.
            first_brace_index = llm_response_str.find('{')
            last_brace_index = llm_response_str.rfind('}')
            if first_brace_index != -1 and last_brace_index != -1 and last_brace_index > first_brace_index:
                json_str_to_parse = llm_response_str[first_brace_index : last_brace_index + 1].strip()
            else:
                print("Error: Could not find a JSON block (neither ```json...``` nor a raw {.*}).")
                return None

        # Parse the extracted JSON string
        parsed_json = json.loads(json_str_to_parse)

        value_parsed = parsed_json.get(key)
        return value_parsed

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}. Problematic string: '{json_str_to_parse}'")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during parsing: {e}")
        return None

def returnFunctionCall(list_of_functions, prompt):
    '''
    AI agent core. It will build an prompt, and parse the llms response to find the best function call that
    fits the user input
    '''

    suitable_prompt = fr'''
You are an intelligent assistant that helps a user by selecting the appropriate function to call based on their request.
Your ONLY output MUST be a single, valid JSON object. Do NOT include any other text, explanations, apologies, or introductory phrases before or after the JSON object.

The JSON object must have exactly one key: "function_name".
If the function requires arguments, the JSON object must also include an "arguments" key, which itself is an object containing the parameters.
If no function is suitable or the request is ambiguous, you MUST select "unknown_action".

Here is the list of available functions and their descriptions:
{list_of_functions}

The user prompt is:
{prompt}

---
Here are some examples of user prompts and the corresponding desired JSON output:

User Prompt: "Show me the picture I was looking at before this one."
Desired JSON Output:
```json
{{
    "function_name": "load_previous_image"
}}

'''
    LLM_repoonse = LLM_request(suitable_prompt)

    ## parsing function name
    function_name = parse_json(LLM_repoonse)
    print(function_name)

    return function_name
# %%
# %%)
