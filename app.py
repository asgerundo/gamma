import dash
from dash import html, dcc, Input, Output, clientside_callback
import plotly.graph_objs as go
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
from flask import send_file
import dropbox
import os

DROPBOX_ACCESS_TOKEN = os.environ.get('DROPBOX_ACCESS_TOKEN')

# Dropbox file path
DROPBOX_FILE_PATH = "/gamma.pfd"

# Initialize Dropbox client
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

app = dash.Dash(__name__)
server = app.server
app.layout = html.Div([
    html.H1("PDF Generator"),
    html.Label("Navn:"),
    dcc.Input(id='navn', type='text', placeholder='Enter navn'),
    html.Label("Email:"),
    dcc.Input(id='email', type='email', placeholder='Enter email'),
    html.Label("Telefonnummer:"),
    dcc.Input(id='telefonnummer', type='tel', placeholder='Enter telefonnummer'),
    html.Label("Adresse:"),
    dcc.Input(id='adresse', type='text', placeholder='Enter adresse'),
    html.Button('Generate PDF', id='generate-pdf', n_clicks=0),
    html.Div(id='output-pdf')
])

@app.callback(
    Output('output-pdf', 'children'),
    [Input('generate-pdf', 'n_clicks')],
    [
        Input('navn', 'value'),
        Input('email', 'value'),
        Input('telefonnummer', 'value'),
        Input('adresse', 'value')
    ]
)
def generate_pdf(n_clicks, navn, email, telefonnummer, adresse):
    if n_clicks > 0:
        metadata, response = dbx.files_download('/gamma.pdf')
        existing_pdf_stream = io.BytesIO(response.content)
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFillColorRGB(1, 1, 1)
        can.setFont("Times-Roman", 14)
        can.drawString(490, 195, navn)
        can.drawString(490, 105, email)
        can.drawString(490, 135, telefonnummer)
        can.drawString(490, 165, adresse)
        can.save()

        packet.seek(0)
        new_pdf = PdfReader(packet)

        existing_pdf = PdfReader(open(existing_pdf_stream, "rb"))
        output = PdfWriter()

        for i in range(len(existing_pdf.pages)):
            page = existing_pdf.pages[i]
            if i < len(new_pdf.pages):
                page.merge_page(new_pdf.pages[i])
            output.add_page(page)

        output_stream = io.BytesIO()
        output.write(output_stream)
        output_stream.seek(0)

        # Return download link for the generated PDF
        return html.A('Download PDF', href='/download-pdf', download='destination.pdf')

@app.server.route('/download-pdf')
def download_pdf():
    print("Downloading PDF triggered")
    # Rest of the function code...


    # Generate the PDF
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFillColorRGB(1, 1, 1)
    can.setFont("Times-Roman", 14)
    can.drawString(490, 195, navn)
    can.drawString(490, 105, email)
    can.drawString(490, 135, telefonnummer)
    can.drawString(490, 165, adresse)
    can.save()

    packet.seek(0)
    new_pdf = PdfReader(packet)

    existing_pdf = PdfReader(open(existing_pdf_stream, "rb"))
    output = PdfWriter()

    for i in range(len(existing_pdf.pages)):
        page = existing_pdf.pages[i]
        if i < len(new_pdf.pages):
            page.merge_page(new_pdf.pages[i])
        output.add_page(page)

    output.write(output_stream)
    output_stream.seek(0)

    # Return the PDF file as a downloadable attachment
    return send_file(output_stream, attachment_filename='destination.pdf', as_attachment=True)

if __name__ == '__main__':
    app.run_server(debug=True)
