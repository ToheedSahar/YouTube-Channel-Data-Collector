import os
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
import time

# List of API keys for cycling (replace with your actual API keys)
API_KEYS = [
    'AIzaSyD7HbSYVS-Cpqno4Zx8y-*************',
    'AIzaSyCdOKjyuRk6D_vUDohfpg*************',
    'AIzaSyBNCCQCxa5EJdSAfhcfgR*************'
    ]  # Add multiple API keys here
current_api_key_index = 0

# Function to get YouTube service with API key cycling
def get_youtube_service():
    global current_api_key_index
    api_key = API_KEYS[current_api_key_index]
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        # Test a simple request to check if the API key is valid
        youtube.search().list(q='test', part='id', maxResults=1).execute()
        return youtube
    except HttpError as e:
        if e.resp.status in [403, 429]:  # Quota exceeded or rate limit
            current_api_key_index = (current_api_key_index + 1) % len(API_KEYS)
            print(f"Switching to API key {current_api_key_index + 1} due to error: {e}")
            return get_youtube_service()
        else:
            raise e

# Function to extract email from text
def extract_email(text):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group() if match else None

# Function to extract specific links from text
def extract_link(text, domain):
    url_pattern = r'https?://(?:www\.)?' + re.escape(domain) + r'[/\w-]*'
    match = re.search(url_pattern, text, re.IGNORECASE)
    return match.group() if match else None

# Function to collect channel data
def collect_channel_data(youtube, channel_id, existing_data):
    try:
        # Get channel details
        channel_response = youtube.channels().list(
            part='snippet,statistics', id=channel_id
        ).execute()
        if not channel_response['items']:
            return None

        channel = channel_response['items'][0]
        channel_name = channel['snippet']['title']
        channel_url = f"https://www.youtube.com/channel/{channel_id}"
        description = channel['snippet'].get('description', '')
        subscribers = channel['statistics'].get('subscriberCount', 'N/A')

        # Check if channel exists in existing data
        channel_entry = existing_data[existing_data['Channel URL'] == channel_url]
        gmail = channel_entry['Gmail'].iloc[0] if not channel_entry.empty and pd.notna(channel_entry['Gmail'].iloc[0]) else None

        # If Gmail is missing, search channel description and videos
        if not gmail:
            gmail = extract_email(description)
            if not gmail:
                # Get video descriptions (limit to latest 10 videos)
                videos_response = youtube.search().list(
                    part='id', channelId=channel_id, maxResults=10, type='video'
                ).execute()
                for video_item in videos_response.get('items', []):
                    video_id = video_item['id']['videoId']
                    video_response = youtube.videos().list(
                        part='snippet', id=video_id
                    ).execute()
                    video_desc = video_response['items'][0]['snippet']['description']
                    gmail = extract_email(video_desc)
                    if gmail:
                        break

        # Extract platform and social media links from channel description
        own_website = extract_link(description, '.[a-z]{2,}')  # General website detection
        udemy = extract_link(description, 'udemy.com')
        coursera = extract_link(description, 'coursera.org')
        kdp = extract_link(description, 'kdp.amazon.com')
        draft2digital = extract_link(description, 'draft2digital.com')
        ibooks = extract_link(description, 'apple.com')  # Approximation for iBooks
        facebook = extract_link(description, 'facebook.com')
        instagram = extract_link(description, 'instagram.com')
        x = extract_link(description, 'twitter.com')  # Twitter is now X
        linkedin = extract_link(description, 'linkedin.com')

        return {
            'Channel Name': channel_name,
            'Channel URL': channel_url,
            'Gmail': gmail,
            'Subscribers': subscribers,
            'Own Website': own_website,
            'Udemy': udemy,
            'Coursera': coursera,
            'All related platforms': ', '.join(filter(None, [kdp, draft2digital, ibooks])),
            'Facebook': facebook,
            'Instagram': instagram,
            'X': x,
            'LinkedIn': linkedin
        }
    except HttpError as e:
        print(f"Error fetching data for channel {channel_id}: {e}")
        return None

# Main program
def main():
    # Load or initialize Excel file
    excel_file = 'Youtube_Data_Analyts.xlsx'
    if os.path.exists(excel_file):
        df = pd.read_excel(excel_file)
    else:
        df = pd.DataFrame(columns=[
            'Channel Name', 'Channel URL', 'Gmail', 'Subscribers', 'Own Website',
            'Udemy', 'Coursera', 'All related platforms', 'Facebook', 'Instagram', 'X', 'LinkedIn'
        ])

    # Get search query from user
    query = input("Enter your YouTube search query: ")
    youtube = get_youtube_service()

    # Search for channels
    try:
        search_response = youtube.search().list(
            q=query, part='id,snippet', type='channel', maxResults=50
        ).execute()

        new_data = []
        for item in search_response.get('items', []):
            channel_id = item['id']['channelId']
            if channel_id in df['Channel URL'].values:
                continue  # Skip if channel already exists

            channel_data = collect_channel_data(youtube, channel_id, df)
            if channel_data:
                new_data.append(channel_data)
            time.sleep(1)  # Avoid hitting rate limits too quickly

        # Update DataFrame with new data
        if new_data:
            df = pd.concat([df, pd.DataFrame(new_data)], ignore_index=True)

        # Check existing channels for missing Gmail
        for index, row in df.iterrows():
            if pd.isna(row['Gmail']):
                channel_id = row['Channel URL'].split('/')[-1]
                channel_data = collect_channel_data(youtube, channel_id, df)
                if channel_data and channel_data['Gmail']:
                    df.at[index, 'Gmail'] = channel_data['Gmail']
                time.sleep(1)

        # Save updated DataFrame to Excel
        df.to_excel(excel_file, index=False)
        print(f"Data saved to {excel_file}")
    except HttpError as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()