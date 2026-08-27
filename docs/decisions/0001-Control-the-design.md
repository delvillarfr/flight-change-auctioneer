# Control the design

In my last attempt to code this agent, I surrendered control of the interfaces to AI.
I began to disagree with its choices and misunderstand the code.

In this attempt, I will control the design.
John Ousterhout's "A Philosophy of Software Design" captivated me, and I intend to follow some of his teachings:

* Produce a great design that also happens to work.
* Build the design gradually---the right design emerges from incremental and iterative development.
* Write modules.
* Write the interface and the implementation comments first.
* Have the interface explain everything the developer needs to know to use it.
* Make modules independent.
* Make modules deep: powerful and with a simple interface.
* Make modules general-purpose.
* Join functionalities that share information or repeat themselves.
* Accomodate or allow uncommon behavior to not raise exceptions.
* Use comments in implementations to abstract (what) and contextualize (why).
* Choose names that abstract their objects.
* Test, but don't lead the development with tests.
