import ray
from typing import Callable, List, Any


@ray.remote
def remote_func(func: Callable, item: Any) -> Any:
    return func(item)


class RayBackend:
    def __init__(self):
        if not ray.is_initialized():
            ray.init(ignore_reinit_error=True, include_dashboard=False)

    def map(self, func: Callable, items: List[Any]) -> List[Any]:
        if not items:
            return []
        futures = [remote_func.remote(func, item) for item in items]
        return ray.get(futures)
