import json
def get_tomatoes(event, context):
    tomatoes = [{"name": "Red Tomato", "price": "30 Rs"},
            {"name": "Yellow Tomato", "price": "35 Rs"},
            {"name": "Small Tomato", "price": "20 Rs"}]
    tomatoesList = {"tomatoes": tomatoes}
    response = {"statusCode": 200, "body": json.dumps(tomatoesList)}
    return response