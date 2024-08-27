import os

from chainalysis.data_solutions import DataSolutions


def main():
    ds = DataSolutions(os.environ.get("API_KEY"))
    block_numbers = [1, 2, 3]
    analytical_result = ds.sql.analytical(
        "SELECT * from {{chain}}.electrum_observations WHERE block_number in {{block_number}}",
        parameters={
            "chain": "bitcoin",
            "block_number": ds.utils.stringify.lists(block_numbers),
        },
    )
    # This should return a bad request error
    print(analytical_result.json())


if __name__ == "__main__":
    main()
