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
        bids: the array of bids, in cents.
        seed: the seed for the random number generator.

    Returns:
        A Result object with a boolean array that indicates which bids won and
        an array specifying each bid's transfer in cents.
        Both arrays are of the same shape as bids.
    """
    # We'll use the number and shape of bids throughout.
    n_bids = bids.size
    shape_bids = bids.shape

    # If the objects are not scarce, everyone wins and pays nothing
    if n_bids <= n_objects:
        winners = np.full(shape_bids, True),
        transfers = np.full(shape_bids, 0)
    else:
        # Introduce a Uniform(0, 1) noise to bids.
        # This preserves the ordering of unequal bids,
        # and orders equal bids randomly.
        # Every order occurs with equal probability.
        rng = np.random.default_rng(seed)
        noisy_bids = bids + rng.uniform(size = shape_bids)

        # Winners are the n_objects highest noisy bids.
        # np.argpartition suffices. np.argsort is easier to read.
        # np.argsort flattens the array of noisy bids.
        id_winners = np.argsort(
                noisy_bids,
                axis = None,
                descending = True
                )[: n_objects]
        winners = np.isin(np.arange(n_bids), id_winners).reshape(shape_bids)

        # Get the highest losing bid.
        price = np.max(bids, where = ~winners)

        # Winners pay the highest losing bid; losers pay nothing.
        transfers = winners.astype(np.int64) * price

    return Result(winners = winners, transfers = transfers)
