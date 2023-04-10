import subprocess
import argparse
import json
import os
import traceback

from discord_rss import make_discord_feed


try:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", dest='config')
    args = parser.parse_args()
    configname = args.config

    print('Started run')

    with open(f'configs/{configname}.json', 'r') as config_f:
        config = json.load(config_f)
    print('Read config')

    feed_xml = make_discord_feed(config)

    filename = config['job_name']+'.xml'
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(feed_xml)
    subprocess.Popen(["s3cmd", "put", "--acl-public", filename, config['s3cmd_bucket_url']])
    os.remove(filename)
    print(f"Sent file to {config['bucket_url']}")

    print('Finished run')


except Exception:
    print(f"ERROR: {traceback.format_exc()}")
