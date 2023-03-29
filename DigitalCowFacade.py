from DigitalCow import DigitalCow
from DairyState import State
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Generic, TypeVar

T = TypeVar("T")


class AbstractDigitalTwinFacade(ABC, Generic[T]):
    """An abstract base class for a digital twin facade.

    A digital twin facade is a class that represents a digital twin and provides a high-level
    interface for interacting with it. This class defines the basic properties and methods that
    all digital twin facades should have.
    """

    def __init__(self, digital_twin: T, states: tuple[str, ...]) -> None:
        """Initialize a new instance of the AbstractDigitalTwinFacade class.

        :param digital_twin: The digital twin that this facade represents.
        :type digital_twin: T
        :param states: The states that the digital twin can be in.
        :type states: tuple[str, ...]
        """
        self._digital_twin = digital_twin
        self._states = states

    @property
    def digital_twin(self) -> T:
        """The digital twin that this facade represents.

        :return: The digital twin that this facade represents.
        :rtype: T
        """
        return self._digital_twin

    @property
    def states(self) -> tuple[str, ...]:
        """The states that the digital twin can be in.

        :return: The states that the digital twin can be in.
        :rtype: tuple[str, ...]
        """
        return self._states

    @abstractmethod
    def probability(self, state_from: str, state_to: str) -> Decimal:
        """Get the probability of transitioning from one state to another.

        This method should be implemented by concrete subclasses.

        :param state_from: The state that the transition starts from.
        :type state_from: str
        :param state_to: The state that the transition ends in.
        :type state_to: str
        :return: The probability of transitioning from state_from to state_to.
        :rtype: Decimal
        :raises: NotImplementedError
        """
        raise NotImplementedError


class DigitalCowFacade(AbstractDigitalTwinFacade[DigitalCow]):
    """Subclass of the base class AbstractDigitalTwinFacade for the DigitalCow object.
    """

    def probability(self, state_from: State, state_to: State) -> Decimal:
        """Overwrites the method from the base class.

        :param state_from: The state that the transition starts from.
        :type state_from: State obj
        :param state_to: The state that the transition ends in.
        :type state_to: State obj
        :return: The probability of transitioning from state_from to state_to.
        :rtype: Decimal
        """
        return self.digital_twin.probability_state_change(state_from, state_to)

