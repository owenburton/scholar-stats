import scholarly

def get_pub_info(p):
    return next(scholarly.search_pubs_query(p))