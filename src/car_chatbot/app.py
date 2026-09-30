import logging
from datetime import date, datetime

import streamlit as st

from car_chatbot.data import get_car_with_dealer, search_cars
from car_chatbot.search import (
    recommend_alternatives,
    understand_car_request,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


st.set_page_config(
    page_title="Car Dealer Assistant",
    layout="centered",
)


def reset_search() -> None:
    """Clear the current search and selection."""
    st.session_state.original_request = None
    st.session_state.results = None
    st.session_state.selected_car = None
    st.session_state.search_request = None
    st.session_state.show_dealer = False
    st.session_state.schedule_call = False
    st.session_state.fallback_used = False


def initialize_state() -> None:
    """Initialize Streamlit session state."""
    defaults = {
        "original_request": None,
        "results": None,
        "selected_car": None,
        "search_request": None,
        "show_dealer": False,
        "schedule_call": False,
        "fallback_used": False,
        "is_processing": False,
        "pending_message": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


initialize_state()


st.title("Car Dealer Assistant")

st.write(
    "Tell me which car you're looking for. "
    "I'll check the available inventory and connect you with the dealer."
)


user_message = st.chat_input(
    "For example: I'm looking for a Toyota Corolla hybrid",
    disabled=st.session_state.is_processing,
)

if user_message and not st.session_state.is_processing:
    st.session_state.pending_message = user_message
    st.session_state.is_processing = True
    st.rerun()

if st.session_state.is_processing and st.session_state.pending_message:
    user_message = st.session_state.pending_message

    reset_search()
    st.session_state.original_request = user_message

    with st.chat_message("user"):
        st.write(user_message)

    try:
        with st.spinner("Checking available cars..."):
            search_request, fallback_used = understand_car_request(
                user_message
            )

            st.session_state.search_request = search_request
            st.session_state.fallback_used = fallback_used

            has_request_information = any(
                [
                    search_request.make,
                    search_request.model,
                    search_request.variant,
                    search_request.preferences,
                ]
            )

            if not has_request_information:
                st.warning(
                    "I couldn't understand enough about the car "
                    "you're looking for. Try mentioning a make, "
                    "model, body type, fuel type, or feature."
                )

            else:
                has_vehicle_identity = any(
                    [
                        search_request.make,
                        search_request.model,
                        search_request.variant,
                    ]
                )

                if has_vehicle_identity:
                    results = search_cars(
                        make=search_request.make,
                        model=search_request.model,
                        variant=search_request.variant,
                    )

                    if results.empty:
                        results = recommend_alternatives(
                            user_message,
                            limit=3,
                        )

                        if not results.empty:
                            st.warning(
                                "The exact car you're looking for "
                                "isn't available in the current "
                                "inventory. Here are some available "
                                "alternatives you may want to consider."
                            )

                else:
                    results = recommend_alternatives(
                        user_message,
                        limit=3,
                    )

                    if not results.empty:
                        st.info(
                            "I found these available cars based on "
                            "what you're looking for."
                        )

                st.session_state.results = results

    except FileNotFoundError:
        logger.exception("Inventory data could not be loaded.")

        st.error(
            "The inventory data is currently unavailable. "
            "Please try again later."
        )

    except Exception:
        logger.exception(
            "Unexpected error while searching for cars."
        )
        st.error(
            "Something went wrong while searching the inventory. "
            "Please try again."
        )

    finally:
        st.session_state.pending_message = None
        st.session_state.is_processing = False



if st.session_state.fallback_used:
    st.info(
        "AI assistance is temporarily unavailable. "
        "Basic inventory matching is being used instead."
    )


results = st.session_state.results


if results is not None and not results.empty:
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
        list(options.keys()),
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

    st.write(
        f"Variant: {car['variant']}"
    )

    st.write(
        f"Price: €{car['price']:,.0f}"
    )

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

            st.write(
                f"**Name:** {dealer['name']}"
            )

            st.write(
                f"**City:** {dealer['city']}"
            )

            st.write(
                f"**Phone:** {dealer['phone']}"
            )

            st.write(
                f"**Email:** {dealer['email']}"
            )


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