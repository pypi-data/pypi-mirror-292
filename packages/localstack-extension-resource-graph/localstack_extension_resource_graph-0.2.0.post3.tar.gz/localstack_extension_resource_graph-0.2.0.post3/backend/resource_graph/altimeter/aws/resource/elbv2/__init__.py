"""ResourceSpec classes for elbv2 resources."""

from resource_graph.altimeter.aws.resource.resource_spec import AWSResourceSpec


class ELBV2ResourceSpec(AWSResourceSpec):
    """Abstract base for ResourceSpec classes for elbv2 resources."""

    service_name = "elbv2"
