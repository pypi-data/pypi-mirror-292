from datetime import date, datetime
from typing import Any, Dict, Union

import pydantic
from pydantic import BaseModel


class DeprecationInfo(BaseModel):
    deprecation_date: Union[datetime, date] = pydantic.Field()
    removal_date: Union[datetime, date] = pydantic.Field()


class GlobalVersions(BaseModel):
    deprecated: Dict[str, DeprecationInfo] = pydantic.Field()
    deployed: Dict[str, Any] = pydantic.Field()
