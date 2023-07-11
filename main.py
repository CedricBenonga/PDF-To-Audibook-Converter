import os
import PyPDF2
import requests
import tkinter as tk
from tkinter import filedialog
from flask_bootstrap import Bootstrap5
from flask import Flask, render_template, redirect, url_for, flash, request


app = Flask(__name__)
app.config['SECRET_KEY'] = "j1095093f5jq9846535609467dzn486h"
Bootstrap5(app)
tts_Endpoint = "https://api.voicerss.org/?"
api_key = os.environ.get("TTS_API_KEY")


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/voice_reader', methods=["GET", "POST"])
def voice_reader():
    if request.method == "POST":
        # Create a tKinter window
        window = tk.Tk()
        # Hide the window and show only the filedialog
        window.withdraw()
        # Bring the filedialog in front of all the windows
        window.wm_attributes('-topmost', 1)

        try:
            file_name = filedialog.askopenfilename(parent=window,
                                                   initialdir="",
                                                   title="Select A File",
                                                   filetypes=(("pdf", ".pdf"),  # show only pdf files
                                                              ("All files", "*")))
        except RuntimeError:
            flash("Your previous pdf file is still reading!")
            return redirect(url_for("voice_reader"))

        try:
            # creating a pdf reader object
            reader = PyPDF2.PdfReader(file_name)
        except FileNotFoundError:
            flash("Sorry! Your file failed to be loaded. Please select another one!")
            return redirect(url_for("home"))

        # # print the number of pages in pdf file
        # print(len(reader.pages))

        # # print the text of the first page
        # print(reader.pages[0].extract_text())

        try:
            pdf_text = reader.pages[0].extract_text()
        except PyPDF2.errors.DependencyError:
            flash("Sorry! Your file failed to be loaded. Please select another one!")
            return redirect(url_for("home"))

        tts_params = {
            "key": api_key,
            "src": pdf_text,
            "hl": "en-us",
            "v": "John"
        }

        response = requests.get(tts_Endpoint, params=tts_params)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            flash("The selected file is either removed or corrupted or not readable. Please select another one!")
            return redirect(url_for("home"))

        tts_data = response.url
        file_loaded = file_name.split("/")[-1]

        return render_template("index.html", tts_data=tts_data, file_loaded=file_loaded)
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
