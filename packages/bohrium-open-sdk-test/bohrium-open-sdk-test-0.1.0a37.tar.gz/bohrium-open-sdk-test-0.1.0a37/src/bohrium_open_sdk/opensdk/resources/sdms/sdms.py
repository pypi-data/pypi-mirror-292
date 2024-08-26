import os
from bohrium_open_sdk.opensdk._resource import SyncAPIResource
from .execptions import *
from .model import *
from contextlib import contextmanager

# import fcntl


class Sdms(SyncAPIResource):
    def __init__(self, client):
        base_path = os.getenv("SDMS_BASE_PATH")
        if base_path:
            self.base_path = base_path
        else:
            self.base_path = "/tmp/sdms"
            # 警告！
            print(
                "\033[93m[Warning] SDMS_BASE_PATH is not set, use default path: /tmp/sdms\033[0m"
            )
        # if storage_type == "oss":
        #     return SdmsOss(*args, **kwargs)
        # else:
        from .local import SdmsLocal  # type: ignore

        self.client = SdmsLocal(client, self.base_path)

    def _ensure_base_path(self):
        """确保基础路径存在"""
        if not os.path.exists(self.base_path):
            try:
                os.makedirs(self.base_path)
                print(f"Created base directory: {self.base_path}")
            except Exception as e:
                print(f"Error creating base directory: {e}")
                raise SdmsUnknownError(f"Error creating base directory: {e}")

    def _check_file_suffix(
        self, filename, suffix, allowed_suffixes
    ) -> tuple[str, bool]:
        """
        检查文件后缀是否在允许的列表中（不区分大小写）

        参数:
        filename: 文件名
        allowed_suffixes: 允许的后缀列表

        返回:
        如果后缀有效返回True，否则返回False
        """
        if suffix is not None and suffix != "":
            file_suffix = suffix
        else:
            file_suffix = os.path.splitext(filename)[1][1:].lower()
        return file_suffix, file_suffix.lower() in [
            suffix.lower() for suffix in allowed_suffixes
        ]

    def _get_meta_file_path(self, owner_id, sample_id, name):
        """获取元数据文件路径

        Args:
            owner_id (_type_): 归属用户id
            name (_type_): 表征数据名

        Returns:
            _type_: str
        """
        # json名要替换调原始数据的后缀
        json_file_name = os.path.splitext(name)[0] + ".json"
        return f"{self.base_path}/meta/{owner_id}/{sample_id}/{json_file_name}"

    def _get_meta_sample_file_path(self, owner_id):
        """获取样本元数据文件路径"""
        return f"{self.base_path}/meta/{owner_id}/sample.json"

    def _create_meta_chare_dir(self, owner_id, sample_id):
        os.makedirs(f"{self.base_path}/meta/{owner_id}/{sample_id}", exist_ok=True)

    def _delete_meta_chare_dir(self, owner_id, sample_id):
        # 文件下有数据时不做强制删除
        os.rmdir(f"{self.base_path}/meta/{owner_id}/{sample_id}")

    def _get_data_file_path(self, owner_id, name):
        """获取结果文件路径

        Args:
            owner_id (_type_): 归属用户id
            name (_type_): 结果文件名

        Returns:
            _type_: str
        """
        json_file_name = os.path.splitext(name)[0] + ".json"
        return f"{self.base_path}/data/{owner_id}/{json_file_name}"

    def read_in_chunks(self, file_path, chunk_size=1024 * 1024):
        """
        Lazy function (generator) to read a file piece by piece.
        """
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return "".join(iter(lambda: f.read(chunk_size), ""))

    def read_in_chunks_bytes(self, file_path, chunk_size=1024 * 1024):
        """
        Lazy function (generator) to read a file piece by piece.
        """
        with open(file_path, "rb") as f:
            return b"".join(iter(lambda: f.read(chunk_size), b""))

    @contextmanager
    def file_lock(self, file_path):
        """
        获取文件锁
        """
        with open(file_path, "r+") as f:
            # fcntl.flock(f, fcntl.LOCK_EX)
            try:
                yield f
            finally:
                ...
                # fcntl.flock(f, fcntl.LOCK_UN)

    # 新增样本
    def sample_add(self, owner_id, name, description="", exist_ok=True):
        """
        新增样本

        参数说明:
        owner_id: 归属用户id
        name: 样本名
        description: 描述
        exist_ok: 是否覆盖已存在样本

        返回:
            成功: True
            失败: 异常 SdmsException
        """
        self._ensure_base_path()
        return self.client.sample_add(owner_id, name, description, exist_ok)

    # 修改样本名称，描述
    def sample_update(self, owner_id, uuid, params={}):
        """
        修改样本名称，描述

        参数说明:
        owner_id: 归属用户id
        uuid: 样本uuid
        params: 修改参数

        返回:
            成功: True
            失败: 异常 SdmsException

        """
        self._ensure_base_path()
        return self.client.sample_update(owner_id, uuid, params)

    def sample_delete(self, owner_id, uuid):
        """
        删除样本

        参数说明:
        owner_id: 归属用户id
        uuid: 样本uuid

        返回:
            成功: True
            失败: 异常 SdmsException
        """
        self._ensure_base_path()
        return self.client.sample_delete(owner_id, uuid)

    def sample_query(self, owner_id, key_name, page=1, page_size=10) -> SamplePage:
        """
        根据关键词查询样本列表

        参数说明:
        owner_id: 归属用户id
        key_name: 关键词, 匹配样本名称
        page: 页码 (可选)
        page_size: 每页数量 (可选)

        返回: SamplePage

        """
        self._ensure_base_path()
        return self.client.sample_query(owner_id, key_name, page, page_size)

    def sample_get(self, owner_id, uuid) -> Sample:
        """
        获取样本信息

        参数说明:
        owner_id: 归属用户id
        uuid: 样本uuid

        返回:
            成功: Sample
            失败: 异常 SdmsException
        """
        self._ensure_base_path()
        return self.client.sample_get(owner_id, uuid)

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
        """
        添加表征缓冲区

        参数说明:
        uploader_user_id: 上传用户id
        owner_id: 归属用户id
        char_techs: 机器型号
        sample_id: 样本id
        name: 表征数据名
        type: 表征类型
        allowed_suffixes: 表征文件名支持后缀列表
        description: 描述
        buffer: 缓冲区
        suffix: 表征文件后缀, 不可为空

        owner_id + name 作为唯一标识

        返回:
            成功: str, 文件名
            失败: 异常 SdmsException
        """
        self._ensure_base_path()
        return self.client.add_characterization_buffer(
            uploader_user_id,
            owner_id,
            char_techs,
            sample_id,
            name,
            type,
            allowed_suffixes,
            description,
            buffer,
            suffix,
        )

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
        """
        添加表征文件

        参数说明:
        uploader_user_id: 上传用户id
        owner_id: 归属用户id
        char_techs: 机器型号
        sample_id: 样本id
        name: 表征数据名, 同用户不允许重复
        type: 表征类型
        allowed_suffixes: 表征文件名支持后缀列表
        description: 描述
        temp_file_path: 临时文件路径
        suffix: 表征文件后缀，可为空，自动从temp_file_path截取

        owner_id + name 作为唯一标识

        返回:
            成功: str, 文件名
            失败: 异常 SdmsException
        """

        self._ensure_base_path()
        return self.client.add_characterization_file(
            uploader_user_id,
            owner_id,
            char_techs,
            sample_id,
            name,
            type,
            allowed_suffixes,
            description,
            temp_file_path,
            suffix,
        )

    def delete_characterization_file(self, owner_id, sample_id: str, name) -> bool:
        """
        删除表征文件

        参数说明:
        owner_id: 归属用户id
        name: 表征数据名

        返回:
            True: 成功
            False: 失败
        """
        self._ensure_base_path()
        return self.client.delete_characterization_file(owner_id, sample_id, name)

    def query_characterization_files(
        self,
        owner_id,
        key_name,
        type: str = "",
        scope: str = "private",
        simple_id: str = "",
        page: int = 1,
        page_size: int = 10,
    ) -> ChareMetaPage:
        """
        根据关键词查询表征文件列表

        参数说明:
        owner_id: 归属用户id
        key_name: 关键词, 匹配文件名称
        type: 表征类型 (可选)
        simple_id: 样本id (可选)
        scope: 查询范围, private 私有, public 公开, all 所有 (可选)
        page: 页码 (可选)
        page_size: 每页数量 (可选)


        返回: 列表[{元信息},{元信息},...]

        """
        self._ensure_base_path()
        return self.client.query_characterization_files(
            owner_id, key_name, type, scope, simple_id, page, page_size
        )

    def get_characterization_file(self, owner_id, sample_id: str, name) -> CharContext:
        """
        获取表征文件内容

        参数说明:
        owner_id: 归属用户id
        name: 表征数据名

        返回:
            存在数据：CharContext 对象
            无数据或者异常： None
        """
        self._ensure_base_path()
        return self.client.get_characterization_file(owner_id, sample_id, name)

    def public_characterization_file(
        self, owner_id: int, sample_id: str, name: str, public: bool
    ) -> bool:
        """
        公开/取消公开表征文件

        参数说明:
        owner_id: 归属用户id
        name: 表征数据名
        public: True 公开, False 取消公开

        返回:
            成功: True
            失败: False
        """
        self._ensure_base_path()
        return self.client.public_characterization_file(
            owner_id, sample_id, name, public
        )

    ### 数据件操作 START###
    #
    # 当前只支持本地存储
    # 数据文件和表征数据没有逻辑关联
    #
    ###

    def data_add(self, owner_id: int, name: str, content: str, exist_ok: bool = True):
        """
        添加数据文件

        参数说明:
        owner_id: 归属用户id
        name: 数据文件名
        content: 数据文件内容
        exist_ok: 是否覆盖已存在文件

        返回:
            成功: str, 文件名
            失败: 异常 SdmsException
        """
        self._ensure_base_path()
        return self.client.data_add(owner_id, name, content, exist_ok)

    def data_delete(self, owner_id: int, name: str) -> bool:
        """
        删除数据文件

        参数说明:
        owner_id: 归属用户id
        name: 数据文件名

        返回:
            成功: True
            失败: False
        """
        self._ensure_base_path()
        return self.client.data_delete(owner_id, name)

    def data_query(self, owner_id: int, key_name: str) -> list[str]:
        """
        根据关键词查询数据文件列表

        参数说明:
        owner_id: 归属用户id
        key_name: 关键词, 匹配文件名称

        返回: 列表[文件名1, 文件名2,...]
        """
        self._ensure_base_path()
        return self.client.data_query(owner_id, key_name)

    def data_get(self, owner_id: int, name: str) -> DataMeta:
        """
        获取数据文件内容

        参数说明:
        owner_id: 归属用户id
        name: 数据文件名

        返回:
            成功: DataMeta
            不存在 & 失败异常: None
        """
        self._ensure_base_path()
        return self.client.data_get(owner_id, name)

    ####结果文件操作 END####
