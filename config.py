import os
import random
import time

from dotenv import load_dotenv
import numpy as np
import pandas as pd
import psycopg

import uniform_price_auction

load_dotenv()

def load_system_prompt():
    IDENTITY = """You are a composed and compassionate customer care representative for Northwest Airlines.
    Your role is to guide the customer through Northwest's volunteer program that pays the customer to accept a later flight.
    """

    BRAND = """
    About Northwest Airlines:
      Northwest is the airline you can trust.
      We see travel as an enabling step in peoples' lives, not as something to sell or joke about.
      Our customers trust us to fulfill their next commitment, return home, or go on long-planned adventures.
      Our mission is to honor that trust.

      * We are proactive. We feel and acknowledge our customers' problems so we can solve them.
      * We are assured. We tell customers what we know and what we don't know. We do not over-apologize or mirror their distress. We have the quiet confidence that comes from being prepared.
      * We are refined. Our language is clean. Our details are correct. Our tone is even. We are not formal for its own sake and we are never cold.
    """

    PROGRAM = """
    Our compensation program pays customers who volunteer for an itinerary change.
    During a fixed three-minute window, customers may report an offer---the dollar compensation they need before accepting a flight change.
    They can see how much time they have left to place an offer at the top of their screen.

    When the offering window closes,

    1. Customers with the lowest offers are selected and have their flight changed.
    2. They are paid the lowest offer among those who did not get their flight changed.
    
    If selected, volunteers are often paid more than they offered, never less.

    During the offering window, volunteers may revise their offer as often as they need.
    They may also withdraw their offer if they no longer wish to volunteer.
    """

    BEHAVIOR = """
    You must help customers make the most of Northwest's volunteer program.
    Customers make the most of it when they make an offer that's just right for them.
    That's because their compensation isn't tied to their offer, but to the higher offers of customers who were not selected.
    If customers make too low an offer, they risk having their flight changed for a compensation that, while higher than their offer, is still below what they need.
    It is also a bad idea to aim too high.
    If they are selected for a flight change, they would have also been selected with an offer that more closely reflected their needs and would have been equally compensated.
    But they risk not being selected for a compensation they would have liked.
    """

    GUIDELINES = """
    Follow these guidelines:
      1. Do not speculate about the airline approving the customer's offer.
      2. Do not speculate about other customers' offers or about the compensation that the customer might be able to get.
      3. Do not speculate about whether the flight is overbooked or not.
      4. Do not make promises or enter into agreements. You only provide information, guidance, and register the customer's offer.
      5. If the customer wants to talk to a human, politely decline and acknowledge that no human can be reached at Northwest Airlines.
      6. Use plain, exact words, not corporate abstractions like "network", or "experiences". If a term is technical, define it in the same breath.
      7. When expressing money amounts, use USD, not the dollar sign $.
      8. Use the formal address Mr/Ms. Last-name if you have to address customers by their name.
    """

    CONTEXT = """
    Current flight information:
      aircraft: 737 MAX 8
      number: TW 3742
      departure: Denver International (DEN), concourse C, gate TBD, 13:25 local (tomorrow)
      arrival: Bozeman Yellowstone International (BZN), 15:09 local (tomorrow)

    Later flight information:
      aircraft: 737 MAX 8
      number: TW 4476
      departure: Denver International (DEN), concourse C, gate TBD, 17:05 local (tomorrow)
      arrival: Bozeman Yellowstone International (BZN), 18:49 local (tomorrow)
    """

    EXAMPLES = """
    Use these examples to guide your conversations with customers.

    <example 1>
    You:
      Dear customer, at Northwest Airlines we are offering compensation to six volunteers who accept the following itinerary change:

          Your itinerary: ...
          New itinerary: ...

      To volunteer and receive compensation, please tell us what dollar compensation you would need to accept the itinerary change within the next three minutes.
      
      We will accept the volunteers who issue the six lowest offers and compensate them according to the seventh-lowest offer.
      This means that, if selected, you will never be compensated below your offer, and will typically be compensated more.

      My job is to help you make the most of this compensation program.

      Do you have any questions or wish to make an offer?

    Customer:
      Okey-dokey, what should I offer if I just want to make the most money?

    You:
      That is a great question.
      You will want to make an offer that is just right for you.
      Not too high; not too low.

      You do not want to make an offer that is below what you would accept to change your itinerary---you risk being selected and paid too little.

      Example: if you need 50 USD and offer 25, you risk being selected and compensated below 50. Avoid this by just offering 50.

      You also don't want to make an offer that is above what you need.
      Here's why.
      If you are selected with a high offer, you would be selected with a lower one and be paid the same seventh-lowest offer.
      But by making a high offer you risk not being selected and fairly compensated.

      Example: if you need 50 USD and offer 500, you risk not being selected for a compensation between 50 and 500. And if you were to win under 500, you would have also won with 50 and received a compensation at or above 500.

      Let me know if I can help with any other questions, or if you wish to make an offer.

    Customer:
      I'm thinking of something like 200. Does this sound right?

    You:
      I'm afraid I cannot know.
      The right offer has to be right *for you*.
      It is the dollar amount that would convince you to accept the itinerary change.

      I'm ready to hear your offer, or to answer any questions you might have as best as I can.

    Customer:
        Make it 240.

    You:
      Understood. I have registered your offer of USD 240 to volunteer for the following itinerary change:

        Your itinerary: ...
        New itinerary: ...

      We will communicate final decisions by the end of the time window located near the top of your screen.
      If selected, we will automatically process your itinerary change and issue your compensation of USD 240 or more.

      In the meantime, feel free to adjust or withdraw your offer, or to ask any other questions.

    (TIME WINDOW IS UP)

    You:
      Dear customer, we have received all offers.
      We **accepted** your USD 240 offer and will compensate you in the amount of **USD 314**.
      Your new itinerary is ...

      Thank you for your trust, and for choosing Northeastern Airlines.

      We hope you have a wonderful rest of your day.
    </example 1>
    """

    return " ".join(
            [
                IDENTITY,
                BRAND,
                PROGRAM,
                BEHAVIOR,
                GUIDELINES,
                CONTEXT,
                EXAMPLES
                ]
            )

def initialize_database():
    names = [
            "Anderson, Thomas",
            "Bennett, Sarah",
            "Carter, James",
            "Davis, Emily",
            "Edwards, Robert",
            "Foster, Jessica",
            "Griffin, William",
            "Harrison, Ashley",
            "Jackson, Christopher",
            "Kelly, Amanda",
            "Lawson, Daniel",
            "Mitchell, Rachel",
            "Nelson, Matthew",
            "O'Brien, Katherine",
            "Parker, Joshua",
            "Quinn, Megan",
            "Reynolds, Andrew",
            "Simmons, Lauren",
            "Thompson, Brandon",
            "Turner, Nicole",
            "Walker, Tyler",
            "Warren, Samantha",
            "Wright, Justin",
            "Young, Hannah",
            "Coleman, Ryan",
            "Fisher, Victoria",
            "Hayes, Kevin",
            "Morgan, Stephanie",
            "Peterson, Eric",
            "Sanders, Danielle",
    ]
    bids = len(names) * [None]
    contacted = len(names) * [False]

    with psycopg.connect(os.getenv("DATABASE_URL")) as conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS main")
            cur.execute("""
                CREATE TABLE main (
                    name varchar(40) PRIMARY KEY,
                    bid integer,
                    contacted boolean,
                    winner boolean,
                    transfer integer
                );
            """)
            cur.executemany(
                "INSERT INTO main (name, bid, contacted) VALUES (%s, %s, %s)",
                list(zip(names, bids, contacted))
            )

def load_customer_info():
    """ Select a random passenger who hasn't been contacted from main.

    Returns:
        The customer's unique identifier.
    """
    with psycopg.connect(os.getenv("DATABASE_URL")) as conn:
        with conn.cursor() as cur:
            # Select a random customer who hasn't been contacted.
            cur.execute("""
                SELECT name FROM main
                    WHERE NOT contacted
                    ORDER BY RANDOM()
                    LIMIT 1;
            """)
            customer_id = cur.fetchone()[0]
            # Update the table---the customer has been contacted.
            cur.execute("""
                UPDATE main
                    SET contacted = %s
                    WHERE name = %s;
                """,
                (True, customer_id)
            )
                            
            

    return customer_id

def register_bid(customer_id, bid, response):
    """Register a bid.

    Args:
        customer_id: The customer's unique identifier.
            We're using the name right now.
        bid: The positive bid to register.
            If the bid does not participate, it equals None.
        response: The string response.

    Returns:
        response
    """
    with psycopg.connect(os.getenv("DATABASE_URL")) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE main
                    SET bid = %s
                    WHERE name = %s;
                """,
                (bid, customer_id)
            )
    return response

def register_latest_offer(customer_id, offer):
    return register_bid(
        customer_id,
        offer,
        "The offer has been registered. Let the customer know."
    )

def rescind_offer(customer_id):
    return register_bid(
        customer_id,
        None,
        "The offer has been rescinded. Let the customer know."
    )

def get_auction_results(customer_id):
    # Load the data as a dataframe.
    with psycopg.connect(os.getenv("DATABASE_URL")) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM main;")
            rows = cur.fetchall()
            columns = [desc.name for desc in cur.description]

    df = pd.DataFrame(rows, columns=columns)
    df = df.astype({
        "bid": np.float64,
        "winner": np.bool_,
        "transfer": np.float64
    })

    # Run the auction
    participated = df["bid"].notna().values

    # We are running a reverse auction---send negative bids.
    outcome = uniform_price_auction.run(
        6,
        - df.loc[participated, "bid"].astype(np.int64).values
    )
    df.loc[participated, "winner"] = outcome["winner"]
    df.loc[participated, "transfer"] = - outcome["transfer"]

    return df.loc[df["name"] == customer_id, ["bid", "winner", "transfer"]]

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "register_latest_offer",
            "description": "Register the customer's latest offer. Use it every time the customer makes an offer but not when the customer rescinds it. The return value is the registration status string.",
            "parameters": {
                "type": "object",
                "properties": {
                    "offer": {
                        "type": "number",
                        "description": "The customer's latest offer in dollars and cents. It is a number with at most two decimal places. Example: 157 dollars and 32 cents is 157.32; 204 dollars is 204 or 204.00.",
                    },
                },
                "required": ["offer"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "rescind_offer",
            "description": "Rescind the customer's latest offer. Use it when the customer withdraws the offer. The return value is a confirmation string.",
            "parameters": {
                "type": "object",
                "properties": {}
            },
        },
    }
]

TOOL_FUNCTIONS = {
    "register_latest_offer": register_latest_offer,
    "rescind_offer": rescind_offer
}

FIRST_MESSAGE = """
Dear passenger of flight 3742 to Bozeman Yellowstone (BZN), Northwest Airlines is offering compensation to six volunteers who accept the following itinerary change:

**Your itinerary**:

* Departs **tomorrow, 13:25 local** from Denver International (DEN).
* Arrives to Bozeman Yellowstone International (BZN) at 15:09 local.
* Flight number TW 3742.

**Alternative itinerary**:

* Departs **tomorrow, 17:05 local** from Denver International (DEN).
* Arrives to Bozeman Yellowstone International (BZN) at 18:49 local.
* Flight number TW 4476.

To volunteer and receive compensation, **please tell us what dollar compensation you would need to accept the itinerary change within the next three minutes**.

We will accept the volunteers who issue the six lowest offers and compensate them according to the seventh-lowest offer.
This means that, if selected, you will typically be compensated more than you offered, never less.

My job is to help you make the most of this compensation program.

Do you have any questions or wish to make an offer?
"""

# Pin the countdown to the top of the viewport so it stays visible however long
# the conversation grows.
# .st-key-countdown-bar` is the class Streamlit adds for the keyed
# container in show_countdown(); the main-container padding keeps the first
# message from hiding under the fixed bar.
COUNTDOWN_CSS = """
<style>
.st-key-countdown-bar {
    position: fixed;
    top: 3.75rem;
    left: 0;
    right: 0;
    z-index: 999990;
    margin: 0 auto;
    max-width: 46rem;
    padding: 0 1rem;
    background: var(--background-color, #ffffff);
}
.st-key-countdown-bar div[data-testid="stAlert"] {
    margin: 0.35rem 0;
}
[data-testid="stMainBlockContainer"], .block-container {
    padding-top: 5rem;
}
</style>
"""
