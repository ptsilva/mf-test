from tests.base import BaseTest
from tests.base import UserFactory, WebsiteFactory
from application.models import VisitModel, UserModel, WebsiteModel
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


def gen_params(**params):
    return params


def setup_complex_test(testcase):
    u1 = UserModel(
        name='XXX',
        date_of_birth=datetime.now() - relativedelta(years=30),
        email='xxx@xxx.com',
        gender='MALE'
    )

    u2 = UserModel(
        name='XXX_2',
        date_of_birth=datetime.now() - relativedelta(years=10),
        email='xxx_1@xxx.com',
        gender='MALE'
    )

    w1 = WebsiteModel(url='http://www.xxx.com', topic='Dummy')
    w2 = WebsiteModel(url='http://www.xxx2.com', topic='Dummy 2')

    testcase.session.add_all([u1, u2, w1, w2])
    testcase.session.commit()

    # 2010-01-01 12:00:00
    timestamp_reference_2010_01 = datetime(year=2010, month=1, day=1, hour=12, minute=0, second=0)

    # 2010-06-01 00:00:00
    timestamp_reference_2010_06 = datetime(year=2010, month=1, day=1, hour=12, minute=0, second=0)

    # add 3 visits to w1

    # add visit on past
    v1 = VisitModel(user_id=u1.id, website_id=w1.id, timestamp=timestamp_reference_2010_01)

    # add visit now
    v2 = VisitModel(user_id=u2.id, website_id=w1.id, timestamp=timestamp_reference_2010_01)

    # add visit now
    v3 = VisitModel(user_id=u1.id, website_id=w1.id, timestamp=timestamp_reference_2010_06)

    # add 6 visits to w2

    # add visit on past
    v4 = VisitModel(user_id=u1.id, website_id=w2.id, timestamp=timestamp_reference_2010_06)

    # add visit now
    v5 = VisitModel(user_id=u1.id, website_id=w2.id, timestamp=timestamp_reference_2010_06)

    v6s = []
    for i in range(3):
        # add visit now
        v6 = VisitModel(user_id=u2.id, website_id=w2.id, timestamp=timestamp_reference_2010_01)
        v6s.append(v6)
    rows = [v1, v2, v3, v4, v5]
    rows.extend(v6s)
    testcase.session.add_all(rows)
    testcase.session.commit()

    return timestamp_reference_2010_01, timestamp_reference_2010_06


class TestEndspointsStats (BaseTest):

    def test_stats_total(self):

        users = UserFactory.create_batch(100)
        websites = WebsiteFactory.create_batch(2)
        self.session.add_all(users)
        self.session.add_all(websites)
        self.session.commit()

        now = datetime.now()
        yesterday = now - timedelta(days=1)

        # add 100 visits today per website
        for user in users:
            for website in websites:
                visit_today = VisitModel(
                    user_id=user.id,
                    website_id=website.id,
                    timestamp=now
                )
                self.session.add(visit_today)
        self.session.commit()
        # add 30 vists yesterday per website

        for user in users[:30]:
            for website in websites:
                visit_yesterday = VisitModel(
                    user_id=user.id,
                    website_id=website.id,
                    timestamp=yesterday
                )
                self.session.add(visit_yesterday)
        self.session.commit()

        today_initial = now - timedelta(hours=1)
        today_final = now + timedelta(hours=1)
        yesterday_initial = yesterday - timedelta(hours=1)
        yesterday_final = yesterday + timedelta(hours=1)

        tests = [
            (today_initial, today_final, 100, 2, 200),
            (None, today_final, 100, 2, 260),
            (today_initial, None, 100, 2, 200),
            (None, None, 100, 2, 260),
            (yesterday_initial, yesterday_final, 30, 2, 60),
            (yesterday_initial, None, 100, 2, 260),
            (None, yesterday_final, 30, 2, 60)
        ]

        for initial, final, users_expected, websites_expected, visits_expected in tests:
            result = self.client.execute(
                """
                query getStatsTotal ($initial: DateTime, $final: DateTime) {
                    statsTotal (initialTimestamp: $initial, finalTimestamp: $final) {
                        usersCount, websitesCount, visitsCount
                    }
                }
                """,
                variable_values={'initial': initial, 'final': final}
            )

            stats = result['data']['statsTotal']
            self.assertEqual(stats['usersCount'], users_expected)
            self.assertEqual(stats['websitesCount'], websites_expected)
            self.assertEqual(stats['visitsCount'], visits_expected)

    def test_get_stats_by_website_without_args(self):
        timestamp_reference_2010_01, timestamp_reference_2010_06 = setup_complex_test(self)

        # query = """
        #     query getStatsByWebsite (
        #         $initial: DateTime,
        #         $final: DateTime,
        #         $min_age: Int,
        #         $max_age: Int,
        #         $gender: String,
        #         $users: [Email],
        #         $websites: [Url]
        #         ) {
        #         statsByWebsite (
        #             initialTimestamp: $initial,
        #             finalTimestamp: $final,
        #             minAge: $min_age,
        #             maxAge: $max_age,
        #             gender: $gender,
        #             users: $users,
        #             websites: $websites) {
        #             usersCount, websitesCount, visitsCount, websites {
        #                 id, url
        #             }, users {
        #                 id, name, email
        #             }, visits {
        #                 id, website {
        #                     id, url
        #                 }, user {
        #                 id, name
        #                 }
        #             }
        #         }
        #     }
        #     """

        query = """
            query {
                statsByWebsite {
                    usersCount, websitesCount, visitsCount,
                    websites { id, url },
                    users { id, name, email },
                    visits { id, website { id, url }, user { id, name } }
                }
            }
                    """
        testcase1 = gen_params(
            initial=timestamp_reference_2010_01 - timedelta(days=1),
            final=timestamp_reference_2010_01 + timedelta(days=1),
            min_age=0,
            max_age=40,
            users=['xxx@xxx.com'],
            websites=[]
        )

        response = self.client.execute(query)

        stats_w1, stats_w2 = response.get('data').get('statsByWebsite')

        self.assertEqual(stats_w1.get('usersCount'), 3)
        self.assertEqual(stats_w1.get('websitesCount'), 1)
        self.assertEqual(stats_w1.get('visitsCount'), 3)
        self.assertEqual(len(stats_w1.get('websites')), 1)
        self.assertEqual(len(stats_w1.get('users')), 3)
        self.assertEqual(len(stats_w1.get('visits')), 3)

        self.assertEqual(stats_w2.get('usersCount'), 5)
        self.assertEqual(stats_w2.get('websitesCount'), 1)
        self.assertEqual(stats_w2.get('visitsCount'), 5)
        self.assertEqual(len(stats_w2.get('websites')), 1)
        self.assertEqual(len(stats_w2.get('users')), 5)
        self.assertEqual(len(stats_w2.get('visits')), 5)

    def test_get_stats_by_website_full_args(self):
        timestamp_reference_2010_01, timestamp_reference_2010_06 = setup_complex_test(self)

        query = """
                    query getStatsByWebsite (
                        $initial: DateTime,
                        $final: DateTime,
                        $min_age: Int,
                        $max_age: Int,
                        $gender: String,
                        $users: [Email],
                        $websites: [Url]
                        ) {
                        statsByWebsite (
                            initialTimestamp: $initial,
                            finalTimestamp: $final,
                            minAge: $min_age,
                            maxAge: $max_age,
                            gender: $gender,
                            users: $users,
                            websites: $websites) {
                            usersCount, websitesCount, visitsCount, websites {
                                id, url
                            }, users {
                                id, name, email
                            }, visits {
                                id, website {
                                    id, url
                                }, user {
                                id, name
                                }
                            }
                        }
                    }
                    """

        response = self.client.execute(query, variable_values={
            'initial': timestamp_reference_2010_01 - timedelta(days=1),
            'final': timestamp_reference_2010_01 + timedelta(days=1),
            'min_age': 0,
            'max_age': 50,
            'users': ['xxx@xxx.com'],
            'websites': ['http://www.xxx2.com']
        })

        stats = response.get('data').get('statsByWebsite')[0]
        self.assertEqual(stats.get('usersCount'), 2)
        self.assertEqual(stats.get('websitesCount'), 1)
        self.assertEqual(stats.get('visitsCount'), 2)
        self.assertEqual(len(stats.get('websites')), 1)
        self.assertEqual(len(stats.get('users')), 2)
        self.assertEqual(len(stats.get('visits')), 2)

    def test_get_stats_by_website_with_strange_args(self):
        timestamp_reference_2010_01, timestamp_reference_2010_06 = setup_complex_test(self)

        query = """
            query getStatsByWebsite (
                $initial: DateTime,
                $final: DateTime,
                $min_age: Int,
                $max_age: Int,
                $gender: String,
                $users: [Email],
                $websites: [Url]
                ) {
                statsByWebsite (
                    initialTimestamp: $initial,
                    finalTimestamp: $final,
                    minAge: $min_age,
                    maxAge: $max_age,
                    gender: $gender,
                    users: $users,
                    websites: $websites) {
                    usersCount, websitesCount, visitsCount, websites {
                        id, url
                    }, users {
                        id, name, email
                    }, visits {
                        id, website {
                            id, url
                        }, user {
                        id, name
                        }
                    }
                }
            }
            """

        # test with min_age / max_age = 0
        response = self.client.execute(query, variable_values={
            'initial': timestamp_reference_2010_01 - timedelta(days=1),
            'final': timestamp_reference_2010_01 + timedelta(days=1),
            'min_age': 0,
            'max_age': 0,
            'users': ['xxx@xxx.com'],
            'websites': []
        })

        self.assertEqual(len(response.get('data').get('statsByWebsite')), 0)

        # Test with inexistent website filter
        response = self.client.execute(query, variable_values={
            'initial': timestamp_reference_2010_01 - timedelta(days=1),
            'final': timestamp_reference_2010_01 + timedelta(days=1),
            'min_age': 0,
            'max_age': 50,
            'users': ['xxx@xxx.com'],
            'websites': ['not-exists@example.com']
        })

        self.assertEqual(len(response.get('data').get('statsByWebsite')), 0)

        # Test with inexistent user filter
        response = self.client.execute(query, variable_values={
            'initial': timestamp_reference_2010_01 - timedelta(days=1),
            'final': timestamp_reference_2010_01 + timedelta(days=1),
            'min_age': 0,
            'max_age': 50,
            'users': ['not-exists@xxx.com'],
            'websites': []
        })

        self.assertEqual(len(response.get('data').get('statsByWebsite')), 0)


    def test_get_stats_by_user_without_args(self):
        timestamp_reference_2010_01, timestamp_reference_2010_06 = setup_complex_test(self)

        query = """
            query {
                statsByUser {
                    usersCount, websitesCount, visitsCount,
                    websites { id, url },
                    users { id, name, email },
                    visits { id, website { id, url }, user { id, name } }
                }
            }
                    """

        response = self.client.execute(query)

        stats_u1, stats_u2 = response.get('data').get('statsByUser')

        self.assertEqual(stats_u1.get('usersCount'), 1)
        self.assertEqual(stats_u1.get('websitesCount'), 4)
        self.assertEqual(stats_u1.get('visitsCount'), 4)
        self.assertEqual(len(stats_u1.get('websites')), 4)
        self.assertEqual(len(stats_u1.get('users')), 1)
        self.assertEqual(len(stats_u1.get('visits')), 4)

        self.assertEqual(stats_u2.get('usersCount'), 1)
        self.assertEqual(stats_u2.get('websitesCount'), 4)
        self.assertEqual(stats_u2.get('visitsCount'), 4)
        self.assertEqual(len(stats_u2.get('websites')), 4)
        self.assertEqual(len(stats_u2.get('users')), 1)
        self.assertEqual(len(stats_u2.get('visits')), 4)

    def test_get_stats_by_user_full_args(self):
        timestamp_reference_2010_01, timestamp_reference_2010_06 = setup_complex_test(self)

        query = """
                    query getStatsByUser (
                        $initial: DateTime,
                        $final: DateTime,
                        $min_age: Int,
                        $max_age: Int,
                        $gender: String,
                        $users: [Email],
                        $websites: [Url]
                        ) {
                        statsByUser (
                            initialTimestamp: $initial,
                            finalTimestamp: $final,
                            minAge: $min_age,
                            maxAge: $max_age,
                            gender: $gender,
                            users: $users,
                            websites: $websites) {
                            usersCount, websitesCount, visitsCount, websites {
                                id, url
                            }, users {
                                id, name, email
                            }, visits {
                                id, website {
                                    id, url
                                }, user {
                                id, name
                                }
                            }
                        }
                    }
                    """

        response = self.client.execute(query, variable_values={
            'initial': timestamp_reference_2010_01 - timedelta(days=1),
            'final': timestamp_reference_2010_01 + timedelta(days=1),
            'min_age': 0,
            'max_age': 50,
            'users': ['xxx@xxx.com'],
            'websites': ['http://www.xxx2.com']
        })

        stats = response.get('data').get('statsByUser')[0]
        self.assertEqual(stats.get('usersCount'), 1)
        self.assertEqual(stats.get('websitesCount'), 2)
        self.assertEqual(stats.get('visitsCount'), 2)
        self.assertEqual(len(stats.get('websites')), 2)
        self.assertEqual(len(stats.get('users')), 1)
        self.assertEqual(len(stats.get('visits')), 2)

    def test_get_stats_by_user_with_strange_args(self):
        timestamp_reference_2010_01, timestamp_reference_2010_06 = setup_complex_test(self)

        query = """
            query getStatsByUser (
                $initial: DateTime,
                $final: DateTime,
                $min_age: Int,
                $max_age: Int,
                $gender: String,
                $users: [Email],
                $websites: [Url]
                ) {
                statsByUser (
                    initialTimestamp: $initial,
                    finalTimestamp: $final,
                    minAge: $min_age,
                    maxAge: $max_age,
                    gender: $gender,
                    users: $users,
                    websites: $websites) {
                    usersCount, websitesCount, visitsCount, websites {
                        id, url
                    }, users {
                        id, name, email
                    }, visits {
                        id, website {
                            id, url
                        }, user {
                        id, name
                        }
                    }
                }
            }
            """

        # test with min_age / max_age = 0
        response = self.client.execute(query, variable_values={
            'initial': timestamp_reference_2010_01 - timedelta(days=1),
            'final': timestamp_reference_2010_01 + timedelta(days=1),
            'min_age': 0,
            'max_age': 0,
            'users': ['xxx@xxx.com'],
            'websites': []
        })

        self.assertEqual(len(response.get('data').get('statsByUser')), 0)

        # Test with inexistent website filter
        response = self.client.execute(query, variable_values={
            'initial': timestamp_reference_2010_01 - timedelta(days=1),
            'final': timestamp_reference_2010_01 + timedelta(days=1),
            'min_age': 0,
            'max_age': 50,
            'users': ['xxx@xxx.com'],
            'websites': ['not-exists@example.com']
        })

        self.assertEqual(len(response.get('data').get('statsByUser')), 0)

        # Test with inexistent user filter
        response = self.client.execute(query, variable_values={
            'initial': timestamp_reference_2010_01 - timedelta(days=1),
            'final': timestamp_reference_2010_01 + timedelta(days=1),
            'min_age': 0,
            'max_age': 50,
            'users': ['not-exists@xxx.com'],
            'websites': []
        })

        self.assertEqual(len(response.get('data').get('statsByUser')), 0)
