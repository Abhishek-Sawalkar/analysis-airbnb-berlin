# https://analysisberlin.herokuapp.com/

import streamlit as st
import streamlit.components.v1 as components
from streamlit_folium import folium_static

import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
import folium
from branca.colormap import linear
import geopandas as gpd

import matplotlib.pyplot as plt
import plotly.express as px
import plotly
from plotly.offline import plot, iplot, init_notebook_mode
import plotly.graph_objs as go
# plot_ly() %>%
#   config(displaylogo = FALSE)

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
html = """
  <style>
    .reportview-container {
      flex-direction: row-reverse;
    }

    header > .toolbar {
      flex-direction: row-reverse;
      left: 1rem;
      right: auto;
    }

    .sidebar .sidebar-collapse-control,
    .sidebar.--collapsed .sidebar-collapse-control {
      left: auto;
      right: 0.5rem;
    }

    .sidebar .sidebar-content {
      transition: margin-right .3s, box-shadow .3s;
    }

    .sidebar.--collapsed .sidebar-content {
      margin-left: auto;
      margin-right: -21rem;
    }

    @media (max-width: 991.98px) {
      .sidebar .sidebar-content {
        margin-left: auto;
      }
    }
  </style>
"""

st.markdown(html, unsafe_allow_html=True)
st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

# @st.cache(allow_output_mutation=True)
# def load_data():
geo_df = gpd.read_file('neighbourhoods.geojson')
# listings_df = pd.read_csv('listings.csv', low_memory=False)
# reviews_df = pd.read_csv('reviews.csv',parse_dates = [2])
# return listings_df, reviews_df, geo_df

@st.cache(allow_output_mutation=True)
def price_paid():
    # listings_df, reviews_df, geo_df =  load_data()
    
    
    # geojson from https://github.com/ljwolf/geopython/blob/master/data/berlin-neighbourhoods.geojson


    # clean the price column (change to numeric)
    # listings_df['price'] = pd.to_numeric(listings_df.price.apply(
    #     lambda x: x.replace("$", "").replace(",","")))
    # room_types = pd.merge(listings_df.room_type.value_counts(), listings_df.groupby('room_type').agg({'price': 'mean'})['price'], left_index=True, right_index=True).reset_index()
    # room_types['Price'] = room_types['price'].apply(lambda x: round(x))
    room_types = [('Entire home/apt',12960,86.747068,87),
                    ('Private room',11664,44.307699,44),
                    ('Shared room',310,73.551613,74),
                    ('Hotel room',230,890.513043,891)]
    room_types = pd.DataFrame(room_types, columns=['index', 'room_type', 'price', 'Price'])
    fig = go.Figure(
        data=[
            go.Bar(name='No. of Listings', x=room_types['index'], y=room_types['room_type'], yaxis='y', offsetgroup=1),
            go.Bar(name='Price Paid', x=room_types['index'], y=room_types['Price'], yaxis='y2', offsetgroup=2)
        ],
        layout={
            'yaxis': {'title': 'Number of Listings'},
    #         'xaxis' : {"Room Type"},
            'yaxis2': {'title': 'Price Paid( $ )', 'overlaying': 'y', 'side': 'right'}
        }
    )

    # Change the bar mode
    fig.update_layout(
        xaxis_title = "Room Type"
        )
    fig.update_layout(barmode='group')
    return fig

@st.cache(allow_output_mutation=True)
def load_gdf():
    return gpd.read_file('dataframe.geojson')

@st.cache(allow_output_mutation=True)
def first_folium_map(gdf_price):
    colormap = linear.OrRd_09.scale(
        gdf_price.price_mean.min(),
        gdf_price.price_mean.max())

    style_function = lambda x: {'weight': 0.5,
                              'fillColor': '#8c8c8c',
                              'fillOpacity': 0,
                              'color': 'black'} if pd.isnull(x['properties']['price_mean'])else {'weight': 0.5,
                                                                                                'fillColor': colormap(x['properties']['price_mean']),
                                                                                                'fillOpacity': .90,
                                                                                                'color': 'black'}

    highlight_function = lambda x: {'weight': 0.5,
                              'fillColor': '#8c8c8c',
                              'fillOpacity': 0,
                              'color': 'black'} if pd.isnull(x['properties']['price_mean']) else {'weight': 0.9,
                                                                                                  'fillColor': colormap(x['properties']['price_mean']),
                                                                                                  'fillOpacity': 1,
                                                                                                  'color': 'black'}

    styles= folium.features.GeoJson(
        gdf_price,
        style_function=style_function,
        highlight_function = highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['neighbourhood_group', 'neighbourhood','price_mean'],
            aliases = ['District/Kiez: ', 'Neighbourhood: ','Average Price Paid: ']))

    # make folium map centered in Berlin
    m = folium.Map(location=[52.51, 13.40], zoom_start=10, tiles='cartodbpositron',
               zoom_control=False, 
               scrollWheelZoom=False,
               dragging=False)

    colormap.caption = 'Average Price Paid'
    colormap.add_to(m)

    m.add_child(styles)

    return m


rad = st.sidebar.radio("Navigation", ['Overview of the project', 'Question 1', 'Question 2', 'Question 3'])

# listings_df, reviews_df, geo_df =  load_data()

# def make_listings_info_df(bins, labels, hosts = False):
#     '''
#     Function to make a dataframe with average values of availability and 
#     listing numbers based on the bins chosen
#     Inputs: bins - a pd.IntervalIndex (pandas IntervalIndex) consisting of the cuts you 
#                     want to divide the listing
#                     counts into
#             labels - a List of strings with each corresponding to each provided 
#                         interval in 'bins'
#             hosts - If False (default), just get the percentage of listings that
#                     correspond to the bin, e.g. if bin is 2 listings, then 
#                     get information for all listings that have a host with 2 listings.
#                     If True, get information for hosts, e.g. if bin is 2 listings,
#                     get information for all hosts that have 2 listings.
#     Output: a Pandas dataframe containing the labels and bins with the corresponding 
#             percentage of listings (or hosts if hosts=True) in each bin along
#             with the average availability (/365 days)
#             of all the listings in that bin
#     '''
#     if hosts:
# #         df = listings_df.groupby('host_id').agg({'calculated_host_listings_count':'sum', 'availability_365':'mean'})
#         df = listings_df.groupby('host_id')[['calculated_host_listings_count',
#                                              'availability_365']].mean()
# #         print(df['calculated_host_listings_count'].value_counts())
        
#     else:
#         df = listings_df.copy()
        
# #    print(df.shape)
        
#     # make a new column with the group/cut that the listing belongs to (based on the number of 
#     # listings the host has)
    
#     # calculated_host_listings_count: The number of listings(total number of rooms a host has) the host has in the current scrape, in the city/region geography.
#     df['num_listings_cut'] = pd.cut(df.calculated_host_listings_count, bins)

#     # get percentage of listings that are the only listing vs. one of many listings
#     num_listings_percent = df.num_listings_cut.value_counts(normalize=True)

#     # get the average availability out of the calendar year that each category offers
#     availability_num_listings = pd.DataFrame(df.groupby('num_listings_cut')['availability_365'].mean()).reset_index()

#     # make dataframe that contains the listing percentages by type of host (host listing num) 
#     # using 'num_listings_perc'
#     df = pd.DataFrame(num_listings_percent).reset_index().rename(columns = {'index': 'cut', 
#                                                                             'num_listings_cut': 'perc_listings'})
#     # make sure the categories/cuts are in order
#     df = df.sort_values(by='cut').reset_index(drop=True) 

#     # merge the string version of groups/cuts into dataframe:
#     df = pd.concat([labels, df], axis=1).rename(columns = {0: 'labels'})

#     # include the average availability for each of these cuts into the dataframe 
#     df = df.merge(availability_num_listings, left_on='cut', 
#                            right_on='num_listings_cut').drop(columns = 'num_listings_cut')
    
#     # make a new column for the listing percentages cleaned (rounded to 4 digits and in percentage format)
#     df['perc_listings_clean'] = df.perc_listings.apply(
#         lambda x: 100*round(x,4))
    
#     return df

config = {'displayModeBar': False}



if rad == "Overview of the project":


  st.markdown("<h1 style='text-align: center; color: #486D87;'>Analysis of Airbnb Berlin</h1>", unsafe_allow_html=True)
  st.markdown("---")
  # st.markdown("<ul> <li>lul</li> <li>foot</li> <li>hand</li></ul>", unsafe_allow_html=True)
  st.markdown("<h3 style='color: #A32CC4;'>- What is Airbnb?</h3>", unsafe_allow_html=True)
  st.write('Airbnb is an online marketplace that connects people who want to rent out their homes with people who are looking for accommodations in specific locales.')

  # st.subheader('- How Does Airbnb Make Money?')

  st.markdown("<h3 style='color: #A32CC4;'>- How Does Airbnb Make Money?</h3>", unsafe_allow_html=True)
  st.write("Airbnb's business model is quite profitable. Companies, like Uber, Lyft, and others, has capitalized on the sharing economy, essentially making money renting out property that it"\
      + " doesn't own. For Airbnb, everytime a new reservation is made, Airbnb takes a service fee from the tenant.")

  # Header
  # st.header("Overview of the Whole Project")
  st.markdown("<h2 style='color: #A32CC4;'>Overview of the Whole Project</h2>", unsafe_allow_html=True)

  st.write('In this Project, I tried to explore the Airbnb Berlin Dataset and tried to answer some questions that can provide some insights about the ratings, host and location of a listing.')

  st.write('**NOTE:** Here I am going to use the word "Listing" which means Residential house.')
  
  # st.subheader("- Dataset:")

  st.markdown("<h3 style='color: #A32CC4;'>- Dataset:</h3>", unsafe_allow_html=True)

  st.write('Airbnb has open sourced their [data](http://insideairbnb.com/get-the-data.html) , which is licensed under a Creative Commons Attribution 4.0 International License.'\
      + ' The dataset is also available [here](https://www.kaggle.com/temporaryaccabhi/berlin-airbnb) and the data dictionary can be found [here](https://docs.google.com/spreadsheets/d/1iWCNJcSutYqpULSQHlNyGInUvHg2BoUGoNRIGa6Szc4/edit#gid=982310896). The data was collected between 2009 and March 2020.'\
      + ' It includes details about the host, host listings, listing location, property type, price, review and ratings.')

  # st.subheader('- Objectives:')

  st.markdown("<h3 style='color: #A32CC4;'>- Objectives:</h3>", unsafe_allow_html=True)

  st.write('I attempted to analyse three questions that I believed were essential from a business standpoint. And they are as follows:-')
  st.write('**Question 1**: What proportion of Airbnb hosts in Berlin likely use hosting as a primary source of income (or are businesses)? ')
  st.write('**Question 2**: How does the price of an Airbnb differ throughout neighbourhoods in Berlin, and what neighbourhoods have the best price for value?')
  st.write("**Question 3**: What neighbourhoods and listing's property deatails have the greatest influence on a listing rating?")

  st.write("")
  st.markdown("#### I'll go over each question one at a time. You can choose any question that interests you and go through it using the slidebar present in the LEFT TOP CORNER.")
  st.markdown("#### While navigating through different questions PLEASE DO CLOSE THE SIDEBAR.")
  

elif rad == "Question 1":

    st.markdown("""
    <style>
    .css-1iyw2u1 {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='text-align: center; color: #486D87;'>Q1:What proportion of Airbnb hosts in Berlin likely use hosting as a primary source of income (or are businesses)?</h2>", unsafe_allow_html=True)
    st.markdown("---")

    st.write("")

    st.markdown("<h3 style='color: #A32CC4;'>- First let's see how many different kinds of listings are there and their average prices:</h3>", unsafe_allow_html=True)



    # st.write(fig)
    col1, col2 = st.columns(2)
    fig = price_paid()
    col1.plotly_chart(fig, config=config)

    col2.markdown('''This bar graph depicts the presence of four different categories of listings, together with their 
                   total count and average price. The findings are as follows:: <ul><li>There are 4 different types 
                   of listing types: Apartment, Private room, Shared room and Hotels. The 'Price Paid' is the average 
                   daily price in local currency ranging from \$44 to \$891, **AND** 'Number of Listings' ranging from 
                   230 to 12,960 listings.</li><li>The majority of the listings are for apartments. This is most likely 
                   due to the fact that many people own many homes and rent them out to supplement their income.</li> 
                   <li>Hotel rooms have the highest average price but the number of listings are way too low. This is 
                   because of the business model of the Airbnb. For people, Airbnb is a cheap alternative of hotels or 
                   to find hotel rooms with cheaper prices, so thats why there are not many hotel host/owners that put 
                   their ads on Airbnb. This explains the low amount of Hotel rooms.</li> <li>The graph says that 
                   Private rooms(\$44) have lower avg price than Shared room(\$74) which doesnt make sense. One of 
                   my assumption for this is that the competition for Private rooms must be way too higher than the 
                   Shared rooms. Due to the fierce competition, the hosts of the private rooms were forced to lower 
                   their price to stay in competition.</li></ul>''', unsafe_allow_html= True)

    # PIE chart

    st.markdown("<h3 style='color: #A32CC4;'>- Now let's see the proportion of hosts based on the number of listings they have.</h3>", unsafe_allow_html=True)

    
    # split the total number of listings that the host has into different groups
    # bins = pd.IntervalIndex.from_tuples([(-1, 1), (1, 3),(3,10),(10,100)])

    # # make a list with strings representing each of the cuts -- the interval is (closed, open] 
    # # meaning (2,3] contains only 3
    # labels = pd.Series(['1 Listing Hosts','2-3 Listings Hosts','4-10 Listings Hosts','11+ Listings Hosts'])

    # # create the dataframe with information about listings based on 
    # # how many listings the host has
    # listings_info_df = make_listings_info_df(bins, labels)

    listings_info_df = pd.DataFrame([('1 Listing','(-1, 1]',0.736727,48.878850,73.67),
                        ('2-3 Listings','(1, 3]',0.162454,91.673924,16.25),
                        ('4-10 Listings','(3, 10]',0.063861,206.164281,6.39),
                        ('11+ Listings','(10, 100]',0.036958,236.570968,3.70)])
    # df.columns = {"Host Listings",'cut','Percentage of Listings','availability_365','perc_listings_clean'}
    # # rename some of the columns to make it more readable in the plot
    listings_info_df = listings_info_df.rename(columns={0:"Host Listings",1:'cut',2:'Percentage of Listings',3:'availability_365',4:'perc_listings_clean'})

    fig = px.pie(listings_info_df, names = 'Host Listings', values='Percentage of Listings', 
             title='Breakdown of Host\'s by Total Number of Listings(Area Based)',
            color_discrete_sequence = px.colors.sequential.Emrld,
             hover_data=['Host Listings'], labels={'Host Listings':'Host Listings'})

    col1, col2 = st.columns(2)
    col1.plotly_chart(fig, config=config)

    col2.markdown('''I divided the hosts into 4 categories based on the number of listings: hosts having 1 listing, 
                    2-3 listings, 4-10 listings and 11+ listings. Take a note that a listing can be an Entire apartment, 
                    Private room, Shared room and Hotel room. The findings are as follows::''')

    col2.markdown('''<ul><li>Around 74% of host only have 1 Listings. We can assume that these 1 Listing host don't 
                    have Shared room or Hotel room as shared room is to accomodate more than 1 tenant and the Hotel 
                    owners would generally host multiple listing instead of only one.</li><li> I thought listings 
                    with Private rooms shouldn't be in this 74% but then this would mean the 74% of host comes from 
                    only Entire apartment listings which doesn't make sense. So I looked into it a little more and 
                    discovered that the host normally rents one room from their own house.</li></ul>''', unsafe_allow_html=True)
    col2.markdown('''<ul><li>Around 16% of host have 2-3 Listings. These will include all type of listings except Hotel Rooms 
                    reason being a hotel owner would like to host all of his rooms instead of just hosting 2-3 rooms.
                    </li><li>Around 6% of host have 4-10 Listings. It include rich hosts who have building/bunglows/apartments to 
                    accomodate as many tenants as possible</li><li> Lastly Around 4% of host have 11+ Listings. This will include 
                    almost all the owners of hotels, hosts having listings of type Shared rooms and Private rooms. 
                    </li></ul>''', unsafe_allow_html=True)

    # Availability room_type

    st.markdown("<h3 style='color: #A32CC4;'>- Let's have a look at the annual availability of these Listings based on Room Type AND number of listing per host.</h3>", unsafe_allow_html=True)

    # availability_room_type = pd.DataFrame(listings_df.groupby('room_type')['availability_365'].mean()).reset_index()
    # availability_room_type['availability_365'] = availability_room_type['availability_365'].apply(lambda x: round(x))
    availability_room_type = pd.DataFrame([('Entire home/apt',85),
            ('Hotel room',275),
            ('Private room',55),
            ('Shared room',114)])
    availability_room_type =availability_room_type.rename(columns={0:'room_type',1:'availability_365'})
    fig = px.bar(availability_room_type, x='room_type', y='availability_365',
          hover_data = ['availability_365'], labels = {'labels': 'Type of Listings', 'availability_365': 'Average Availability per Year'})
    fig.update_layout(
        yaxis_title="Average Number of Days Available in Year",
        xaxis_title = "Type of Listings",
        title = "Average Availability of Listings Based on Type of Listing")

    col1, col2 = st.columns(2)
    col1.plotly_chart(fig, config=config)

    # Availability listing
    # st.markdown("<h3 style='color: #A32CC4;'>- Let's have a look at the annual availability of host having different total number of Listings.</h3>", unsafe_allow_html=True)
    # Make the same hosts info dataframe but for different intervals to look at 
    # average availability of listings
    # throughout the year

    # bins = pd.IntervalIndex.from_tuples([(-1, 1), (1, 2), (2,3),(3,4),(4, 100)])

    # labels = pd.Series(['1 Listing','2 Listings','3 Listings','4 Listings','5+ Listings'])

    # # make the host info dataframe
    # hosts_info_df = make_listings_info_df(bins, labels, hosts=True)
    # # change formatted percentage of listings for input into the bar plot
    # hosts_info_df['perc_listings_clean'] = hosts_info_df.perc_listings.apply(
    #     lambda x: "Represents {:.2f}% of Listings".format(x*100))
    # hosts_info_df['availability_365'] = hosts_info_df['availability_365'].apply(lambda x: round(x))
    # print(hosts_info_df)
    # plot results using Plotly express

    hosts_info_df = pd.DataFrame([('1 Listing','(-1, 1]',0.893015,49,'Represents 89.30% of Listings'),
            ('2 Listings','(1, 2]',0.075193,85,'Represents 7.52% of Listings'),
            ('3 Listings', '(2, 3]',0.015511,114,'Represents 1.55% of Listings'),
            ('4 Listings','(3, 4]',0.005684,179,'Represents 0.57% of Listings'),
            ('5+ Listings','(4, 100]',0.010597,225,'Represents 1.06% of Listings')])
    hosts_info_df = hosts_info_df.rename(columns={0: 'labels',1:'cut',2:'perc_listings',3:'availability_365',4:'perc_listings_clean'})


    fig = px.bar(hosts_info_df, x='labels', y='availability_365',
          hover_data = ['perc_listings_clean'], labels = {'labels': 'Num Listings',
                                                        'availability_365': 'Average Availability per Year',
                                                      'perc_listings_clean': 'Percentage'})
    fig.update_layout(
        yaxis_title="Average Number of Days Available in Year",
        xaxis_title = "Host's Number of Listings",
        title = "Host's Average Availability by Number of Listings")

    col1.plotly_chart(fig, config=config)

    col2.markdown('''Firstly explaining what availability means, it means the number of the days in a year the
                     listing is vacant. Basically from these two graph we want to know how successful these types 
                     of listings are based on the availability. A listing may not be available because it has been 
                     booked by some tenant or blocked by the host. So lesser the availability means the listing is 
                     used more. The First graph tells about the availability based on different kinds of listing 
                     present whereas the Second graph tells about the availability based on number of listing per 
                     host have.''', unsafe_allow_html=True)
    col2.markdown('''The following are the findings of the First graph:</br><ul><li>We can see that the Hotel rooms have 
                    the highest average annual availability which make sense as we already stated that Airbnb is a cheap 
                    alternative of hotels, also it is very unlikely that all the rooms will be full all year long.</li><li>
                    After analysing figure 1 and shared and private room availability, I came to the conclusion that people 
                    prefer private rooms to entire apartments to save money, which is why there is a high demand for private 
                    rooms, resulting in high competition between hosts who have private room listings. If all of the private 
                    rooms are booked, people will go for the shared Room listing, and the host of shared room knows that 
                    these people will pay a little more to avoid renting the entire apartment. As a result, Shared rooms 
                    are more expensive than Private rooms.</li></ul>''', unsafe_allow_html=True)
    col2.markdown("")
    col2.markdown("")
    col2.markdown("")
    col2.markdown("")
    col2.markdown('''The following are the findings of the Second graph:</br><ul><li>This graph is very intuitive. We can 
                    easily figure out that if there is a host having 5+ listing would likely have atleast one empty listing, 
                    thus having the highest availability than the rest.</li><li>The least availability are the host of 1 listing 
                    is mostly because their is high demand of Entire Apartment and Private rooms so having a high demand and 
                    high supply makes the 1 listing availability lowest.</li><li>We can notice a constant increase, which is most 
                    likely due to the fact that all of the listings (more than one) being booked at the same time is extremely 
                    unusual, and this probability decreases as the number of listings owned by a single owner increases.</li></ul>''', unsafe_allow_html=True)

elif rad == "Question 2":
    st.markdown("<h2 style='text-align: center; color: #486D87;'>Q2:How does the price of an Airbnb differ throughout neighbourhoods in Berlin, and what neighbourhoods have the best price for value?</h2>", unsafe_allow_html=True)
    st.markdown("---")

    st.write("")
    gdf_price = load_gdf()
    # gdf_price = gpd.read_file('dataframe.geojson')
    # print(gdf_price.shape)
    # make map of average prices paid in each neighbourhood of Berlin


    m =  first_folium_map(gdf_price)


    plt.rcParams['figure.figsize'] = [20, 13]
    fig, ax = plt.subplots()

    gdf_price.plot(
        ax=ax, 
        column='neighbourhood_group',
        categorical=True, 
        legend=True, 
        legend_kwds={'title': 'District/Kiez', 'loc': 'upper right', 'fontsize': 15},
        cmap='tab20', 
        edgecolor='black',   
    )

    ax.set(
        title='Berlin District/Kiez'
    );
    
    st.markdown("<h3 style='color: #A32CC4;'>- Price distribution in Berlin's various neighbourhoods</h3>", unsafe_allow_html=True)
    st.write("")

    col1, col2 = st.columns(2)
    
    col2.pyplot(fig=fig, config=config)    
    with col1:
        folium_static(m)

    st.markdown("<h4 style='color: #A32CC4;'>- - Interpretations - -</h4>", unsafe_allow_html=True)
    st.markdown('''I created a map to represent the average price paid per night in different neighbourhood of Berlin using
                 the Folium library. Darker the color means higher the average price paid and vice versa. I have also provided 
                 the a map to denote where various district/kiez are located. The findings are as follows:<ul><li>The first 
                 thing we notice is how, with a few exceptions like Dammvorstadt and müggelheim, the colour lightens as we move 
                 away from Central Berlin. This is because most of the tourist places are in the central Berlin.</li>
                 <li>Some neighbourhoods have no colour since there aren't enough listings(<50 listings) to reliably anticipate 
                 their average price. There are no tourist attractions in these areas. Essentially, these are the locations where 
                 Berlin's population resides.</li><li>The majority of the tourist attractions are located in the Mitte and 
                 Friedrichshain-Kreuzberg District. Most of Germany's historic sites, such as the rebuilt 
                 Reichstag, the Berlin Wall, the German Historical Museum, and the Brandenburg Gate, are located in these 
                 locations. These locations also house some of the world's most renowned art galleries, as well as some of the 
                 most magnificent parks, such as Charlottenburg Palace Gardens, the oldest of which dates back to 1695.
                 </li><li>Due to its ski resorts, palaces, and Devil Lake, the South-Eastern (Treptow-Köpenick) area of Berlin 
                 is bit pricey. Domestic tourism has a greater impact in this area, since people travel to Treptow to get away 
                 from their hectic lives.</li><li>As a result, the districts of Mitte, Friedrichshain-Kreuzberg, and 
                 Treptow-Köpenick account for the majority of Airbnb's revenue. The reason for this is that Berlin is Germany's 
                 historical hub, with world-famous Galleries and Parks, palaces, and ski resorts in the south-eastern section of 
                 the city.</li></ul>''', unsafe_allow_html=True)

    


    # GRAPH

    st.markdown("<h3 style='color: #A32CC4;'>- Price distribution in Berlin's various neighbourhoods based on Location Rating </h3>", unsafe_allow_html=True)
    st.markdown("")

    location_reviews = pd.DataFrame(pd.read_csv('location_reviews.csv'))

    location_reviews['Location Rating'] = location_reviews['Location Rating'].apply(lambda x: round(x, 2))
    location_reviews['price'] = location_reviews['price'].apply(lambda x: round(x))

    fig = px.bar(location_reviews, x = 'neighbourhood_group_cleansed', 
                y = 'price', color = 'Location Rating')
    fig.update_layout(
        title="Average District Price Relative to Location Rating",
        xaxis_title = "District",
        yaxis_title = "Price per Night ($)"
        )

    col1, col2 = st.columns(2)
    col1.plotly_chart(fig, config=config)

    col2.markdown('''The bars show the average nightly price in various neighbourhoods. The hue represents the District's average 
    rating. The greater the yellowish tint, the better the neighborhood's location rating, and vice versa. The graph was sorted 
    by location rating, which indicates that the location rating decreases as we move from left to right.The findings are as 
    follows:<ul><li>The colour bar on the left hand side shows that the location rating runs from 9 to 10, which is a respectable 
    score. What I discovered from the data is that users generally leave reviews in either the high range of 8-10 or the low 
    range of 1-3, implying that people only leave reviews if they are really pleased with the listing or extremely dissatisfied 
    with their listings.</li><li>The graph is divided into two parts, the first of which comprises the first five districts and 
    the second of which contains the remaining districts. The first half has a rating of 9.7 or higher, whereas the second 
    section has a rating of less than 9.7. We can also observe that all of the districts with a high average price paid have 
    a high location rating, indicating that people get good value for their money. The second portion of the graph presents 
    a different tale; the ratings are low and the reviews are negative, indicating that individuals are unhappy with the 
    listings. There are two possible reasons for their lower rating: the tenant expected a better experience than what he or she 
    paid for, or the listing was genuinely awful even for that much money.</li></ul>''', unsafe_allow_html=True) 





elif rad == "Question 3":
    st.markdown('''<h2 style='text-align: center; color: #486D87;'>Q3:What neighbourhoods and listing's property deatails have the greatest 
                    influence on a listing rating?</h2>''', unsafe_allow_html=True)
    st.markdown("---")

    st.write("")

    st.markdown('''<h3 style='color: #486D87;'>Overview:</h3>''', unsafe_allow_html=True)

    st.markdown('''Our goal here is to do data modelling, and in order to do so, we must first turn our data into a usable format. 
                Keep in mind that the feature will only be related to locations. We'll also conduct some data cleaning and 
                feature engineering. So we will be talking about:</br><ul><li>Data Cleaning and Transformation</li><li>Feature 
                Engineering</li><li>Modelling</li><li>Insights</li></ul>''', unsafe_allow_html=True)

    st.write("")

    st.markdown('''<h3 style='color: #486D87;'>Transforming the data:</h3>''', unsafe_allow_html=True)
    st.markdown('''<h4>- Remove the redundant features:</h4></br>We must first remove all unnecessary features before analysing 
                the data. It is said that we must only use location-based and listing-type details and nothing else; these 
                elements include information on a listing's neighbourhood, district, property type and room type. Anything 
                else, such as features holding information about the interior of the listing, the item's pricing, availability, 
                and features containing information on the host, should be excluded from the 
                dataset.</br>''', unsafe_allow_html=True)

    st.markdown('''<h4>- Creating One hot encoded features:</h4></br>Multiple features, such as listing type, listing 
                neighbourhood, and listing district, can be subdivided. Using One hot encoding, the listing type feature can be 
                divided into four categories (private, shared, hotel, and entire apartment rooms), the neighbourhood can be 
                divided into 137 categories (Moabit Ost, Parkviertel, and so on), and the district can be divided into 12 
                categories (Pankow, Mitte, and so on).''', unsafe_allow_html=True)

    st.markdown('''<h4>- Adding new Geographical features based on the listing's location:</h4></br>''', unsafe_allow_html=True)

    st.markdown('''1. <strong>Distance of listings relative to the center of the city:</strong></br>''', unsafe_allow_html=True)
    st.markdown('''It is evident from the sub-header what feature we are implementing. We measured the distance between the city 
                centre and each of our listings. As you may have noticed in Q2, the average price paid and average location 
                rating were both greater in the centre than in any other section of the city, thus incorporating this data into a 
                feature could be beneficial.''', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('''2. <strong>Distances of listings to closest train station/underground:</strong></br>''', unsafe_allow_html=True)
        st.write('')
        st.markdown('''<ul><li>For this I used OSM(Open Street Map) to get all the information about all the train 
                    stating/underground and then took the distance between the listing and the nearest train station to create a 
                    new feature.</li><li>I also separated railway stations into two types: S-Bahn and U-Bahn. S-Bahn is faster 
                    and is not known by the government, but U-Bahn is slower and is owned by the government. Dist station, dist 
                    sbahn, and dist ubahn are the three new features.</li><li>The reason for including this feature is because 
                    tourists want to stay in a location from where they can quickly travel to different neighbourhoods. So I 
                    considered adding a railway station or a bus station, but the data for bus stops appeared to be limited and a 
                    little inaccurate, so I settled with the train station.</li></ul>''', unsafe_allow_html=True)


    with col2:
        st.markdown('<h3 align="center" style="font-size:19px"><b>Station Locations</b></h3>', unsafe_allow_html=True)
        # folium_static(m)
        st.image('./images/station.png')

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('''3. <strong>Distance to closest Biergarten:</strong></br>''', unsafe_allow_html=True)

        st.markdown('''<ul><li>A beer garden (German: Biergarten) is an outdoor area in which beer and food are served, typically 
                    at shared tables.</li><li>There are many Biergarten in Berlin, so I used OSM to extract locations of every 
                    Biergarten in Berlin and then took the distance between the listing and the nearest biergarten.</li><li>
                    Because Germany is known for its beer gardens, which are one of the most popular attractions in Berlin, I 
                    believed that including them in the model would be advantageous.</li></ul>''', unsafe_allow_html=True)

    with col2:
        st.markdown('<h3 align="center" style="font-size:19px"><b>Biergarten Locations</b></h3>', unsafe_allow_html=True)
        # folium_static(m)
        st.image('./images/garten.png')


    st.markdown('''<h3 style='color: #486D87;'>Modelling and Insights:</h3>''', unsafe_allow_html=True)
    st.write("")
    st.markdown('''<h4>- Target Variable:</h4></br>''', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        col1.markdown('''<ul><li>The target variable is heavily unbalanced as you can see from the bar graph. So instead of using a multi-class 
                    classification problem, I merged all the rating from 1-9 in one class and rating with only 10 as another class 
                    making this as a binary classification problem.</li><li>So we can say that we are trying to predict if a listing has a 
                    10 rating or a 1-9 rating instead of trying to predict the rating ranging from 1-10.</li><li>Class 0 means 10 Rating 
                    and Class 1 means rating ranging from 1-9.</li></ul>''', unsafe_allow_html=True)

    with col2:
        col2.image('./images/class.png')

    st.markdown('''<h4>- Applying Machine Learning Models:</h4></br>''', unsafe_allow_html=True)
    st.markdown('''I used Logistic Regression and tuned as much as I can. I used Logistic Regression so I can get the base line 
                score quickly instead of using very complex models which would take a lot of produce results. For hypertunning 
                of parameters I used GridSearchCV, to provide the best hyperparamters required by the model, the model produced 
                a decent result as you can see in the below table.''', unsafe_allow_html=True)

    st.markdown('''
                ```python
                lr_model = LogisticRegression(random_state=0,solver='newton-cg', penalty='l2', class_weight='balanced', 
                              max_iter=700, warm_start=True, multi_class='ovr', C=1)
                ```
                </br>''', unsafe_allow_html=True)

    res = pd.DataFrame([('Precision', '0.777'), ('Recall', '0.720'), ('F1-Score', '0.748'), ('Area Under the Curve', '0.811')], columns=['Metric', 'Score'])
    # st.table(res)

    col1, col2 = st.columns(2)
    col1.table(res)
    col2.image('./images/confusion_matrix.png')

    st.markdown('''<h4>- Insights from the Model:</h4></br>''', unsafe_allow_html=True)

    st.image('./images/loc_feat_imp.png')
    st.write("")
    st.markdown('''<ul><li>First of all, A higher score in feature importance means that the specific feature will have a larger effect on the model 
                that is being used to predict a certain variable.</li><li>As a result, attributes linked to 'property type' are 
                frequently employed in Logistic Regression models to predict the target value. The model makes extensive use of 
                features related to 'neighbourhood,' but not as much as features related to 'property type.'</li><li>Looks like features based on 
                room_type is not that much used by the model which is bit suprising.</li><li>The model also thinks 'distance to 
                S-Bahn station' feature is important, this feature which we got from feature engineering. Which means people do 
                think about the nearest station, more specifically S-bahn.</li><li>The most significant property types for the 
                model, such as Boat, Bungalow, Houseboat, and so on, are very expensive to rent, which can mean that listing with 
                expensive property can be easily predicted by the model.</li></ul>''', unsafe_allow_html=True)







    
    

    



