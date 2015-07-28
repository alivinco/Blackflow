__author__ = 'alivinco'

def get_next_id(values):
    next_id = 0
    for item in values:
        if item["id"]>next_id:next_id = item["id"]
    return next_id + 1