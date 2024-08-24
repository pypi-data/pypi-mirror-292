from modelbit.api import MbApi
from modelbit.internal.auth import mbApiReadOnly
from modelbit.git.filter import GitFilter
from modelbit.git.git_protocol import GitProtocol
from modelbit.git.workspace import findWorkspace
from modelbit.internal.local_config import getWorkspaceConfig
from modelbit.telemetry import eatErrorAndLog
from modelbit.git.validations import writePreCommitHook

errorHandler = lambda msg: eatErrorAndLog(mbApiReadOnly(), msg)  # type: ignore


@errorHandler('Failed to filter files.')
def process():
  workspaceId = findWorkspace()

  config = getWorkspaceConfig(workspaceId)
  if not config:
    raise KeyError("workspace config not found")
  api = MbApi(config.gitUserAuthToken, config.cluster)

  writePreCommitHook()  # install/update hooks during normal git workflows

  gitApi = GitFilter(workspaceId, api)
  protocol = GitProtocol(gitApi)
  protocol.filterProcess()
