import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

# =========================================================
# LEAD RESCUE AI
# =========================================================

st.set_page_config(
    page_title="Lead Rescue AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# THEME
# =========================================================

st.markdown("""
<style>

/* MAIN APP */
.stApp {
    background:
        radial-gradient(circle at 85% 10%, rgba(255,115,0,.08), transparent 25%),
        linear-gradient(135deg, #07111c 0%, #0a1521 50%, #07101a 100%);
    color: #f5f7fa;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #08121d 0%, #0b1723 100%);
    border-right: 1px solid #1d2b38;
}

section[data-testid="stSidebar"] * {
    color: #e8edf2;
}

/* HEADINGS */
h1, h2, h3 {
    color: #ffffff !important;
    font-weight: 800 !important;
}

/* ORANGE ACCENT */
.orange {
    color: #ff7a00;
}

.brand {
    font-size: 32px;
    font-weight: 900;
    letter-spacing: -1px;
    margin-bottom: 0px;
}

.tagline {
    color: #8899aa;
    letter-spacing: 4px;
    font-size: 11px;
    margin-top: -5px;
    margin-bottom: 25px;
}

/* HERO */
.hero {
    padding: 32px;
    border-radius: 20px;
    border: 1px solid #203040;
    background:
        linear-gradient(145deg, rgba(17,32,47,.96), rgba(9,20,31,.96));
    box-shadow: 0 18px 45px rgba(0,0,0,.25);
    margin-bottom: 22px;
}

.hero-label {
    color: #ff7a00;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 2px;
}

.hero-title {
    color: white;
    font-size: 42px;
    line-height: 1.03;
    font-weight: 900;
    margin-top: 10px;
}

.hero-text {
    color: #a9b6c3;
    font-size: 17px;
    margin-top: 14px;
    max-width: 700px;
}

/* METRIC CARDS */
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #101e2b, #0a1621);
    border: 1px solid #203142;
    padding: 18px;
    border-radius: 16px;
    box-shadow: 0 8px 22px rgba(0,0,0,.18);
}

div[data-testid="stMetricLabel"] {
    color: #9eacb9;
}

div[data-testid="stMetricValue"] {
    color: #ffffff;
}

/* FORMS */
div[data-testid="stForm"] {
    background: rgba(13,27,40,.88);
    border: 1px solid #213344;
    border-radius: 18px;
    padding: 25px;
}

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
textarea {
    background-color: #101f2c !important;
    border-color: #2a3d4f !important;
    color: white !important;
}

/* BUTTONS */
.stButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(90deg, #ff6a00, #ff9418);
    color: #07111c;
    border: none;
    border-radius: 10px;
    font-weight: 900;
    min-height: 48px;
    box-shadow: 0 7px 18px rgba(255,122,0,.20);
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    color: #07111c;
    border: none;
    transform: translateY(-1px);
}

/* DATAFRAME */
div[data-testid="stDataFrame"] {
    border: 1px solid #203142;
    border-radius: 14px;
    overflow: hidden;
}

/* DIVIDERS */
hr {
    border-color: #203040 !important;
}

/* CAPTIONS */
.stCaption {
    color: #718294 !important;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# STORAGE - TEMPORARY SESSION STORAGE
# Database comes next.
# =========================================================

if "leads" not in st.session_state:
    st.session_state.leads = []

# =========================================================
# CENTRAL TIME
# =========================================================

def central_time():
    return datetime.now(
        ZoneInfo("America/Chicago")
    ).strftime("%m/%d/%Y %I:%M %p")

# =========================================================
# LEAD SCORING
# =========================================================

def score_lead(urgency, budget, service):
    score = 0

    # Urgency
    if urgency == "Emergency / ASAP":
        score += 45
    elif urgency == "Today":
        score += 35
    elif urgency == "This Week":
        score += 20
    else:
        score += 5

    # Budget
    if budget == "$5,000+":
        score += 35
    elif budget == "$2,000 - $5,000":
        score += 28
    elif budget == "$500 - $2,000":
        score += 20
    else:
        score += 8

    # Higher-value / urgent service types
    major_services = [
        "Electrical Panel / Breaker",
        "No Power / Electrical Problem",
        "Remodel / New Construction",
        "EV Charger",
        "Generator"
    ]

    if service in major_services:
        score += 15
    else:
        score += 8

    # Keep score at 100 max
    score = min(score, 100)

    if score >= 70:
        rating = "🔥 HOT"
    elif score >= 40:
        rating = "🟡 WARM"
    else:
        rating = "🔵 COLD"

    return rating, score

# =========================================================
# SIDEBAR BRAND
# =========================================================

st.sidebar.markdown("""
<div class="brand">
⚡ LEAD <span class="orange">RESCUE</span> AI
</div>

<div class="tagline">
CAPTURE • QUALIFY • CLOSE
</div>
""", unsafe_allow_html=True)

mode = st.sidebar.radio(
    "NAVIGATION",
    [
        "🏠 Dashboard",
        "➕ Request Service",
        "📋 Lead Pipeline",
        "📊 Analytics",
        "🔳 QR Code"
    ]
)

st.sidebar.divider()

st.sidebar.markdown("""
**Never lose another lead.**

Capture customers while you're working and know who needs your attention first.
""")

# =========================================================
# DASHBOARD
# =========================================================

if mode == "🏠 Dashboard":

    st.markdown("""
    <div class="hero">
        <div class="hero-label">LEAD RESCUE AI</div>

        <div class="hero-title">
            Never Lose Another<br>
            <span class="orange">Lead.</span>
        </div>

        <div class="hero-text">
            Customers request service from your link or QR code.
            Lead Rescue AI captures, qualifies and organizes the
            opportunity while you're working.
        </div>
    </div>
    """, unsafe_allow_html=True)

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

    col1.metric("TOTAL LEADS", total_leads)
    col2.metric("🔥 HOT LEADS", hot_leads)
    col3.metric("🆕 NEW LEADS", new_leads)
    col4.metric(
        "💰 POTENTIAL REVENUE",
        f"${potential_value:,.0f}"
    )

    st.divider()

    st.subheader("Recent Leads")

    if not leads:

        st.info(
            "No leads yet. Open Request Service and submit a test lead."
        )

    else:

        df = pd.DataFrame(leads)

        st.dataframe(
            df[
                [
                    "Score",
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

# =========================================================
# CUSTOMER REQUEST SERVICE
# =========================================================

elif mode == "➕ Request Service":

    st.markdown("""
    <div class="hero">
        <div class="hero-label">REQUEST SERVICE</div>

        <div class="hero-title">
            How Can We<br>
            <span class="orange">Help?</span>
        </div>

        <div class="hero-text">
            Tell us what's going on. Your request will be reviewed
            and the contractor can contact you directly.
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("lead_form"):

        st.subheader("Contact Information")

        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input(
                "Name *",
                placeholder="Your name"
            )

            phone = st.text_input(
                "Phone *",
                placeholder="(956) 555-1234"
            )

            email = st.text_input(
                "Email",
                placeholder="name@email.com"
            )

        with col2:

            zipcode = st.text_input(
                "ZIP Code *",
                placeholder="78520"
            )

            service = st.selectbox(
                "Service Needed",
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
                "When Do You Need Service?",
                [
                    "Emergency / ASAP",
                    "Today",
                    "This Week",
                    "Just Getting a Quote"
                ]
            )

        col3, col4 = st.columns(2)

        with col3:

            budget = st.selectbox(
                "Approximate Project Budget",
                [
                    "Under $500",
                    "$500 - $2,000",
                    "$2,000 - $5,000",
                    "$5,000+"
                ]
            )

        with col4:

            source = st.selectbox(
                "How Did You Find Us?",
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
            "Describe the Problem or Project",
            placeholder=(
                "Example: My electrical panel smells burnt "
                "and the breaker keeps tripping..."
            ),
            height=130
        )

        submitted = st.form_submit_button(
            "⚡ SEND SERVICE REQUEST",
            use_container_width=True
        )

        if submitted:

            if not name or not phone or not zipcode:

                st.error(
                    "Please enter your name, phone number and ZIP code."
                )

            else:

                rating, score = score_lead(
                    urgency,
                    budget,
                    service
                )

                lead = {
                    "Date": central_time(),
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

                st.success(
                    "✅ SERVICE REQUEST RECEIVED"
                )

                st.write(
                    "Your request has been sent to the contractor."
                )

                st.markdown(
                    f"### Lead Priority: {rating}"
                )

                if urgency == "Emergency / ASAP":

                    st.warning(
                        "⚠️ If you see fire, smoke, active sparking, "
                        "or another immediate danger, move to a safe "
                        "location and contact emergency services."
                    )

# =========================================================
# LEAD PIPELINE
# =========================================================

elif mode == "📋 Lead Pipeline":

    st.title("📋 Lead Pipeline")

    st.write(
        "Know which leads need your attention first."
    )

    leads = st.session_state.leads

    if not leads:

        st.info("No leads in the pipeline yet.")

    else:

        df = pd.DataFrame(leads)

        st.dataframe(
            df[
                [
                    "Score",
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

        hot = df[df["Rating"] == "🔥 HOT"]

        if hot.empty:

            st.write("No HOT leads currently.")

        else:

            st.dataframe(
                hot[
                    [
                        "Score",
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

# =========================================================
# ANALYTICS
# =========================================================

elif mode == "📊 Analytics":

    st.title("📊 Lead Analytics")

    leads = st.session_state.leads

    if not leads:

        st.info(
            "Analytics will appear as leads are captured."
        )

    else:

        df = pd.DataFrame(leads)

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("Lead Sources")

            source_counts = (
                df["Source"]
                .value_counts()
                .rename_axis("Source")
                .reset_index(name="Leads")
            )

            st.bar_chart(
                source_counts,
                x="Source",
                y="Leads"
            )

        with col2:

            st.subheader("Lead Quality")

            rating_counts = (
                df["Rating"]
                .value_counts()
                .rename_axis("Rating")
                .reset_index(name="Leads")
            )

            st.bar_chart(
                rating_counts,
                x="Rating",
                y="Leads"
            )

# =========================================================
# QR CODE PLACEHOLDER
# =========================================================

elif mode == "🔳 QR Code":

    st.markdown("""
    <div class="hero">
        <div class="hero-label">LEAD CAPTURE</div>

        <div class="hero-title">
            Turn Anything Into A
            <span class="orange">Lead Source.</span>
        </div>

        <div class="hero-text">
            Put your Lead Rescue AI QR code on business cards,
            trucks, websites, invoices, yard signs and social media.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("🔳 Your Customer QR Code")

    st.info(
        "QR generation is coming in our next build. "
        "It will open this contractor's Request Service page."
    )

    st.write("Future tracking options:")

    st.write("• Business Card")
    st.write("• Truck / Vehicle")
    st.write("• Facebook")
    st.write("• Website")
    st.write("• Yard Sign")
    st.write("• Invoice / Receipt")

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "⚡ Lead Rescue AI • CAPTURE • QUALIFY • CLOSE"
)
