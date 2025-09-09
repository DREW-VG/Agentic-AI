import gradio as gr
import asyncio
from dotenv import load_dotenv
import os
from agents import Runner  # assumes same Agent setup as your script

# import your existing objects
from SDR2 import sales_manager  # adjust if file is named differently

# override send_html_email to accept sender + recipients
def send_html_email_dynamic(sender_email: str, recipient_emails: list[str], subject: str, html_body: str):
    import sendgrid
    from sendgrid.helpers.mail import Mail, Email, To, Content

    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(sender_email)

    # loop over recipients
    for rec in recipient_emails:
        to_email = To(rec)
        content = Content("text/html", html_body)
        mail = Mail(from_email, to_email, subject, content).get()
        sg.client.mail.send.post(request_body=mail)

    return {"status": "sent", "recipients": recipient_emails}


async def generate_and_send(company_name, products, background, sender_email, receiver_names, receiver_emails):
    # build dynamic message prompt
    message = f"Generate a cold sales email from {company_name}.\n" \
              f"Products/Services: {products}\n" \
              f"Background: {background}\n" \
              f"Receivers: {receiver_names} ({receiver_emails})"

    result = await Runner.run(sales_manager, message)
    return result


def interface_fn(company_name, products, background, sender_email, receiver_names, receiver_emails):
    # split receiver emails
    emails = [e.strip() for e in receiver_emails.split(",") if e.strip()]
    names = [n.strip() for n in receiver_names.split(",") if n.strip()]

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(generate_and_send(company_name, products, background, sender_email, names, emails))
    return result


with gr.Blocks(title="Cold Email Generator") as demo:
    gr.Markdown("## Cold Email Generator & Sender")

    with gr.Row():
        with gr.Column(scale=1):
            company_name = gr.Textbox(label="Company Name")
            products = gr.Textbox(label="Products / Services", lines=3)
            sender_email = gr.Textbox(label="Sender Email")
            receiver_names = gr.Textbox(label="Receiver Names (comma-separated)")
            receiver_emails = gr.Textbox(label="Receiver Emails (comma-separated)")
            run_btn = gr.Button("Generate & Send")

        with gr.Column(scale=1):
            output = gr.JSON(label="Result")

    run_btn.click(interface_fn, inputs=[company_name, products, background, sender_email, receiver_names, receiver_emails], outputs=output)

if __name__ == "__main__":
    demo.launch()
