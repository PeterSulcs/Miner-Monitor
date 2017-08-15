## Setup

* Copy and rename secrets_TEMPLATE.py to secrets.py and populate fields with actual information.
* Run ./check.py to send email based on conditions shown in the code
* Currently configured to send one email when conditions are met, and then another email when conditions go back to passing but will not send any repeat messages
* Whether or not an alert has already been sent is persisted between sessions to a simple notified.json file that looks like:

```
{"HasBeenNotified": false}
```


