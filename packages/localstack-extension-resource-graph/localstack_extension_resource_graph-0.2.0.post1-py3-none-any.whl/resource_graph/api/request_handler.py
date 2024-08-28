import json
import logging
from typing import TypedDict

from resource_graph.config import COMPUTE_STATUS_PATH, GENERATE_GRAPH_PATH, GET_ARNS_PATH, GET_SUPPORTED_RESOURCES, IMPORT_GRAPH_PATH

from backend.resource_graph.api.resource_extractor import ResourceExtractor
from localstack.http import Request, route
from localstack.utils.strings import to_str

from resource_graph.altimeter.aws.scan.settings import DEFAULT_RESOURCE_SPEC_CLASSES

LOG = logging.getLogger(__name__)

class ActionStatus(TypedDict):
    status: str
    error: str | None
    
class ScanningStatus(TypedDict):
    is_scanning: bool
    is_importing: bool
    has_error: bool
    
class ResourcesList(TypedDict):
    resources: list[str]

class RequestHandler:
    resource_extractor: ResourceExtractor
    rdf_path: str | None

    def __init__(self):
        self.resource_extractor = ResourceExtractor.get()
        self.rdf_path = None

    @route(GET_SUPPORTED_RESOURCES, methods=["GET"])
    def handle_get_supported_resources(self, request: Request, **kwargs):
        resList = []
        for x in DEFAULT_RESOURCE_SPEC_CLASSES:
            resList.append(f"{x.service_name}:{x.type_name}")
        return ResourcesList(resources=sorted(resList))

    @route(COMPUTE_STATUS_PATH, methods=["GET"])
    def handle_get_compute_status(self, request: Request, **kwargs):
        is_scanning, is_importing, has_error = self.resource_extractor.get_compute_status()
        return ScanningStatus(
            is_scanning=is_scanning,
            is_importing=is_importing,
            has_error=has_error,
        )

    @route(GENERATE_GRAPH_PATH, methods=["POST"])
    def handle_generate_file(self, request: Request, **kwargs):
        payload = _get_json(request)
        if "regions" not in payload or payload["regions"] == []:
            return ActionStatus(
                status="error",
                error="Missing regions in payload"
                )
        e, path = self.resource_extractor.start_scanner(payload["regions"])
        if not e:
            self.rdf_path = path
            return ActionStatus(status="success",error=None)
        else:
            return ActionStatus(status="error",error=str(e))

    @route(GET_ARNS_PATH, methods=["GET"])
    def handle_get_arns(self, request: Request, **kwargs):
        return self.resource_extractor.get_arn_dict()

    @route(IMPORT_GRAPH_PATH, methods=["POST"])
    def handle_replicate(self, request: Request, **kwargs):
        payload = _get_json(request)
        if "port" not in payload:
            return ActionStatus(
                status="error",
                error="missing neptune port in payload"
                )
        try:
            if not self.rdf_path:
                regions = payload["regions"] if "regions" in payload else []
                e, path = self.resource_extractor.start_scanner(regions)
                if e:
                    raise Exception(e)
                self.rdf_path = path
            self.resource_extractor.read_xml_blocks(self.rdf_path, payload["port"])
            return ActionStatus(status="success",error=None)
        except Exception as e:
            LOG.error(e)
            return ActionStatus(status="error",error=str(e))


def _get_json(request: Request) -> dict:
    try:
        return request.json # type: ignore
    except Exception:
        return json.loads(to_str(request.data))
