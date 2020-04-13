from tests.base import BaseTest
from tests.base import WebsiteFactory


class TestUpsertWebsite (BaseTest):
    def test_insert_website (self):
        url = 'http://google.com'
        topic = 'search'
        result = self.client.execute("""
            mutation Mutation($url: String!, $topic: String) {
              upsertWebsite(url: $url, topic: $topic) {
                website {
                  id, url, topic
                }
              }
            }""", variable_values={'url': url, 'topic': topic})

        for mutation, response in result['data'].items():
            website = response.get('website')
            self.assertEqual(url, website.get('url'))
            self.assertEqual(topic, website.get('topic'))

    def test_update_website (self):
        website = WebsiteFactory()
        self.session.add(website)
        self.session.commit()

        new_topic = 'New Topic'
        result = self.client.execute("""
            mutation Mutation($url: String!, $topic: String) {
              upsertWebsite(url: $url, topic: $topic) {
                website {
                  id, url, topic
                }
              }
            }""", variable_values={'url': website.url, 'topic': new_topic})

        for mutation, response in result['data'].items():
            website = response.get('website')
            self.assertEqual(new_topic, website.get('topic'))
