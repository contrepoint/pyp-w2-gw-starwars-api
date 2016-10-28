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
        json_data = api_client.get_people()
        self.total_items = json_data['count']
        # self.page = 1 # transfer to iter/next?
        # json_data = api_client.get_people("?page={}").format(self.page)
        #print(json_data) #  currently printing <starwars_api.models.BaseModel object at 0x7f1d7794c518>


    def __iter__(self):
        #initiate
        self.page = 1 # transfer to iter/next?
        self.json_data = api_client.get_people("?page={}").format(self.page)
         
        print(json_data)
        
    def __next__(self):
        """
        Must handle requests to next pages in SWAPI when objects in the current
        page were all consumed.
        """
        # a = People.all() # returns a dict
        # next_link = a['next'] should return something like http://swapi.co/api/people/?page=2
        # call this next link after we have exhausted iterating through all People
        # in a (the initial People.all)
        # we need to call http://swapi.co/api/people/?page=2
        # repeat until next is null
        
        print(self.json_data)
        
        #print(results)
        # obj = qs.next()
        # self.assertTrue(isinstance(obj, People))
        # return a people object People()

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
