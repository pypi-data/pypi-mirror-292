import os
import json
import shutil
import uuid

from bohrium_open_sdk.opensdk.resources.sdms.model import Sample
from .sdms import Sdms
from datetime import datetime
import time
from operator import itemgetter
from .execptions import *
from .model import *
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import partial

logger = logging.getLogger(__name__)


class SdmsLocal(Sdms):
    def __init__(self, client, base_path):
        self.base_path = base_path

    def _add_characterization_preare(
        self,
        uploader_user_id: int,
        owner_id: int,
        char_techs: str,
        sample_id: str,
        name: str,
        type: str,
        allowed_suffixes=["xlsx", "pdf", "csv", "xls"],
        suffix="",
        description="",
    ):
        # 构建JSON数据
        data = {
            "uploader_user_id": uploader_user_id,
            "owner_id": owner_id,
            "char_techs": char_techs,
            "sample_id": sample_id,
            "name": name,
            "type": type,
            "allowed_suffixes": allowed_suffixes,
            "file_suffix": suffix,
            "description": description,
            "uuid": str(uuid.uuid4()),
            "file_path": f"{self.base_path}/raw_data/{owner_id}/{name}.{suffix}",
            "create_timestamp": int(time.time()),
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        char_meta = CharMeta(**data)
        # 确保目录存在
        os.makedirs(f"{self.base_path}/raw_data/{owner_id}", exist_ok=True)
        os.makedirs(f"{self.base_path}/meta/{owner_id}/{sample_id}", exist_ok=True)

        # 原数据
        meta_file_path = self._get_meta_file_path(owner_id, sample_id, name)

        return char_meta, meta_file_path

    def add_characterization_buffer(
        self,
        uploader_user_id: int,
        owner_id: int,
        char_techs: str,
        sample_id: str,
        name: str,
        type: str,
        allowed_suffixes=["xlsx", "pdf", "csv", "xls"],
        description="",
        buffer="",
        suffix="",
    ):

        try:
            # 检查文件后缀
            res = self._check_file_suffix("", suffix, allowed_suffixes)
            if not res[1]:
                logger.error(
                    f"add | user: {owner_id} | {name} | 不支持的文件后缀: {suffix}"
                )
                raise SdmsInvalidFileFormatError(f"不支持的文件后缀: {suffix}")

            # 检查样本是否存在
            self.sample_get(owner_id, sample_id)

            data, meta_file_path = self._add_characterization_preare(
                uploader_user_id,
                owner_id,
                char_techs,
                sample_id,
                name,
                type,
                allowed_suffixes,
                res[0],
                description,
            )

            # 如果原数据已存在，则返回错误
            if os.path.exists(meta_file_path):
                logger.error(
                    f"add | user: {owner_id} | {name} | 文件已存在: {os.path.basename(meta_file_path)}"
                )
                raise SdmsFileDuplicateError(
                    f"文件已存在: {os.path.basename(meta_file_path)}"
                )

            with open(meta_file_path, "w") as f:
                json.dump(data.to_dict(), f, indent=4)

            # 写入文件
            # 检查数据类型
            if isinstance(buffer, str):
                # 如果是字符串，使用文本写入模式
                with open(data.file_path, "w", encoding="utf-8") as file:
                    file.write(buffer)
            elif isinstance(buffer, bytes):
                # 如果是二进制数据，使用二进制写入模式
                with open(data.file_path, "wb") as file:
                    file.write(buffer)
            else:
                raise ValueError("不支持的数据类型。数据必须是字符串或二进制。")

            logger.info(f"add | user: {owner_id} | {name} | 上传成功")
            return os.path.basename(meta_file_path)
        except SdmsException as e:
            raise e
        except Exception as e:
            logger.error(f"add | user: {owner_id} | {name} | 异常: {e}")
            raise SdmsUnknownError(str(e))

    def add_characterization_file(
        self,
        uploader_user_id: int,
        owner_id: int,
        char_techs: str,
        sample_id: str,
        name: str,
        type: str,
        allowed_suffixes=["xlsx", "pdf", "csv", "xls"],
        description="",
        temp_file_path="",
        suffix="",
    ):

        try:
            # 检查文件后缀
            res = self._check_file_suffix(temp_file_path, suffix, allowed_suffixes)
            if not res[1]:
                logger.error(
                    f"add | user: {owner_id} | {name} | 不支持的文件后缀: {suffix}"
                )
                raise SdmsInvalidFileFormatError(f"不支持的文件后缀: {suffix}")

            # 确保临时文件存在
            if not os.path.exists(temp_file_path):
                logger.error(
                    f"add | user: {owner_id} | {name} | 临时文件不存在: {temp_file_path}"
                )
                raise SdmsFileNotFoundError(f"临时文件不存在: {temp_file_path}")

            # 检查样本是否存在
            self.sample_get(owner_id, sample_id)

            data, meta_file_path = self._add_characterization_preare(
                uploader_user_id,
                owner_id,
                char_techs,
                sample_id,
                name,
                type,
                allowed_suffixes,
                res[0],
                description,
            )

            # 原数据
            meta_file_path = self._get_meta_file_path(owner_id, sample_id, name)

            # 如果原数据已存在，则返回错误
            if os.path.exists(meta_file_path):
                logger.error(
                    f"add | user: {owner_id} | {name} | 文件已存在: {os.path.basename(meta_file_path)}"
                )
                raise SdmsFileDuplicateError(
                    f"文件已存在: {os.path.basename(meta_file_path)}"
                )

            with open(meta_file_path, "w") as f:
                json.dump(data.to_dict(), f, indent=4)

            # 复制文件
            shutil.copy2(temp_file_path, data.file_path)
            logger.info(f"add | user: {owner_id} | {name} | 上传成功")
            return os.path.basename(meta_file_path)

        except SdmsException as e:
            raise e
        except Exception as e:
            logger.error(f"add | user: {owner_id} |  {name} | 异常: {e}")
            raise SdmsUnknownError(str(e))

    def delete_characterization_file(self, user_id, sample_id: str, name):

        try:
            # 文件不存在, 直接返回成功
            meta_file_path = self._get_meta_file_path(user_id, sample_id, name)
            if not os.path.exists(meta_file_path):
                logger.info(f"delete | user: {user_id} | {name} | 文件不存在")
                return True

            # 读取JSON文件
            with open(meta_file_path, "r") as f:
                data = json.load(f)
            # 删除原始数据文件
            os.remove(data["file_path"])
            # 删除JSON文件
            os.remove(meta_file_path)

            logger.info(f"delete | user: {user_id} | {name} | 删除成功")
            return True
        except Exception as e:
            logger.error(f"delete | user: {user_id} | {name} | 异常: {e}")
            return False

    def _filter_data(self, data, user_id, scope, key_name, filter_criteria):
        """
        根据给定的过滤条件过滤数据
        """
        if scope == "public":
            # 如果 public 为 True，检查 public 字段
            return (
                data.get("public") == True
                and (key_name is None or key_name == "" or key_name in data.get("name"))
                and all(
                    data.get(key) == value for key, value in filter_criteria.items()
                )
            )

        if scope == "all":
            # 如果 public 为 True，检查 public 字段
            ok = data.get("public") == True
            # 该文件属于该用户，默认可以被查到
            ok = ok or data.get("owner_id") == user_id
            return (
                ok
                and (key_name is None or key_name == "" or key_name in data.get("name"))
                and all(
                    data.get(key) == value for key, value in filter_criteria.items()
                )
            )
        return (
            key_name is None or key_name == "" or key_name in data.get("name")
        ) and all(data.get(key) == value for key, value in filter_criteria.items())

    def _get_all_json_files(self, directory):
        """
        递归获取目录及其所有子目录中的所有 JSON 文件
        """
        json_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                # 排除sample.json文件
                if file.endswith(".json") and file != "sample.json":
                    json_files.append(os.path.join(root, file))
        return json_files

    # 分页查询
    def read_and_filter_file(
        self, file_path, user_id, scope, key_name, filter_criteria
    ):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                if self._filter_data(data, user_id, scope, key_name, filter_criteria):
                    return {
                        "file_path": file_path,
                        "data": data,
                        "mtime": os.path.getmtime(file_path),
                    }
        except json.JSONDecodeError:
            print(f"Error decoding JSON in file: {file_path}")
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")
        return None

    def search_files(
        self,
        user_id,
        scope,
        key_name,
        directory,
        filter_criteria,
        page=1,
        page_size=10,
    ):
        all_files = self._get_all_json_files(directory)

        with ThreadPoolExecutor(max_workers=16) as executor:
            partial_read_and_filter = partial(
                self.read_and_filter_file,
                user_id=user_id,
                scope=scope,
                key_name=key_name,
                filter_criteria=filter_criteria,
            )
            results = list(
                filter(None, executor.map(partial_read_and_filter, all_files))
            )

        # 按文件更新时间倒序排序
        results.sort(key=lambda x: x["mtime"], reverse=True)

        # 计算分页
        total_items = len(results)
        total_pages = (total_items + page_size - 1) // page_size
        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        paginated_results = results[start_index:end_index]

        return ChareMetaPage(
            page=page,
            total_items=total_items,
            total_pages=total_pages,
            data=[CharMeta(**result["data"]) for result in paginated_results],
        )

    def query_characterization_files(
        self,
        user_id,
        key_name,
        type,
        scope,
        simple_id,
        page,
        page_size,
    ):

        try:
            filter_criteria = {}
            # 获取用户目录下的所有文件
            directory = f"{self.base_path}/meta/{user_id}"
            if scope == "public" or scope == "all":
                directory = f"{self.base_path}/meta"

            if type:
                filter_criteria["type"] = type
            if simple_id:
                filter_criteria["sample_id"] = simple_id

            result = self.search_files(
                user_id=user_id,
                scope=scope,
                key_name=key_name,
                directory=directory,
                filter_criteria=filter_criteria,
                page=page,
                page_size=page_size,
            )

            return result
        except Exception as e:
            logger.error(f"query | user: {user_id} | {key_name} | 异常: {e}")
            return []

    def get_characterization_file(self, owner_id, sample_id: str, name):

        try:
            # 读取JSON文件
            meta_file_path = self._get_meta_file_path(owner_id, sample_id, name)
            with open(meta_file_path, "r") as f:
                data = json.load(f)

            meta_data = CharMeta.from_json(data)
            # 判断文件是否存在
            raw_data_path = meta_data.file_path

            if not os.path.exists(raw_data_path):
                logger.error(f"get | user: {owner_id} | {name} | 文件不存在")
                return None

            # 读取原始数据文件
            raw_bytes = self.read_in_chunks_bytes(raw_data_path)

            return CharContext(meta_data, raw_bytes)
        except Exception as e:
            logger.error(f"get | user: {owner_id} | {name} | 异常: {e}")
            return None

    def public_characterization_file(
        self, owner_id: int, sample_id: str, name: str, public: bool
    ):
        try:
            # 读取JSON文件
            meta_file_path = self._get_meta_file_path(owner_id, sample_id, name)
            with open(meta_file_path, "r") as f:
                data = json.load(f)

            data["public"] = public

            with open(meta_file_path, "w") as f:
                json.dump(data, f, indent=4)

            return True
        except Exception as e:
            logger.error(f"public | user: {owner_id} | {name} | 异常: {e}")
            return False

    def data_add(self, owner_id: int, name: str, content: str, exist_ok: bool = True):

        data_file_path = self._get_data_file_path(owner_id, name)
        if os.path.exists(data_file_path):
            if not exist_ok:
                logger.error(f"data add | user: {owner_id} | {name} | 文件已存在")
                raise SdmsFileDuplicateError(
                    f"文件已存在: {os.path.basename(data_file_path)}"
                )
            return self.data_put(owner_id, name, content)

        timestamp = int(time.time())
        yyyymmdd = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 构建JSON数据
        data = {
            "owner_id": owner_id,
            "name": name,
            "content": content,
            "create_timestamp": timestamp,
            "create_time": yyyymmdd,
            "update_timestamp": timestamp,
            "update_time": yyyymmdd,
        }
        data_meta = DataMeta(**data)

        # 确保目录存在
        os.makedirs(f"{self.base_path}/data/{owner_id}", exist_ok=True)

        try:
            # 写入文件
            with open(data_file_path, "w", encoding="utf-8") as file:
                json.dump(data_meta.to_dict(), file, indent=4)

            logger.info(f"data add | user: {owner_id} | {name} | 上传成功")
            return os.path.basename(data_file_path)
        except Exception as e:
            logger.error(f"data add | user: {owner_id} | {name} | 异常: {e}")
            raise SdmsUnknownError(str(e))

    def data_put(self, owner_id: int, name: str, content: str):

        data_file_path = self._get_data_file_path(owner_id, name)
        if not os.path.exists(data_file_path):
            logger.error(f"data put | user: {owner_id} | {name} | 文件不存在")
            raise SdmsFileNotFoundError(
                f"文件不存在: {os.path.basename(data_file_path)}"
            )

        # 读取现有数据
        datastr = self.read_in_chunks(data_file_path)
        data_data = DataMeta.from_json(datastr)
        data_data.update_timestamp = int(time.time())
        data_data.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data_data.content = content

        try:
            # 写入文件
            with open(data_file_path, "w", encoding="utf-8") as file:
                json.dump(data_data.to_dict(), file, indent=4)

            logger.info(f"data put | user: {owner_id} | {name} | 更新成功")
            return os.path.basename(data_file_path)
        except Exception as e:
            logger.error(f"data put | user: {owner_id} | {name} | 异常: {e}")
            raise SdmsUnknownError(str(e))

    def data_delete(self, owner_id: int, name: str):

        data_file_path = self._get_data_file_path(owner_id, name)
        if not os.path.exists(data_file_path):
            logger.error(f"data delete | user: {owner_id} | {name} | 文件不存在")
            return False

        try:
            os.remove(data_file_path)
            logger.info(f"data delete | user: {owner_id} | {name} | 删除成功")
            return True
        except Exception as e:
            logger.error(f"data delete | user: {owner_id} | {name} | 异常: {e}")
            return False

    def data_query(self, owner_id: int, key_name: str):

        try:
            # 获取用户目录下的所有文件
            data_dir = f"{self.base_path}/data/{owner_id}"
            if not os.path.exists(data_dir):
                logger.error(f"query | user: {owner_id} | {key_name} | 文件列表为空")
                return []

            # 获取文件列表并添加修改时间
            files = []
            for file in os.listdir(data_dir):
                if key_name in file or key_name is None or key_name == "":
                    file_path = os.path.join(data_dir, file)
                    update_time = os.path.getmtime(file_path)
                    files.append((file, update_time))
            # 按修改时间倒序排序
            files.sort(key=itemgetter(1), reverse=True)
            result = []
            # 剔除文件后缀
            for file, _ in files:
                result.append(os.path.splitext(file)[0])

            return result
        except Exception as e:
            logger.error(f"query | user: {owner_id} | {key_name} | 异常: {e}")
            return []

    def data_get(self, owner_id: int, name: str):
        try:
            data_file_path = self._get_data_file_path(owner_id, name)
            if not os.path.exists(data_file_path):
                logger.error(f"data get | user: {owner_id} | {name} | 文件不存在")
                return None

            data = self.read_in_chunks(data_file_path)

            return DataMeta.from_json(data)
        except Exception as e:
            logger.error(f"data get | user: {owner_id} | {name} | 异常: {e}")
            return None

    def sample_add(self, owner_id, name, description="", exist_ok=True):
        # 确保目录存在
        os.makedirs(f"{self.base_path}/meta/{owner_id}", exist_ok=True)

        # 获取用户下的sample.json文件
        sample_file_path = self._get_meta_sample_file_path(owner_id)
        # 文件不存在创建文件
        if not os.path.exists(sample_file_path):
            with open(sample_file_path, "w") as f:
                json.dump([], f)
        with self.file_lock(sample_file_path):

            with open(sample_file_path, "r", encoding="utf-8") as f:
                samples_data = json.load(f)

            samples = [Sample.from_json(sample_data) for sample_data in samples_data]

            # 判断是否已存在
            matching_sample = next(
                (sample for sample in samples if sample.name == name), None
            )
            if matching_sample:
                if not exist_ok:
                    raise SdmsFileDuplicateError(f"文件已存在: {name}")
                else:
                    return self.sample_update(
                        owner_id, matching_sample.uuid, {"description": description}
                    )

            new_uuid = str(uuid.uuid4())
            timestamp = int(time.time())
            yyyymmdd = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sample = Sample(
                uuid=new_uuid,
                name=name,
                description=description,
                owner_id=owner_id,
                create_timestamp=timestamp,
                create_time=yyyymmdd,
                update_timestamp=timestamp,
                update_time=yyyymmdd,
            )
            # 添加新 Sample 并写入文件
            samples.append(sample)
            samples_data = [sample.to_dict() for sample in samples]
            with open(sample_file_path, "w", encoding="utf-8") as f:
                json.dump(samples_data, f, indent=4, ensure_ascii=False)
        # 创建表征数据目录
        self._create_meta_chare_dir(owner_id, new_uuid)
        return True

    def sample_update(self, owner_id, uuid, params={}):
        sample_file_path = self._get_meta_sample_file_path(owner_id)
        if not os.path.exists(sample_file_path):
            raise SdmsFileNotFoundError(
                f"文件不存在: {os.path.basename(sample_file_path)}，请先创建样本"
            )
        with self.file_lock(sample_file_path):
            with open(sample_file_path, "r", encoding="utf-8") as f:
                samples_data = json.load(f)

            samples = [Sample.from_json(sample_data) for sample_data in samples_data]

            # Find the sample to update
            sample_to_update = next((s for s in samples if s.uuid == uuid), None)
            if not sample_to_update:
                raise SdmsSampleNotFoundError(f"Sample with UUID {uuid} not found")

            # Update sample attributes
            for key, value in params.items():
                if hasattr(sample_to_update, key):
                    setattr(sample_to_update, key, value)

            sample_to_update.update_timestamp = int(time.time())
            sample_to_update.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with open(sample_file_path, "w", encoding="utf-8") as f:
                json.dump(
                    [s.to_dict() for s in samples], f, indent=4, ensure_ascii=False
                )

        return True

    def sample_delete(self, owner_id, uuid):
        sample_file_path = self._get_meta_sample_file_path(owner_id)
        if not os.path.exists(sample_file_path):
            raise SdmsFileNotFoundError(
                f"文件不存在: {os.path.basename(sample_file_path)}，请先创建样本"
            )
        with self.file_lock(sample_file_path):
            with open(sample_file_path, "r", encoding="utf-8") as f:
                samples_data = json.load(f)

            samples = [Sample.from_json(sample_data) for sample_data in samples_data]

            # Find the sample to delete
            sample_to_delete = next((s for s in samples if s.uuid == uuid), None)
            if not sample_to_delete:
                raise SdmsSampleNotFoundError(f"Sample with UUID {uuid} not found")

            # Delete the sample
            samples.remove(sample_to_delete)

            with open(sample_file_path, "w", encoding="utf-8") as f:
                json.dump(
                    [s.to_dict() for s in samples], f, indent=4, ensure_ascii=False
                )

        # 删除表征数据目录
        self._delete_meta_chare_dir(owner_id, uuid)
        return True

    def sample_query(self, owner_id, key_name, page, page_size) -> SamplePage:
        sample_file_path = self._get_meta_sample_file_path(owner_id)
        if not os.path.exists(sample_file_path):
            return SamplePage(page=page, total_items=0, total_pages=0, data=[])
        with self.file_lock(sample_file_path):
            with open(sample_file_path, "r", encoding="utf-8") as f:
                samples_data = json.load(f)

            samples = [Sample.from_json(sample_data) for sample_data in samples_data]

            if key_name:
                samples = [s for s in samples if key_name in s.name]

            total_items = len(samples)
            total_pages = (total_items + page_size - 1) // page_size
            start_index = (page - 1) * page_size
            end_index = start_index + page_size

            # 改为按更新时间倒序排序
            samples.sort(key=lambda x: x.update_timestamp, reverse=True)
            paginated_samples = samples[start_index:end_index]

            return SamplePage(
                page=page,
                total_items=total_items,
                total_pages=total_pages,
                data=paginated_samples,
            )

    def sample_get(self, owner_id, uuid) -> Sample:
        if not uuid:
            raise SdmsSampleNotFoundError("Sample UUID is required")

        sample_file_path = self._get_meta_sample_file_path(owner_id)
        if not os.path.exists(sample_file_path):
            raise SdmsFileNotFoundError(
                f"文件不存在: {os.path.basename(sample_file_path)}，请先创建样本"
            )
        with self.file_lock(sample_file_path):
            with open(sample_file_path, "r", encoding="utf-8") as f:
                samples_data = json.load(f)

            samples = [Sample.from_json(sample_data) for sample_data in samples_data]

            sample = next((s for s in samples if s.uuid == uuid), None)
            if not sample:
                raise SdmsSampleNotFoundError(f"Sample with UUID {uuid} not found")

            return sample
