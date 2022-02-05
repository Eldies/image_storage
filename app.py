# -*- coding: utf-8 -*-
from flask import Flask

import views


app = Flask(__name__)

app.add_url_rule('/ping', view_func=views.ping)
