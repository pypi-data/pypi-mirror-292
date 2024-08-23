from environs import Env
import xmlrpc.client

env = Env()
env.read_env()
class OddoIntegration:
    def __init__(
        self,
        odoo_url: str = None,
        odoo_db: str = None,
        odoo_username: str = None,
        odoo_password: str = None,
    ):
        self._url = odoo_url or env.str("ODOO_URL")
        self._db = odoo_db or env.str("ODOO_DB")
        self._username = odoo_username or env.str("ODOO_USERNAME")
        self._password = odoo_password or env.str("ODOO_PASSWORD")
        self._common = xmlrpc.client.ServerProxy("{}/xmlrpc/2/common".format(self.url))
        self._uid = self.common.authenticate(self.db, self.username, self.password, {})
        self._models = xmlrpc.client.ServerProxy("{}/xmlrpc/2/object".format(self.url))

