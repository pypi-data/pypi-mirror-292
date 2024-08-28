def required_last(schema: dict) -> dict:
    """Modify JSON schema to recursively put all 'required' fields at the end of the schema.

    This is done because otherwise the 'required' fields
    are checked by jsonschema before filling the defaults,
    which can cause the validation to fail.

    Returns
    -------
    dict
        Modified schema.
        Note that the input schema is modified in-place,
        so the return value is a reference to the (now modified) input schema.
    """
    if "required" in schema:
        schema["required"] = schema.pop("required")
    for key in ["anyOf", "allOf", "oneOf", "prefixItems"]:
        if key in schema:
            for subschema in schema[key]:
                required_last(subschema)
    for key in ["if", "then", "else", "not", "items", "additionalProperties"]:
        if key in schema and isinstance(schema[key], dict):
            required_last(schema[key])
    if "properties" in schema and isinstance(schema["properties"], dict):
        for subschema in schema["properties"].values():
            required_last(subschema)
    return schema