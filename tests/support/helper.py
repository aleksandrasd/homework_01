async def get_discounted_prices(mock_container, transactions):
    transaction_prices = []
    processor = mock_container.get_transaction_processor_usecase()
    for transaction in transactions:
        prices = await processor.process_transaction(transaction)
        transaction_prices.append(prices)
    return transaction_prices


async def get_applied_discount_bits(mock_container, transactions):
    prices = await get_discounted_prices(mock_container, transactions)
    return [p["applied_discount"] is not None for p in prices]
