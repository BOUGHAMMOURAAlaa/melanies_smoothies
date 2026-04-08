# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Titre de l'application
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie")

# Saisie du nom
name_on_order = st.text_input("Name on Smoothie:")
st.write('The name on your Smoothie will be:', name_on_order)

# Établir la connexion à Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Récupérer les données depuis Snowflake
my_dataframe = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convertir le Snowpark Dataframe en Pandas Dataframe pour utiliser la fonction loc
pd_df = my_dataframe.to_pandas()

# Sélection des ingrédients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)

# Si des ingrédients sont sélectionnés
if ingredients_list:
    ingredients_string = ''
    
    # Boucle sur chaque fruit choisi
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        
        # Afficher les informations nutritionnelles de l'API
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    # Préparer la requête d'insertion dans Snowflake
    my_insert_stmt = """insert into SMOOTHIES.PUBLIC.ORDERS(ingredients, name_on_order)
                        values ('""" + ingredients_string + """', '""" + name_on_order + """')"""

    # Bouton pour soumettre la commande
    time_to_insert = st.button('Submit Order')
    
    # Exécuter la requête si le bouton est cliqué
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
