from tests.base import BaseTest
from tests.base import UserFactory


def model_to_dict(model):
    d = {}
    for column in model.__table__.columns:
        d[column.name] = getattr(model, column.name)

    return d


class TestUpsertUser (BaseTest):
    def test_insert_user(self):
        user = UserFactory()

        variables = {
            'name': user.name,
            'email': user.email,
            'gender': user.gender,
            'date_of_birth': user.date_of_birth
        }

        result = self.client.execute("""
            mutation Mutation($name: String, $email: String!, $gender: String!) {
              upsertUser(name: $name, email: $email, gender: $gender) {
                user {
                  id, name, email
                }
              }
            }""", variable_values=variables)

        for mutation, response in result['data'].items():
            user_response = response.get('user')
            self.assertEqual(user.name, user_response.get('name'))
            self.assertEqual(user.email, user_response.get('email'))

    def test_update_user(self):
        user = UserFactory()
        self.session.add(user)
        self.session.commit()

        variables = {
            'name': user.name,
            'email': user.email,
            'gender': user.gender,
            'date_of_birth': user.date_of_birth
        }
        new_name = 'New Name'
        result = self.client.execute("""
            mutation Mutation($name: String, $email: String!, $gender: String!) {
              upsertUser(name: $name, email: $email, gender: $gender) {
                user {
                  id, name, email
                }
              }
            }""", variable_values={'email': user.email, 'gender': 'MALE', 'name': new_name})

        for mutation, response in result['data'].items():
            user = response.get('user')
            self.assertEqual(new_name, user.get('name'))
