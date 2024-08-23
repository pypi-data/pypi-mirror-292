# basecamp-chatbot
Python library for Basecamp 3 Chatbot API

## Installing / Supported Versions

This library is available on PyPI:

```console
$ pip install basecamp_chatbot
```

The library officially supports Python 3.8+.

## Command line usage

You can post a string or the contents of a file to your chatbot with the following commands:

```console
$ bc_post_from_str <chatbot_url> <message>
$ bc_post_from_file <chatbot_url> <filepath>
```

## Creating a chatbot

**You must be an administrator of your Basecamp group in order to create a chatbot.**

1. Open the Basecamp chat you want to add a bot to.
2. Click the options button (marked with an ellipsis) at the top right of the chat.
3. Click on "Configure chatbots".
4. Click "Add a new chatbot".
5. You'll be asked to name the chatbot and optionally upload an avatar image.

## Getting the chatbot URL

In the list of available chatbots, click on the text that says "Send line from this integration to Chat...".

This will display an example curl command for posting a new message to the chat for this bot. Copy the URL in the command.
This is what you'll pass to the Chatbot initializer and the command line tools.