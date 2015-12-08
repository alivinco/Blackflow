"""This is a sample function for zipping an entire directory into a zipfile"""

# This seems to work OK creating zip files on both windows and linux. The output
# files seem to extract properly on windows (built-in Compressed Folders feature,
# WinZip, and 7-Zip) and linux. However, empty directories in a zip file appear
# to be a thorny issue. The solution below seems to work but the output of
# "zipinfo" on linux is concerning. Also the directory permissions are not set
# correctly for empty directories in the zip archive. This appears to require
# some more in depth research.

# I got some info from:
# http://www.velocityreviews.com/forums/t318840-add-empty-directory-using-zipfile.html
# http://mail.python.org/pipermail/python-list/2006-January/535240.html
import os
import zipfile
import requests


def zip_dir(dir_path=None, zip_file_path=None, include_dir_in_zip=True):
    """Create a zip archive from a directory.

    Note that this function is designed to put files in the zip archive with
    either no parent directory or just one parent directory, so it will trim any
    leading directories in the filesystem paths and not include them inside the
    zip archive paths. This is generally the case when you want to just take a
    directory and make it into a zip file that can be extracted in different
    locations.

    :param dir_path: string path to the directory to archive. This is the only
    required argument. It can be absolute or relative, but only one or zero
    leading directories will be included in the zip archive.
    :param zip_file_path: string path to the output zip file. This can be an absolute
    or relative path. If the zip file already exists, it will be updated. If
    not, it will be created. If you want to replace it from scratch, delete it
    prior to calling this function. (default is computed as dir_path + ".zip")
    :param include_dir_in_zip: string path to the output zip file. This can be an absolute
    or relative path. If the zip file already exists, it will be updated. If
    not, it will be created. If you want to replace it from scratch, delete it
    prior to calling this function. (default is computed as dir_path + ".zip")
    :return:

"""
    if not zip_file_path:
        zip_file_path = dir_path + ".zip"
    if not os.path.isdir(dir_path):
        raise OSError("dir_path argument must point to a directory. "
                      "'%s' does not." % dir_path)
    parent_dir, dir_to_zip = os.path.split(dir_path)

    # Little nested function to prepare the proper archive path
    def trim_path(path):
        archive_path = path.replace(parent_dir, "", 1)
        if parent_dir:
            archive_path = archive_path.replace(os.path.sep, "", 1)
        if not include_dir_in_zip:
            archive_path = archive_path.replace(dir_to_zip + os.path.sep, "", 1)
        return os.path.normcase(archive_path)

    out_file = zipfile.ZipFile(zip_file_path, "w",compression=zipfile.ZIP_DEFLATED)
    for (archiveDirPath, dirNames, file_names) in os.walk(dir_path):
        for file_name in file_names:
            file_path = os.path.join(archiveDirPath, file_name)
            out_file.write(file_path, trim_path(file_path))
        # Make sure we get empty directories as well
        if not file_names and not dirNames:
            zip_info = zipfile.ZipInfo(trim_path(archiveDirPath) + "/")
            # some web sites suggest doing
            # zipInfo.external_attr = 16
            # or
            # zipInfo.external_attr = 48
            # Here to allow for inserting an empty directory.  Still TBD/TODO.
            out_file.writestr(zip_info, "")
    out_file.close()


def unzip_dir(zip_file, dest_dir):
    with zipfile.ZipFile(zip_file,"r") as zp:
        zp.extractall(dest_dir)


def send_file_to_app_store(app_id,file_path,app_store_api_uri):
    data = {"id":app_id}
    file = {'file': open(file_path, 'rb')}
    r = requests.post(app_store_api_uri,data=data,files=file)
    if r.status_code == 200 :
        print "File saved successfully"
        os.remove(file_path)
    else:
        print "Server error"

if __name__ == "__main__":
    zip_dir("../../apps/lib/AlarmApp_v1")
    # unzip_dir("../../apps/lib/AlarmApp_v1.zip","../../apps/AlarmApp_v1")
    send_file_to_app_store("565c2411f8f87822daebe850","../../apps/lib/AlarmApp_v1.zip","http://localhost:8080/bfhub/api/file")