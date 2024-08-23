import os
# from dotenv import load_dotenv
import numpy as np

from layernext import LayerNextClient
# load_dotenv()  # take environment variables from .env.

API_KEY="key_yyq1jzhjv7o4ixqrj4hleh27k6s9o4qv"
SECRET="rzx8knm2q6j8dxrhtuk7"
LAYERX_URL="https://api.dev-llm.layernext.ai"
#LAYERX_URL="http://127.0.0.1:3000"

client = LayerNextClient(API_KEY, SECRET, LAYERX_URL)

unique_list = [
    "chat_Mahela Panduka Bandara_2ab6b694-7e2a-4f98-8e05-5e3638ed727b.pdf"
]

#res = client.find_elements(unique_list, "What is the university of Mahela?")
res = client.retrieve_documents_with_structure(["resume"], ["Mahela Panduka Bandara"], "What is the university of Mahela?" )
print(res)
