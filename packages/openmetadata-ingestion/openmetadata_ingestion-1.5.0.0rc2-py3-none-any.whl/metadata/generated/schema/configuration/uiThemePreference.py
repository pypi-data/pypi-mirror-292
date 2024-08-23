# generated by datamodel-codegen:
#   filename:  configuration/uiThemePreference.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel

from . import logoConfiguration, themeConfiguration


class UiThemePreference(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    customLogoConfig: Annotated[
        logoConfiguration.LogoConfiguration,
        Field(
            description="References the LogoConfiguration schema which includes settings related to the custom logos used in the application's user interface."
        ),
    ]
    customTheme: Annotated[
        themeConfiguration.ThemeConfiguration,
        Field(
            description="References the ThemeConfiguration schema that defines the custom theme color used in the application's user interface."
        ),
    ]
