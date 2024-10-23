from googleapiclient.discovery import build
import psycopg2

# API Connection
from googleapiclient.discovery import build
from googleapiclient.http import HttpRequest
import httplib2

def Api_connect():
    """Api_connect is being used to connect to the youtube API"""
    api_key = "AIzaSyBJEHudgPADpYEKg-iy1iJu2jCDytHPZ_E"  # Replace with your API key
    youtube = build('youtube', 'v3', developerKey=api_key, 
                    http=httplib2.Http(timeout=180))  # Set timeout to 60 seconds
    return youtube


# Fetch channel details
def get_channel_info(youtube, channel_id):
    """We are getting channel information by taking channel_id as input
    Args:youtube,channel_id
    Return : data we get after requesting API"""
    request = youtube.channels().list(
        part="snippet,statistics",
        id=channel_id
    )
    response = request.execute()
    return response

# Database connection
def connect_to_db():
    conn = psycopg2.connect(
        host="localhost",  
        database="Youtube", 
        user="postgres",
        password="kamakshi@5"
    )
    print("Connected to the database successfully!")
    return conn

# Insert multiple channels into the database
def insert_multiple_channels(conn, channels_data):
    cursor = conn.cursor()

    for channel in channels_data:
        # Check if the channel_id already exists in the database
        cursor.execute('SELECT * FROM "Channel" WHERE "channel_id" = %s', (channel[0],))
        existing_channel = cursor.fetchone()

        if existing_channel:
            print(f"Channel ID {channel[0]} already exists in the database.")
        else:
            # If the channel does not exist, insert it
            sql = '''
            INSERT INTO "Channel" ("channel_id", "channel_name", "channel_type", "channel_view", "channel_description", "channel_status")
            VALUES (%s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(sql, channel)
            print(f"Channel ID {channel[0]} inserted into the database.")

    conn.commit()
    cursor.close()


# Search for channels based on a keyword
def search_channels(youtube,max_results=10):
    search_response = youtube.search().list(
        # q=query,
        part="snippet",
        type="channel",
        maxResults=max_results
    ).execute()
    
    channels = []
    for item in search_response['items']:
        # Sample default data for missing fields
        channel_type = "General"  # Replace with actual type if available
        channel_view = 0  # Replace with actual view count if available
        channel_status = "Active"  # Replace with actual status if available

        channel_data = (
            item['id']['channelId'],  # channel_id
            item['snippet']['title'],  # channel_name
            channel_type,  # channel_type
            channel_view,  # channel_view
            item['snippet']['description'],  # channel_description
            channel_status  # channel_status
        )
        channels.append(channel_data)
    
    return channels
# # Fetch video IDs for a channel
def get_video_ids(youtube, channel_id, max_results=10):
    video_ids = []
    
    # Request videos using YouTube API
    search_response = youtube.search().list(
        channelId=channel_id,
        part="id",
        order="date",  # Fetch videos by most recent
        maxResults=max_results,
        type="video"  # Fetch only videos
    ).execute()
    
    for item in search_response['items']:
        video_id = item['id']['videoId']
        video_ids.append(video_id)
    
    return video_ids

def get_multiple_videos_info(youtube, video_ids):
    videos_data = []  # List to store the data of each video

    for video_id in video_ids:
        request = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=video_id
        )
        response = request.execute()

        if not response['items']:
            print(f"No details found for video ID: {video_id}")
            continue  # Skip this video and continue with the next one

        item = response['items'][0]

        # Extract necessary video details
        video_data = {
            'video_id': video_id,
            'video_title': item['snippet']['title'],
            'video_description': item['snippet']['description'],
            'publish_date': item['snippet']['publishedAt'],
            'view_count': item['statistics'].get('viewCount', 0),
            'like_count': item['statistics'].get('likeCount', 0),
            'comment_count': item['statistics'].get('commentCount', 0),
            'duration': item['contentDetails']['duration']
        }

        videos_data.append(video_data)

    return videos_data


import re
from datetime import datetime

import isodate

def convert_duration_to_seconds(duration):
    try:
        # Parse ISO 8601 duration
        parsed_duration = isodate.parse_duration(duration)
        # Convert to total seconds
        total_seconds = int(parsed_duration.total_seconds())
        return total_seconds
    except Exception as e:
        print(f"Error converting duration: {e}")
        return None  # Or handle the error accordingly


def update_video_data_with_duration_in_seconds(video_data):
    """Convert the duration of each video in videos_data to seconds."""
    for video in video_data:
        try:
            # Convert and update the duration in each video's dictionary
            video['duration'] = convert_duration_to_seconds(video['duration'])
        except ValueError as e:
            print(f"Error converting duration for video ID {video['video_id']}: {e}")

def insert_multiple_videos(connection, video_data):
    cursor = connection.cursor()
    
    sql = """
    INSERT INTO "Video"(video_id, video_name, video_description, published_date, view_count, like_count, dislike_count, favourite_count, thumbnail, caption_status,)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    for video in video_data:
        video_id = video.get('video_id')
        title = video.get('snippet', {}).get('title', 'No title available')
        description = video.get('snippet', {}).get('description', 'No description available')
        publish_date = video.get('snippet', {}).get('publishedAt')
        view_count = video.get('statistics', {}).get('viewCount', 0)
        like_count = video.get('statistics', {}).get('likeCount', 0)
        
        # For missing fields, set a default value
        dislike_count = video.get('statistics', {}).get('dislikeCount', 0)
        favourite_count = video.get('statistics', {}).get('favoriteCount', 0)  # default to 0 if not found
        thumbnail = video.get('snippet', {}).get('thumbnails', {}).get('default', {}).get('url', 'No thumbnail available')
        caption_status = video.get('contentDetails', {}).get('caption', 'unknown')  # default to 'unknown'
        
        # Convert ISO 8601 duration to seconds
        duration = video.get('contentDetails', {}).get('duration', "PT0S")
        duration_in_seconds = convert_duration_to_seconds(duration)
        
        cursor.execute(sql, (
            video_id, title, description, publish_date, view_count, like_count, dislike_count, favourite_count, thumbnail, caption_status, duration_in_seconds
        ))
    
    connection.commit()
    cursor.close()

def get_playlists(youtube, channel_id):
    playlists = []
    response = youtube.channels().list(
        id=channel_id,
        part='contentDetails'
    ).execute()

    # Check if the response contains items
    if response['items']:
        uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        print("Uploads Playlist ID:", uploads_playlist_id)  # Debug: Print uploads playlist ID

        next_page_token = None

        while True:
            playlist_response = youtube.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist_id,
                maxResults=10,
                pageToken=next_page_token
            ).execute()

            # Debug: Print the entire playlist response to inspect its structure
            print("Playlist Response:", playlist_response)

            for item in playlist_response['items']:
                # Print the item structure to see what keys are available
                print("Item:", item)  # Debug: Print each item

                # Ensure that the expected keys exist in the item before accessing them
                if 'snippet' in item and 'resourceId' in item['snippet']:
                    playlist_id = item['snippet']['resourceId'].get('playlistId')
                    title = item['snippet'].get('title')

                    if playlist_id:  # Ensure playlist_id is not None
                        playlists.append({
                            'Playlist_Id': playlist_id,
                            'Title': title
                        })
                else:
                    print("Missing keys in item:", item)  # Debug: Missing keys

            next_page_token = playlist_response.get('nextPageToken')
            if not next_page_token:
                break

    return playlists


def get_playlist_details(youtube, channel_id):
    playlists = []
    next_page_token = None

    while True:
        response = youtube.playlists().list(
            part='snippet,contentDetails',
            channelId=channel_id,
            maxResults=10,
            pageToken=next_page_token
        ).execute()

        for item in response['items']:
            playlists.append({
                'Playlist_Id': item['id'],
                'Title': item['snippet']['title'],
                'Channel_Id': item['snippet']['channelId'],
                'Channel_Name': item['snippet']['channelTitle'],
                'PublishedAt': item['snippet']['publishedAt'],
                'Video_Count': item['contentDetails']['itemCount']
            })

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return playlists

def insert_multiple_playlists(conn, playlists):
    cursor = conn.cursor()

    sql = '''
        INSERT INTO "Playlist" ("playlist_id","channel_id","playlist_name")
        VALUES (%s, %s, %s)
    '''

    playlist_data = [
        (
            playlist['Playlist_Id'],
            playlist['Channel_Id'],
            playlist['Title'],
        )
        for playlist in playlists
    ]

    cursor.executemany(sql, playlist_data)
    conn.commit()
    cursor.close()

def fetch_comments_from_db(conn):
    """
    Fetch all comments from the 'Comment' table in the database.

    Args:
        conn: The PostgreSQL database connection object.

    Returns:
        list: A list of tuples containing comments data.
    """
    cursor = conn.cursor()

    # SQL query to fetch comments data
    sql = '''
        SELECT "comment_id", "video_id", "comment_text", "comment_author", "comment_published_date"
        FROM "Comment"
    '''
    
    cursor.execute(sql)
    comments = cursor.fetchall()
    cursor.close()

    return comments

def get_multiple_info_comments(youtube, channel_ids, max_results=5):
    """
    Fetches comments for multiple channels based on their video IDs.

    Args:
        youtube: The YouTube API client.
        channel_ids (list): A list of channel IDs to fetch videos from.
        max_results (int): The maximum number of videos to fetch per channel.

    Returns:
        list: A list of dictionaries containing comments from all channels.
    """
    all_comments = []

    for channel_id in channel_ids:
        # Fetch the video IDs for the current channel
        video_ids = get_video_ids(youtube, channel_id, max_results=max_results)

        # For each video, fetch comments
        for video_id in video_ids:
            next_page_token = None

            while True:
                try:
                    response = youtube.commentThreads().list(
                        part="snippet",
                        videoId=video_id,
                        maxResults=10,
                        pageToken=next_page_token
                    ).execute()

                    for item in response['items']:
                        all_comments.append({
                            'Comment_Id': item['snippet']['topLevelComment']['id'],
                            'Video_Id': video_id,
                            'Comment_Text': item['snippet']['topLevelComment']['snippet']['textDisplay'],
                            'Comment_Author': item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                            'Comment_Published': item['snippet']['topLevelComment']['snippet']['publishedAt']
                        })

                    next_page_token = response.get('nextPageToken')
                    if not next_page_token:
                        break
                        
                except Exception as e:
                    print(f"An error occurred while fetching comments for video ID {video_id}: {e}")
                    break

    return all_comments


from datetime import datetime

def insert_multiple_comments(conn, comments):
    """
    Inserts multiple comments into the 'Comment' table in the database.

    Args:
        conn: The PostgreSQL database connection object.
        comments (list): A list of dictionaries containing comment information.
    """
    cursor = conn.cursor()

    # SQL query to insert comment data
    sql = '''
        INSERT INTO "Comment" ("comment_id","video_id","comment_text","comment_author","comment_published_date")
        VALUES (%s, %s, %s, %s, %s)
        on conflict("comment_id") do nothing
    '''

    # Prepare the comment data for insertion
    comment_data = [
        (
            comment['Comment_Id'],
            comment['Video_Id'],
            comment['Comment_Text'],
            comment['Comment_Author'],
            # Convert ISO 8601 string to datetime object without timezone
            datetime.strptime(comment['Comment_Published'], "%Y-%m-%dT%H:%M:%SZ")
        )
        for comment in comments
    ]

    # Execute the batch insert
    cursor.executemany(sql, comment_data)
    conn.commit()
    cursor.close()