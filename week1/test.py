import os
from google import genai
from dotenv import load_dotenv
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
# response = client.models.generate_content(model="gemini-3.5-flash", contents="Say hello in one word.")
response = client.models.generate_content(model="gemini-2.5-flash", contents="Say hello in one word.")
print(response.text)


# -------------------------------------------------------------
# 5. Check the API test-
# python .\test.py
# (.venv) PS C:\Users\psinh\Desktop\MasaiProjects\WhatsApp_On-Cruise-Control\week1> python .\test.py
# Direct use of automatic function calling (AFC) in Models.generate_content is not recommended. Instead, we recommend to use AFC in Chat.send_message. Similarly, direct use of AFC in Models.generate_content_stream is not recommended. Instead, we recommend to use AFC in Chat.send_message_stream.
# Hello
# (.venv) PS C:\Users\psinh\Desktop\MasaiProjects\WhatsApp_On-Cruise-Control\week1> 

# ------------------------------------------------------------------------------------------------
# 4. python .\persona\test_persona.py-
# (.venv) PS C:\Users\psinh\Desktop\MasaiProjects\WhatsApp_On-Cruise-Control\week1> python .\persona\test_persona.py
# Direct use of automatic function calling (AFC) in Models.generate_content is not recommended. Instead, we recommend to use AFC in Chat.send_message. Similarly, direct use of AFC in Models.generate_content_stream is not recommended. Instead, we recommend to use AFC in Chat.send_message_stream.
# [friends] I am going to be late today, can you pick me up? -> Achaa, chalega. Main aa jaati hoon pick karne. Time bata de bas. 😂
# [family] Diwali pe ghar aaoge kya? -> Haan, I'll definitely be there! ❤️
# [professional] I have a new video ready. When can we connect? -> Badhiya hai, yaar! Kab connect karein?
# [friends] Coffee chale this evening? -> Haan, shaam ko free hoon, chalein? ☕
# [family] Dinner mein kya khana hai? -> Kuch simple bana lein? Jo aapko theek lage.
# (.venv) PS C:\Users\psinh\Desktop\MasaiProjects\WhatsApp_On-Cruise-Control\week1> 

# ----------------------------------------------------------------------------------------
# 3. Check style_signals.json Run-
# python -m json.tool .\persona\style_signals.json > $null
# if ($LASTEXITCODE -eq 0) { "style_signals.json: VALID" } else { "style_signals.json: INVALID" }
# (.venv) PS C:\Users\psinh\Desktop\MasaiProjects\WhatsApp_On-Cruise-Control\week1> python -m json.tool .\persona\style_signals.json > $null
# (.venv) PS C:\Users\psinh\Desktop\MasaiProjects\WhatsApp_On-Cruise-Control\week1> if ($LASTEXITCODE -eq 0) { "style_signals.json: VALID" } else { "style_signals.json: INVALID" }
# style_signals.json: VALID
# (.venv) PS C:\Users\psinh\Desktop\MasaiProjects\WhatsApp_On-Cruise-Control\week1> 

# ----------------------------------------------------------------------------------------
# 2. Check persona.json Run
# python -m json.tool .\persona\persona.json > $null
# if ($LASTEXITCODE -eq 0) { "persona.json: VALID" } else { "persona.json: INVALID" }

# (.venv) PS C:\Users\psinh\Desktop\MasaiProjects\WhatsApp_On-Cruise-Control\week1> python -m json.tool .\persona\persona.json > $null
# (.venv) PS C:\Users\psinh\Desktop\MasaiProjects\WhatsApp_On-Cruise-Control\week1> if ($LASTEXITCODE -eq 0) { "persona.json: VALID" } else { "persona.json: INVALID" }
# persona.json: VALID
# (.venv) PS C:\Users\psinh\Desktop\MasaiProjects\WhatsApp_On-Cruise-Control\week1> 
# -----------------------------------------------------------------------------------