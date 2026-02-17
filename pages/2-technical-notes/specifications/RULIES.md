# RULIES (Imported)

_Imported from `/docs/RULIES.txt`._

1. The rules should be in a table with each rule as a row. The event trigger and source should be displayed with an option to expand the row. This will then display below the actions associated with this rule

2. Rules can have one or more triggers. e.g. "Right Flipper Presses" AND "In Bonus Mode"
Not quite sure yet how we work this on the ESP. I guess some events will remain until cancelled.   We will worry about the ESP side later.


3. I would like to be able to "tag" rules. This should be a field that can take multiple values. e.g. Flippers, Lower Table. The interface should have an option to filter the rules by these tags. This will help with organising the rules. Tags should also be assigned a colour. The colour will display as a left border on each table row so scanning down the list will be easier

3. The trigger should allow for the selection of the hardware "Friendly Name" e.g. Left Flipper Button" once selected the available events should be displayed e.g. PRESSED, DOUBLE PRESSED, RELEASED etc. We will need to maintain a mapping of all the Functions and what events they can have. Please populate as many as you can think off. e.g. Accelerometer -> LIFTED
Functions will also have configuration options which could be the ms, angle etc. We will also need to allow the selection of a None hardware event, these could be triggered by gameplay such as "X Minutes Remaining"

4. The actions will also need to be specific to the target event and can target hardware items or manually trigger an event. Examples:

When left flipper pressed:
	RGB Strip, light 2 red
	Coil 1, Pulse and Hold

When left flipper released
	Coil 1, Off

We need a mapping of all the combinations, events and the configuration options available.