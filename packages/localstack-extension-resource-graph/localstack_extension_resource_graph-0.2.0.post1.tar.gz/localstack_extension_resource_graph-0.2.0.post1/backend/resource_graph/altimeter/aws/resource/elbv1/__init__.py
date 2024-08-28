"""ResourceSpec classes for classic elb resources."""

from resource_graph.altimeter.aws.resource.resource_spec import AWSResourceSpec


class ELBV1ResourceSpec(AWSResourceSpec):
    """Abstract base for ResourceSpec classes for classic elb resources."""

    service_name = "elb"
