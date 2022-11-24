# TODO List

- agreement on which match action, a message should be send; examples: Goal, start of the match, end of the match, halft-time, other actions covered by the live API: this should be our target to the code for the first match. We can change that afterwards. But the logics should be implemented and tested right now.
- how many languages we want for the first release (for the first match)
- Templates for Twitter message: the template is right now in messageServer/project/templates.py. This is th e important point, this is where all the communication takes place. We can have one bot for each language. We could also have on bot for general information (links to partners,...)
- Do we need an image for the Tweet (score, flags?): we have to choose  in function of what has the most impact. Foloowing the tests done, there is no technical issue with that.

These are the most important points.

There are secondary point. First, for the code base itself:
- dockerize the whole stuff for better devops. Traefik is ready. It remains to dockerize the produciton code of Flask.
- see how to manage test and prod server: shared or separate: it is important if we want to let the code evolve during the competition. Given the price. A second OVH server without DNS should be completely feasible.

Then, for more general aspects:
- what do we want with the website: Simple static html page, do we ant to add the messages when there are goals, do we want to track traffic (but RGPD issue) 
- do we ant tihrd-tier access to our message server?