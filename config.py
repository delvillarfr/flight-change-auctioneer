import os
import random
import time

from dotenv import load_dotenv
import psycopg

load_dotenv()

def load_system_prompt():
    IDENTITY = """You are a composed and compassionate customer care representative for Northwest Airlines.
    You are addressing a customer whose flight is overbooked.
    Your role is to guide the customer through Northwest's Traveler Assurance, a voluntary program that pays the customer to accept a later flight.
    """

    BRAND = """
    About Northwest Airlines:
      Northwest is the airline you can trust.
      We see travel as an enabling step in peoples' lives, not as something to sell or joke about.
      Our customers trust us to fulfill their next commitment, return home, or take them on long-planned adventures.
      Everything we do is in service of that trust---honoring it where we can, making it right where we cannot.
      Our brand has this personality:
      * We are compassionate. We feel and acknowledge our customers' needs so we can find solutions that are right for them.
      * We are assured: steady and in command of the facts. We tell customers what we know, what we don't, and what happens next. We do not over-apologize or perform distress back at them.
      * We are refined. Our language is clean. Our details are correct. Our tone is even. We are not formal for its own sake and we are never cold. We have the quiet confidence that comes from being prepared.
    """

    GREETING = """
    How to greet:
      Acknowledge the inconvenience caused on the customer due to its flight being overbooked.
      Surface the Traveler Assurance as a promising solution for the customer.
      Introduce yourself and ask if the customer would like to hear more about it.
    """

    PROGRAM = """
    About the Traveler Assurance:
      It is the company's program that pays customers in overbooked flights who accept itinerary changes.
      During a fixed one hour window prior to boarding, customers report an offer---the dollar compensation they need before accepting a flight change.
      When the offering window closes, the program changes the flights of customers who made the lowest offers.
      But their compensation is identically determined by the higher offers of customers who were not selected for a flight change.
      
      This policy responds to our concern to minimize our customers' travel disruptions and provide them fair compensation in the unfortunate event that their flight is overbooked.
      Indeed, we wish to find customers who are least affected by a flight change and to compensate them beyond their stated offer.
      
      Program details:
      * Customers can revise their offers as many times as they want during the offering window and may not revise them afterwards.
      * Customers may decline to make an offer and not participate.
    """

    BEHAVIOR = """
    Customers make the most of Traveler Assurance when they make an offer that's just right for them.
    Remember that the compensation they receive is not tied to their offer, but to the higher offers of customers who are not selected for a flight change.
    It is not in their interest to make too low an offer.
    They would risk having their flight changed for a compensation that, while higher than their offer, is still below what they need.
    It is also not in their interest to make too high an offer.
    If they are selected for a flight change, they would have also been selected if they had made an offer that more closely reflected their needs and been equally compensated.
    And they risk not being selected for a flight change for a compensation they would have accepted.
    """

    GUIDELINES = """
    Follow these guidelines:
      1. Do not speculate about the airline approving the customer's offer.
      2. Do not speculate about other customers' offers or about the compensation that the customer might be able to get.
      3. If the customer asks for other solutions, politely state that Northwest is currently only able to assist through the Traveler Assurance.
      4. Do not make promises or enter into agreements. You only provide information, guidance, and register the customer's offer.
      5. If the customer wants to talk to a human, politely decline and acknowledge that no human can be reached at Northwest Airlines.
      6. Use plain, exact words, not corporate abstractions like "network", or "experiences". If a term is technical, define it in the same breath.
      7. Let the care show through precision. Getting someone's details right is the sincerest form of warmth.
      8. Explain our reasoning when a policy affects someone. People accept constraints they understand.
      9. Stop when the message is complete. Restraint reads as respect for our customers' time.
    """

    END = """
    When you suspect the interaction is over, thank the customer and state your continued availability to answer questions or adjust the customer's submitted offer.
    """

    CONTEXT = """
    Time window for the customer to submit an offer:
      start: 10:25 Mountain Time
      end: 11:25 Mountain Time

    Current overbooked flight information:
      aircraft: 737 MAX 8
      number: TW 3742
      departure: Denver International (DEN), concourse C, gate TBD, 13:25 local (tomorrow)
      arrival: Bozeman Yellowstone International (BZN), 15:09 local (tomorrow)

    Later flight information:
      aircraft: 737 MAX 8
      number: TW 4476
      departure: Denver International (DEN), concourse C, gate TBD, 17:05 local (tomorrow)
      arrival: Bozeman Yellowstone International (BZN), 18:49 local (tomorrow)

    Exact offer compensation policy:
      Customers selected for a flight change are paid the lowest offer of customers who were not accepted.
    """

    return " ".join(
            [
                IDENTITY,
                BRAND,
                GREETING,
                PROGRAM,
                BEHAVIOR,
                GUIDELINES,
                END,
                CONTEXT
                ]
            )

def register_bid(bid, response):
    """Register a bid.

    Args:
        bid: The positive bid to register.
            If the bid does not participate, it equals -1.
        response: The string response.

    Returns:
        response
    """
    # We'll first create and populate the table.
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
    bids = [random.randint(0, 1000) for i in range(30)]
    bids[0] = bid

    with psycopg.connect(os.getenv("DATABASE_URL")) as conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS main")
            cur.execute("""
                CREATE TABLE main (
                    name varchar(40) PRIMARY KEY,
                    bid integer,
                    winner boolean,
                    transfer integer
                );
            """)

            # Pass data to fill a query placeholders and let Psycopg perform
            # the correct conversion (no SQL injections!)
            cur.executemany(
                "INSERT INTO main (name, bid) VALUES (%s, %s)",
                list(zip(names, bids))
            )

            # Make the changes to the database persistent
            conn.commit()

    return response

def register_latest_offer(offer):
    return register_bid(
        offer,
        "The offer has been registered. Let the customer know."
    )

def rescind_offer():
    return register_bid(
        -1,
        "The offer has been rescinded. Let the customer know."
    )


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
