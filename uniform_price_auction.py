import numpy as np
import numpy.typing as npt
from typing import TypedDict

class Result(TypedDict):
    winners: npt.NDArray[np.bool_]
    # Transfers are integers that represent cents.
    transfers: npt.NDArray[np.int64]

def run(
        n_objects: int,
        bids: npt.NDArray[np.int64],
        seed: int = None
        ) -> Result:
    """Execute the uniform price auction.

    The number of winning bids is at most n_objects.
    The highest bids win and pay the highest losing bid.

    If the highest losing bid equals the lowest winning bid,
    there are bids tied at the margin.
    Winners are chosen uniformly at random, meaning that the probability of
    winning is the same for all bids at the margin.

    If there are few bids (n_objects or less), every bid wins and pays 0.
    The objects are not scarce.

    Args:
        n_objects: the number of objects for sale, the supply.
        bids: the profile of bids, in cents.
        seed: the seed for the random number generator.

    Returns:
        A Result object with the vector that indicates the winning bids and the vector of transfers in cents.
        Both vectors are of the same shape as bids.
    """
    # We'll use the number of bids throughout.
    n_bids = bids.size

    # If the objects are not scarce, everyone wins and pays nothing
    if n_bids <= n_objects:
        winners = np.full(n_bids, True),
        transfers = np.full(n_bids, 0)
    else:
        # Introduce a Uniform(0, 1) noise to bids.
        # This preserves the ordering of unequal bids,
        # and orders equal bids randomly.
        # Every order occurs with equal probability.
        rng = np.random.default_rng(seed)
        noisy_bids = bids + rng.uniform(size = n_bids)

        # Winners are the n_objects highest noisy bids.
        # np.argpartition suffices. np.argsort is easier to read.
        id_winners = np.argpartition(
                noisy_bids,
                n_objects,
                descending = True
                )[: n_objects]
        winners = np.isin(np.arange(n_bids), id_winners)

        # Get the highest losing bid.
        price = np.max(bids, where = ~winners)

        # Winners pay the highest losing bid; losers pay nothing.
        transfers = winners.astype(np.int64) * price

    return Result(winners = winners, transfers = transfers)
