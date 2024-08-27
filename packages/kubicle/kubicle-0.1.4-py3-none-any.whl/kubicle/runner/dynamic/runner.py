import os
from typing import Optional, Dict, List

from kubicle.runner.base import JobRunner, DEFAULT_OWNER_REF
from kubicle.server.models import V1UserProfile


def DynamicRunner(
    local: bool = False,
    namespace: Optional[str] = None,
    owner_ref: V1UserProfile = DEFAULT_OWNER_REF,
    img: Optional[str] = None,
    envs: Dict[str, str] = {},
    include_env: List[str] = [],
) -> JobRunner:
    """
    Returns a JobRunner that dynamically loads a module and function at runtime.
    """

    from kubicle.runner.k8s.runner import K8sJobRunner
    from kubicle.runner.process.runner import ProcessJobRunner

    is_local = os.getenv("JOB_LOCAL")
    if is_local:
        if is_local.lower == "true":
            local = True

    if local:
        return ProcessJobRunner(owner_ref=owner_ref)
    else:
        return K8sJobRunner(
            namespace=namespace,
            owner_ref=owner_ref,
            img=img,
            envs=envs,
            include_env=include_env,
        )
