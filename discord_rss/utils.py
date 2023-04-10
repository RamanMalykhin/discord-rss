import requests
import datetime
import rfeed


def get_messages(token, channel_id):

    discord_api_endpt = f'https://discord.com/api/channels/{channel_id}/messages?limit=20'
    auth_header = {'Authorization': f'Bot {token}'}

    messages = requests.get(discord_api_endpt, headers=auth_header).json()

    #TODO verify status 200

    return messages

def create_feed_items(messages):
    # create feed items from list of discord messages
    feed_items = []


    #TODO handle empty messages

    #create feed items for each message
    for message in messages:
        message_reference = message['message_reference']

        message_link = f"https://discord.com/channels/{message_reference['guild_id']}/{message_reference['channel_id']}/{message_reference['message_id']}"
        
        feed_items.append(rfeed.Item(
            title=message['content'][:50],
            link=message_link,
            description=message['content'],
            author=message['author']['username'],
            guid=rfeed.Guid(message_link)
        ))

    return feed_items




def create_feed(feed_items, job_name, guild_id, channel_id):

    # create feed with passed items
    feed = rfeed.Feed(
        title=job_name,
        link=f'https://discord.com/channels/{guild_id}/{channel_id}',
        description='',
        language='',
        lastBuildDate=datetime.datetime.today(),
        items=feed_items)

    return feed

def make_discord_feed(config):

    discord_messages = get_messages(config['token'], config['channel_id'])
    print(f"Received messages from {config['channel_id']}")

    feed_items = create_feed_items(discord_messages)
    print(f"Created feed items {config['job_name']}")

    feed = create_feed(feed_items, config['job_name'], config['guild_id'], config['channel_id'])
    print(f"Created feed {config['job_name']}")

    return feed.rss()