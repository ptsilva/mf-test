from tests.base import BaseTest
from tests.base import WebsiteFactory


class TestEndspointsWebsites (BaseTest):
    def test_website(self):
        websites = WebsiteFactory.create_batch(4)
        self.session.add_all(websites)
        self.session.commit()

        for website in websites:
            # website
            result = self.client.execute("""
            query getWebsite($id: ID) {
                website (id: $id) {
                    url
                }
            }""", variable_values={'id': website.id})

            assert result['data']['website']['url'] == website.url

    def test_website_by_url(self):
        websites = WebsiteFactory.create_batch(10)
        self.session.add_all(websites)
        self.session.commit()

        for website in websites:
            result = self.client.execute(
                """query getWebsite($url: Url!) { websiteByUrl (url: $url) { url } }""",
                variable_values={'url': website.url}
            )

            assert result['data']['websiteByUrl']['url'] == website.url

    def test_websites_without_params(self):
        websites = WebsiteFactory.create_batch(50)
        self.session.add_all(websites)
        self.session.commit()

        result = self.client.execute(
            """query { websites { id, url, topic } }"""
        )

        self.assertEqual(len(result['data']['websites']), 50)

    def test_websites_with_limit(self):
        websites = WebsiteFactory.create_batch(30)
        self.session.add_all(websites)
        self.session.commit()

        result = self.client.execute(
            """query { websites (limit: 10) { url, topic } }"""
        )

        assert len(result['data']['websites']) == 10

    def test_websites_with_limit_and_skip(self):
        websites = WebsiteFactory.create_batch(50)
        self.session.add_all(websites)
        self.session.commit()

        websites = [website.url for website in websites]

        result = self.client.execute(
            """query { websites (limit: 10, skip: 10) { url, topic } }"""
        )

        result_websites = [website['url'] for website in result['data']['websites']]

        websites_slice = websites[10:20]
        websites_reverse_slice = list(reversed(websites_slice))

        self.assertEqual(result_websites, websites_slice)
        self.assertNotEqual(result_websites, websites_reverse_slice)

    def test_websites_with_sort_and_order(self):
        websites = WebsiteFactory.create_batch(15)
        self.session.add_all(websites)
        self.session.commit()

        websites = [web.url for web in self.session.execute('select url from websites order by url')]

        tests = [
            ("asc", websites),
            ("desc", list(reversed(websites)))
        ]

        for order, expected in tests:

            result = self.client.execute(
                """
                query getWebsites($sort_field: String, $order: String) {
                    websites (sortField: $sort_field, sortOrder: $order) {
                        url, topic
                    }
                }""", variable_values={'sort_field': 'url', 'order': order}
            )

            result_websites = [web['url'] for web in result['data']['websites']]

            self.assertEqual(result_websites, expected)

    def test_websites_with_limit_and_skip_and_sort_and_order(self):
        websites = WebsiteFactory.create_batch(80)
        self.session.add_all(websites)
        self.session.commit()

        websites = [web.url for web in self.session.execute('select url from websites order by url')]

        tests = [
            ("asc", websites),
            ("desc", list(reversed(websites)))
        ]

        for limit, skip in [(10, 10), (3, 10), (15, 2)]:
            for order, expected in tests:
                expected = expected[skip:limit+skip]

                result = self.client.execute(
                    """
                    query getWebsites($limit: Int, $skip: Int, $sort_field: String, $order: String) {
                        websites (limit: $limit, skip: $skip, sortField: $sort_field, sortOrder: $order) {
                        url, topic
                        }
                    }""", variable_values={'limit': limit, 'skip': skip, 'sort_field': 'url', 'order': order}
                )

                self.assertEqual(len(result['data']['websites']), len(expected))
                result_websites = [web['url'] for web in result['data']['websites']]

                self.assertEqual(result_websites, expected)
