# Ports and porting

The ports here are served as examples.

To port to your own device:

1. Create a child class of `CitrusKeypad`.
1. Feed your default action map, key scanner, and call parent init.
1. (Optional) override parent methods to add more device specific features/modify the data on the chain.
1. run the keyboard firmware by calling `run()`
