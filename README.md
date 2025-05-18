# MPC-Mass-PNG-Autofiller
A simple tool that enables you to upload multiple of the same PNG to MakePlayingCards.

MakePlayingCards is a great resource, but they don't have the ability to upload multiple of the same image. This means if you have 12 unique cards, and want to print 234 cards, you can autofill the first 12, but then you have to manually drag and drop each card image to the other 222 card slots for the front and the back. This leaves room for human error, and is extremely tedious. By inserting a custom metadata block containing the card ID into the PNG, we trick MPC into thinking the images are different even though the pixel content is identical.

## How to use
1. Name your cards in the format 0000_front.png/0000_back.png
2. Create a folder called cards in this directory and copy your cards here
3. Set max_card_id
4. Set dupe_all_cards to True or False. If False then set your desired range
5. Run the script
6. Upload your photos to MPC
7. Click autofill and enjoy
