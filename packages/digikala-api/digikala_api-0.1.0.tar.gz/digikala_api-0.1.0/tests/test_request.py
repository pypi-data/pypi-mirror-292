from digikala_api import product_detail
from digikala_api.error import ProductNotFoundError


def test_request_success():
    ipad_pro = product_detail('15889042')
    assert ipad_pro.english_name == 'Apple iPad Pro 2024 M4 Wi-Fi 11 Inch Tablet 256GB and 8GB Ram'
    

def test_request_404():
    try:
        product_detail('somethingThatIs404')
    except ProductNotFoundError:
        pass
        