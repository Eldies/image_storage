# -*- coding: utf-8 -*-
import json


class InvalidTokenError(ValueError):
    pass


class TokenDoesNotHaveIdError(InvalidTokenError):
    pass


def get_user_id_from_token(token):
    try:
        decoded_token = json.loads(token)
        return decoded_token['id']
    except KeyError:
        raise TokenDoesNotHaveIdError()
    except:
        raise InvalidTokenError
