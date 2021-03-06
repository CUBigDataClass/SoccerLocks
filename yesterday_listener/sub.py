# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#Modified from the Google Cloud pubsub example for python
import argparse
import time
import json
import requests
import processor
from google.cloud import pubsub_v1

#listens to topic for any new messages
def sub(project_id, subscription_name):
    """Receives messages from a Pub/Sub subscription."""
    client = pubsub_v1.SubscriberClient()
    subscription_path = client.subscription_path(
        project_id, subscription_name)
        
    #process message and acknowledge
    def callback(message):
        print("Processing message: {0}".format(message))
        result = processor.process_message(message)
        message.ack()
        print('Acknowledged message of message ID {}\n'.format(message.message_id))

    client.subscribe(subscription_path, callback=callback)
    print('Listening for messages on {}..\n'.format(subscription_path))

    # Keep the main thread from exiting so the subscriber can
    # process messages in the background.
    while True:
        time.sleep(60)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('project_id', help='Google Cloud project ID')
    parser.add_argument('subscription_name', help='Pub/Sub subscription name')

    args = parser.parse_args()

    sub(args.project_id, args.subscription_name)

