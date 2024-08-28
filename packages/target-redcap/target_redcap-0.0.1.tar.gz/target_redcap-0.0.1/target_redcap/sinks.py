"""redcap target sink class, which handles writing streams."""


from singer_sdk.sinks import BatchSink
from target_redcap.client import REDCapWrapperClient
import json


class redcapSink(BatchSink):
    """redcap target sink class."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._client = None

    max_size = 10000  # Max records to write in one batch
    
    @property
    def client(self) -> REDCapWrapperClient:
        if not self._client:
            self._client = REDCapWrapperClient(
                self.config.get("base_url"),
                self.config.get("token"),
                self.logger,
            )
        return self._client

    def process_batch(self, context: dict) -> None:
        """Write out any prepped records and return once fully written.

        Args:
            context: Stream partition or context dictionary.
        """
        # Instantiate a REDCap API client
        
        records = context["records"]
        self.logger.info(records)

        for record in records:
            record.pop('id', None)
        
        records = json.dumps(records)
        records_to_submit = json.loads(records)
        self.logger.info(records_to_submit)
        
        self.client.set_records(
            records_to_submit
        )
    
        # Clean up records
        #context["records"] = []