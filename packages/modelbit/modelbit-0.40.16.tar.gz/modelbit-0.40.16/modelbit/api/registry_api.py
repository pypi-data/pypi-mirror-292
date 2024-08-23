import logging
from typing import Any, Dict, List, cast
from modelbit.api import MbApi, writeLimiter, readLimiter
from modelbit.helpers import getCurrentBranch
from modelbit.internal.retry import retry
from modelbit.internal.secure_storage import DownloadableObjectInfo

logger = logging.getLogger(__name__)


class RegistryApi:
  api: MbApi

  def __init__(self, api: MbApi):
    self.api = api

  def delete(self, names: List[str]):
    writeLimiter.maybeDelay()
    self.api.getJsonOrThrow("api/cli/v1/registry/delete", {"branch": getCurrentBranch(), "names": names})

  @retry(2, logger)
  def storeContentHashAndMetadata(self, objects: Dict[str, Dict[str, Any]]):
    writeLimiter.maybeDelay()
    self.api.getJsonOrThrow("api/cli/v1/registry/set", {"branch": getCurrentBranch(), "objects": objects})

  def getRegistryDownloadInfo(self):
    readLimiter.maybeDelay()
    resp = self.api.getJsonOrThrow("api/cli/v1/registry/get_signed_url", {"branch": getCurrentBranch()})
    if "downloadInfo" in resp:
      return RegistryDownloadInfo(resp["downloadInfo"])

  def fetchModelMetrics(self, modelNames: List[str]) -> Dict[str, Dict[str, Any]]:
    readLimiter.maybeDelay()
    resp = self.api.getJsonOrThrow("api/cli/v1/registry/get_metadata", {
        "branch": getCurrentBranch(),
        "modelNames": modelNames
    })

    if "metadataByName" not in resp:
      logger.warn(f"Unexpected response, metadataByName missing from {resp.keys()}")
      return {}

    metricsByName: Dict[str, Dict[str, Any]] = {}
    metadataByName = cast(Dict[str, Dict[str, Any]], resp["metadataByName"])
    for name, metadata in metadataByName.items():
      if "metrics" in metadata and metadata["metrics"] is not None:
        metricsByName[name] = metadata["metrics"]
    return metricsByName

  @retry(2, logger)
  def updateMetadata(self, name: str, metrics: Dict[str, Any], mergeMetrics: bool = False):
    writeLimiter.maybeDelay()
    self.api.getJsonOrThrow("api/cli/v1/registry/update_metadata", {
        "branch": getCurrentBranch(),
        "name": name,
        "metrics": metrics,
        "mergeMetrics": mergeMetrics
    })


class RegistryDownloadInfo(DownloadableObjectInfo):

  def __init__(self, data: Dict[str, Any]):
    super().__init__(data)
    self.id: str = data["id"]

  def cachekey(self) -> str:
    return self.id
