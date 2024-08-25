"""
Lyzr tool spec.
"""

import types
import typing as t
from inspect import Signature

from lyzr_automata import Tool

from composio import Action, ActionType, AppType, TagType, WorkspaceConfigType
from composio.constants import DEFAULT_ENTITY_ID
from composio.tools import ComposioToolSet as BaseComposioToolSet
from composio.tools.toolset import MetadataType, ProcessorsType
from composio.utils.shared import (
    get_signature_format_from_schema_params,
    json_schema_to_model,
)


class ComposioToolSet(BaseComposioToolSet):
    """
    Composio toolset for Lyzr framework.
    """

    def __init__(
        self,
        api_key: t.Optional[str] = None,
        base_url: t.Optional[str] = None,
        entity_id: str = DEFAULT_ENTITY_ID,
        output_in_file: bool = False,
        workspace_config: t.Optional[WorkspaceConfigType] = None,
        workspace_id: t.Optional[str] = None,
        metadata: t.Optional[MetadataType] = None,
        processors: t.Optional[ProcessorsType] = None,
    ) -> None:
        """
        Initialize composio toolset.

        :param api_key: Composio API key
        :param base_url: Base URL for the Composio API server
        :param entity_id: Entity ID for making function calls
        :param output_in_file: Whether to write output to a file
        """
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            runtime="lyzr",
            entity_id=entity_id,
            output_in_file=output_in_file,
            workspace_config=workspace_config,
            workspace_id=workspace_id,
            metadata=metadata,
            processors=processors,
        )

    def _wrap_tool(
        self,
        schema: t.Dict,
        entity_id: t.Optional[str] = None,
    ) -> Tool:
        """
        Wrap composio tool as Lyzr `Tool` object.
        """
        name = schema["name"]
        description = schema["description"]

        def function(**kwargs: t.Any) -> t.Dict:
            """Composio tool wrapped as Lyzr tool."""
            return self.execute_action(
                action=Action(value=name),
                params=kwargs,
                entity_id=entity_id or self.entity_id,
            )

        action_func = types.FunctionType(
            function.__code__,
            globals=globals(),
            name=name,
            closure=function.__closure__,
        )
        action_func.__signature__ = Signature(  # type: ignore
            parameters=get_signature_format_from_schema_params(
                schema_params=schema["parameters"],
            )
        )
        action_func.__doc__ = description
        return Tool(
            name=name,
            desc=description,
            function=action_func,
            function_input=json_schema_to_model(
                json_schema=schema["parameters"],
            ),
            function_output=json_schema_to_model(
                json_schema=schema["response"],
            ),
            default_params={},
        )

    def get_actions(
        self,
        actions: t.Sequence[ActionType],
        entity_id: t.Optional[str] = None,
    ) -> t.List[Tool]:
        """
        Get composio tools wrapped as Lyzr `Tool` objects.

        :param actions: List of actions to wrap
        :param entity_id: Entity ID to use for executing function calls.
        :return: Composio tools wrapped as `Tool` objects
        """
        return [
            self._wrap_tool(
                schema=schema.model_dump(exclude_none=True),
                entity_id=entity_id or self.entity_id,
            )
            for schema in self.get_action_schemas(actions=actions)
        ]

    def get_tools(
        self,
        apps: t.Sequence[AppType],
        tags: t.Optional[t.List[TagType]] = None,
        entity_id: t.Optional[str] = None,
    ) -> t.Sequence[Tool]:
        """
        Get composio tools wrapped as Lyzr `Tool` objects.

        :param apps: List of apps to wrap
        :param tags: Filter the apps by given tags
        :param entity_id: Entity ID to use for executing function calls.
        :return: Composio tools wrapped as `Tool` objects
        """
        return [
            self._wrap_tool(
                schema=schema.model_dump(exclude_none=True),
                entity_id=entity_id or self.entity_id,
            )
            for schema in self.get_action_schemas(apps=apps, tags=tags)
        ]
