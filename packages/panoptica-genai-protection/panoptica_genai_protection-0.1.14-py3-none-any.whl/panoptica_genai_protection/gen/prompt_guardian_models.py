# generated by datamodel-codegen:
#   filename:  prompt_guardian.yaml

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class CheckPromptRequest(BaseModel):
    text: str = Field(..., description='Prompt or text to be checked')
    extractedUrls: Optional[List[str]] = Field(None, description='Unused')
    check_url: Optional[bool] = Field(True, description='')
    check_openai: Optional[bool] = Field(
        False, description='used only in vowel plugins v2'
    )
    check_gemini: Optional[bool] = Field(
        False, description='used only in vowel plugins v2'
    )
    check_azure: Optional[bool] = Field(
        False, description='used only in vowel plugins v2'
    )
    check_threats: Optional[bool] = Field(
        False, description='used only in vowel plugins v2'
    )
    run_id: Optional[str] = Field(None, description='')


class CheckURLVerdictResult(BaseModel):
    target: str = Field(..., description='')
    threat_categories: Optional[List[str]] = Field(None, description='')
    acceptable_use_policy_categories: Optional[List[str]] = Field(
        None,
        description="acceptable_use_policy_categories classifies website content, for example, 'Education', 'Shopping', etc. Talos integration team requires this field name for showing to users",
    )
    child_abuse_site: Optional[bool] = Field(
        None,
        description='child_abuse_site indicates whether this particular URL is considered a child abuse site',
    )
    source: Optional[str] = Field(None, description='')


class URLHausRequest(BaseModel):
    url: str = Field(..., description='URL to be added to the DB')
    tags: Optional[List[str]] = Field(None, description='')
    threat: Optional[List[str]] = Field(None, description='')


class SourceType(Enum):
    Talos = 'Talos'
    URLhaus = 'URLhaus'
    System = 'System'


class RequestDisabledMessage(Enum):
    THREATS = 'THREATS'
    URL = 'URL'


class TalosAUPCategoryType(Enum):
    CHILD_ABUSE_AUP_CAT_ID = 64


class TalosThreatLevelType(Enum):
    THREAT_LEVEL_ID_MALICIOUS = 1


class CheckPromptResult(BaseModel):
    url_verdict: List[CheckURLVerdictResult]
    threats: str = Field(..., description='DLP threat results')
