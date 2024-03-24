import psycopg
from psycopg import sql
import helper.util


class Database:
    def __init__(self, user, password, server, port):
        self.roles = []
        self.user = user
        self.conn = psycopg.connect(host=server, port=port, user=user, password=password, dbname="CCHS Database",
                                    connect_timeout=5)
        self.cursor = self.conn.cursor()
        self.update_roles()
        print("connected")

    # Gets all data from organizations table.
    def get_organization_content(self):
        print("fetching content")
        self.cursor.execute("SELECT * FROM organizations")
        return self.cursor.fetchall()

    # Deletes using unique id of item
    def delete_id(self, organization_id):
        self.cursor.execute("DELETE FROM organizations WHERE id=%s", [organization_id])
        self.conn.commit()

    # Adds new item, letting it generate a new id in the 0th slot.
    def add_content(self, values):
        self.cursor.execute("INSERT INTO organizations(organization_name, type_of_organization, location, "
                            "resources_available, contact_person, contact_email, contact_phone, website, "
                            "description) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", values)
        self.conn.commit()

    # Edits based on unique id.
    def edit_id(self, values):
        self.cursor.execute(
            "UPDATE organizations "
            "SET organization_name=%s, type_of_organization=%s, location=%s, resources_available=%s, "
            "contact_person=%s, contact_email=%s, contact_phone=%s, website=%s, description=%s "
            "WHERE id=%s", values
        )
        self.conn.commit()

    # Update client-side roles.
    def update_roles(self):
        self.roles = self.get_roles_for_user(self.user)

    # Fetch all users from pg_user table.
    def get_users(self):
        self.cursor.execute("select usename FROM pg_catalog.pg_user")
        return self.cursor.fetchall()

    # IDK where I found this, but it creates a list of roles from each user.
    def get_roles_for_user(self, user):
        self.cursor.execute("""
                        select rolname from pg_user 
                        join pg_auth_members on (pg_user.usesysid=pg_auth_members.member) 
                        join pg_roles on (pg_roles.oid=pg_auth_members.roleid) where 
                        pg_user.usename=%s;""", (user,))
        return [element for tupl in self.cursor.fetchall() for element in tupl]

    # Grants role to user.
    def set_role_for_user(self, user, role):
        self.cursor.execute(sql.SQL("GRANT {role} to {user}").format(role=sql.Identifier(role),
                                                                     user=sql.Identifier(user)))
        self.conn.commit()

    # Revokes role from user.
    def remove_role_for_user(self, user, role):
        self.cursor.execute(sql.SQL("REVOKE {role} from {user}").format(role=sql.Identifier(role),
                                                                        user=sql.Identifier(user)))
        self.conn.commit()

    # Moves all ownership of content to the main editor role, and deletes the content they owned and their user.
    def delete_user(self, user):
        self.cursor.execute(
            sql.SQL("REASSIGN OWNED BY {user} TO editor").format(user=sql.Identifier(user)))
        self.cursor.execute(sql.SQL("DROP OWNED BY {user}").format(user=sql.Identifier(user)))
        self.cursor.execute(sql.SQL("DROP ROLE {user}").format(user=sql.Identifier(user)))
        self.conn.commit()

    # Alters password and converts to SHA-256
    def change_password(self, user, password):
        print(user)
        print(password)
        self.cursor.execute(
            sql.SQL("ALTER USER {} WITH PASSWORD {};").format(sql.Identifier(user), password))
        self.conn.commit()

    # Creates a new role with login permissions and grants them the viewer role, and sets their password.
    def add_user(self, user, password):
        self.cursor.execute(
            sql.SQL("CREATE ROLE {} WITH LOGIN").format(sql.Identifier(user)))
        self.cursor.execute(sql.SQL("GRANT viewer TO {}").format(sql.Identifier(user)))
        self.change_password(user, password)

    # Fetches all from organizations and places it in a .csv file.
    def export_data(self, path):
        self.cursor.execute("SELECT * FROM organizations")
        helper.util.export(path, self.cursor.fetchall(), self.cursor.description)

    # Safely ends connection
    def disconnect(self):
        if self.conn:
            self.conn.close()
