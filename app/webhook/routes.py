from flask import Blueprint,  request, jsonify
from datetime import datetime





webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

@webhook.route('/receiver', methods=["POST"])
def receiver():
   return ""