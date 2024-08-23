# from quart import Quart, request, abort, jsonify, make_response
from individual.data_fix.matome_jikkou import jikkou_kari

import json

# 追加部分
class Config:
    def __init__(self, application_id=None):
        self.application_id = application_id

config = Config()

def initialize(application_id):
    global config
    config = Config(application_id)

    global rakuten_id
    rakuten_id = config.application_id


# app = Quart(__name__)

# @app.route('/jikkou/<string:isbn>')
# async def kari(isbn):
#     new_data = await jikkou_kari(f"{isbn}", rakuten_id)
#     json_str = json.dumps(new_data, ensure_ascii=False)
#     response = await make_response(json_str)
#     return response

# app.run(host='0.0.0.0', port=8080)



async def kari(isbn):
    new_data = await jikkou_kari(f"{isbn}", rakuten_id)
    # json_str = json.dumps(new_data, ensure_ascii=False)
    # response = await make_response(json_str)
    # return response
    return new_data