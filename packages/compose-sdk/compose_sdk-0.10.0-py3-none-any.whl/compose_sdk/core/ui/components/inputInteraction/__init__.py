from ...constants import (
    INTERACTION_TYPE,
    TYPE,
    INPUT_UTILS,
    Nullable,
    ComponentReturn,
)
from .tableComponent import table, dataframe


def input_text(
    id: str,
    *,
    label: Nullable.Str = None,
    required: bool = True,
    description: Nullable.Str = None,
    validate: Nullable.Callable = None,
    on_enter: Nullable.Callable = None,
    style: Nullable.Style = None
) -> ComponentReturn:
    return {
        "model": {
            "id": id,
            "label": label,
            "description": description,
            "required": required,
            "hasValidateHook": validate is not None,
            "style": style,
            "properties": {
                "hasOnEnterHook": on_enter is not None,
            },
        },
        "hooks": {
            "validate": validate,
            "onEnter": on_enter,
        },
        "type": TYPE.INPUT_TEXT,
        "interactionType": INTERACTION_TYPE.INPUT,
    }


def input_email(
    id: str,
    *,
    label: Nullable.Str = None,
    required: bool = True,
    description: Nullable.Str = None,
    validate: Nullable.Callable = None,
    on_enter: Nullable.Callable = None,
    style: Nullable.Style = None
) -> ComponentReturn:
    return {
        "model": {
            "id": id,
            "label": label,
            "description": description,
            "required": required,
            "hasValidateHook": validate is not None,
            "style": style,
            "properties": {
                "hasOnEnterHook": on_enter is not None,
            },
        },
        "hooks": {
            "validate": validate,
            "onEnter": on_enter,
        },
        "type": TYPE.INPUT_EMAIL,
        "interactionType": INTERACTION_TYPE.INPUT,
    }


def input_url(
    id: str,
    *,
    label: Nullable.Str = None,
    required: bool = True,
    description: Nullable.Str = None,
    validate: Nullable.Callable = None,
    on_enter: Nullable.Callable = None,
    style: Nullable.Style = None
) -> ComponentReturn:
    return {
        "model": {
            "id": id,
            "label": label,
            "description": description,
            "required": required,
            "hasValidateHook": validate is not None,
            "style": style,
            "properties": {
                "hasOnEnterHook": on_enter is not None,
            },
        },
        "hooks": {
            "validate": validate,
            "onEnter": on_enter,
        },
        "type": TYPE.INPUT_URL,
        "interactionType": INTERACTION_TYPE.INPUT,
    }


def input_number(
    id: str,
    *,
    label: Nullable.Str = None,
    required: bool = True,
    description: Nullable.Str = None,
    validate: Nullable.Callable = None,
    on_enter: Nullable.Callable = None,
    style: Nullable.Style = None
) -> ComponentReturn:
    return {
        "model": {
            "id": id,
            "label": label,
            "description": description,
            "required": required,
            "hasValidateHook": validate is not None,
            "style": style,
            "properties": {
                "hasOnEnterHook": on_enter is not None,
            },
        },
        "hooks": {
            "validate": validate,
            "onEnter": on_enter,
        },
        "type": TYPE.INPUT_NUMBER,
        "interactionType": INTERACTION_TYPE.INPUT,
    }


def input_password(
    id: str,
    *,
    label: Nullable.Str = None,
    required: bool = True,
    description: Nullable.Str = None,
    validate: Nullable.Callable = None,
    on_enter: Nullable.Callable = None,
    style: Nullable.Style = None
) -> ComponentReturn:
    return {
        "model": {
            "id": id,
            "label": label,
            "description": description,
            "required": required,
            "hasValidateHook": validate is not None,
            "style": style,
            "properties": {
                "hasOnEnterHook": on_enter is not None,
            },
        },
        "hooks": {
            "validate": validate,
            "onEnter": on_enter,
        },
        "type": TYPE.INPUT_PASSWORD,
        "interactionType": INTERACTION_TYPE.INPUT,
    }


def radio_group(
    id: str,
    options: INPUT_UTILS.SelectOptions,
    *,
    label: Nullable.Str = None,
    required: bool = True,
    description: Nullable.Str = None,
    validate: Nullable.Callable = None,
    on_select: Nullable.Callable = None,
    style: Nullable.Style = None
) -> ComponentReturn:
    return {
        "model": {
            "id": id,
            "label": label,
            "description": description,
            "required": required,
            "hasValidateHook": validate is not None,
            "style": style,
            "properties": {
                "hasOnSelectHook": on_select is not None,
                "options": options,
            },
        },
        "hooks": {
            "validate": validate,
            "onSelect": on_select,
        },
        "type": TYPE.INPUT_RADIO_GROUP,
        "interactionType": INTERACTION_TYPE.INPUT,
    }


def select_dropdown_single(
    id: str,
    options: INPUT_UTILS.SelectOptions,
    *,
    label: Nullable.Str = None,
    required: bool = True,
    description: Nullable.Str = None,
    validate: Nullable.Callable = None,
    on_select: Nullable.Callable = None,
    style: Nullable.Style = None
) -> ComponentReturn:
    return {
        "model": {
            "id": id,
            "label": label,
            "description": description,
            "required": required,
            "hasValidateHook": validate is not None,
            "style": style,
            "properties": {
                "hasOnSelectHook": on_select is not None,
                "options": options,
            },
        },
        "hooks": {
            "validate": validate,
            "onSelect": on_select,
        },
        "type": TYPE.INPUT_SELECT_DROPDOWN_SINGLE,
        "interactionType": INTERACTION_TYPE.INPUT,
    }


def select_dropdown_multi(
    id: str,
    options: INPUT_UTILS.SelectOptions,
    *,
    label: Nullable.Str = None,
    required: bool = True,
    description: Nullable.Str = None,
    validate: Nullable.Callable = None,
    on_select: Nullable.Callable = None,
    style: Nullable.Style = None,
    min_selections: int = INPUT_UTILS.MULTI_SELECTION_MIN_DEFAULT,
    max_selections: int = INPUT_UTILS.MULTI_SELECTION_MAX_DEFAULT
) -> ComponentReturn:
    return {
        "model": {
            "id": id,
            "label": label,
            "description": description,
            "required": required,
            "hasValidateHook": validate is not None,
            "style": style,
            "properties": {
                "hasOnSelectHook": on_select is not None,
                "options": options,
                "minSelections": min_selections,
                "maxSelections": max_selections,
            },
        },
        "hooks": {
            "validate": validate,
            "onSelect": on_select,
        },
        "type": TYPE.INPUT_SELECT_DROPDOWN_MULTI,
        "interactionType": INTERACTION_TYPE.INPUT,
    }


def input_file_drop(
    id: str,
    *,
    label: Nullable.Str = None,
    required: bool = True,
    description: Nullable.Str = None,
    validate: Nullable.Callable = None,
    style: Nullable.Style = None,
    on_change: Nullable.Callable = None,
    accepted_file_types: Nullable.List.Str = None,
    min_count: int = INPUT_UTILS.MULTI_SELECTION_MIN_DEFAULT,
    max_count: int = INPUT_UTILS.MULTI_SELECTION_MAX_DEFAULT
) -> ComponentReturn:
    return {
        "model": {
            "id": id,
            "label": label,
            "description": description,
            "required": required,
            "hasValidateHook": validate is not None,
            "style": style,
            "properties": {
                "hasOnFileChangeHook": on_change is not None,
                "acceptedFileTypes": accepted_file_types,
                "minCount": min_count,
                "maxCount": max_count,
            },
        },
        "hooks": {
            "validate": validate,
            "onFileChange": on_change,
        },
        "type": TYPE.INPUT_FILE_DROP,
        "interactionType": INTERACTION_TYPE.INPUT,
    }
