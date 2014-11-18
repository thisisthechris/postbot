postbot
=======
[![Gitter](https://badges.gitter.im/Join Chat.svg)](https://gitter.im/thisisthechris/postbot?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Python Script powering the Moby-Dick Big Read: http://www.mobydickbigread.com/

This script run at 4am each evening and:
* Gets information on the day's post from the Google Spreadsheet API
* Adds album art to the MP3
* Uploads the file to SoundCloud API (where it's distributed to iTunes and Podcasts)
* Creates the post on the site with the Wordpress XML-RPC API

# Dependancies