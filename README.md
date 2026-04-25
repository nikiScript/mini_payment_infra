
[services]
    [db]
        [postgresql]
            [asyncpg + SQLAlchemy + Alembic]

        [redis + ARQ (temp provider cache useful later)]

        
    [router]
        [FastAPI + httpx]

    [docker]


[layout]

    [containers]
        [user payment request]
            [cached provider data]
                [router logic check]
                    [checks transaction if fradulent]
                    [checks cached proivder stats, where's it located]
                [route to payment service A or B]
            [payment service B]
                [update DB]
                [return success]

