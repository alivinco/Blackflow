import os
import zipfile
import requests
import logging

from blackflow.libs.utils import compose_app_full_name, split_app_full_name

log = logging.getLogger("bf_app_store")


class AppStore:
    def __init__(self, app_store_uri="http://localhost:8080/bfhub/api", apps_dir_path="./"):
        self.app_store_uri = app_store_uri
        self.apps_dir_path = apps_dir_path

    @staticmethod
    def get_auth_header(id_token):
        return {"Authorization":"Bearer %s"%id_token}

    @staticmethod
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

        out_file = zipfile.ZipFile(zip_file_path, "w", compression=zipfile.ZIP_DEFLATED)
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

    @staticmethod
    def unzip_dir(zip_file, dest_dir):
        with zipfile.ZipFile(zip_file, "r") as zp:
            zp.extractall(dest_dir)

    @classmethod
    def download_file(cls,url,local_file_path,id_token):
        # NOTE the stream=True parameter
        r = requests.get(url, stream=True,headers=cls.get_auth_header(id_token))
        with open(local_file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    #f.flush() commented by recommendation from J.F.Sebastian
        return "saved"

    def pack_and_upload_app(self, app_full_name,id_token):
        developer,app_name,version = split_app_full_name(app_full_name)
        app_full_name = compose_app_full_name(developer, app_name, version)
        tmp_file_path = os.path.join(self.apps_dir_path, app_full_name+".zip")
        app_dir = os.path.join(self.apps_dir_path, "lib", app_full_name)
        if not os.path.exists(app_dir):
            return None, "App %s can't be found "%app_full_name

        app_meta = self.get_app_by_full_name(developer, app_name, float(version),id_token)
        if app_meta:
            app_id = app_meta["id"]
        else:
            log.info("App doesn't exist in app store . Adding to app store")
            app_id = self.register_app(developer, app_name, float(version),id_token)

        if app_id:
            AppStore.zip_dir(app_dir, tmp_file_path)
            log.debug("App was saved to %s" % tmp_file_path)
            r_status = self.upload_file_to_app_store(app_id, tmp_file_path ,id_token)
            if r_status == 200:
                log.info("App was uploaded successfully to AppStore")
                return app_id, None
            else:
                log.error("App upload process failed")
                return None , "App store api returned status = %s"%r_status
        else:
            log.error("App registration failed because of error")
            return None , "Can't get app_id"

    def download_and_unpack_app(self, app_id,id_token):
        app_meta = self.get_app_by_id(app_id,id_token)
        tmp_file_path = os.path.join(self.apps_dir_path, app_meta["file"])
        log.info("Downloading app file %s from app store "%app_meta["file"])
        self.download_file(self.app_store_uri+"/apps/file/"+app_id, tmp_file_path,id_token)
        AppStore.unzip_dir(tmp_file_path,os.path.join(self.apps_dir_path,"lib"))
        os.remove(tmp_file_path)
        log.info("App %s was successfully downloaded and installed "%app_meta["file"])
        return compose_app_full_name(app_meta["developer"], app_meta["app_name"], app_meta["version"])

    def upload_file_to_app_store(self, app_id, file_path ,id_token):
        data = {"id": app_id}
        file = {'file': open(file_path, 'rb')}
        r = requests.post(self.app_store_uri + "/apps/file", data=data, files=file , headers = self.get_auth_header(id_token))
        if r.status_code == 200:
            log.info("App %s was sent to app store successfully" % file_path)
            os.remove(file_path)
            return r.status_code
        else:
            log.info("App %s failed to upload to app store . Error %s" % (file_path, r))
            return r.status_code

    def get_app_by_full_name(self, developer, app_name, version , id_token):
        r = requests.get(self.app_store_uri + "/apps/by_full_name", params={"developer": developer, "app_name": app_name, "version": version},
                         headers=self.get_auth_header(id_token))
        if r.status_code == 200:
            return r.json()
        else:
            return None

    def get_app_by_id(self, app_id , id_token):
        r = requests.get(self.app_store_uri + "/apps/id/"+app_id,headers=self.get_auth_header(id_token))
        return r.json()

    def register_app(self, developer, app_name, version , id_token):
        new_app = {"app_name": app_name, "developer": developer, "version": float(version)}
        log.debug("Registering new app %s"%new_app)
        r = requests.post(self.app_store_uri + "/apps", json=new_app, headers=self.get_auth_header(id_token))
        if r.status_code == 200:
            return r.json()["app_id"]
        else:
            return None


if __name__ == "__main__":
    # zip_dir("../../apps/lib/AlarmApp_v1")
    # unzip_dir("../../apps/lib/AlarmApp_v1.zip","../../apps/AlarmApp_v1")
    ast = AppStore("http://localhost:8080/bfhub/api", apps_dir_path="../../apps")
    # print ast.get_app_by_full_name("alivinco", "WebTest6", 2.2)["id"]

    #print ast.pack_and_upload_app("alivinco", "ServoCam", 1)

    print ast.pack_and_upload_app("alivinco_nAppStoreTester_v1.1")
    #ast.download_and_unpack_app("566c935ba08b4fadf6d46763")

    # AppStore.zip_dir("../../apps/lib/alivinco_nAlarmApp_v1")
    # ast.upload_file_to_app_store("565c2411f8f87822daebe850","../../apps/lib/AlarmApp_v1.zip")
    # ast.upload_file_to_app_store("565c2411f8f87822daebe850","../../apps/lib/AlarmApp_v1.zip")
    # AppStore.download_file("http://localhost:8080/bfhub/api/file/56614b02f8f87822daebe854","../../apps/DeviceTypes_SDS11847-8.pdf")
    # AppStore.download_file("http://localhost:8080/bfhub/api/file/566c4dc0a08b4fadf6d46760","../../apps/alivinco_nServoCam_v1.zip")
    # AppStore.unzip_dir("../../apps/alivinco_nServoCam_v1.zip","../../apps")