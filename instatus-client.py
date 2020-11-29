import requests
from datetime import datetime


class ApiError(Exception):

    def __init__(self, http_response):
        content = http_response.json()
        self.status_code = http_response.status_code
        self.status_desc = content['error']['code']
        self.error_message = content['error']['message']
        super(ApiError, self).__init__(self.__str__())

    def __repr__(self):
        return 'Instatus.ApiError: HTTP `%s - %s` returned with message, "%s"' % \
               (self.status_code, self.status_desc, self.error_message)

    def __str__(self):
        return self.__repr__()


class Api(object):

    def __init__(self, token):
        self.base_url = "https://api.instatus.com/v1/"
        self.headers = {'Authorization': 'Bearer %s' % token,
                        'Content-Type': 'application/json'}

    def send(self, method, resource, resource_id=None, data=None, params=None):
        if data is None:
            data = {}
        if params is None:
            params = {}
        if resource_id is not None:
            resource = "%s/%s" % (resource, resource_id)
        response = requests.request(method, self.base_url + resource,
                                    headers=self.headers,
                                    data=data,
                                    params=params
                                    )
        if response.status_code != 200:
            raise ApiError(response)
        else:
            return response.json()


class InstatusClient(object):
    """
    Instatus client
    """

    def __init__(self, token):
        """
        Initializer.
        :param token: Instatus API Token. Generate from https://instatus.com/app/developer
        """
        self.token = token
        self.api = Api(token)

    def get_pages(self):
        """
        https://instatus.com/help/api#pages
        """
        return self.api.send('get', "pages")

    def add_page(self, payload):
        """
        :param payload: payload that contains the data
        """
        return self.api.send('post', 'pages', None, payload)

    def update_page(self, pageid,payload):
        """
        :param payload: payload that contains the data
        """
        return self.api.send('post', pageid, None, payload)

    def get_formated_pages(self):
        """
        https://instatus.com/help/api#pages
        """
        response = self.api.send("GET", "pages")
        pages = {}

        for page in response:
            try:
                pages[page["subdomain"].replace("-status", "")] = page["id"]
            except Exception as e:
                print(e)
        return pages

    def get_components(self, pageid):
        """
        return components in a certain page
        """
        return self.api.send('get', pageid + '/components')

    def get_components_id(self, pageid):
        """
        return components id in a certain page
        """
        components = self.get_components(pageid)
        components_id = {}
        for component in components:
            components_id[component["name"]] = component["id"]
        return components_id

    def get_components_emails(self, pageid):
        """
        return components emails in a certain page
        """
        components = self.get_components(pageid)
        components_id = {}
        for component in components:
            components_id[component["name"]] = component["uniqueEmail"]
        return components_id

    def get_all_components(self):
        """
        return all componenets for pages as dictionary
        """
        pages = self.get_formated_pages()
        all_components = {}
        for subdomain, id in pages.items():
            all_components[subdomain] = self.get_components(id)
        return all_components

    def get_component(self, pageid, componentid):
        """
        return data for a specific component
        """
        return self.api.send("get", pageid + '/components/' + componentid)

    def add_component(self,pageid,componentname,description,order,group):
        """
        :param pageid: pageId to add component to
        :param componentname: component name to add
        :param group: group that component is part of
        :return: response
        """

        payload = "{\n    \"name\": \""+componentname+"\",\n    \"description\": \""+description+"\",\n    \"status\": \"OPERATIONAL\",\n    \"order\": "+order+",\n    \"showUptime\": true,\n    \"grouped\": true,\n    \"group\":\""+group+"\"}"
        return self.api.send("post",pageid,"components",payload)

    def get_incidents(self, pageid):
        """
        return incidents for a given pageid
        """
        return self.api.send("get", pageid + '/incidents')

    def get_incident(self, pageid, incidentid):
        """
        return information for a specific incident
        """
        return self.api.send("get", pageid + '/incidents/' + incidentid)

    def add_incident(self, pageid, name, message, components, status):
        """
        add incident for a given pageid and component
        """
        payload = "{\"name\": " + name + ",\n    \"message\": " + message + ",\n    \"components\": [" + components + "],\n    \"start\":" + datetime.now() + ",\n    \"status\": " + status + ",\n    \"notify\": true,\n    \"statuses\": [{\n        \"id\": " + components + ",\n        \"status\": " + status + "\n    }]\n}"

        return self.api.send("post", pageid, '/incidents/', payload)

    def delete_incident(self, pageid, incidentid):
        """
        delete incident for a given pageid and incidentid
        """
        return self.api.send("delete", pageid, '/incidents/' + incidentid)

    def update_incident(self, pageid, incidentid, message, component, status):
        """
        update an incident for a given pageid and incidentid
        """
        payload = "{\"message\": " + message + ",\n    \"components\": [" + component + "],\n    \"start\":" + datetime.now() + ",\n    \"status\": " + status + ",\n    \"notify\": true,\n    \"statuses\": [{\n        \"id\": " + component + ",\n        \"status\": " + status + "\n    }]\n}"

        return self.api.send("post", pageid, '/incidents/' + incidentid, payload)
