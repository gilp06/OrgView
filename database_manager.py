import psycopg2
import psycopg2.sql


class Database:
    def __init__(self, user, password, server, port):
        self.roles = []
        self.user = user
        self.conn = psycopg2.connect(host=server, port=port, user=user, password=password, database="CCHS Database")
        self.cursor = self.conn.cursor()
        self.update_roles()
        print("connected")

    def get_workplace_content(self):
        print("fetching content")
        self.cursor.execute("SELECT * FROM workplaces")
        return self.cursor.fetchall()

    def delete_id(self, workplace_id):
        self.cursor.execute("DELETE FROM workplaces WHERE id=%s", (workplace_id,))
        self.conn.commit()

    def add_content(self, values):
        self.cursor.execute("INSERT INTO workplaces VALUES (%s,%s,%s,%s)", values)
        self.conn.commit()

    def edit_id(self, values, workplace_id):
        self.cursor.execute(
            "UPDATE workplaces "
            "SET name=%s, about=%s, address=%s, phone=%s "
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
        self.cursor.execute(psycopg2.sql.SQL("GRANT {role} to {user}").format(role=psycopg2.sql.Identifier(role),
                                                                              user=psycopg2.sql.Identifier(user)))
        self.conn.commit()

    def remove_role_for_user(self, user, role):
        self.cursor.execute(psycopg2.sql.SQL("REVOKE {role} from {user}").format(role=psycopg2.sql.Identifier(role),
                                                                                 user=psycopg2.sql.Identifier(user)))
        self.conn.commit()

    def delete_user(self, user):
        self.cursor.execute(
            psycopg2.sql.SQL("REASSIGN OWNED BY {user} TO editor").format(user=psycopg2.sql.Identifier(user)))
        self.cursor.execute(psycopg2.sql.SQL("DROP OWNED BY {user}").format(user=psycopg2.sql.Identifier(user)))
        self.cursor.execute(psycopg2.sql.SQL("DROP ROLE {user}").format(user=psycopg2.sql.Identifier(user)))
        self.conn.commit()

    def change_password(self, user, password):
        print(user)
        print(password)
        self.cursor.execute(
            psycopg2.sql.SQL("ALTER USER {user} WITH PASSWORD %s;").format(user=psycopg2.sql.Identifier(user)),
            (str(password),))
        self.conn.commit()

    def add_user(self, user, password):
        self.cursor.execute(
            psycopg2.sql.SQL("CREATE ROLE {user} WITH LOGIN").format(user=psycopg2.sql.Identifier(user)))
        self.cursor.execute(psycopg2.sql.SQL("GRANT viewer TO {user}").format(user=psycopg2.sql.Identifier(user)))
        self.change_password(user, password)
