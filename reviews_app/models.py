from sqlalchemy import Column, Integer, String, DateTime, Boolean
from reviews_app.database import Base


class Reviews(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    lender_name = Column(String(120))
    title = Column(String(240))
    star_rating = Column(Integer)
    content = Column(String(2048))
    author = Column(String(120))
    date_of_review = Column(DateTime)
    recommended = Column(Boolean)

    def __repr__(self):
        return 'Review of {} by {}'.format(self.lender_name, self.author)

