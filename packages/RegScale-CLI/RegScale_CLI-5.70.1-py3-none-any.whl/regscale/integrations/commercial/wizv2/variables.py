#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Wiz Variables """

from regscale.core.app.utils.variables import RsVariableType, RsVariablesMeta


class WizVariables(metaclass=RsVariablesMeta):
    """
    Wiz Variables class to define class-level attributes with type annotations and examples
    """

    # Define class-level attributes with type annotations and examples
    wizFullPullLimitHours: RsVariableType(int, 8)  # type: ignore # noqa: F722
    wizUrl: RsVariableType(str, "https://api.us27.app.wiz.io/graphql", required=False)  # type: ignore # noqa: F722
    wizIssueFilterBy: RsVariableType(str, '{"projectId": ["84874a63-4af8-554a-9c67-e50c78f17f32"], "type": ["API_GATEWAY"]}')  # type: ignore # noqa: F722,F821
    wizAccessToken: RsVariableType(str, "", sensitive=True)  # type: ignore # noqa: F722,F821
    WizClientId: RsVariableType(str, "", sensitive=True)  # type: ignore # noqa: F722,F821
    WizClientSecret: RsVariableType(str, "", sensitive=True)  # type: ignore # noqa: F722,F821
    wizLastInventoryPull: RsVariableType(str, "2022-01-01T00:00:00Z", required=False)  # type: ignore # noqa: F722
