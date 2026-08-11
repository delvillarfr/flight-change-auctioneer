# Flight-Change Auctioneer

> An airline AI agent that auctions flight-changes to customers on overbooked flights.

$n$ customers checked in for a flight with $m < n$ seats.
What should the airline's revenue manager do?

If she just denied boarding to some customers, she would trigger legal fees and damage the airline's reputation.
Better to be nice and convince them to accept a later flight.

But not every customer will accept.
Not for a modest compensation, that is.
Our manager needs to find those who don't mind the delay so much.
She needs to allocate $n-m$ flight-changes to $n$ customers for a small compensation.

This repository offers her a customer-facing agent that runs a uniform price reverse auction.
The agent chats with customers and collects their bids.
When the auction's over, the $n-m$ customers who bid the lowest win.
The manager changes their flight and pays them the lowest bid that didn't get a flight-change.
Right above all their bids.
If the agent collects too few bids ($n-m$ or fewer), the auction is void.

The uniform price format makes customers not want to bid very high.
In fact, it makes them want to bid the smallest compensation they need to accept the flight-change---their flight-change *cost*.
A customer can't win and raise her compensation by bidding more than her cost because her compensation equals a bid that didn't win.
If she bids high, she just risks missing on a well-compensated flight change.
She also doesn't want to bid low---she just risks winning the flight-change for a compensation that's too small for her.

The formal result is that it is a weakly dominant strategy for customers to bid their true cost in the uniform price reverse auction of identical goods when they have private values and unit demands.
Unit demands means that each customer can have at most one flight-change.
Private values means that every customer knows how much the flight change costs her---others know nothing that would make her reevaluate.
