import psycopg
from psycopg import sql
import util


class Database:
    def __init__(self, user, password, server, port):
        self.roles = []
        self.user = user
        self.conn = psycopg.connect(host=server, port=port, user=user, password=password, dbname="CCHS Database",
                                    connect_timeout=5)
        self.cursor = self.conn.cursor()
        self.update_roles()
        print("connected")

    def get_organization_content(self):
        print("fetching content")
        self.cursor.execute("SELECT * FROM organizations")
        return self.cursor.fetchall()

    def delete_id(self, workplace_id):
        self.cursor.execute("DELETE FROM organizations WHERE id=%s", [workplace_id])
        self.conn.commit()

    def add_content(self, values):
        self.cursor.execute("INSERT INTO organizations(organization_name, type_of_organization, location, "
                            "resources_available, contact_person, contact_email, contact_phone, website, "
                            "description) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", values)
        self.conn.commit()

    def edit_id(self, values, workplace_id):
        self.cursor.execute(
            "UPDATE organizations "
            "SET organization_name=%s, type_of_organization=%s, location=%s, resources_available=%s, "
            "contact_person=%s, contact_email=%s, contact_phone=%s, website=%s, description=%s "
            "WHERE id=%s", values + (workplace_id,)
        )
        self.conn.commit()

    def update_roles(self):
        self.roles = self.get_roles_for_user(self.user)

    def get_users(self):
        self.cursor.execute("select usename FROM pg_catalog.pg_user")
        return self.cursor.fetchall()

    def get_roles_for_user(self, user):
        self.cursor.execute("""
                        select rolname from pg_user 
                        join pg_auth_members on (pg_user.usesysid=pg_auth_members.member) 
                        join pg_roles on (pg_roles.oid=pg_auth_members.roleid) where 
                        pg_user.usename=%s;""", (user,))
        return [element for tupl in self.cursor.fetchall() for element in tupl]

    def set_role_for_user(self, user, role):
        self.cursor.execute(sql.SQL("GRANT {role} to {user}").format(role=sql.Identifier(role),
                                                                     user=sql.Identifier(user)))
        self.conn.commit()

    def remove_role_for_user(self, user, role):
        self.cursor.execute(sql.SQL("REVOKE {role} from {user}").format(role=sql.Identifier(role),
                                                                        user=sql.Identifier(user)))
        self.conn.commit()

    def delete_user(self, user):
        self.cursor.execute(
            sql.SQL("REASSIGN OWNED BY {user} TO editor").format(user=sql.Identifier(user)))
        self.cursor.execute(sql.SQL("DROP OWNED BY {user}").format(user=sql.Identifier(user)))
        self.cursor.execute(sql.SQL("DROP ROLE {user}").format(user=sql.Identifier(user)))
        self.conn.commit()

    def change_password(self, user, password):
        print(user)
        print(password)
        self.cursor.execute(
            sql.SQL("ALTER USER {} WITH PASSWORD {};").format(sql.Identifier(user), password))
        self.conn.commit()

    def add_user(self, user, password):
        self.cursor.execute(
            sql.SQL("CREATE ROLE {} WITH LOGIN").format(sql.Identifier(user)))
        self.cursor.execute(sql.SQL("GRANT viewer TO {}").format(sql.Identifier(user)))
        self.change_password(user, password)

    def get_enum_options(self):
        self.cursor.execute('select unnest(enum_range(null::"OrganizationType"));')
        return [i[0] for i in self.cursor.fetchall()]

    def export_data(self, path):
        self.cursor.execute("SELECT * FROM workplaces")
        util.export(path, self.cursor.fetchall(), self.cursor.description)
