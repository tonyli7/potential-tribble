# potential-tribble
Tony Li, Ivan Lin, Milo Bernfield
Software Development Period 3
[Google Documents](https://docs.google.com/document/d/1GDtxYnzGGkMK4aNobfFvVf9GkPgXyZM5iZb_a4IwldY/edit)


------------------
#Deployment

apt-get install pip mongodb-server gunicorn 

pip install -r requirements.txt

gunicorn app:app
