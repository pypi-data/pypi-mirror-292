"""redcap target class."""

from singer_sdk.target_base import Target
from singer_sdk import typing as th

from target_redcap.sinks import (
    redcapSink,
)


class Targetredcap(Target):
    """Sample target for redcap."""

    name = "target-redcap"
    config_jsonschema = th.PropertiesList(    
        th.Property(
            "token",
            th.StringType,
            description="The token to authenticate against the API service"
        ),
        th.Property(
            "base_url",
            th.StringType,
            description="Base URL for RedCap API service"
        ),
        th.Property(
            "api_timeout",
            th.IntegerType,
            description="Base URL for RedCap API service"
        ),
        th.Property(
            "action",
            th.StringType,
            description="Specify form for export."
        ),
        th.Property(
            "content",
            th.StringType,
            description="Specify form for export."
        ),
        th.Property(
            "forms",
            th.ArrayType(th.StringType),
            description="Specify form for export."
        ),
        th.Property(
            "events",
            th.StringType,
            description="Specify events for export."
        ),
        th.Property(
            "format",
            th.StringType,
            description="Specify format for export."
        ),
        th.Property(
            "rawOrLabel",
            th.StringType,
            description="Specify raw or label data for export."
        ),
        th.Property(
            "rawOrLabelHeaders",
            th.StringType,
            description="Specify raw or label data headers for export."
        ),
        th.Property(
            "exportCheckboxLabel",
            th.StringType,
            description="Specify checbox labels for export."
        ),
        th.Property(
            "exportSurveyFields",
            th.StringType,
            description="Specify survey fields for export."
        ),
        th.Property(
            "returnFormat",
            th.StringType,
            description="Specify survey return format for export."
        ),
        th.Property(
            "type",
            th.StringType,
            description="Specify type for export."
        ),
        th.Property(
            "exportDataAccessGroups",
            th.StringType,
            description="Specify export for data access group."
        ),
    ).to_dict()
    default_sink_class = redcapSink
