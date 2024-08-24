# -*- coding: utf-8 -*-

from geodefi.classes import Validator
from geodefi.globals import VALIDATOR_STATE

from src.classes import Trigger
from src.daemons import TimeDaemon
from src.database.validators import save_portal_state, save_local_state, fetch_pool_id
from src.globals import get_logger, get_sdk


# TODO: (later) Stop and throw error after x attempts: This should be fault tolerant.
class FinalizeExitTrigger(Trigger):
    """Trigger for the FINALIZE_EXIT. This time trigger is used to finalize the exit of a validator.
    It is triggered after the initial delay is passed. Initial delay is set according to exit epoch.
    It stops the daemon after the exit is finalized.

    Attributes:
        name (str): The name of the trigger to be used when logging etc. (value: FINALIZE_EXIT)
        pubkey (str): The public key of the validator to finalize the exit
    """

    name: str = "FINALIZE_EXIT"

    def __init__(self, pubkey: str) -> None:
        """Initializes a FinalizeExitTrigger object.
        The trigger will process the changes of the daemon after a loop.
        It is a callable object. It is used to process the changes of the daemon.
        It can only have 1 action.

        Args:
            pubkey (str): The public key of the validator to finalize the exit
        """

        Trigger.__init__(self, name=self.name, action=self.finalize_exit)
        self.pubkey: str = pubkey
        get_logger().debug(f"{self.name} is initated for pubkey: {pubkey}")

    # pylint: disable-next=unused-argument
    def finalize_exit(self, daemon: TimeDaemon, *args, **kwargs) -> None:
        """Finalizes the exit of the validator. Stops the daemon after the exit is finalized.
        Updates the database by setting the portal and local status to EXITED for the validator.

        Args:
            daemon (TimeDaemon): The daemon that triggers the action
        """

        # Check if the validator is in the exit state on the beacon chain
        val: Validator = get_sdk().portal.validator(self.pubkey)
        if val.beacon_status == "active_exiting":
            # TODO: (later) reminder: these statuses what to do when
            # TODO: (later)  if it is too late from, after the initial delay is passed
            #       check current epoch and compare with the exit epoch
            #       Too late => 1 week send mail to operator and us no raise here
            return

        pool_id: int = int(fetch_pool_id(self.pubkey))
        get_sdk().portal.finalizeExit(pool_id, self.pubkey)

        # set db portal and local status to EXITED for validator
        save_portal_state(self.pubkey, VALIDATOR_STATE.EXITED)
        save_local_state(self.pubkey, VALIDATOR_STATE.EXITED)

        # stop the daemon since the validator is exited now and there is no need to check it anymore
        daemon.stop()
