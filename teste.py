import google.generativeai as genai



genai.configure(api_key="AIzaSyDFr_NUmjyc1UT3mJBEAI7-LljPUf5viDI")

model = genai.GenerativeModel("gemini-2.0-flash")
resp = model.generate_content("diga oi")
print(resp.text)
