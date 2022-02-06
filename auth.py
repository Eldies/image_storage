# -*- coding: utf-8 -*-
import json


def get_user_id_from_token(token):
    decoded_token = json.loads(token)
    return decoded_token['id']
