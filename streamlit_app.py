# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
  """Pick the fruits you want in your custom Smoothie!
  """
)

customer_name = st.text_input("How should we call you?", placeholder="Your name")
st.write("The name on your smoothie will be", customer_name)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

ingredients_list = st.multiselect(
    "Choose up to 5 fruits",
    my_dataframe,
    max_selections=5,
    placeholder="Pick a fruit"
)

if ingredients_list:
    ingredients_string = ''
    # ingredients_string = ', '.join(ingredients_list) + '.'
    for fruit in ingredients_list:
        ingredients_string += fruit + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        st.subheader(fruit + ' Nutrition Information')
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        sf_df =  st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
    
    st.write("You selected:")
    st.text(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                        values ('""" + ingredients_string + """' , '""" + customer_name + """')"""

    order_submitted = st.button('Submit Order')

    if order_submitted:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {customer_name}!', icon="✅")
      

