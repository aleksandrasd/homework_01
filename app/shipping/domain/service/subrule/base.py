import logging
from typing import Any, Mapping

logger = logging.getLogger(__name__)


class BaseRuleSystem:
    """
    Base class for rule system.

    Base class for rule system. Example of rule system: eligibility rule
    system. Class that inherits rule system becomes a registered rule (e.g.,
    class becomes an eligibility rule if it inherits eligibility rule system).
    This class provides default behavior for a rule system.

    Subrule classes must contain attribute `__rule_name__` - a string that
    contains unique name for a rule. If the attribute is missing, exception is
    raised.

    Methods:
      get_rules: returns registered rules.
      __init_subclass__: registers a rule.
    """

    _rules: dict[str, type[Any]] | None = None

    @classmethod
    def get_rules(cls) -> Mapping[str, type[Any]]:
        """Get registered rules.

        Returns:
            rules name (taken from subclass'es attribute __rule_name__).
        """
        return cls._rules if cls._rules is not None else {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if cls._rules is None:
            cls._rules = {}

        if "__rule_name__" in cls.__dict__:
            logger.debug(
                "Subrule system: %s. Adding rule: %s.",
                cls.__rule_system__,
                cls.__rule_name__,
            )
            if cls.__rule_name__ in cls._rules:
                raise ValueError(
                    f"Can't register rule {cls.__rule_name__},",
                    " because it is already registered.",
                )
            cls._rules[cls.__rule_name__] = cls
        elif "__rule_system__" not in cls.__dict__:
            raise TypeError(
                (
                    "Class must contain attribute __rule_system__"
                    " or __rule_name__."
                )
            )
