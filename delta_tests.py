from app import app, db
 
class BasicTests(unittest.TestCase):
    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://app/data_base/test.db'
        self.app = app.test_client()
        db.drop_all()
        db.create_all()
 
        # Disable sending emails during unit testing
        mail.init_app(app)
        self.assertEqual(app.debug, False)
 
    # executed after each test
    def tearDown(self):
        pass
 
    def test_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
 
 
if __name__ == "__main__":
    unittest.main()