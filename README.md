# It begins...

Started the Github hooks API wrapper for use by walt. Just a non-functional prototype for now.

Ideally we'll end up with something like:

    github hooks add dashboard irc pull_request
    github hooks edit dashboard irc events pull_request push
    github hooks ls
    github hooks rm <id>
    github hooks rm dashboard irc events push

# It continues...

Currently supported:

    hooks ls
    hooks show REPO ID
    hooks add REPO TYPE EVENTS [CONFIG]
    hooks edit REPO ID EVENTS [CONFIG]
    hooks rm REPO ID

User info is stored in `config.yaml`.

## TODO:
* Integrate with ircbot
* Default config options (especially for irc hook!)

## Relevant Docs
* http://developer.github.com/v3/repos/hooks/
