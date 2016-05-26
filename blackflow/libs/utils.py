import socket
__author__ = 'alivinco'


def get_next_id(values):
    next_id = 0
    for item in values:
        if item["id"] > next_id: next_id = item["id"]
    return next_id + 1


def split_app_full_name(app_full_name):
    delim_name = app_full_name.find("_n")
    developer = app_full_name[:delim_name]
    delim_version = app_full_name.find("_v")
    app_name = app_full_name[delim_name+2:delim_version]
    version = app_full_name[delim_version + 2:]
    return developer, app_name, version


def compose_app_full_name(developer,app_name,version):
    return "%s_n%s_v%s"%(developer,app_name,version)


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("gmail.com",80))
        ip = s.getsockname()[0]
        s.close()
    except:
        ip = None
    return ip