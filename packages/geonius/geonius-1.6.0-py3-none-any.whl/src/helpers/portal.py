# -*- coding: utf-8 -*-

from typing import Any
from itertools import repeat
from geodefi.globals import ID_TYPE
from geodefi.utils import to_bytes32, get_key

from src.globals import get_sdk, get_config, get_logger
from src.utils.thread import multithread


# pylint: disable-next=invalid-name
def get_StakeParams() -> list[Any]:
    """Returns the result of portal.StakeParams function.

    Returns:
        list: list of StakeParams
    """
    get_logger().debug("Calling StakeParams() from portal")
    return get_sdk().portal.functions.StakeParams().call()


# pylint: disable-next=invalid-name
def get_allIdsByType(_type: ID_TYPE, index: int) -> int:
    """A helper function to call allIdsByType on Portal. Returns the ID of the given type and index.

    Args:
        type (ID_TYPE): type of the ID to be fetched.
        index (int): index of the ID to be fetched.

    Returns:
        int: ID of the given type and index.
    """

    get_logger().debug("Calling allIdsByType() from portal")
    return get_sdk().portal.functions.allIdsByType(_type, index).call()


# related to pools >


def get_name(pool_id: int) -> str:
    """Returns the name of the pool with given ID.

    Args:
        pool_id (int): ID of the pool to fetch name for.

    Returns:
        str: Name of the pool.
    """

    get_logger().debug("Fetching the name of a pool: {pool_id}")
    return get_sdk().portal.functions.readBytes(pool_id, to_bytes32("NAME")).call().decode("utf-8")


def get_maintainer(_id: int) -> str:
    """Returns the maintainer of the given ID.

    Args:
        id (int): ID of the pool or operator to fetch maintainer for.
    """

    get_logger().debug("Fetching the maintainer of id: {_id}")
    return get_sdk().portal.functions.readAddress(_id, to_bytes32("maintainer")).call()


def get_wallet_balance(_id: int) -> str:
    """Returns the internal wallet a balance for the given ID.

    Args:
        id (int): ID of the pool or operator to fetch maintainer for.
    """

    get_logger().debug("Fetching the wallet balance for id: {_id}")
    return get_sdk().portal.functions.readUint(_id, to_bytes32("wallet")).call()


def get_withdrawal_address(pool_id: int) -> str:
    """Returns the withdrawal address for given pool.

    Args:
        pool_id (int): ID of the pool to fetch withdrawal address for.

    Returns:
        str: Withdrawal address of the pool.
    """

    get_logger().debug("Fetching the withdrawal address of a pool: {pool_id}")
    res = get_sdk().portal.functions.readAddress(pool_id, to_bytes32("withdrawalPackage")).call()

    return res


def get_surplus(pool_id: int) -> int:
    """Returns the Ether amount that can be used to create validators for given pool, as wei.

    Args:
        pool_id (int): ID of the pool to fetch surplus for.

    Returns:
        int: Surplus of the pool in wei.
    """

    get_logger().debug(f"Fetching the surplus of a pool: {get_name(pool_id)}")
    return get_sdk().portal.functions.readUint(pool_id, to_bytes32("surplus")).call()


def get_fallback_operator(pool_id: int) -> int:
    """Returns the fallbackOperator for given pool.
    Fallback Operators can create validators without approval.

    Args:
        pool_id (int): ID of the pool to fetch fallback operator for.

    Returns:
        int: Fallback operator ID of the pool.
    """
    get_logger().debug("Fetching the fallbackOperator of a pool: {pool_id}")
    return get_sdk().portal.functions.readUint(pool_id, to_bytes32("fallbackOperator")).call()


def can_stake(pubkey: str) -> bool:
    """Checks if the validator proposal for the given pubkey is approved by Oracle

    Args:
        pubkey (str): public key of the validator.

    Returns:
        bool: True if can proceed and call stake. False if not yet confirmed; or alienated.
    """
    get_logger().debug(f"Checking if the validator can be staked and finalized: {pubkey}")
    return get_sdk().portal.functions.canStake(pubkey).call()


def get_pools_count() -> int:
    """Returns the number of current pools from Portal

    Returns:
        int: Number of pools.
    """

    get_logger().debug("Fetching the pools count of a pool: {pool_id}")
    return get_sdk().portal.functions.allIdsByTypeLength(ID_TYPE.POOL).call()


def get_all_pool_ids(start_index: int = 0) -> list[int]:
    """Returns the all current pool IDs from async Portal calls.
    It uses multithread to get all pool IDs.

    Args:
        start_index (int, optional): Index to start fetching pool IDs from. Default is 0.

    Returns:
        list[int]: list of pool IDs.
    """
    return multithread(
        get_allIdsByType,
        repeat(ID_TYPE.POOL),
        range(start_index, get_pools_count(), 1),
    )


# validators


def get_owned_pubkeys_count() -> int:
    """Returns the number of all validators that is owned by the operator.

    Returns:
        int: Number of validators owned by the operator.
    """
    get_logger().debug("Fetching the number of pools owned pubkeys from a validator: {pool_id}")
    return (
        get_sdk()
        .portal.functions.readUint(get_config().operator_id, to_bytes32("validators"))
        .call()
    )


def get_owned_pubkey(index: int) -> str:
    """Returns the pubkey of given index for the operator's validator list.

    Args:
        index (int): index to look for pubkey in validators array

    Returns:
        str: Pubkey of the validator.
    """
    pk: str = (
        get_sdk()
        .portal.functions.readBytes(index, get_key(get_config().operator_id, "validators"))
        .call()
    )
    get_logger().debug("Fetching an owned pubkey. index:{index} : pubkey:{pk}")
    return pk


def get_all_owned_pubkeys(start_index: int = 0) -> list[str]:
    """Returns all of the validator pubkeys that is owned by the operator.

    Args:
        start_index (int, optional): Index to start fetching pubkeys from. Default is 0.

    Returns:
        list[str]: list of validator pubkeys.
    """
    return multithread(
        get_owned_pubkey,
        range(start_index, get_owned_pubkeys_count(), 1),
    )


def get_operator_allowance(pool_id: int) -> int:
    """Returns the result of portal.operatorAllowance function.

    Args:
        pool_id (int): ID of the pool to fetch operator allowance for.

    Returns:
        int: Operator allowance for the given pool.
    """
    return get_sdk().portal.functions.operatorAllowance(pool_id, get_config().operator_id).call()
