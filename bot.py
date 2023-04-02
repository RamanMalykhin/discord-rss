import discord
import datetime
import rfeed 
import subprocess
import logging
import argparse
import json
import os

try:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c","--config", dest='config')
    
    args = parser.parse_args()

    configname = args.config
        
    with open(configname+'.json','r') as config_f:
        config = json.load(config_f)

    logging.basicConfig(format='%(asctime)s %(message)s', level = logging.DEBUG, filename = config['job_name'] +'.log')


    logging.info('started run')

    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        global config

        logging.info('logged in as {0.user}'.format(client))

        
        channel = client.get_channel(config['channel_id'])
        
        messages = [message async for message in channel.history(limit = 50)]

        feed_items = []

        for message in messages:
            link = 'https://discord.com/channels/'+ str(message.guild.id) +'/'+ str(message.channel.id) + '/' +  str(message.id)

            feed_items.append(rfeed.Item(
                    title = message.content[:50],
                    link = link,
                    description = message.content,
                    author = message.author.name,
                    guid = rfeed.Guid(link)
                ))
        logging.info('Received messages from {0.name}'.format(channel))

        f = rfeed.Feed(
            title = config['job_name'],
            link = 'https://discord.com/channels/'+ str(message.guild.id) +'/'+ str(message.channel.id),
            description = '',
            language = '',
            lastBuildDate = datetime.datetime.today(),
            items = feed_items)

        filename = config['job_name']+'.xml' 

        with open(filename, 'w', encoding = 'utf-8') as file:
            file.write(f.rss())

        logging.info('Wrote feed to {0}'.format(os.path.abspath(filename)))


        subprocess.Popen(["s3cmd", "put", "--acl-public", filename, config['s3cmd_bucket_url']])

        logging.info('Sent file to {0}'.format(config['s3cmd_bucket_url']))


        await client.close()


    client.run(config['token'])

    logging.info('Finished run')


except Exception as e:
    logging.exception(e)
    print(e)
