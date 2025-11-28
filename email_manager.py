from email_reader import fetch_unread_emails
from ai_email_agent import summarize_and_categorize_email
from sheets_client import append_email_row

def all_read():
    print("No unread emails to process.")

def run_email_summarization(max_emails=20):
    print("Script has been started ")
    emails = fetch_unread_emails(max_count=max_emails)
    print(f"""Emails decoded: {emails}""")
    print("Length of emails list",len(emails))
    if len(emails)==0:
        #return all_read()
      return "No unread emails to process."

    stats = {"Sales": 0, "Support": 0, "Feedback": 0, "Other": 0}

    print("Now sending the emails to ai agent one by one")
    for e in emails:
        summary, category = summarize_and_categorize_email(e)
        append_email_row(category, e, summary)
        stats[category] += 1


    total = sum(stats.values())
    stat_str = ", ".join(f"{k}: {v}" for k, v in stats.items() if v > 0)
    return f"Processed {total} emails. Breakdown: {stat_str}"

# run_email_summarization()