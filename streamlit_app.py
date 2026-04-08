# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Établir la connexion pour Streamlit Cloud
cnx = st.connection("snowflake")
session = cnx.session()

# Write directly to the app
st.title("Customize Your Smoothie!")
st.write("Choose the fruits you want in your custom Smoothie")

name_on_order = st.text_input("Name on Smoothie")
st.write('The name on your Smoothie will be:', name_on_order)

# Récupérer les données depuis Snowflake
my_dataframe = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS").select(col('FRUIT_NAME'))

ingredients_list = st.multiselect(
    'choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # --- L'appel API est maintenant dans la boucle ! ---
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
    
    st.write(ingredients_string)

    my_insert_stmt = """insert into SMOOTHIES.PUBLIC.ORDERS(ingredients, name_on_order)
                        values ('""" + ingredients_string + """', '""" + name_on_order + """')"""

    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
