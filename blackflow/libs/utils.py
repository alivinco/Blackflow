__author__ = 'alivinco'


def get_next_id(values):
    next_id = 0
    for item in values:
        if item["id"] > next_id: next_id = item["id"]
    return next_id + 1


def split_app_full_name(app_full_name):
    delim = app_full_name.find("_v")
    app_name = app_full_name[:delim]
    version = app_full_name[delim + 2:]
    return app_name, version


def compose_app_full_name(app_name,version):
    return "%s_v%s"%(app_name,version)
