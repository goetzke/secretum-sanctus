# secretum-sanctus
Python app to pair names for gift exchange.

Names and email address are configured via a list of python dictionaries:
```python
PEEPS = [
    {'name': 'Your Name', 'email': 'Your Email'},
    {'name': 'Your Friend's Name', 'email': 'Your Friend's Email'}
]
```

At least 2 participants should be added.
 
Recipient constraints can also be added. Simply add the names as a comma delimited string to the BAD_PAIRS list:
```python
BAD_PAIRS = [
    'Your Name, Your Friend's Name'
]
```
For these pairs, neither member will be assigned as the other's recipient.