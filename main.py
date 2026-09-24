"""
Runs the full Planner -> Creator -> Runner -> Reporter pipeline against
one sample user story for https://dreamjourney-ce04d.web.app/.

Usage:
    python main.py
"""

# from graph import build_graph

# JIRA_TICKET = """
# Title: Guest books a travel package via the booking form

# As a Guest visiting the Dream Journey site
# I want to fill out and submit the booking form (name, phone number, place,
# package info, number of people, date & time, address, message)
# So that I can reserve my selected travel package and see a confirmation

# Acceptance criteria:
# - All required fields (name, number, place, address) must be filled before
#   the form can be submitted
# - Submitting a fully completed form displays a "Success" confirmation
# - Clicking "Book Now" / "Book Your Slot" on any package scrolls to the
#   booking section so the guest can complete their reservation
# - Submitting with required fields empty does not show "Success" and keeps
#   the guest on the booking form
# """.strip()

# TARGET_URL = "https://dreamjourney-ce04d.web.app/"


# def main():
#     app = build_graph()
#     result = app.invoke({"jira_ticket": JIRA_TICKET, "target_url": TARGET_URL})
#     print(result["report_text"])


# if __name__ == "__main__":
#     main()

from graph import build_graph

JIRA_TICKET = """
Title: Guest books a travel package via the booking form
As a Guest visiting the Dream Journey site
I want to fill out and submit the booking form (name, phone number, place,
package info, number of people, date & time, address, message)
So that I can reserve my selected travel package and see a confirmation

Acceptance criteria:
- All required fields (name, number, place, address) must be filled before submission
- Submitting a fully completed form displays a "Success" confirmation
- Clicking "Book Now" scrolls to the booking section
- Submitting with required fields empty does not show "Success"
""".strip()

TARGET_URL = "https://dreamjourney-ce04d.web.app/"

def main():
    app = build_graph()
    result = app.invoke({"jira_ticket": JIRA_TICKET, "target_url": TARGET_URL})
    print(result["report_text"])

if __name__ == "__main__":
    main()