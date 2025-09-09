from dotenv import load_dotenv

load_dotenv(override=True)

import os
import gradio as gr

openai_api_key = os.getenv('OPENAI_API_KEY')

if openai_api_key:
    print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
else:
    print("OpenAI API Key not set - please head to the troubleshooting guide in the setup folder")

from openai import OpenAI

openai = OpenAI()

question = "Please propose a hard, challenging question to assess someone's IQ. Respond only with the question."
messages = [{"role": "user", "content": question}]
response = openai.chat.completions.create(model="gpt-4.1-mini", messages=messages)
question = response.choices[0].message.content
print(question)

messages = [{"role": "user", "content": question}]
response = openai.chat.completions.create(model="gpt-4.1-nano", messages=messages)
answer = response.choices[0].message.content
print(answer)

evaluation = f"Based on the {question} and {answer}, please provide a evaluation of the answer. and comment on its intelligence level"
messages = [{"role": "user", "content": evaluation}]
response = openai.chat.completions.create(model="gpt-4.1-mini", messages=messages)
evaluation = response.choices[0].message.content
print(evaluation)





# def chat(message, history):
#     messages = [{"role": "system", "content": question}] 
#     response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
#     return response.choices[0].message.content

# gr.ChatInterface(chat, type="messages").launch()
