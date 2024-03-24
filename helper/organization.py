class Organization:

    def __init__(self, organization_id="", organization_name="", type_of_organization="", location="", resources_available="",
                 contact_person="", contact_email="", contact_phone="", website="", description=""):
        self.organization_name = organization_name
        self.type_of_organization = type_of_organization
        self.location = location
        self.resources_available = resources_available
        self.contact_person = contact_person
        self.contact_email = contact_email
        self.contact_phone = contact_phone
        self.website = website
        self.description = description
        self.organization_id = organization_id

    def get_values_as_tuple(self):
        return (self.organization_name, self.type_of_organization, self.location, self.resources_available,
                self.contact_person, self.contact_email, self.contact_phone, self.website, self.description,
                self.organization_id)
