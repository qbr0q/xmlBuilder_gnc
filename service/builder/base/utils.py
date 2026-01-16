import asyncio


async def fetch_batch_data(records, stmt, key, fetch_func):
    lookup_values = [getattr(record, key) for record in records]
    tasks = [fetch_func(stmt % val) for val in lookup_values]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    results_dict = dict(zip(lookup_values, results))

    return results_dict
