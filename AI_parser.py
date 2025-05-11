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

def parse_function_name(llm_response_str: str):
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

        function_name = parsed_json.get("function_name")
        return function_name

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
Based on the user's prompt:

{prompt}
Choose the best function that first the user needs. Answer in a JSON format with the following structure:

{{
    "function_name":{{}}
}}

Possible function calls are:

{list_of_functions}

'''
    LLM_repoonse = LLM_request(suitable_prompt)

    ## parsing function name
    function_name = parse_function_name(LLM_repoonse)
    print(function_name)

    return function_name
# %%
