import logging
from datetime import date, datetime

import streamlit as st

from car_chatbot.data import get_car_with_dealer, search_cars
from car_chatbot.search import understand_car_request


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Car Dealer Assistant",
    page_icon="🚗",
    layout="centered",
)


def reset_search() -> None:
    """Clear the current search and selection."""
    st.session_state.results = None
    st.session_state.selected_car = None
    st.session_state.show_dealer = False
    st.session_state.schedule_call = False


def initialize_state() -> None:
    """Initialize Streamlit session state."""
    defaults = {
        "results": None,
        "selected_car": None,
        "show_dealer": False,
        "schedule_call": False,
        "fallback_used": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


initialize_state()

st.title("🚗 Car Dealer Assistant")
st.write(
    "Tell me which car you're looking for. "
    "I'll check the available inventory and connect you with the dealer."
)

user_message = st.chat_input(
    "For example: I'm looking for a Toyota Corolla hybrid"
)

if user_message:
    reset_search()

    with st.chat_message("user"):
        st.write(user_message)

    try:
        with st.spinner("Checking available cars..."):
            search_request, fallback_used = understand_car_request(
                user_message
            )

            st.session_state.fallback_used = fallback_used

            if not any(
                [
                    search_request.make,
                    search_request.model,
                    search_request.variant,
                ]
            ):
                st.warning(
                    "I couldn't identify a specific car from that request. "
                    "Please include a make or model, for example "
                    "'Toyota Corolla' or 'BMW X3'."
                )
            else:
                results = search_cars(
                    make=search_request.make,
                    model=search_request.model,
                    variant=search_request.variant,
                )

                st.session_state.results = results

    except FileNotFoundError:
        logger.exception("Inventory data could not be loaded.")
        st.error(
            "The inventory data is currently unavailable. "
            "Please try again later."
        )

    except Exception:
        logger.exception("Unexpected error while searching for cars.")
        st.error(
            "Something went wrong while searching the inventory. "
            "Please try again."
        )
    st.session_state.fallback_used = fallback_used

#can be used to show the banner for Gemini fall back

#if st.session_state.fallback_used:
#   st.info(
#        "AI assistance is temporarily unavailable. "
#       "Basic inventory search is being used instead."
#   )


results = st.session_state.results

if results is not None:
    if results.empty:
        st.warning(
            "I couldn't find a matching car in the current inventory. "
            "Try another make, model, or a broader search."
        )

    else:
        st.subheader("Available Cars")

        options = {}

        for index, car in results.iterrows():
            label = (
                f"{car['year']} {car['make']} {car['model']} "
                f"— {car['variant']} — €{car['price']:,.0f}"
            )

            options[label] = index

        selected_label = st.selectbox(
            "Choose a car:",
            options.keys(),
        )

        if st.button(
            "Select this car",
            type="primary",
            use_container_width=True,
        ):
            selected_index = options[selected_label]
            selected_row = results.loc[selected_index]

            st.session_state.selected_car = get_car_with_dealer(
                selected_row
            )

            st.session_state.show_dealer = False
            st.session_state.schedule_call = False


selected = st.session_state.selected_car

if selected:
    car = selected["car"]
    dealer = selected["dealer"]

    st.divider()

    st.subheader("Your Selection")

    st.write(
        f"**{car['year']} {car['make']} {car['model']}**"
    )
    st.write(f"Variant: {car['variant']}")
    st.write(f"Price: €{car['price']:,.0f}")

    if dealer is None:
        st.error(
            "Dealer information is unavailable for this vehicle."
        )

    else:
        st.write(
            f"This vehicle is available through "
            f"**{dealer['name']}** in {dealer['city']}."
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "Dealer Details",
                use_container_width=True,
            ):
                st.session_state.show_dealer = True
                st.session_state.schedule_call = False

        with col2:
            if st.button(
                "Schedule a Call",
                use_container_width=True,
            ):
                st.session_state.schedule_call = True
                st.session_state.show_dealer = False


        if st.session_state.show_dealer:
            st.subheader("Dealer Details")

            st.write(f"**Name:** {dealer['name']}")
            st.write(f"**City:** {dealer['city']}")
            st.write(f"**Phone:** {dealer['phone']}")
            st.write(f"**Email:** {dealer['email']}")


        if st.session_state.schedule_call:
            st.subheader("Schedule a Dealer Call")

            with st.form("schedule_form"):
                call_date = st.date_input(
                    "Preferred date",
                    min_value=date.today(),
                )

                call_time = st.time_input(
                    "Preferred time"
                )

                submitted = st.form_submit_button(
                    "Confirm Call",
                    type="primary",
                    use_container_width=True,
                )

                if submitted:
                    appointment = datetime.combine(
                        call_date,
                        call_time,
                    )

                    st.success(
                        "Call request confirmed!"
                    )

                    st.write(
                        f"**Dealer:** {dealer['name']}"
                    )
                    st.write(
                        f"**Phone:** {dealer['phone']}"
                    )
                    st.write(
                        "**Requested time:** "
                        f"{appointment.strftime('%d %B %Y at %H:%M')}"
                    )

                    st.caption(
                        "This is a demonstration only. "
                        "No external booking has been created."
                    )