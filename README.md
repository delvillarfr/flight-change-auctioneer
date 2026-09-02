# Flight-Change Auctioneer

> An airline AI agent that auctions flight-changes to customers on overbooked flights.

The agents chats with customers and collects their bids.
When the auction ends, it finds the winners and calculates their transfers.

The agent implements a uniform price reverse auction.
Customers who bid the lowest amounts win and are paid the lowest bid among those that didn't win.

Customers can only get one flight change, i.e., they have a unit demand.
Here, it is a weakly dominant strategy for customers to bid their true flight change cost---the smallest compensation they need to accept the flight-change.[1]
The assumption is that customers have private values: they know how much the flight change would cost them and others cannot make them reevaluate.

## References

[1] Krishna, V. (2009). *Auction Theory* (2nd ed.). Academic Press. ISBN: 978-0-12-374507-1. Section 12.1.3 (Vickrey Auctions), p. 179.
