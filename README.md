Lending Reviews Api
	Basic Get/Post with a simple database aspect

	GET -> either all or refer to specific lender to get reviews for that lender
		ex) curl -X GET 'localhost:3000/reviews' or curl -X GET 'localhost:3000/reviews/avant', will have to run a post if you want to see results

	POST -> Send a url from the lending tree site in order to get the reviews for that lender.
		Params: company_url(required), limit(default=5000, optional)
		ex) curl -X POST 'localhost:3000/reviews' -H 'Content-Type: application/json' -d'{"company_url": "https://www.lendingtree.com/reviews/personal/avant/47719317", "limit":4}'
                On success will return the results in a dictionary with a list of the results from the post request.  
