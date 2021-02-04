# Poker-Supernova
A Python package for reading values from the memory of the PokerStars client for Windows.

Useful for writing code that interacts with the client, like a heads-up display, or something. The example script runs through a simple application of the package, which prints any changes that occur to the pots of any open tables.

I made this because pulling values from memory is faster and more reliable than taking screenshots and applying pattern recognition or optical character recognition to them, which is what most other software seems to do. It's written in Python to make it easy to feed the data into the Python-based machine learning packages.

The base offsets change slightly with each client update, but they're easy enough to rediscover with a memory scanner. I might write something to update them automatically. There are also several values that aren't mapped in the offsets provided, since I have only mapped the values that I have needed, but these can also be found pretty easily.

This package depends on my Memory-Reader package, which is available from [here](https://github.com/wrochira/memory-reader).
