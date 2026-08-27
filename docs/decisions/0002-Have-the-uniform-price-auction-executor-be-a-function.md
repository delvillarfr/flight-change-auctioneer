# Have the uniform price auction executor be a function

If I created instead a UniformPriceAuction class, its interface should not accept the n_objects parameter, the number of objects for sale.
The amount of flight changes needed to accomodate an overbooked flight can change in a moment's notice.
So I predict that users will want to run the auction with many objects for sale.
Doing so and having to create a new object instance feels cumbersome.

I wanted to create a class to group the allocations and transfers functionalities given they both use the profile of bids.
But when I thought of their implementation, I realized they both need to compute properties of the empirical distribution of bids.
So even as methods within a class they repeat themselves.

I decided instead to have a single function that executes the auction and returns both the winners and the transfers as a pre-defined typed dictionary.
This allows for one-shot calls to run the auction under evolving flight-change needs and bids.
