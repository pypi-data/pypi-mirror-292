"""
Base URL: https://www.pathwaycommons.org/pc2/

Endpoints
---------
/search
/top_pathways
/traverse
/neighborhood
/pathsbetween
/pathsfromto
/commonstream
"""

from fast_bioservices.base import BaseModel
from fast_bioservices.fast_http import FastHTTP, Response
from fast_bioservices.settings import default_workers


class PathwayCommons(BaseModel, FastHTTP):
    def __init__(
        self,
        *,
        cache: bool = True,
        show_progress: bool = False,
        workers: int = default_workers,
    ):
        self._url: str = "https://www.pathwaycommons.org/pc2/v2"
        BaseModel.__init__(self, url=self._url)
        FastHTTP.__init__(self, cache=cache, workers=workers, show_progress=show_progress, max_requests_per_second=3)

    def fetch(
        self,
    ):
        pass
