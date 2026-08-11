import numpy as np
import numpy.typing as npt
from typing import TypedDict

class AuctionResult(TypedDict):
    winners: npt.NDArray[np.bool_]
    transfers: npt.NDArray[np.int64]

def run(n_objects: int, bid_vector: npt.NDArray[np.int64]) -> AuctionResult:
    """Execute the uniform price reverse auction.

    There are at most n_objects winning bids.
    The lowest bids win and pay the lowest losing bid.

    If the highest winning bid equals the lowest losing bid, there are bids tied at the margin.
    Those that win are chosen randomly.

    If there are few bids (n_objects or less), every bid wins and pays 0.
    The objects are not scarce.

    Args:
        n_objects: the number of objects for sale, the supply.
        bid_vector: the profile of bids, in USD cents.

    Returns:
        An AuctionResult with the boolean vector of winners and the vector of transfers in cents.
    """
    # Initialize the AuctionResult result.

    # If the objects are not scarce, everyone wins and pays zero.

    # Get the histogram of bids.

    # Get the highest winning bid.

    # If the cumulative bid frequency at this bid equals n_objects,
    # all bidders at and below this bid win and pay the lowest bid higher than it.

    # Otherwise the cumulative bid frequency at this bid exceeds n_objects.
    # It can't be under n_objects if the highest winning bid is correct.

    # Select the highest winning bids at random to match n_objects.
    # Winners pay the highest winning bid.
