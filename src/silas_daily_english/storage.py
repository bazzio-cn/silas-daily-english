import json
import shutil
from pathlib import Path
from typing import Optional

from .config import require_env


class LocalPublisher:
    def __init__(self, root: Path):
        self.root = root

    def load_state(self) -> Optional[dict]:
        path = self.root / "state.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def upload(self, source: Path, key: str) -> None:
        destination = self.root / key
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


class COSPublisher:
    def __init__(self):
        from qcloud_cos import CosConfig, CosS3Client

        self.bucket = require_env("COS_BUCKET")
        self.prefix = require_env("COS_PREFIX").strip("/")
        config = CosConfig(
            Region=require_env("COS_REGION"),
            SecretId=require_env("TENCENT_SECRET_ID"),
            SecretKey=require_env("TENCENT_SECRET_KEY"),
            Scheme="https",
        )
        self.client = CosS3Client(config)

    def load_state(self) -> Optional[dict]:
        try:
            response = self.client.get_object(
                Bucket=self.bucket,
                Key=self._key("state.json"),
            )
        except Exception as error:
            if "NoSuchKey" in str(error) or "404" in str(error):
                return None
            raise
        return json.loads(response["Body"].get_raw_stream().read().decode("utf-8"))

    def upload(self, source: Path, key: str) -> None:
        self.client.upload_file(
            Bucket=self.bucket,
            LocalFilePath=str(source),
            Key=self._key(key),
        )

    def _key(self, key: str) -> str:
        return "{}/{}".format(self.prefix, key.lstrip("/"))
