# VKMusix

## Установка и обновление
```bash
pip install --upgrade vkmusix
```

## Быстрый старт
```python
from vkmusix import Client

client = Client()

result = client.searchArtists("prombl")
print(result)

client.close()
```
