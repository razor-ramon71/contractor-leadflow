import streamlit as st
import pandas as pd
import boto3
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
from botocore.exceptions import ClientError

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
# DARK / ORANGE THEME
# =========================================================

st.markdown("""
textarea {
    color: #ffffff !important;
    background-color: #111f2c !important;
    caret-color: #ff7a00 !important;
    }
textarea::placeholder {
    color:#7f91a3 !important;
    opacity: 1 !important;
    }
<style>

.stApp {
    background:
        radial-gradient(circle at 85% 10%, rgba(255,115,0,.08), transparent 25%),
        linear-gradient(135deg, #07111c 0%, #0a1521 50%, #07101a 100%);
    color: #f5f7fa;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #08121d 0%, #0b1723 100%);
    border-right: 1px solid #1d2b38;
}

section[data-testid="stSidebar"] * {
    color: #e8edf2;
}

h1, h2, h3 {
    color: #ffffff !important;
    font-weight: 800 !important;
}

.orange {
    color: #ff7a00;
}

.brand {
    font-size: 30px;
    font-weight: 900;
    letter-spacing: -1px;
}

.tagline {
    color: #8899aa;
    letter-spacing: 4px;
    font-size: 11px;
    margin-top: -4px;
    margin-bottom: 25px;
}

.hero {
    padding: 32px;
    border-radius: 20px;
    border: 1px solid #203040;
    background: linear-gradient(
        145deg,
        rgba(17,32,47,.96),
        rgba(9,20,31,.96)
    );
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

div[data-testid="stForm"] {
    background: rgba(13,27,40,.88);
    border: 1px solid #213344;
    border-radius: 18px;
    padding: 25px;
}

.stButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(90deg, #ff6a00, #ff9418);
    color: #07111c;
    border: none;
    border-radius: 10px;
    font-weight: 900;
    min-height: 48px;
}

.lead-card {
    padding: 24px;
    border-radius: 18px;
    border: 1px solid #243748;
    background: linear-gradient(145deg, #101e2b, #0a1621);
    margin-top: 12px;
    margin-bottom: 18px;
}

.detail-label {
    color: #7f91a3;
    font-size: 12px;
    letter-spacing: 1px;
    font-weight: 700;
}

.detail-value {
    color: #ffffff;
    font-size: 17px;
    font-weight: 700;
    margin-bottom: 12px;
}

hr {
    border-color: #203040 !important;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# AWS DYNAMODB CONNECTION
# =========================================================

@st.cache_resource
def get_table():

    dynamodb = boto3.resource(
        "dynamodb",
        region_name=st.secrets["AWS_REGION"],
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"]
    )

    return dynamodb.Table(
        st.secrets["DYNAMODB_TABLE"]
    )

try:
    table = get_table()
    database_ready = True

except Exception:
    table = None
    database_ready = False

# =========================================================
# CENTRAL TIME
# =========================================================

def central_now():

    return datetime.now(
        ZoneInfo("America/Chicago")
    )

def display_time():

    return central_now().strftime(
        "%m/%d/%Y %I:%M %p"
    )

# =========================================================
# LEAD SCORING
# =========================================================

def score_lead(urgency, budget, service):

    score = 0

    if urgency == "Emergency / ASAP":
        score += 45

    elif urgency == "Today":
        score += 35

    elif urgency == "This Week":
        score += 20

    else:
        score += 5

    if budget == "$5,000+":
        score += 35

    elif budget == "$2,000 - $5,000":
        score += 28

    elif budget == "$500 - $2,000":
        score += 20

    else:
        score += 8

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

    score = min(score, 100)

    if score >= 70:
        rating = "🔥 HOT"

    elif score >= 40:
        rating = "🟡 WARM"

    else:
        rating = "🔵 COLD"

    return rating, score

# =========================================================
# DATABASE FUNCTIONS
# =========================================================

def save_lead(lead):

    try:
        table.put_item(Item=lead)
        return True

    except ClientError:
        return False


def load_leads():

    if not database_ready:
        return []

    try:
        response = table.scan()
        items = response.get("Items", [])

        # DynamoDB Scan can be paginated.
        while "LastEvaluatedKey" in response:

            response = table.scan(
                ExclusiveStartKey=response[
                    "LastEvaluatedKey"
                ]
            )

            items.extend(
                response.get("Items", [])
            )

        items.sort(
            key=lambda x: x.get(
                "created_at",
                ""
            ),
            reverse=True
        )

        return items

    except ClientError:
        return []


def update_lead_status(lead_id, status):

    try:

        table.update_item(
            Key={
                "lead_id": lead_id
            },
            UpdateExpression="SET #s = :status",
            ExpressionAttributeNames={
                "#s": "status"
            },
            ExpressionAttributeValues={
                ":status": status
            }
        )

        return True

    except ClientError:
        return False

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown("""
<div class="brand">
⚡ LEAD <span class="orange">RESCUE</span> AI
</div>

<div class="tagline">
CAPTURE • QUALIFY • CLOSE
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
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

if database_ready:

    st.sidebar.success(
        "● AWS DATABASE CONNECTED"
    )

else:

    st.sidebar.error(
        "● DATABASE CONNECTION ERROR"
    )

# =========================================================
# LOAD DATABASE LEADS
# =========================================================

leads = load_leads()

# =========================================================
# DASHBOARD
# =========================================================

if page == "🏠 Dashboard":

    st.markdown("""
    <div class="hero">

        <div class="hero-label">
            LEAD RESCUE AI
        </div>

        <div class="hero-title">
            Never Lose Another<br>
            <span class="orange">Lead.</span>
        </div>

        <div class="hero-text">
            Capture customers while you're working.
            Lead Rescue AI qualifies every opportunity
            and shows you which leads need attention first.
        </div>

    </div>
    """, unsafe_allow_html=True)

    total_leads = len(leads)

    hot_leads = sum(
        1 for x in leads
        if x.get("rating") == "🔥 HOT"
    )

    new_leads = sum(
        1 for x in leads
        if x.get("status") == "New"
    )

    potential_value = 0

    for lead in leads:

        budget = lead.get("budget", "")

        if budget == "$5,000+":
            potential_value += 5000

        elif budget == "$2,000 - $5,000":
            potential_value += 3500

        elif budget == "$500 - $2,000":
            potential_value += 1250

        elif budget:
            potential_value += 250

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "TOTAL LEADS",
        total_leads
    )

    c2.metric(
        "🔥 HOT LEADS",
        hot_leads
    )

    c3.metric(
        "🆕 NEW LEADS",
        new_leads
    )

    c4.metric(
        "💰 POTENTIAL REVENUE",
        f"${potential_value:,.0f}"
    )

    st.divider()

    st.subheader("Recent Leads")

    if not leads:

        st.info(
            "No permanent leads yet. "
            "Submit a new Request Service."
        )

    else:

        dashboard_rows = []

        for lead in leads:

            dashboard_rows.append({
                "Score": lead.get("score", 0),
                "Rating": lead.get("rating", ""),
                "Customer": lead.get("customer", ""),
                "Phone": lead.get("phone", ""),
                "Service": lead.get("service", ""),
                "Urgency": lead.get("urgency", ""),
                "Budget": lead.get("budget", ""),
                "Source": lead.get("source", ""),
                "Status": lead.get("status", ""),
                "Date": lead.get("display_date", "")
            })

        st.dataframe(
            pd.DataFrame(dashboard_rows),
            use_container_width=True,
            hide_index=True
        )

# =========================================================
# REQUEST SERVICE
# =========================================================

elif page == "➕ Request Service":

    st.markdown("""
    <div class="hero">

        <div class="hero-label">
            REQUEST SERVICE
        </div>

        <div class="hero-title">
            Tell Us What You
            <span class="orange">Need.</span>
        </div>

        <div class="hero-text">
            Submit your project or service request.
            No app download required.
        </div>

    </div>
    """, unsafe_allow_html=True)

    with st.form(
        "lead_form",
        clear_on_submit=True
    ):

        c1, c2 = st.columns(2)

        with c1:

            name = st.text_input(
                "Name *"
            )

            phone = st.text_input(
                "Phone *"
            )

            email = st.text_input(
                "Email"
            )

            zipcode = st.text_input(
                "ZIP Code *"
            )

        with c2:

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
                "Example: Electrical panel smells burnt "
                "and the breaker keeps tripping..."
            ),
            height=140
        )

        submitted = st.form_submit_button(
            "⚡ SEND SERVICE REQUEST",
            use_container_width=True
        )

    if submitted:

        if not name or not phone or not zipcode:

            st.error(
                "Please enter your name, "
                "phone number and ZIP code."
            )

        elif not database_ready:

            st.error(
                "Database is not connected."
            )

        else:

            rating, score = score_lead(
                urgency,
                budget,
                service
            )

            now = central_now()

            lead = {
                "lead_id": str(uuid.uuid4()),
                "created_at": now.isoformat(),
                "display_date": display_time(),
                "customer": name,
                "phone": phone,
                "email": email,
                "zipcode": zipcode,
                "service": service,
                "urgency": urgency,
                "budget": budget,
                "source": source,
                "rating": rating,
                "score": score,
                "status": "New",
                "description": description
            }

            if save_lead(lead):

                st.success(
                    "✅ SERVICE REQUEST RECEIVED"
                )

                st.markdown(
                    f"### Lead Priority: "
                    f"{rating} — {score}/100"
                )

                if urgency == "Emergency / ASAP":

                    st.warning(
                        "⚠️ If there is fire, smoke, "
                        "active sparking or immediate danger, "
                        "move to a safe location and contact "
                        "emergency services."
                    )

            else:

                st.error(
                    "The request could not be saved. "
                    "Please try again."
                )

# =========================================================
# LEAD PIPELINE + FULL JOB DETAILS
# =========================================================

elif page == "📋 Lead Pipeline":

    st.title("📋 Lead Pipeline")

    st.write(
        "Select a customer to view the complete job request."
    )

    if not leads:

        st.info(
            "No leads have been saved yet."
        )

    else:

        lead_options = {}

        for lead in leads:

            label = (
                f"{lead.get('rating', '')}  "
                f"{lead.get('customer', 'Unknown')} — "
                f"{lead.get('service', '')}"
            )

            lead_options[label] = lead

        selected_label = st.selectbox(
            "SELECT LEAD",
            list(lead_options.keys())
        )

        selected = lead_options[
            selected_label
        ]

        st.divider()

        st.markdown(
            f"## {selected.get('rating', '')} "
            f"{selected.get('customer', '')}"
        )

        st.markdown(
            f"### Lead Score: "
            f"{selected.get('score', 0)}/100"
        )

        c1, c2, c3 = st.columns(3)

        with c1:

            st.markdown(
                '<div class="detail-label">'
                'PHONE</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f"### {selected.get('phone', '—')}"
            )

            st.markdown(
                '<div class="detail-label">'
                'EMAIL</div>',
                unsafe_allow_html=True
            )

            st.write(
                selected.get("email") or "Not provided"
            )

        with c2:

            st.markdown(
                '<div class="detail-label">'
                'SERVICE</div>',
                unsafe_allow_html=True
            )

            st.write(
                selected.get("service", "—")
            )

            st.markdown(
                '<div class="detail-label">'
                'URGENCY</div>',
                unsafe_allow_html=True
            )

            st.write(
                selected.get("urgency", "—")
            )

        with c3:

            st.markdown(
                '<div class="detail-label">'
                'BUDGET</div>',
                unsafe_allow_html=True
            )

            st.write(
                selected.get("budget", "—")
            )

            st.markdown(
                '<div class="detail-label">'
                'ZIP CODE</div>',
                unsafe_allow_html=True
            )

            st.write(
                selected.get("zipcode", "—")
            )

        st.divider()

        st.subheader(
            "📝 Customer's Job Description"
        )

        description = selected.get(
            "description",
            ""
        )

        if description:

            st.info(description)

        else:

            st.write(
                "Customer did not provide a description."
            )

        st.subheader(
            "📣 Lead Source"
        )

        st.write(
            selected.get("source", "Unknown")
        )

        st.subheader(
            "🕐 Request Received"
        )

        st.write(
            selected.get(
                "display_date",
                ""
            )
        )

        st.divider()

        st.subheader(
            "Lead Status"
        )

        status_options = [
            "New",
            "Contacted",
            "Estimate Scheduled",
            "Won",
            "Lost"
        ]

        current_status = selected.get(
            "status",
            "New"
        )

        try:
            status_index = status_options.index(
                current_status
            )

        except ValueError:
            status_index = 0

        new_status = st.selectbox(
            "UPDATE STATUS",
            status_options,
            index=status_index
        )

        if st.button(
            "SAVE STATUS",
            use_container_width=True
        ):

            if update_lead_status(
                selected["lead_id"],
                new_status
            ):

                st.success(
                    f"Status updated to "
                    f"{new_status}."
                )

                st.rerun()

            else:

                st.error(
                    "Status could not be updated."
                )

        st.divider()

        st.subheader(
            "Contractor Actions"
        )

        phone = selected.get(
            "phone",
            ""
        )

        if phone:

            clean_phone = (
                phone
                .replace("(", "")
                .replace(")", "")
                .replace("-", "")
                .replace(" ", "")
            )

            st.markdown(
                f"📞 **Call:** {phone}"
            )

            st.markdown(
                f"💬 **Text:** {phone}"
            )

        st.caption(
            "One-tap mobile Call/Text buttons "
            "are coming with the mobile upgrade."
        )

# =========================================================
# ANALYTICS
# =========================================================

elif page == "📊 Analytics":

    st.title("📊 Analytics")

    if not leads:

        st.info(
            "Analytics will appear after "
            "permanent leads are captured."
        )

    else:

        rows = []

        for lead in leads:

            rows.append({
                "Source": lead.get(
                    "source",
                    "Unknown"
                ),
                "Rating": lead.get(
                    "rating",
                    "Unknown"
                ),
                "Status": lead.get(
                    "status",
                    "Unknown"
                )
            })

        df = pd.DataFrame(rows)

        c1, c2 = st.columns(2)

        with c1:

            st.subheader(
                "Lead Sources"
            )

            st.bar_chart(
                df["Source"].value_counts()
            )

        with c2:

            st.subheader(
                "Lead Quality"
            )

            st.bar_chart(
                df["Rating"].value_counts()
            )

# =========================================================
# QR
# =========================================================

elif page == "🔳 QR Code":

    st.markdown("""
    <div class="hero">

        <div class="hero-label">
            LEAD CAPTURE
        </div>

        <div class="hero-title">
            Turn Anything Into A
            <span class="orange">
            Lead Source.
            </span>
        </div>

        <div class="hero-text">
            Put your Lead Rescue AI QR code on
            business cards, trucks, websites,
            invoices, yard signs and social media.
        </div>

    </div>
    """, unsafe_allow_html=True)

    st.info(
        "🔳 QR generation is the next upgrade."
    )

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "⚡ Lead Rescue AI • CAPTURE • QUALIFY • CLOSE"
)
