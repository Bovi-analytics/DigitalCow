from DigitalCow import DigitalCow
from decimal import Decimal
from chain_simulator import AbstractDigitalTwinFacade


class DigitalCowFacade(AbstractDigitalTwinFacade[DigitalCow]):
    """Subclass of the base class AbstractDigitalTwinFacade for the DigitalCow object.
    """

    def probability(self, state_from: str, state_to: str) -> Decimal:
        """Overwrites the method from the base class.

        :param state_from: The state that the transition starts from.
        :type state_from: str
        :param state_to: The state that the transition ends in.
        :type state_to: str
        :return: The probability of transitioning from state_from to state_to.
        :rtype: Decimal
        """
        return self.digital_twin.probability_state_change(state_from, state_to)

