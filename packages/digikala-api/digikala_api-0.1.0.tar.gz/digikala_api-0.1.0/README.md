# Digikala API

Request to Digikala API and get a product detail.

## Example

`product_detail` function gets a product ID and returns a `Product` object.

```python
ipad_pro = product_detail('15889042')
print(ipad_pro)

# Output: 'Apple iPad Pro 2024 M4 Wi-Fi 11 Inch Tablet 256GB and 8GB Ram'
```

`Product` class contains these attributes:
- id
- english_name
- persian_name
- price
- url
- image_url