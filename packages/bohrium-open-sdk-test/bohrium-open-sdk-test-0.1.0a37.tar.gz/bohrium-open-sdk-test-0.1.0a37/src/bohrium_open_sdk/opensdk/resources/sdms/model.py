from dataclasses import dataclass, asdict, field
import json


@dataclass
class CharMeta:
    uploader_user_id: str
    owner_id: str
    char_techs: str
    sample_id: str
    name: str
    type: str
    allowed_suffixes: list
    file_suffix: str
    description: str
    uuid: str
    file_path: str
    create_timestamp: int
    create_time: str
    public: bool = False

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_json(cls, json_data):
        # 如果 json_data 是字符串，先解析它
        if isinstance(json_data, str):
            json_data = json.loads(json_data)

        # 创建 CharMeta 实例
        return cls(**json_data)


@dataclass
class CharContext:
    char_meta: CharMeta
    raw_data: bytes

    def to_dict(self):
        return asdict(self)


@dataclass
class DataMeta:
    owner_id: str
    name: str
    content: str
    create_timestamp: int
    create_time: str
    update_timestamp: int
    update_time: str

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_json(cls, json_data):
        # 如果 json_data 是字符串，先解析它
        if isinstance(json_data, str):
            json_data = json.loads(json_data)

        # 创建 ResultMeta 实例
        return cls(**json_data)


@dataclass
class ChareMetaPage:
    page: int
    total_items: int
    total_pages: int
    data: list[CharMeta] = field(default_factory=list)

    @classmethod
    def from_json(cls, json_data):
        # 如果 json_data 是字符串，先解析它
        if isinstance(json_data, str):
            json_data = json.loads(json_data)

        # 创建 ChareMetaPage 实例
        return cls(**json_data)


@dataclass
class Sample:
    uuid: str
    name: str
    description: str
    owner_id: str
    create_timestamp: int
    create_time: str
    update_timestamp: int
    update_time: str

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_json(cls, json_data):
        # 如果 json_data 是字符串，先解析它
        if isinstance(json_data, str):
            json_data = json.loads(json_data)

        # 创建 Sample 实例
        return cls(**json_data)


@dataclass
class SamplePage:
    page: int
    total_items: int
    total_pages: int
    data: list[Sample] = field(default_factory=list)

    @classmethod
    def from_json(cls, json_data):
        # 如果 json_data 是字符串，先解析它
        if isinstance(json_data, str):
            json_data = json.loads(json_data)

        # 创建 SamplePage 实例
        return cls(**json_data)
