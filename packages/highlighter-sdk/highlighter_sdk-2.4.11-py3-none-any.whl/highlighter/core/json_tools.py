from datetime import datetime
from json import JSONEncoder
from uuid import UUID

__all__ = ["HLJSONEncoder"]


class HLJSONEncoder(JSONEncoder):
    def default(self, obj):
        # ToDo: Maybe add more custom endoders for various
        # HLBaseModels
        if isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)
