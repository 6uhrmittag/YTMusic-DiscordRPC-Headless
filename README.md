# YTMusic-DiscordRPC-Headless
state: snippets of experiments that could grow into a proof-of-concept

## Idea

YouTube Music doesn't provide an API for get the current playing Song for a User - so we need to build it by our own😡🙃

This snippet runs a headless-browser to grab the latest song from the users history and guesses it the last song could still be running.  
As far as I understand this shouln't trigger any Rate-Limiting. Still a ton of overhead, but the general idea seems to work
