import typing

from rest_framework.exceptions import ValidationError

StrategyResult = typing.TypeVar("StrategyResult")


class Strategy(typing.Generic[StrategyResult]):
    is_validated = False

    def validate(self) -> None:
        self._validate()
        self.is_validated = True

    def _validate(self) -> None:
        """Здесь у дочерних классов должна выполняться валидация."""

    def start(self) -> StrategyResult:
        if not self.is_validated:
            self.validate()

        return self._start()

    def _start(self) -> StrategyResult:
        """Здесь у дочерних классов должна быть бизнес-логика."""

    def _raise(
        self,
        non_field_errors: list[str] | None = None,
        **kwargs: dict[str, list[str]],
    ) -> None:
        """
        Использовать этот метод чтоб упасть с ошибкой.

        Если падение происходит в рамках запроса DRF, то ответ превратится в HTTP 400.

        Примеры:
        1. self._raise(["foobar"])
        -> ValidationError({"non_field_errors": ["foobar"]})

        2. self._raise(foo=["bar"])
        -> ValidationError({"foo": ["bar"]})

        3. self._raise(["foobar"], foo=["bar"])
        -> ValidationError({"non_field_errors": ["foobar], "foo": ["bar"]})
        """

        messages = {**kwargs}
        if non_field_errors:
            messages["non_field_errors"] = non_field_errors

        raise ValidationError(messages)
