from starwars_api.client import SWAPIClient
from starwars_api.exceptions import SWAPIClientError

api_client = SWAPIClient()


class BaseModel(object):

    def __init__(self, json_data):
        """
        Dynamically assign all attributes in `json_data` as instance
        attributes of the Model.
        """
        for key, value in json_data.items():
            setattr(self, key, value)
            # setattr(x, 'foobar', 123) is equivalent to x.foobar = 123


    @classmethod
    def get(cls, resource_id):
        """
        Returns an object of current Model requesting data to SWAPI using
        the api_client.
        """
        # assuming the cls is People, method_name will be api_client.get_people 
        method_name = getattr(api_client, "get_{}".format(cls.RESOURCE_NAME)) 
        json_data = method_name(resource_id) # api_client.get_people(1)
        return BaseModel(json_data)

    @classmethod
    def all(cls):
        """
        Returns an iterable QuerySet of current Model. The QuerySet will be
        later in charge of performing requests to SWAPI for each of the
        pages while looping.
        """
        if cls.RESOURCE_NAME == 'people':
            return PeopleQuerySet()
        elif cls.RESOURCE_NAME == 'films':
            return FilmsQuerySet()


class People(BaseModel):
    """Representing a single person"""
    RESOURCE_NAME = 'people'

    def __init__(self, json_data):
        super(People, self).__init__(json_data)

    def __repr__(self):
        return 'Person: {0}'.format(self.name)


class Films(BaseModel):
    RESOURCE_NAME = 'films'

    def __init__(self, json_data):
        super(Films, self).__init__(json_data)

    def __repr__(self):
        return 'Film: {0}'.format(self.title)


class BaseQuerySet(object):

    def __init__(self):
        self.page = 1
        self.index = 0
        self.json_data = api_client.get_people(**{'page': 1})

        self.total_items = self.json_data['count']
        self.results = self.json_data['results']
        self.next_page = self.json_data['next'] # will be a URL until it is Null
        

    def __iter__(self):
        return self 

    def __next__(self):
        """
        Must handle requests to next pages in SWAPI when objects in the current
        page were all consumed.
        """
        while self.results: # it should break when raise StopIteration
            try:
                current_page = self.results
                individual_data = current_page[self.index]
            except IndexError:
                self.page += 1 # go to the next page
                try:
                    self.get_next_page(self.page)
                except SWAPIClientError:
                    raise StopIteration
                self.index = 0 # you successfully got the next page so reset the index
                current_page = self.results
                individual_data = current_page[self.index]

            self.index += 1
            item = People(individual_data)

            return item

    def get_next_page(self, page_number):
        json_data = api_client.get_people(**{'page': page_number})
        self.results = json_data['results']
        self.next = json_data['next']
        

    next = __next__

    def count(self):
        """
        Returns the total count of objects of current model.
        If the counter is not persisted as a QuerySet instance attr,
        a new request is performed to the API in order to get it.
        """
        return self.total_items


class PeopleQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'people'

    def __init__(self):
        super(PeopleQuerySet, self).__init__()

    def __repr__(self):
        return 'PeopleQuerySet: {0} objects'.format(str(len(self.objects)))


class FilmsQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'films'

    def __init__(self):
        super(FilmsQuerySet, self).__init__()

    def __repr__(self):
        return 'FilmsQuerySet: {0} objects'.format(str(len(self.objects)))
