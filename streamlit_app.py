# Import python packages
import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

# Title
st.title("Customize Your Smoothie :cup_with_straw:")

st.write(
"""
Choose the fruits you want in your custom Smoothie!
"""
)

# Name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

# Create Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit options table
my_dataframe = (
    session.table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"))
)

# Convert to pandas dataframe
pd_df = my_dataframe.to_pandas()

# Multiselect for ingredients
ingredients_list = st.multiselect(
    "Choose upto 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

if ingredients_list:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:

        ingredients_string += fruit_chosen + " "

        search_on = fruit_chosen.lower()

        st.write("The search value for", fruit_chosen, "is", search_on)

        st.subheader(f"{fruit_chosen} Nutrition Information")

        # API request
        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        # Convert API response to dataframe
        nutrition_df = pd.json_normalize(
            smoothiefroot_response.json()
        )

        st.dataframe(
            data=nutrition_df,
            use_container_width=True
        )

    # Insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    st.write(my_insert_stmt)

    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()

        st.success(
            f"Your Smoothie is ordered, {name_on_order}!",
            icon="✅"
        )
