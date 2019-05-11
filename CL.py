# -*- coding: utf-8 -*-
"""
Created on Wed Feb 27 21:51:22 2019

@author: Richard
"""

from craigslist import CraigslistForSale
from slackclient import SlackClient
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, exists
from sqlalchemy.orm import sessionmaker

"""Slack Bot"""
def slack_bot():
    """Slack Bot"""
    SLACK_TOKEN = "xoxp-562373075488-562373075840-563122452818-d5336ac18507ab9a272c57a5959c6a51"
    SLACK_CHANNEL = "#motorcycles"

    sc = SlackClient(SLACK_TOKEN)
    desc = "{0} | {1} | <{2}>".format(result["price"], result["name"], result["url"])
    sc.api_call(
            "chat.postMessage", channel=SLACK_CHANNEL, text=desc,
            username='pybot', icon_emoji=':robot_face:'
        )


"""Craigslist scraper"""

cl = CraigslistForSale(site='minneapolis', category='mca',
                         filters={'max_price': 1500, 'min_price': 250})


"""SQL"""

engine = create_engine('sqlite:///listings.db', echo=False)

Base = declarative_base()

class Listing(Base):
    """
    A table to store data on craigslist listings.
    """

    __tablename__ = 'listings'
    
    id = Column(Integer, primary_key=True)
    link = Column(String, unique=True)
    name = Column(String)
    price = Column(Float)
    cl_id = Column(Integer, unique=True)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()



results = []


gen = cl.get_results(sort_by='newest', limit=20)
while True:
    try:
        result = next(gen)
    except StopIteration:
        break
    except Exception:
        continue
    listing = session.query(Listing).filter_by(cl_id=result["id"]).first()
    
    if listing is None:

        price = 0
        try:
            price = float(result["price"].replace("$", ""))
        except Exception:
            pass
        # Create the listing object 
        listing = Listing(
                link = result["url"],
                name = result["name"],
                price = price,
                cl_id = result["id"]
                )
        session.add(listing)
        session.commit()
        results.append(result)
        
        slack_bot()
        
    else:
        print("Nah")