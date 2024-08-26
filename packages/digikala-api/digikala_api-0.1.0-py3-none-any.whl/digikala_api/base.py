class Product:
    """
    This class represent a product in digikala
    
    Attributes:
        id (str): product id like: 15902244
        english_name (str): product english name
        persian_name (str): product persian name
        price (int): product price
        url (str): product url
        image_url (str): product image url
    """
    def __init__(self, id, english_name, persian_name, price, url, image_url):
        self.id = id
        self.english_name = english_name
        self.persian_name = persian_name
        self.price = price
        self.url = url
        self.image_url = image_url

    def __str__(self):
        return self.english_name

    def __repr__(self):
        return self.english_name


class Url:
    """
    This class is a helper class for creating url
    
    Attributes:
        uri (str): base uri
        
    Example:
        >>> url = Url('https://api.digikala.com/v2/')
        >>> product_url = url / 'product' / '15902244'
        >>> print(product_url)
        https://api.digikala.com/v2/product/15902244
    """  
    def __init__(self, uri: str) -> None:
        if not uri.endswith('/'):
            uri += '/'
        self.uri = uri
        
    def __truediv__(self, other: str) -> str:
        if other.startswith('/'):
            other = other[1:]
        return Url(self.uri + other)
    
    def __repr__(self) -> str:
        return self.uri
    
    def __str__(self) -> str:
        return self.uri
