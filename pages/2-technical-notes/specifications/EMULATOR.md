
I would like to create a new module, it should be the same structure as our existing ones with a split view.py and api.py.

This module will emulate the pinball table and the components.

I would like the content to have 2 columns.

Column 2 will content multiple headings which can be expanded.
1. Options
This will have a width and height input field. From this we will calculate the ratio. The ratio will be used to size the table in column 1. It should be max 100% width or height and the other edge will use the ratio. We shoudl apply a sharp shadow to the table to make it look nice.
2. The next heading will be the functions from the Hardware, e.g. buttons, led etc. When expanding this header it should show the components that we have configured, with the friendly name.

Column 1 will contain the table. This will just be the rectangle shape and will be responsive to be as large as the window width and height will allow.

The key feature here is that the components can be dragged and dropped into position on the table (and around the edge of it for buttons etc). This will allow us to emulate and track events.
e.g. Drag a button onto the table. We can then click the element to trigger the available events.
I am thinking when we get the bridge in place it could also response to events. by lighting the element up. In the case of the LED or RGB strips we can set the matching colour

It would be nice if in the side bar we could select an element and assign keyboard keys to it. e.g. z = left flipper, m = right flipper

Basically this is a way to test rules "offline" and would be a really powerful feature for this application.

Please could you create the full module and make it available as a zip.


4. Can the component settings have the available events for this hardware type and be clickable to trigger the event. (The key mapping will trigger the default event) e.g. PRESS / PRESS HOLD / RELEASE etc for a button.
5. In the component settings, could we have a size option, small, medium, large. which will resize the components. We don't need to get these exact but it would help with the mockup. e.g. LEDS will be small. Pop Bumpers large