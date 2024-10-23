import streamlit as st
from project import Api_connect, get_channel_info, connect_to_db, insert_multiple_channels,get_multiple_videos_info, get_video_ids,update_video_data_with_duration_in_seconds
import pandas as pd
import plotly.express as px
import pymysql

# Custom CSS for the sliding header and black background
st.markdown("""
    <style>
    /* Custom background and text color for the entire app */
    .stApp {
        background-color: black;
        color: white; /* White text color */
    }
    
    /* Custom background color for the sidebar */
    .css-1d391kg {
        background-color: red;
    }

    /* Custom header style with sliding animation */
    .sliding-header {
        font-size: 40px;
        font-weight: bold;
        color: #FFFFFF;  /* White color for the header */
        animation: slide 3s forwards;
    }

    @keyframes slide {
        from {
            transform: translateX(-100%);
        }
        to {
            transform: translateX(0%);
        }
    }
    </style>
    """, unsafe_allow_html=True)

# Example usage of the sliding header in your app
st.markdown('<h1 class="sliding-header">Welcome to My Streamlit App</h1>', unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", ["Home", "Channel Search", "Data Hub", "FAQ"])

# YouTube API Connection

youtube = Api_connect()
# Home Page
if selection == "Home":
    st.markdown('<div class="sliding-header">YouTube Data Harvesting and Warehousing</div>', unsafe_allow_html=True)
    st.write("Welcome to the YouTube Data Harvesting and Warehousing app!")

# Channel Search Page
elif selection == "Channel Search":
    st.title("Channel Search")
    
    # Connect to YouTube API
    # youtube = Api_connect()
    
    search_option = st.radio("Search by", ("Channel ID"))
    
    if search_option == "Channel ID":
        search_query = st.text_input("Enter YouTube Channel ID")
        
        if search_query:
            st.write(f"Searching for channel ID: {search_query}")
            
            # Fetch channel information
            channel_info = get_channel_info(youtube, search_query)
            
            if channel_info:
                channel_data = (
                    channel_info['items'][0]['id'],
                    channel_info['items'][0]['snippet']['title'],
                    "General",
                    channel_info['items'][0]['statistics']['viewCount'],
                    channel_info['items'][0]['snippet']['description'],
                    "Active"
                )
                
                # Display channel information
                st.write("Channel Name:", channel_data[1])
                st.write("Subscribers:", channel_info['items'][0]['statistics']['subscriberCount'])
                st.write("Total Views:", channel_data[3])
                st.write("Total Videos:", channel_info['items'][0]['statistics']['videoCount'])
                st.write("Description:", channel_data[4])
                
                # Insert channel data into the database
                conn = connect_to_db()
                insert_multiple_channels(conn, [channel_data])
                st.write("Channel data inserted into the database.")
                conn.commit()

# Data Hub Page
elif selection == "Data Hub":
    st.title("Data Hub")
    
    # Connect to the database and fetch channels
    conn = connect_to_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT "channel_id", "channel_name" FROM "Channel"')
    channels = cursor.fetchall()

    
    if channels:
        # Select channel from database
        selected_channel = st.selectbox("Select a Channel to View Details", channels)
        
        if selected_channel:
            channel_id = selected_channel[0]
            
            # Get video details
            video_ids = get_video_ids(youtube, channel_id)
            video_info = get_multiple_videos_info(youtube, video_ids)

        if video_info:
                st.subheader(f"Videos for Channel ID: {channel_id}")
                video_df = pd.DataFrame(video_info)
                st.dataframe(video_df)
        else:
                st.write("No video data found for this channel.")

    cursor.close()
    conn.close()


# FAQ Page
elif selection == "FAQ":
    if selection == "Query Zone":
        st.subheader(':blue[Queries and Results ]')
        st.write('''(Queries were answered based on :orange[**Channel Data analysis**] )''')

    
    # Selectbox creation
    question_tosql = st.selectbox('Select your Question]',
                                  ('1. What are the names of all the videos and their corresponding channels?',
                                   '2. Which channels have the most number of videos, and how many videos do they have?',
                                   '3. What are the top 10 most viewed videos and their respective channels?',
                                   '4. How many comments were made on each video, and what are their corresponding video names?',
                                   '5. Which videos have the highest number of likes, and what are their corresponding channel names?',
                                   '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?',
                                   '7. What is the total number of views for each channel, and what are their corresponding channel names?',
                                   '8. What are the names of all the channels that have published videos in the year 2022?',
                                   '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?',
                                   '10. Which videos have the highest number of comments, and what are their corresponding channel names?'),
                                  key='collection_question')
    conn = connect_to_db()
    cur = conn.cursor()



    # Create a connection to SQL
    # connect_for_question = pymysql.connect(host='', user='', password='',port=, db='')


    # Q1
    if question_tosql == '1. What are the names of all the videos and their corresponding channels?':
        cur.execute('''SELECT v.video_name, c.channel_name FROM "Video" v JOIN "Playlist" p ON v.playlist_id = p.playlist_id JOIN "Channel" c ON p.channel_id = c.channel_id;''')
        result_1 = cur.fetchall()
        df1 = pd.DataFrame(result_1, columns=['Channel Name', 'Video Name']).reset_index(drop=True)
        df1.index += 1
        st.dataframe(df1)

    # Q2
    elif question_tosql == '2. Which channels have the most number of videos, and how many videos do they have?':

        col1, col2 = st.columns(2)
        with col1:
            cur.execute('''SELECT c.channel_name, COUNT(*) AS video_count FROM "Video" v JOIN "Playlist" p ON v.playlist_id = p.playlist_id JOIN "Channel" c ON p.channel_id = c.channel_id GROUP BY c.channel_name ORDER BY video_count DESC;''')
            result_2 = cur.fetchall()
            df2 = pd.DataFrame(result_2, columns=['Channel Name', 'Video Count']).reset_index(drop=True)
            df2.index += 1
            st.dataframe(df2)

        with col2:
            fig_vc = px.bar(df2, y='Video Count', x='Channel Name', text_auto='.2s', title="Most number of videos", )
            fig_vc.update_traces(textfont_size=16, marker_color='#E6064A')
            fig_vc.update_layout(title_font_color='#1308C2 ', title_font=dict(size=25))
            st.plotly_chart(fig_vc, use_container_width=True)

    # Q3
    elif question_tosql == '3. What are the top 10 most viewed videos and their respective channels?':

        col1, col2 = st.columns(2)
        with col1:
            cur.execute('''SELECT c.channel_name,v.view_count FROM "Video" as v JOIN "Playlist" p ON v.playlist_id = p.playlist_id JOIN "Channel" c ON p.channel_id = c.channel_id order by v.view_count LIMIT 10;''')
            result_3 = cur.fetchall()
            df3 = pd.DataFrame(result_3, columns= ['Video Name', 'View count','Channel Name']).reset_index(drop=True)
            df3.index += 1
            st.dataframe(df3)

        with col2:
            fig_topvc = px.bar(df3, y='View count', x='Video Name', text_auto='.2s', title="Top 10 most viewed videos")
            fig_topvc.update_traces(textfont_size=16, marker_color='#E6064A')
            fig_topvc.update_layout(title_font_color='#1308C2 ', title_font=dict(size=25))
            st.plotly_chart(fig_topvc, use_container_width=True)

    # Q4
    elif question_tosql == '4. How many comments were made on each video, and what are their corresponding video names?':
        cur.execute('''SELECT v.video_name,v.comment_count FROM "Video" v''')
        result_4 = cur.fetchall()
        df4 = pd.DataFrame(result_4, columns=['Video Name', 'Comment count']).reset_index(drop=True)
        df4.index += 1
        st.dataframe(df4)

    # Q5
    elif question_tosql == '5. Which videos have the highest number of likes, and what are their corresponding channel names?':
        cur.execute('''SELECT v.video_name,v.like_count,c.channel_name FROM "Video" v JOIN "Playlist" p ON v.playlist_id = p.playlist_id JOIN "Channel" c ON p.channel_id = c.channel_id ORDER BY v.like_count DESC''')
        result_5 = cur.fetchall()
        df5 = pd.DataFrame(result_5, columns=['Channel Name', 'Video Name', 'Like count']).reset_index(drop=True)
        df5.index += 1
        st.dataframe(df5)

    # Q6
    elif question_tosql == '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?':
        st.write('**Note:- In November 2021, YouTube removed the public dislike count from all of its videos.**')
        cur.execute('''SELECT v.video_name,v.like_count FROM "Video" v''')
        result_6 = cur.fetchall()
        df6 = pd.DataFrame(result_6, columns=['Channel Name', 'Video Name', 'Like count', ]).reset_index(drop=True)
        df6.index += 1
        st.dataframe(df6)

    # Q7
    elif question_tosql == '7. What is the total number of views for each channel, and what are their corresponding channel names?':

        col1, col2 = st.columns(2)
        with col1:
            cur.execute('''SELECT channel_name,channel_view FROM "Channel"ORDER BY channel_view DESC;''')
            result_7 = cur.fetchall()
            df7 = pd.DataFrame(result_7, columns=['Channel Name', 'Total number of views']).reset_index(drop=True)
            df7.index += 1
            st.dataframe(df7)

        with col2:
            fig_topview = px.bar(df7, y='Total number of views', x='Channel Name', text_auto='.2s',
                                 title="Total number of views", )
            fig_topview.update_traces(textfont_size=16, marker_color='#E6064A')
            fig_topview.update_layout(title_font_color='#1308C2 ', title_font=dict(size=25))
            st.plotly_chart(fig_topview, use_container_width=True)

    # Q8
    elif question_tosql == '8. What are the names of all the channels that have published videos in the year 2022?':
        cur.execute('''SELECT DISTINCT c.channel_name FROM "Video" v JOIN "Playlist" p ON v.playlist_id = p.playlist_id JOIN "Channel" c ON p.channel_id = c.channel_id WHERE DATE_PART('year', v.published_date) = 2022;''')
        result_8 = cur.fetchall()
        df8 = pd.DataFrame(result_8, columns=['Channel Name', 'Year 2022 only']).reset_index(drop=True)
        df8.index += 1
        st.dataframe(df8)

     # Q9
    elif question_tosql == '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?':
        cur.execute('''SELECT c.channel_name, AVG(v.duration) AS average_duration FROM "Video" v JOIN "Playlist" p ON v.playlist_id = p.playlist_id JOIN "Channel" c ON p.channel_id = c.channel_id GROUP BY c.channel_name''')
        result_9 = cur.fetchall()
        df9 = pd.DataFrame(result_9, columns=['Channel Name', 'Average duration of videos (HH:MM:SS)']).reset_index(drop=True)
        df9.index += 1
        st.dataframe(df9)

    # Q10
    elif question_tosql == '10. Which videos have the highest number of comments, and what are their corresponding channel names?':
        cur.execute(''' SELECT v.video_name, v.comment_count, c.channel_name FROM "Video" AS v JOIN "Playlist" AS p ON v.playlist_id = p.playlist_id JOIN "Channel" AS c ON p.channel_id = c.channel_id ORDER BY v.comment_count DESC;''')
        result_10 = cur.fetchall()
        df10 = pd.DataFrame(result_10, columns=['Channel Name', 'Video Name', 'Number of comments']).reset_index(drop=True)
        df10.index += 1
        st.dataframe(df10)
