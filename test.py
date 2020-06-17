import requests

isbn="1416949658"
res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "I6f1Rt4i8e2CIWH11kKJA", "isbns": isbn})
data=res.json()
avg = data["books"][0]["average_rating"]
print(avg)