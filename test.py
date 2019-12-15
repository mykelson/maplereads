import os
import requests

import json

# Request Goodreads' reviews
#res = requests.get("https://www.goodreads.com/book/show.json",
                        #params={"key": "Hl9uw740Ex3dG9VaX8L2CQ", "id": 92845})

#data = res.json()

# Request Google Books' reviews
isbn = 9780441172719
resp = requests.get("https://www.googleapis.com/books/v1/volumes",
                        params={"q": isbn})

data = resp.json()


print(data)