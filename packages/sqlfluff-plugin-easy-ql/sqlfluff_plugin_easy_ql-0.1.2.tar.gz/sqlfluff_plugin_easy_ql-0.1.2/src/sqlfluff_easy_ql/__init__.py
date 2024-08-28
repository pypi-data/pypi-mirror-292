from typing import List, Type

from sqlfluff.core.config import ConfigLoader
from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.rules import BaseRule


@hookimpl
def get_rules() -> List[Type[BaseRule]]:
    """Get plugin rules.

    NOTE: It is much better that we only import the rule on demand.
    The root module of the plugin (i.e. this file which contains
    all of the hook implementations) should have fully loaded before
    we try and import the rules. This is partly for performance
    reasons - but more because the definition of a BaseRule requires
    that all of the get_configs_info() methods have both been
    defined _and have run_ before so all the validation information
    is available for the validation steps in the meta class.
    """
    # i.e. we DO recommend importing here:
    from sqlfluff_easy_ql.rules import (
        Rule_EasyQL_L002,
        Rule_EasyQL_L003
    )  # noqa: F811
    from sqlfluff_easy_ql.LT02 import Rule_EasyQL_LT02
    from sqlfluff_easy_ql.LT01 import Rule_EasyQL_LT01

    return [Rule_EasyQL_LT01, Rule_EasyQL_LT02,
            Rule_EasyQL_L002, Rule_EasyQL_L003]


@hookimpl
def load_default_config() -> dict:
    """Loads the default configuration for the plugin."""
    return ConfigLoader.get_global().load_config_resource(
        package="sqlfluff_easy_ql",
        file_name="easy_ql_default_config.cfg",
    )


@hookimpl
def get_configs_info() -> dict:
    """Get rule config validations and descriptions."""
    return {
        "forbidden_columns": {"definition": "A list of column to forbid"},
    }
