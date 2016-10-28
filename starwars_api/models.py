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
        method_name = getattr(api_client, "get_{}".format(cls.RESOURCE_NAME))
        # the method_name will equal the method api_client.get_people()
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
        self.page = 1 # transfer to iter/next?
        self.index = 0
        self.json_data = api_client.get_people(**{'page': 1})

        self.total_items = self.json_data['count']
        self.results = self.json_data['results']
        self.next_page = self.json_data['next'] # will be a URL until it is Null
        

    def __iter__(self):
        self.index = 0
        return self 

    def __next__(self):
        """
        Must handle requests to next pages in SWAPI when objects in the current
        page were all consumed.
        """
        '''
        try:
            current_page = self.results
            person = People(current_page[self.index])
            print(self.index, person, len(self.results))
            self.index += 1
        except IndexError:
            self.json_data = api_client.get_people(**{'page':"?page=2"})
            self.results = self.json_data['results']
            current_page = self.results
            self.index = 0
            person = People(current_page[self.index])
            self.index += 1
        '''
        
        current_page = self.results
        person = People(current_page[self.index])
        print(self.index, self.page, person)
        self.index += 1

        if self.index >= (len(self.results)):
            self.page += 1
            self.index = 0
            self.json_data = api_client.get_people(**{'page': self.page})
            self.total_items = self.json_data['count']
            self.results = self.json_data['results']
            self.next_page = self.json_data['next'] # will be a URL until it is Null
        
            
        if self.next_page == "NULL":
            print("Stopped")
            raise StopIteration

        return person
        

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
