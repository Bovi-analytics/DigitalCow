# $Id:
# Author: Gabe van den Hoeven
# Copyright:
"""


"""


from DigitalCow import DigitalCow
from DairyState import State
from chain_simulator import AbstractDigitalTwinFacade
from decimal import Decimal


class DigitalCowFacade(AbstractDigitalTwinFacade[DigitalCow]):
    """Subclass of the base class AbstractDigitalTwinFacade for the DigitalCow object.
    """

    def probability(self, state_from: State, state_to: State) -> Decimal:
        """Overwrites the method from the base class.

        :param state_from: The state that the transition starts from.
        :type state_from: DairyState.State
        :param state_to: The state that the transition ends in.
        :type state_to: DairyState.State
        :return: The probability of transitioning from state_from to state_to.
        :rtype: Decimal
        """
        return self.digital_twin.probability_state_change(state_from, state_to)

