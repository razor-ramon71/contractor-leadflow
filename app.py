import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Contractor LeadFlow",
    page_icon="⚡",
    layout="wide"
)

# -------------------------
# SESSION STORAGE
# -------------------------

if "leads" not in st.session_state:
    st.session_state.leads = []

# -------------------------
# LEAD SCORING
# -------------------------

def score_lead(urgency, budget):
    score = 0

    if urgency == "Emergency / ASAP":
        score += 50
    elif urgency == "Today":
        score += 40
    elif urgency == "This Week":
        score += 25
    else:
        score += 10

    if budget == "$5,000+":
        score += 40
    elif budget == "$2,000 - $5,000":
        score += 30
    elif budget == "$500 - $2,000":
        score += 20
    else:
        score += 10

    if score >= 70:
        return "🔥 HOT", score
    elif score >= 40:
        return "🟡 WARM", score
    else:
        return "🔵 COLD", score


# -------------------------
# SIDEBAR
# -------------------------

st.sidebar.title("⚡ LeadFlow")

mode = st.sidebar.radio(
    "Choose View",
    ["👤 Request Service", "🛠️ Contractor Dashboard"]
)

st.sidebar.divider()

st.sidebar.caption(
    "Turn calls, QR scans and online traffic into qualified contractor leads."
)


# =====================================================
# CUSTOMER REQUEST PAGE
# =====================================================

if mode == "👤 Request Service":

    st.title("⚡ Request Service")

    st.subheader("Tell us what you need.")

    st.write(
        "Submit your request and a contractor will review the details "
        "and contact you as soon as possible."
    )

    with st.form("lead_form"):

        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Your Name *")
            phone = st.text_input("Phone Number *")
            email = st.text_input("Email")
            zipcode = st.text_input("ZIP Code *")

        with col2:

            service = st.selectbox(
                "What do you need help with?",
                [
                    "Electrical Panel / Breaker",
                    "No Power / Electrical Problem",
                    "Outlet / Switch",
                    "Lighting",
                    "Remodel / New Construction",
                    "EV Charger",
                    "Generator",
                    "Inspection / Troubleshooting",
                    "Other"
                ]
            )

            urgency = st.selectbox(
                "When do you need service?",
                [
                    "Emergency / ASAP",
                    "Today",
                    "This Week",
                    "Just Getting a Quote"
                ]
            )

            budget = st.selectbox(
                "Approximate Project Budget",
                [
                    "Under $500",
                    "$500 - $2,000",
                    "$2,000 - $5,000",
                    "$5,000+"
                ]
            )

            source = st.selectbox(
                "How did you find us?",
                [
                    "QR Code",
                    "Google",
                    "Facebook",
                    "Website",
                    "Referral",
                    "Business Card",
                    "Truck / Vehicle",
                    "Other"
                ]
            )

        description = st.text_area(
            "Describe the problem or project",
            placeholder=(
                "Example: Breaker keeps tripping and half of the house "
                "loses power..."
            )
        )

        submitted = st.form_submit_button(
            "🚀 Request Service",
            use_container_width=True
        )

        if submitted:

            if not name or not phone or not zipcode:

                st.error(
                    "Please enter your name, phone number and ZIP code."
                )

            else:

                rating, score = score_lead(urgency, budget)

                lead = {
                    "Date": datetime.now().strftime("%m/%d/%Y %I:%M %p"),
                    "Customer": name,
                    "Phone": phone,
                    "Email": email,
                    "ZIP": zipcode,
                    "Service": service,
                    "Urgency": urgency,
                    "Budget": budget,
                    "Source": source,
                    "Rating": rating,
                    "Score": score,
                    "Status": "New",
                    "Description": description
                }

                st.session_state.leads.append(lead)

                st.success("✅ Your service request has been received!")

                st.info(
                    "A contractor will review your request and contact "
                    "you as soon as possible."
                )

                if urgency == "Emergency / ASAP":
                    st.warning(
                        "⚠️ If there is fire, smoke, sparking, or an "
                        "immediate danger, contact emergency services "
                        "and move to a safe location."
                    )


# =====================================================
# CONTRACTOR DASHBOARD
# =====================================================

else:

    st.title("🛠️ Contractor Dashboard")

    leads = st.session_state.leads

    total_leads = len(leads)

    hot_leads = sum(
        1 for lead in leads
        if lead["Rating"] == "🔥 HOT"
    )

    new_leads = sum(
        1 for lead in leads
        if lead["Status"] == "New"
    )

    potential_value = 0

    for lead in leads:

        if lead["Budget"] == "$5,000+":
            potential_value += 5000

        elif lead["Budget"] == "$2,000 - $5,000":
            potential_value += 3500

        elif lead["Budget"] == "$500 - $2,000":
            potential_value += 1250

        else:
            potential_value += 250

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("📥 Total Leads", total_leads)
    col2.metric("🔥 Hot Leads", hot_leads)
    col3.metric("🆕 New Leads", new_leads)
    col4.metric(
        "💰 Potential Value",
        f"${potential_value:,.0f}"
    )

    st.divider()

    st.subheader("📋 Lead Pipeline")

    if not leads:

        st.info(
            "No leads yet. Submit a test request from the "
            "Request Service page."
        )

    else:

        df = pd.DataFrame(leads)

        st.dataframe(
            df[
                [
                    "Rating",
                    "Customer",
                    "Phone",
                    "Service",
                    "Urgency",
                    "Budget",
                    "Source",
                    "Status",
                    "Date"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader("🔥 Priority Leads")

        priority = df[df["Rating"] == "🔥 HOT"]

        if priority.empty:
            st.write("No hot leads currently.")

        else:
            st.dataframe(
                priority[
                    [
                        "Customer",
                        "Phone",
                        "Service",
                        "Urgency",
                        "Budget",
                        "Description"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )


# -------------------------
# FOOTER
# -------------------------

st.divider()

st.caption(
    "Contractor LeadFlow • Capture. Qualify. Close."
)
