import requests
import base64
from flask import Flask, render_template, request
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)

# Load your Resend API key
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

# Function to generate a PDF eBook
def generate_pdf(topic):
    filename = f"{topic.replace(' ', '_')}.pdf"
    c = canvas.Canvas(filename, pagesize=letter)

    # Add Title and Content to the PDF
    c.setFont("Helvetica", 16)
    c.drawString(100, 750, f"eBook on {topic}")
    c.setFont("Helvetica", 12)
    c.drawString(100, 730, "Generated using AI-powered tools.")
    
    # Add some text content (customize this based on your eBook content)
    content = f"This is an example eBook on {topic}.\nThis content was generated using AI.\n"
    y_position = 710
    for line in content.split("\n"):
        c.drawString(100, y_position, line)
        y_position -= 20
    
    c.save()
    return filename

# Home route for the form
@app.route('/')
def index():
    return render_template('index.html')

# Route to generate eBook and send it via email
@app.route('/generate', methods=['POST'])
def generate():
    topic = request.form['topic']
    email = request.form['email']

    # Generate the PDF eBook
    filename = generate_pdf(topic)

    # Read and encode the PDF file
    with open(filename, "rb") as f:
        pdf_data = f.read()
        encoded_pdf = base64.b64encode(pdf_data).decode()

    # Prepare the email data for Resend API
    data = {
        "from": "your-email@onresend.com",  # Use Resend's default email for testing or your verified email
        "to": [email],
        "subject": f"Your eBook on {topic}",
        "text": f"Hi! Here is your eBook on {topic}.",
        "attachments": [
            {
                "filename": filename,
                "content": encoded_pdf,
                "content_type": "application/pdf"
            }
        ]
    }

    # Send the email using Resend API
    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        },
        json=data
    )

    # Check if the email was sent successfully
    if response.status_code == 200:
        return "eBook sent to your email!"
    else:
        return f"Failed to send email: {response.text}"

# Google Analytics integration (optional)
@app.after_request
def add_google_analytics(response):
    # Replace UA-XXXXXXXXX-X with your actual Google Analytics tracking ID
    google_analytics_script = """
    <script async src="https://www.googletagmanager.com/gtag/js?id=UA-XXXXXXXXX-X"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'UA-XXXXXXXXX-X');
    </script>
    """
    response.set_data(response.get_data().replace(b"</body>", google_analytics_script.encode() + b"</body>"))
    return response

if __name__ == "__main__":
    app.run(debug=True)