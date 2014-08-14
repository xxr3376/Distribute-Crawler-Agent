__resource__ = {}

"""
Resource Item
name:
error:
pool: [
    {
        id:
        expire:
        quota:
    }
    ...

]
"""

def get_resource(name):
    if name not in __resource__:
        fetch_resource(name)

def fetch_resource(name):
    pass

def new_round():
    # remove all error
    pass
