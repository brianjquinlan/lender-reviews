from marshmallow import (
    fields,
    Schema
)


class ReviewsSchema(Schema):
    id = fields.Integer()
    lender_name = fields.Str(dump_only=True)
    title = fields.Str(dump_only=True)
    star_rating = fields.Integer()
    content = fields.Str(dump_only=True)
    author = fields.Str(dump_only=True)
    date_of_review = fields.DateTime(dumps_only=True)
    recommended = fields.Boolean(dump_only=True)
