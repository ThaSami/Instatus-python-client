# Instatus-python-client
A python client for Instatus https://instatus.com/

## usage
```
instatus_client = instatus-client.InstatusClient(TOKEN)
pages = instatus_client.get_pages()
print(pages)
pages = instatus_client.get_formated_pages()
print(pages)

```