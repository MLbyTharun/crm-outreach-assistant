import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.types import interrupt
from agent.state import FollowUpState
from agent.email_sender import send_email


def make_generate_node(llm):
    """
    Factory — takes the FollowUpGenerator instance from session state
    and returns the generate node function.
    """
    def generate_followups(state: FollowUpState) -> dict:
        generated = []

        for customer in state["customers"]:
            try:
                body = llm.generate(
                    customer={
                        "name":             customer.get("name", ""),
                        "contact":          customer.get("contact", ""),
                        "company":          customer.get("company", ""),
                        "last_interaction": str(customer.get("last_interaction", "")),
                        "next_followup":    str(customer.get("next_followup", "")),
                        "status":           customer.get("status", ""),
                        "interest_level":   customer.get("interest_level", ""),
                        "notes":            customer.get("notes", ""),
                    },
                    tone="professional"
                )
            except Exception as e:
                body = f"Error generating email: {str(e)}"

            generated.append({
                "name":     customer.get("name", ""),
                "email":    customer.get("contact", ""),
                "company":  customer.get("company", ""),
                "subject":  f"Following up — {customer.get('company', '')}",
                "body":     body,
                "approved": True,   # default to approved, human can reject
            })

        return {"generated_emails": generated}

    return generate_followups


def review_emails(state: FollowUpState) -> dict:
    """
    Pauses graph execution for human review.
    Streamlit will resume with edited emails via Command(resume=...).
    """
    reviewed = interrupt({"emails": state["generated_emails"]})
    return {"reviewed_emails": reviewed}


def send_emails(state: FollowUpState) -> dict:
    """
    Sends all approved emails and returns results.
    """
    results = []

    for email in state["reviewed_emails"]:
        if not email.get("approved", False):
            results.append({**email, "status": "skipped", "error": None})
            continue

        result = send_email(
            to=email["email"],
            subject=email["subject"],
            body=email["body"],
        )

        results.append({
            **email,
            "status": result["status"],
            "error":  result["error"],
        })

    return {"sent_results": results}