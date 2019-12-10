

import uuid, os
import logging
import shutil
import json

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Utils(metaclass=Singleton):

    def create_and_get_ID(self):
        self.id = str(uuid.uuid4()).split("-")[4]
        return self.id

    def get_ID(self):
        return self.id

    def folder_path(self, filename):
        folder_name = os.path.dirname(filename)
        return folder_name

    def create_path(self, filename):
        folder_name = self.folder_path(filename)
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)


    def read_data_from_file(self, file_path):
        path = self.get_path(file_path)
        try:
            logger.debug("reading data from "+str(path))
            data = None
            if os.path.exists(path):
                with open(path, "r") as json_file:
                    data = json.load(json_file)
            return data
        except Exception as e:
            logger.error("Error while reading file ", str(path))
            logger.error(e)

    def store_data(self, fname, data):
        path = self.get_path(fname)
        self.create_path(path)
        logger.debug("path " + str(path))

        try:

            with open(path, 'w', encoding='utf-8') as outfile:
                json.dump(data, outfile, ensure_ascii=False, indent=2) # working

            logger.debug("input data saved in " + str(path))
        except Exception as e:
            logger.error("Error while storing file ", path)
            logger.error(e)


    def store_data_raw(self, fname, data):

        path = self.get_path(fname)
        #folder_path = self.getFolderPath(path)
        logger.debug("path " + str(path))

        try:

            #with open(path, "wb") as outfile:
                #outfile.write(str(data).encode('utf8'))

            with open(path, "w", encoding='utf-8') as outfile:
                json.dump(data, outfile, ensure_ascii=False, indent=2)
                # outfile.write(str(data))

            logger.debug("input data saved in " + str(path))
        except Exception as e:
            logger.error("Error while storing file ", path)
            logger.error(e)

    def get_path(self, relative_path):
        path_to_send = os.path.abspath(relative_path)
        #logger.debug("abs path " + str(path_to_send))
        return path_to_send

    def isFile(self, path):
        path = self.get_path(path)
        if os.path.isfile(path):
            return True
        else:
            return False

    def del_file_if_existing(self,filepath):
        filepath=self.get_path(filepath)
        logger.debug("filepath "+str(filepath))
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            logger.error("Error while deleting file ", filepath)
            logger.error(e)

    def deleteFile(self, path):
        path = self.get_path(path)
        if self.isFile(path):
            try:
                os.remove(path)
            except Exception as e:
                logger.error(e)
        else:
            logger.error("Path not existing")

    def delete_folder(self, folder_path):
        folder_path = self.get_path(folder_path)
        shutil.rmtree(folder_path, ignore_errors=True)

    def get_stored_data(self, fname):
        path = self.get_path(fname)
        #logger.debug("filepath for thread id "+str(filepath))
        try:
            if self.isFile(path):
                with open(path, "r") as myfile:
                    content = myfile.read()
                # logger.debug("File: " + str(optimization_result)+" type "+str(type(optimization_result)))
                data = json.loads(content)
                return data
            else:
                logger.debug("Filepath "+str(path)+" not existing")
                return 1

        except Exception as e:
            logger.debug("File path not existing")
            logger.error(e)
            return 1

    def is_dir_empty(self, folder_path):
        folder_path = self.get_path(folder_path)
        for dirpath, dirnames, files in os.walk(folder_path):
            if files or dirnames:
                return False
            if not files or dirnames:
                return True