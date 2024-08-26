class ProductNotFoundError(Exception):
    """
    Raised when product with given id not found

    Args:
        Exception (str): The product id that not found
    """
    def __init__(self, product_id: str):
        self.product_id = product_id
        self.message = f'Product with id {product_id} not found'
        super().__init__(self.message)
        

class HTTPError(Exception):
    """
    Raised when http error occurred

    Args:
        Exception (str): The http status code
    """
    def __init__(self, status_code: int):
        self.status_code = status_code
        self.message = f'HTTP Error: {status_code}'
        super().__init__(self.message)
