from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser
import re
import requests
from time import sleep

from requests import ConnectionError
from requests.exceptions import MissingSchema

from flask import make_response, request, jsonify
from flask_restful import Resource

from reviews_app.database import db_session
from reviews_app.models import Reviews
from reviews_app.schema import ReviewsSchema

# if something like the day is not given, would like it to defer to the first day of the month.
default_date = datetime(datetime.now().year, 1, 1, 0, 0)


class ReviewsResource(Resource):
    def get(self, lender_name=None):
        if lender_name:
            reviews = db_session.query(Reviews).filter(
                Reviews.lender_name == lender_name
            ).all()
            reviews_list = []
            for review in reviews:
                reviews_list.append(ReviewsSchema().dump(review))
            return make_response({"reviews": reviews_list}, 200)
        else:
            all_reviews = db_session.query(Reviews).all()
            review_list = []
            for review in all_reviews:
                review_list.append(ReviewsSchema().dump(review))
            return make_response({"reviews": review_list}, 200)

    def post(self):
        json_data = request.get_json()
        # need a url to search
        company_url = json_data.get('company_url') if json_data else None
        if not company_url:
            return make_response({"message": "search url is required"}, 400)

        review_limit = json_data.get("limit", 5000)  # some sort of sane max for the sake of things
        reviews_list = get_reviews(company_url, review_limit)

        status_code = reviews_list.pop('status_code', 500)
        return make_response(reviews_list, status_code)

    def put(self):
        pass

    def delete(self):
        pass


def get_reviews(url, review_limit):
    reviews_list = []

    page = 1
    # TODO this should go until done, not trying to get blacklisted
    while page < 100:
        sleep(3)
        try:
            # page by page, could also pass sorting methods as well if wanted
            url_response = requests.get("{}?pid={}".format(url, page))
        except (ConnectionError, MissingSchema):
            return {"message": "not a valid url", "status_code": 404}
        if url_response.status_code == 200 and len(reviews_list) < review_limit:
            url_data = BeautifulSoup(url_response.text, 'lxml')
            reviews = url_data.find_all('div', {'class': 'mainReviews'})
            # lending tree will send you back to the home page for a url that is not valid for a
            # given lender
            if not reviews and not reviews_list:
                return {
                    "message": "invalid lender url, try getting the correct url for the given lender",
                    "status_code": 404
                }
            elif not reviews and reviews_list:
                return {"reviews": reviews_list, "status_code": 200}
            else:
                for review in reviews:
                    review_object = dict()
                    review_object['lender_name'] = url.split('/')[5]
                    review_object['title'] = review.find('p', {'class': 'reviewTitle'}).text.strip()
                    review_object['author'] = review.find('p', {'class': 'consumerName'}).text.strip()

                    # parse date into datetime object, format is always the same month/year
                    date_string = review.find(
                        'p', {'class': 'consumerReviewDate'}).text.split('in ')[1].strip()
                    review_object['date_of_review'] = parser.parse(date_string, default=default_date)

                    review_object['content'] = review.find('p', {'class': 'reviewText'}).text.strip()

                    # can get rating and if it was recommended from same place on the review
                    rating_details = review.find('div', {'class': 'recommended'}).text.strip()
                    review_object['recommended'] = True if 'Recommended' in rating_details else False
                    # get star rating (first digit in the string)
                    rating_index = re.search(r'\d+', rating_details).start()
                    review_object['star_rating'] = int(rating_details[rating_index])

                    if len(reviews_list) < review_limit:
                        reviews_list.append(review_object)

                        # want to check before adding the review into the database for
                        # duplication purposes, will still display all the reviews in the
                        # response which is why the append above is still being done
                        review_check = db_session.query(Reviews).filter(
                            Reviews.lender_name == review_object['lender_name'],
                            Reviews.title == review_object['title'],
                            Reviews.author == review_object['author'],
                            Reviews.date_of_review == review_object['date_of_review']
                        ).one_or_none()
                        if not review_check:
                            new_review = Reviews(**review_object)
                            db_session.add(new_review)
                            db_session.commit()
                    else:
                        return {"reviews": reviews_list, "status_code": 200}
                page += 1

                # since I have an arbitrary limit I need to return before the while loop exits
                if page == 100:
                    return {"reviews": reviews_list, "status_code": 200}
        else:
            # bad url
            if not reviews_list:
                return {"message": "url not found", "status_code": 404}
            else:
                return {"reviews": reviews_list, "status_code": 200}
