from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, Runner, trace, function_tool, OpenAIChatCompletionsModel
from typing import Dict
import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content
import asyncio
import gradio as gr

# Load environment variables
load_dotenv(override=True)

openai_api_key = os.getenv("OPENAI_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

# ===== Agent Instructions =====
instructions1 = "You are a sales agent working for {company_name}, a company that provides {products}. You write professional, serious cold emails."
instructions2 = "You are a humorous, engaging sales agent working for {company_name}, a company that provides {products}. You write witty, engaging cold emails that are likely to get a response."
instructions3 = "You are a busy sales agent working for {company_name}, a company that provides {products}. You write concise, to the point cold emails."

# ===== API Clients =====
gemini_base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
deepseek_base_url = "https://api.deepseek.com/v1"

deepseek_client = AsyncOpenAI(base_url=deepseek_base_url, api_key=deepseek_api_key)
gemini_client = AsyncOpenAI(base_url=gemini_base_url, api_key=google_api_key)

# ===== Models =====
deepseek_model = OpenAIChatCompletionsModel(model="deepseek-chat", openai_client=deepseek_client)
gemini_model = OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=gemini_client)

# ===== Sales Agents =====
sales_agent1 = Agent(name="DeepSeek Sales Agent", instructions=instructions1, model=deepseek_model)
sales_agent2 = Agent(name="Gemini Sales Agent", instructions=instructions2, model=gemini_model)
sales_agent3 = Agent(name="OpenAI Sales Agent", instructions=instructions3, model="gpt-4o-mini")

description = "Write a cold sales email"
tool1 = sales_agent1.as_tool(tool_name="sales_agent1", tool_description=description)
tool2 = sales_agent2.as_tool(tool_name="sales_agent2", tool_description=description)
tool3 = sales_agent3.as_tool(tool_name="sales_agent3", tool_description=description)

# ===== Send Email Tool =====
@function_tool
def send_html_email(subject: str, html_body: str, from_email: str, to_emails: str) -> Dict[str, str]:
    """Send out an email with the given subject and HTML body"""
    sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))

    from_email_obj = Email(from_email)
    to_emails_list = [e.strip() for e in to_emails.split(",") if e.strip()]

    sent_list = []
    failed_list = []

    for to in to_emails_list:
        try:
            to_email_obj = To(to)
            content = Content("text/html", html_body)
            mail = Mail(from_email_obj, to_email_obj, subject, content)
            response = sg.client.mail.send.post(request_body=mail.get())

            if response.status_code in (200, 202):  # 202 = accepted
                sent_list.append(to)
            else:
                failed_list.append({"email": to, "code": response.status_code})

        except Exception as e:
            failed_list.append({"email": to, "error": str(e)})

    return {
        "status": "success" if sent_list else "failed",
        "sent_to": sent_list,
        "failed": failed_list
    }

# ===== Supporting Agents =====
subject_instructions = "You write a subject for a cold sales email. \
You are given a message and you need to write a subject for an email that is likely to get a response."

html_instructions =  "you can convert a text email body to an HTML email body.\
You are given a text email body which might have some markdown \
and you need to convert it to an HTML email body with simple, clear, compelling layout and design. \
Do not include a footer as this will be added by another tool."

subject_writer = Agent(name="Email subject writer", instructions=subject_instructions, model="gpt-4o-mini")
subject_tool = subject_writer.as_tool(tool_name="subject_writer", tool_description="Write a subject for a cold sales email")

html_converter = Agent(name="HTML email body converter", instructions=html_instructions, model="gpt-4o-mini")
html_tool = html_converter.as_tool(tool_name="html_converter", tool_description="Convert a text email body to an HTML email body")

email_tools = [subject_tool, html_tool, send_html_email]

instructions = "You are an email formatter and sender. First use subject_writer to write a subject, then use html_converter to convert the body to HTML, then send_html_email with the subject, HTML body, sender, and receivers."

emailer_agent = Agent(
    name="Email Manager",
    instructions=instructions,
    tools=email_tools,
    model="gpt-4o-mini",
    handoff_description="Convert an email to HTML and send it"
)

# ===== Sales Manager =====
tools = [tool1, tool2, tool3]
handoffs = [emailer_agent]

instructions = "You are a sales manager working for {company_name}.\
You use the tools given to you to generate cold sales emails.\
You never generate sales emails yourself; you always use the tools.\
You try all 3 sales agent tools at least once before choosing the best one.\
After picking the email, you handoff to the Email Manager to format and send the email."

sales_manager = Agent(
    name="Sales Manager",
    instructions=instructions,
    tools=tools,
    handoffs=handoffs,
    model="gpt-4o-mini"
)

# ===== Main Flow =====
async def generate_and_send(company_name, products, sender_email, receiver_names, receiver_emails):
    message = f"""
    use tool to Generate a cold sales email for {company_name}.
    Products/Services: {products}
    Sender: {sender_email}
    Receivers: {receiver_names} ({receiver_emails})
    """

    result = await Runner.run(sales_manager, message)
    return result


def interface_fn(company_name, products, sender_email, receiver_names, receiver_emails):
    emails = [e.strip() for e in receiver_emails.split(",") if e.strip()]
    names = [n.strip() for n in receiver_names.split(",") if n.strip()]

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(
        generate_and_send(company_name, products, sender_email, names, emails)
    )

    print("Runner Result:", result)


    draft1_content = "Drafts..."
    draft2_content = "Drafts..."
    draft3_content = "Drafts..."
    final_pick_content = result

    return draft1_content, draft2_content, draft3_content, final_pick_content


# ===== Gradio Interface =====
with gr.Blocks(title="Cold Email Generator") as demo:
    gr.Markdown("## Cold Email Generator & Sender")

    with gr.Row():
        with gr.Column(scale=1):
            company_name = gr.Textbox(label="Company Name")
            products = gr.Textbox(label="Products / Services", lines=3,)
            sender_email = gr.Textbox(label="Sender Email")
            receiver_names = gr.Textbox(label="Receiver Names (comma-separated)")
            receiver_emails = gr.Textbox(label="Receiver Emails (comma-separated)")
            run_btn = gr.Button("Generate & Send")

        with gr.Column(scale=1):
            # output = gr.JSON(label="Result")
            draft1_content = gr.Textbox(label="Gemini (Output Under Development)", lines=10)
            draft2_content = gr.Textbox(label="Deepseek (Output Under Development)", lines=10)
            draft3_content = gr.Textbox(label="OpenAI (Output Under Development)", lines=10)
            final_pick_content = gr.Textbox(label="Final Pick", lines=10)

    run_btn.click(
        interface_fn,
      
        inputs=[company_name, products, sender_email, receiver_names, receiver_emails],
        outputs=[draft1_content, draft2_content, draft3_content, final_pick_content]
    )

# ===== Debug CLI Run =====
async def main() -> None:
    with trace("Automated SDR"):
        result = await Runner.run(sales_manager, "Send out a cold sales email addressed to Dear CEO")
        print(result)

if __name__ == "__main__":
    demo.launch()
  
