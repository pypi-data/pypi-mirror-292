import pandas
from ...constants import (
    INTERACTION_TYPE,
    TYPE,
    INPUT_UTILS,
    Nullable,
    ComponentReturn,
    TableData,
)


def get_model_actions(
    actions: Nullable.TableActions,
) -> Nullable.TableActionsWithoutOnClick:
    if actions is None:
        return None

    return [
        {key: value for key, value in action.items() if key != "on_click"}
        for action in actions
    ]


def get_hook_actions(actions: Nullable.TableActions) -> Nullable.TableActionsOnClick:
    if actions is None:
        return None

    return [action["on_click"] for action in actions]


def _table(
    id: str,
    data: TableData,
    *,
    label: Nullable.Str = None,
    required: bool = True,
    description: Nullable.Str = None,
    validate: Nullable.Callable = None,
    on_select: Nullable.Callable = None,
    columns: Nullable.TableColumns = None,
    actions: Nullable.TableActions = None,
    style: Nullable.Style = None,
    min_selections: int = INPUT_UTILS.MULTI_SELECTION_MIN_DEFAULT,
    max_selections: int = INPUT_UTILS.MULTI_SELECTION_MAX_DEFAULT,
    allow_select: bool = True
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
                "data": data,
                "columns": columns,
                "actions": get_model_actions(actions),
                "minSelections": min_selections,
                "maxSelections": max_selections,
                "allowSelect": allow_select,
            },
        },
        "hooks": {
            "validate": validate,
            "onSelect": on_select,
            "onRowActions": get_hook_actions(actions),
        },
        "type": TYPE.INPUT_TABLE,
        "interactionType": INTERACTION_TYPE.INPUT,
    }


def table(
    id: str,
    data: TableData,
    *,
    label: Nullable.Str = None,
    required: bool = True,
    description: Nullable.Str = None,
    validate: Nullable.Callable = None,
    on_select: Nullable.Callable = None,
    columns: Nullable.TableColumns = None,
    actions: Nullable.TableActions = None,
    style: Nullable.Style = None,
    min_selections: int = INPUT_UTILS.MULTI_SELECTION_MIN_DEFAULT,
    max_selections: int = INPUT_UTILS.MULTI_SELECTION_MAX_DEFAULT,
    allow_select: bool = True
) -> ComponentReturn:
    return _table(
        id,
        data,
        label=label,
        required=required,
        description=description,
        validate=validate,
        on_select=on_select,
        style=style,
        columns=columns,
        actions=actions,
        min_selections=min_selections,
        max_selections=max_selections,
        allow_select=allow_select,
    )


def dataframe(
    id: str,
    df: pandas.DataFrame,
    *,
    label: Nullable.Str = None,
    required: bool = True,
    description: Nullable.Str = None,
    validate: Nullable.Callable = None,
    on_select: Nullable.Callable = None,
    actions: Nullable.TableActions = None,
    style: Nullable.Style = None,
    min_selections: int = INPUT_UTILS.MULTI_SELECTION_MIN_DEFAULT,
    max_selections: int = INPUT_UTILS.MULTI_SELECTION_MAX_DEFAULT,
    allow_select: bool = True
) -> ComponentReturn:

    # Replace empty values in the dataframe with None
    df = df.replace({None: "", pandas.NA: "", float("nan"): ""})

    # Create the "columns" array
    columns: INPUT_UTILS.TableColumns = [
        {"key": col, "label": col} for col in df.columns
    ]

    # Create the "table" array
    table: TableData = df.to_dict(orient="records")  # type: ignore

    return _table(
        id,
        table,
        label=label,
        required=required,
        description=description,
        validate=validate,
        on_select=on_select,
        style=style,
        columns=columns,
        actions=actions,
        min_selections=min_selections,
        max_selections=max_selections,
        allow_select=allow_select,
    )
