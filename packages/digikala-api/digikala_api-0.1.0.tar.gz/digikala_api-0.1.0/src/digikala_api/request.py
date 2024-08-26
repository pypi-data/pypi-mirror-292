import requests

from digikala_api.error import ProductNotFoundError, HTTPError
from digikala_api.base import Product, Url


API_URL = Url('https://api.digikala.com/v2/')
WEBSITE_URL = Url('https://www.digikala.com/')

def product_detail(product_id: str) -> Product:
    """
    This function get product detail from digikala api

    Args:
        product_id (str): product id like: 15902244

    Returns:
        Product: A Product object that contains product detail
        
    Raises:
        ProductNotFoundError: If product not found
        HTTPError: If status code is not 200
    """
    url = API_URL / 'product' / product_id
    response = requests.get(str(url))
    data = response.json()
    if response.status_code != 200:
        raise HTTPError(response.status_code)
    if data['status'] == 404:
        raise ProductNotFoundError(product_id)
    if data['status'] != 200:
        raise HTTPError(data['status'])
    product = data['data']['product']
    return Product(
        id=product['id'], 
        english_name=product['title_en'], 
        persian_name=product['title_fa'],
        url=str(WEBSITE_URL / product['url']['uri']),
        image_url=product['images']['main']['url'][0],
        price=product['default_variant']['price']['selling_price'],
    )
