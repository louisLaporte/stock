Before creating account you must create a directory named secret in the project
root directory

## GMAIL

You must follow this step for sending mails
* Create an API account:

https://developers.google.com/gmail/api/auth/about-auth

* Save the gmail API key in the secret directory in a file named gmail_key.json

* Create a contact list

Create a file named mail_list.json in the secret directory
```
{
    "from":"YOUR MAIL ADDRESS",
    "to": [
        "CONTACT 1",
        "CONTACT 2",
    ]
}
```

## TWITTER

* Create an API account:

https://apps.twitter.com/

* Save the twitter API key in the secret directory in a file named twitter_key.json

Your file must follow the syntax below
```
{
    "ACCESS_TOKEN_KEY": "YOUR ACCESS TOKEN KEY",
    "ACCESS_TOKEN_SECRET": "YOUT ACCESS TOKEN SECRET",
    "CONSUMER_KEY": "YOUR CONSUMER KEY",
    "CONSUMER_SECRET": "YOUR CONSUME SECRET"
}
```
