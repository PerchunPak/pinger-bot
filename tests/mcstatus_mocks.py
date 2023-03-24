"""These are mocks for ``mcstatus``' answer objects to stop using aliases or deprecated properties."""
import abc
import typing

import mcstatus.status_response


def raise_exception_for_alias(new_name: str) -> None:
    """Raise an exception for using an unwanted alias."""
    raise AttributeError(f"Unwanted alias used. Please use '{new_name}' instead.")


class MockedBaseStatusResponse(mcstatus.status_response.BaseStatusResponse, abc.ABC):
    @property
    def description(self) -> typing.NoReturn:  # type: ignore[misc] # Implicit return in function which does not return
        raise_exception_for_alias("motd")


class MockedBedrockStatusResponse(mcstatus.status_response.BedrockStatusResponse):
    @property
    def players_online(self) -> typing.NoReturn:  # type: ignore[misc] # Implicit return in function which does not return
        raise_exception_for_alias("players.online")

    @property
    def players_max(self) -> typing.NoReturn:  # type: ignore[misc] # Implicit return in function which does not return
        raise_exception_for_alias("players.max")

    @property
    def map(self) -> typing.NoReturn:  # type: ignore[misc] # Implicit return in function which does not return
        raise_exception_for_alias("map_name")


class MockedJavaStatusPlayer(mcstatus.status_response.JavaStatusPlayer):
    @property
    def fake_id(self) -> typing.NoReturn:  # type: ignore[misc] # Implicit return in function which does not return
        raise_exception_for_alias("uuid")

    def __post_init__(self) -> None:
        self._uuid = self.id
        self.id = self.fake_id

    @property
    def uuid(self) -> str:
        return self._uuid


class MockedBedrockStatusVersion(mcstatus.status_response.BedrockStatusVersion):
    @property
    def version(self) -> typing.NoReturn:  # type: ignore[misc] # Implicit return in function which does not return
        raise_exception_for_alias("name")


mcstatus.status_response.BaseStatusResponse = MockedBaseStatusResponse  # type: ignore[misc] # Cannot assign to a type
mcstatus.status_response.BedrockStatusResponse = MockedBedrockStatusResponse  # type: ignore[misc] # Cannot assign to a type
mcstatus.status_response.JavaStatusPlayer = MockedJavaStatusPlayer  # type: ignore[misc] # Cannot assign to a type
mcstatus.status_response.BedrockStatusVersion = MockedBedrockStatusVersion  # type: ignore[misc] # Cannot assign to a type
