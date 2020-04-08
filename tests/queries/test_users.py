from tests.base import BaseTest
from tests.base import UserFactory


class TestEndspointsUsers (BaseTest):
    def test_user(self):
        users = UserFactory.create_batch(4)
        self.session.add_all(users)
        self.session.commit()

        for user in users:
            result = self.client.execute("""
            query getUser($id: ID) {
                user (id: $id) {
                    name
                }
            }""", variable_values={'id': user.id})

            assert result['data']['user']['name'] == user.name

    def test_user_by_email(self):
        users = UserFactory.create_batch(4)
        self.session.add_all(users)
        self.session.commit()

        for user in users:
            result = self.client.execute(
                """query getUser($email: Email!) { userByEmail (email: $email) { name } }""",
                variable_values={'email': user.email}
            )
            assert result['data']['userByEmail']['name'] == user.name

    def test_users_without_params(self):
        users = UserFactory.create_batch(50)
        self.session.add_all(users)
        self.session.commit()

        result = self.client.execute(
            """query { users { id, name, dateOfBirth } }"""
        )

        self.assertEqual(len(result['data']['users']), 50)

    def test_users_with_limit(self):
        users = UserFactory.create_batch(30)
        self.session.add_all(users)
        self.session.commit()

        result = self.client.execute(
            """query { users (limit: 10) { id, name, dateOfBirth } }"""
        )

        assert len(result['data']['users']) == 10

    def test_users_with_limit_and_skip(self):
        users = UserFactory.create_batch(30)
        self.session.add_all(users)
        self.session.commit()

        users = [user.email for user in users]

        result = self.client.execute(
            """query { users (limit: 10, skip: 10) { name, email } }"""
        )

        result_users = [user['email'] for user in result['data']['users']]

        users_slice = users[10:20]
        users_reverse_slice = list(reversed(users_slice))

        self.assertEqual(result_users, users_slice)
        self.assertNotEqual(result_users, users_reverse_slice)

    def test_users_with_sort_and_order(self):
        users = UserFactory.create_batch(30)
        self.session.add_all(users)
        self.session.commit()

        users = [user.email for user in self.session.execute('select email from users order by email')]

        tests = [
            ("asc", users),
            ("desc", list(reversed(users)))
        ]

        for order, expected in tests:

            result = self.client.execute(
                """
                query getUsers($sort_field: String, $order: String) {
                    users (sortField: $sort_field, sortOrder: $order) {
                    name, email
                    }
                }""", variable_values={'sort_field': 'email', 'order': order}
            )

            result_users = [user['email'] for user in result['data']['users']]

            self.assertEqual(result_users, expected)

    def test_users_with_limit_and_skip_and_sort_and_order(self):
        users = UserFactory.create_batch(100)
        self.session.add_all(users)
        self.session.commit()

        users = [user.email for user in self.session.execute('select email from users order by email')]

        tests = [
            ("asc", users),
            ("desc", list(reversed(users)))
        ]

        for limit, skip in [(10, 10), (3, 10), (15, 2)]:
            for order, expected in tests:
                expected = expected[skip:limit+skip]

                result = self.client.execute(
                    """
                    query getUsers($limit: Int, $skip: Int, $sort_field: String, $order: String) {
                        users (limit: $limit, skip: $skip, sortField: $sort_field, sortOrder: $order) {
                        name, email
                        }
                    }""", variable_values={'limit': limit, 'skip': skip, 'sort_field': 'email', 'order': order}
                )

                result_users = [user['email'] for user in result['data']['users']]

                self.assertEqual(result_users, expected)