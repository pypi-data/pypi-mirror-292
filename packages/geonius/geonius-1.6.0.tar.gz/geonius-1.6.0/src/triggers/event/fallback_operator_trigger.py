# -*- coding: utf-8 -*-

from typing import Iterable
from web3.types import EventData

from src.classes import Trigger, Database
from src.exceptions import DatabaseError
from src.database.pools import save_fallback_operator
from src.helpers.event import event_handler
from src.helpers.portal import get_fallback_operator
from src.helpers.validator import check_and_propose
from src.globals import get_logger, get_config


class FallbackOperatorTrigger(Trigger):
    """Triggered when a pool changes it's fallback operator.
    Updates the database with the latest info.

    Attributes:
        name (str): name of the trigger to be used when logging etc. (value: FALLBACK_OPERATOR)
    """

    name: str = "FALLBACK_OPERATOR"

    def __init__(self) -> None:
        """Initializes a FallbackOperatorTrigger object.
        The trigger will process the changes of the daemon after a loop.
        It is a callable object.
        It is used to process the changes of the daemon.
        It can only have 1 action.
        """

        Trigger.__init__(self, name=self.name, action=self.update_fallback_operator)
        get_logger().debug(f"{self.name} is initated.")

    def __filter_events(self, event: EventData) -> bool:
        """Filters the events to check if the event is for the script's OPERATOR_ID.

        Args:
            event (EventData): Event to be checked

        Returns:
            bool: True if the event is for the script's OPERATOR_ID, False otherwise
        """

        return event.args.operatorId == get_config().operator_id

    def __parse_events(self, events: Iterable[EventData]) -> list[tuple]:
        """Parses the events to saveable format.
        Returns a list of tuples. Each tuple represents a saveable event.

        Args:
            events (Iterable[EventData]): list of FallbackOperator emits

        Returns:
            list[tuple]: list of saveable events
        """

        saveable_events: list[tuple] = []
        for event in events:
            saveable_events.append(
                (
                    str(event.args.poolId),
                    event.args.threshold,
                    event.blockNumber,
                    event.transactionIndex,
                    event.logIndex,
                )
            )

        return saveable_events

    def __save_events(self, events: list[tuple]) -> None:
        """Saves the events to the database.

        Args:
            events (list[tuple]): list of FallbackOperator emits
        """
        try:
            with Database() as db:
                db.executemany(
                    "INSERT INTO FallbackOperator VALUES (?,?,?,?,?)",
                    events,
                )
            get_logger().debug(f"Inserted {len(events)} events into FallbackOperator table")
        except Exception as e:
            raise DatabaseError(f"Error inserting events to table FallbackOperator") from e

    # pylint: disable-next=unused-argument
    def update_fallback_operator(self, events: Iterable[EventData], *args, **kwargs) -> None:
        """Checks if the fallback operator is set as script's OPERATOR_ID
        for encountered pool ids within provided "FallbackOperator" emits.

        Args:
            events (Iterable[EventData]): list of events
        """

        filtered_events: Iterable[EventData] = event_handler(
            events, self.__parse_events, self.__save_events, self.__filter_events
        )

        # gather pool ids from filtered events
        pool_ids: list[int] = [x.args.poolId for x in filtered_events]

        for pool_id in pool_ids:
            fallback: int = get_fallback_operator(pool_id)

            # check if the fallback id is OPERATOR_ID
            # if so, column value is set to 1, sqlite3 don't do booleans
            save_fallback_operator(pool_id, fallback == get_config().operator_id)

            # if able to propose any new validators do so
            check_and_propose(pool_id)
