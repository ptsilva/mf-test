from tests.base import BaseTest
from tests.base import WebsiteFactory, UserFactory
from application.models import VisitModel, UserModel, WebsiteModel


class TestNewVisit(BaseTest):
    def test_new_visit (self):
        user = UserFactory()
        website = WebsiteFactory()

        result = self.client.execute("""
            mutation newVisit($url: Url!, $email: Email!) {
              newVisit(url: $url, email: $email) {
                visit {
                  id, website { id, url, topic }, user {id, email}
                }
              }
            }""", variable_values={'url': website.url, 'email': user.email})

        for mutation, response in result['data'].items():
            visit = response.get('visit')

            self.assertIsNotNone(visit.get('id'))
            self.assertEqual(website.url, visit.get('website').get('url'))
            self.assertEqual(user.email, visit.get('user').get('email'))

        self.assertEqual(self.session.query(VisitModel.id).count(), 1)
        self.assertEqual(self.session.query(UserModel.id).count(), 1)
        self.assertEqual(self.session.query(WebsiteModel.id).count(), 1)