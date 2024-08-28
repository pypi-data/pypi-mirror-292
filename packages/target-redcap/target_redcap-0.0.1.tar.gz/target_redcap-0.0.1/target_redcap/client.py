import json
from target_redcap.utils import Session


class REDCapWrapperClient:

    def __init__(
            self,
            base_url,
            token,
            logger
    ):    
        self.logger = logger
        self.token = token
        self.api = base_url
        
    def _get_response(self, content, params=None, **kwargs):
        all_params = {
            "token": self.token,
            "content": content,
            "format": "json",
            "returnContent": "count",
            "returnFormat": "json",
            "dateFormat": "MDY",
            "action": "import"
        }
        all_params.update(params or {})
        if "data" in all_params and not isinstance(all_params["data"], str):
            all_params["data"] = json.dumps(all_params["data"])
        all_params = {k: v for k, v in all_params.items() if v is not None}
        self.logger.info(all_params)
        resp = Session(status_forcelist=(502, 503, 504)).post(
            self.api, data=all_params, **kwargs
        )
        self.logger.info(resp)
        return resp

    def set_records(self, records, type="eav", overwrite=False, auto_number=False):
        args = {
            "type": type,
            "data": records,
            "overwriteBehavior": "normal",
            "forceAutoNumber": "false"
        }
        self.logger.info(args)
        if auto_number:
            args["returnContent"] = "auto_ids"
        return self._get_response("record", params=args)