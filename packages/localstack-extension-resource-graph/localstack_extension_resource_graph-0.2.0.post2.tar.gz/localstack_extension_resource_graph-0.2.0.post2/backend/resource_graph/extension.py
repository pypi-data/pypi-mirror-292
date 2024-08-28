import logging
import typing as t

from resource_graph.api.cors_handler import CorsLiberator

from backend.resource_graph.api.request_handler import RequestHandler
from localstack.extensions.patterns.webapp import WebAppExtension
from localstack.aws.chain import CompositeResponseHandler

from .api.web import WebApp

LOG = logging.getLogger(__name__)


class ResourceGraph(WebAppExtension):
    name = "resource-graph"
    
    def __init__(self):
        super().__init__(template_package_path=None)
        
    def collect_routes(self, routes: list[t.Any]):
        routes.append(WebApp())
        routes.append(RequestHandler())

    def update_response_handlers(self, handlers: CompositeResponseHandler):
        super().update_response_handlers(handlers)
        handlers.append(CorsLiberator())

