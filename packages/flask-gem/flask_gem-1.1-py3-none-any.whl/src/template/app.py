"""App Main."""
import os

from flask import render_template

# App Initialization
from . import create_app  # from __init__ file

app = create_app(os.getenv("CONFIG_MODE"))

controllers = []

# Hello World!
@app.route('/')
def home():
    return render_template('index.html',data = controllers )

# Applications Routes
from .routes import *
# if __name__ == "__main__":
#     app.run()
