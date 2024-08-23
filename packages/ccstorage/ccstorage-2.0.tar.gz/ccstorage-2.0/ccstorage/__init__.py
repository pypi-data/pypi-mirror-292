import os
import io
import json
from typing import Union
import avro.schema
import avro.io


class CCIO:

    @staticmethod
    def read_string(file_name):
        if os.path.isfile(file_name):
            with open(file_name) as f:
                lst = f.read()
                return lst
        else:
            return None

    @staticmethod
    def save_string(string, file_name):
        dir_path = os.path.dirname(file_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        with open(file_name, "w") as f:
            f.write(string)

    @staticmethod
    def read_bytes(file_name):
        if os.path.isfile(file_name):
            with open(file_name, 'rb') as file:
                read_data = file.read()
                return read_data
        else:
            return None

    @staticmethod
    def save_bytes(bytes, file_name):
        dir_path = os.path.dirname(file_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        try:
            with open(file_name, 'wb') as file:
                file.write(bytes)
        except Exception as inst:
            print('CCIO save_bytes failed:', inst)


class CCStorage:

    def __init__(self, root_dir_path: str, relative_file_path: str, storage_type: str= 'json', storage_schema=''):
        self.__abs_path: str = os.path.realpath(os.path.join(root_dir_path, relative_file_path))
        self.__storage_type = storage_type
        if storage_type == 'avro':
            try:
                self.__storage_schema = avro.schema.parse(storage_schema)
            except Exception as inst:
                print('CCStorage avro storage schema error:', str(inst))
        self.__storage_dict: {str: str} = {}
        self.force_reload_at_data_access = False  # 每次存取字段时都要强制读写持久化文件，daemon中重启进程的storage建议开启
        self.content_loaded = False
        self.read()

    def __write_in_json(self) -> None:
        json_str = json.dumps(self.__storage_dict, indent=4, ensure_ascii=False)
        CCIO.save_string(json_str, self.__abs_path)

    def __write_in_avro(self) -> None:
        try:
            bytes_writer = io.BytesIO()
            encoder = avro.io.DatumWriter(self.__storage_schema)
            encoder.write(self.__storage_dict, avro.io.BinaryEncoder(bytes_writer))
            serialized_data = bytes_writer.getvalue()
            CCIO.save_bytes(serialized_data, self.__abs_path)
        except Exception as inst:
            print('__write_in_avro failed:', str(inst))
        return

    def write(self) -> None:
        if self.__storage_type == 'avro':
            self.__write_in_avro()
        else:
            self.__write_in_json()

    def __read_in_json(self) -> None:
        content = CCIO.read_string(self.__abs_path)
        if content is not None and isinstance(content, str):
            try:
                result = json.loads(content)
                if isinstance(result, dict):
                    self.__storage_dict = result
                    self.content_loaded = True
                    return True
            except Exception as e:
                print('ccstorage __read_in_json exception: ', e)
        self.content_loaded = False
        return False

    def __read_in_avro(self) -> None:
        serialized_data = CCIO.read_bytes(self.__abs_path)
        if serialized_data is not None:
            try:
                bytes_reader = io.BytesIO(serialized_data)
                decoder = avro.io.DatumReader(self.__storage_schema)
                result = decoder.read(avro.io.BinaryDecoder(bytes_reader))
                if isinstance(result, dict):
                    self.__storage_dict = result
                    self.content_loaded = True
                    return True
            except Exception as e:
                print('ccstorage __read_in_avro exception: ', e)
        self.content_loaded = False
        return False

    def read(self) -> bool:
        if self.__storage_type == 'avro':
            return self.__read_in_avro()
        else:
            return self.__read_in_json()

    def resort(self, key: str, reverse: bool):
        sorted_data = sorted(self.__storage_dict.items(), key=lambda x: x[1][key], reverse=reverse)
        self.__storage_dict = sorted_data

    def __setitem__(self, key: str, value: Union[str, int, float, dict, list, None]) -> None:
        if self.force_reload_at_data_access is True:
            self.read()
        if value is None:
            self.__storage_dict.pop(key, None)
        else:
            self.__storage_dict[key] = value
        if self.force_reload_at_data_access:
            self.write()

    def __getitem__(self, item) -> Union[str, float, dict, list]:
        if self.force_reload_at_data_access:
            self.read()
        return self.__storage_dict.get(item)

    def get(self, key):
        return self.__storage_dict.get(key)

    def keys(self):
        return self.__storage_dict.keys()
