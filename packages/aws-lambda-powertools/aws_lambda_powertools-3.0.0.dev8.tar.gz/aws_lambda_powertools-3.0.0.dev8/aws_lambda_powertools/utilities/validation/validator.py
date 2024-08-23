from __future__ import annotations

import logging
from typing import Any, Callable

from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from aws_lambda_powertools.utilities import jmespath_utils
from aws_lambda_powertools.utilities.validation.base import validate_data_against_schema

logger = logging.getLogger(__name__)


@lambda_handler_decorator
def validator(
    handler: Callable,
    event: dict | str,
    context: Any,
    inbound_schema: dict | None = None,
    inbound_formats: dict | None = None,
    outbound_schema: dict | None = None,
    outbound_formats: dict | None = None,
    envelope: str = "",
    jmespath_options: dict | None = None,
    **kwargs: Any,
) -> Any:
    """Lambda handler decorator to validate incoming/outbound data using a JSON Schema

    Parameters
    ----------
    handler : Callable
        Method to annotate on
    event : dict
        Lambda event to be validated
    context : Any
        Lambda context object
    inbound_schema : dict
        JSON Schema to validate incoming event
    outbound_schema : dict
        JSON Schema to validate outbound event
    envelope : dict
        JMESPath expression to filter data against
    jmespath_options : dict
        Alternative JMESPath options to be included when filtering expr
    inbound_formats: dict
        Custom formats containing a key (e.g. int64) and a value expressed as regex or callback returning bool
    outbound_formats: dict
        Custom formats containing a key (e.g. int64) and a value expressed as regex or callback returning bool

    Example
    -------

    **Validate incoming event**

        from aws_lambda_powertools.utilities.validation import validator

        @validator(inbound_schema=json_schema_dict)
        def handler(event, context):
            return event

    **Validate incoming and outgoing event**

        from aws_lambda_powertools.utilities.validation import validator

        @validator(inbound_schema=json_schema_dict, outbound_schema=response_json_schema_dict)
        def handler(event, context):
            return event

    **Unwrap event before validating against actual payload - using built-in envelopes**

        from aws_lambda_powertools.utilities.validation import validator, envelopes

        @validator(inbound_schema=json_schema_dict, envelope=envelopes.API_GATEWAY_REST)
        def handler(event, context):
            return event

    **Unwrap event before validating against actual payload - using custom JMESPath expression**

        from aws_lambda_powertools.utilities.validation import validator

        @validator(inbound_schema=json_schema_dict, envelope="payload[*].my_data")
        def handler(event, context):
            return event

    **Unwrap and deserialize JSON string event before validating against actual payload - using built-in functions**

        from aws_lambda_powertools.utilities.validation import validator

        @validator(inbound_schema=json_schema_dict, envelope="Records[*].powertools_json(body)")
        def handler(event, context):
            return event

    **Unwrap, decode base64 and deserialize JSON string event before validating against actual payload - using built-in functions**

        from aws_lambda_powertools.utilities.validation import validator

        @validator(inbound_schema=json_schema_dict, envelope="Records[*].kinesis.powertools_json(powertools_base64(data))")
        def handler(event, context):
            return event

    **Unwrap, decompress ZIP archive and deserialize JSON string event before validating against actual payload - using built-in functions**

        from aws_lambda_powertools.utilities.validation import validator

        @validator(inbound_schema=json_schema_dict, envelope="awslogs.powertools_base64_gzip(data) | powertools_json(@).logEvents[*]")
        def handler(event, context):
            return event

    Returns
    -------
    Any
        Lambda handler response

    Raises
    ------
    SchemaValidationError
        When schema validation fails against data set
    InvalidSchemaFormatError
        When JSON schema provided is invalid
    InvalidEnvelopeExpressionError
        When JMESPath expression to unwrap event is invalid
    """  # noqa: E501
    if envelope:
        event = jmespath_utils.query(
            data=event,
            envelope=envelope,
            jmespath_options=jmespath_options,
        )

    if inbound_schema:
        logger.debug("Validating inbound event")
        validate_data_against_schema(data=event, schema=inbound_schema, formats=inbound_formats)

    response = handler(event, context, **kwargs)

    if outbound_schema:
        logger.debug("Validating outbound event")
        validate_data_against_schema(data=response, schema=outbound_schema, formats=outbound_formats)

    return response


def validate(
    event: Any,
    schema: dict,
    formats: dict | None = None,
    envelope: str | None = None,
    jmespath_options: dict | None = None,
):
    """Standalone function to validate event data using a JSON Schema

     Typically used when you need more control over the validation process.

    Parameters
    ----------
    event : dict
        Lambda event to be validated
    schema : dict
        JSON Schema to validate incoming event
    envelope : dict
        JMESPath expression to filter data against
    jmespath_options : dict
        Alternative JMESPath options to be included when filtering expr
    formats: dict
        Custom formats containing a key (e.g. int64) and a value expressed as regex or callback returning bool

    Example
    -------

    **Validate event**

        from aws_lambda_powertools.utilities.validation import validate

        def handler(event, context):
            validate(event=event, schema=json_schema_dict)
            return event

    **Unwrap event before validating against actual payload - using built-in envelopes**

        from aws_lambda_powertools.utilities.validation import validate, envelopes

        def handler(event, context):
            validate(event=event, schema=json_schema_dict, envelope=envelopes.API_GATEWAY_REST)
            return event

    **Unwrap event before validating against actual payload - using custom JMESPath expression**

        from aws_lambda_powertools.utilities.validation import validate

        def handler(event, context):
            validate(event=event, schema=json_schema_dict, envelope="payload[*].my_data")
            return event

    **Unwrap and deserialize JSON string event before validating against actual payload - using built-in functions**

        from aws_lambda_powertools.utilities.validation import validate

        def handler(event, context):
            validate(event=event, schema=json_schema_dict, envelope="Records[*].powertools_json(body)")
            return event

    **Unwrap, decode base64 and deserialize JSON string event before validating against actual payload - using built-in functions**

        from aws_lambda_powertools.utilities.validation import validate

        def handler(event, context):
            validate(event=event, schema=json_schema_dict, envelope="Records[*].kinesis.powertools_json(powertools_base64(data))")
            return event

    **Unwrap, decompress ZIP archive and deserialize JSON string event before validating against actual payload - using built-in functions**

        from aws_lambda_powertools.utilities.validation import validate

        def handler(event, context):
            validate(event=event, schema=json_schema_dict, envelope="awslogs.powertools_base64_gzip(data) | powertools_json(@).logEvents[*]")
            return event

    Raises
    ------
    SchemaValidationError
        When schema validation fails against data set
    InvalidSchemaFormatError
        When JSON schema provided is invalid
    InvalidEnvelopeExpressionError
        When JMESPath expression to unwrap event is invalid
    """  # noqa: E501
    if envelope:
        event = jmespath_utils.query(
            data=event,
            envelope=envelope,
            jmespath_options=jmespath_options,
        )

    validate_data_against_schema(data=event, schema=schema, formats=formats)
