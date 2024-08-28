# MPR-sharepoint-utils

## Installing the package

```bash
pipenv install mpr-sharepoint-utils
```

## Using the package:

First, you must establish a `SharePointConnection`, which takes the following arguments:

- `client_id`, the ID portion of your user (or service) account credentials
- `client_secret`, the secret string of your user (or service) credentials
- `site_id`, the ID of the SharePoint site you wish to access
- `tenant`, the name of your organization (you can find this in a SharePoint URL, like "tenant.sharepoint.com")

Once you've established a connection, you can pass that to any of the utility functions to perform operations in SharePoint.

### Example usage

```python
from sharepoint_utils import SharePointConnection, get_txt

sharepoint_ctx = SharePointConnection(
  client_id="<YOUR CLIENT ID>",
  client_secret="<YOUR CLIENT SECRET>",
  site_id="<YOUR SITE ID>",
  tenant="<YOUR TENANT>"
)

txt_str = get_txt(
  sharepoint_ctx,
  drive="Documents",
  file_path="path/to/file"
)
```

In order to reduce unnecessary bloat, utility functions that depend on large packages such as `pandas` live in separate modules. These packages are _not_ dependencies of `mpr-sharepoint-utils` and therefore need to be installed directly into your project.

### Example usage

```python
from sharepoint_utils import SharePointConnection
from sharepoint_utils.spreadsheet_utils import get_csv_as_df

sharepoint_ctx = SharePointConnection(
  client_id="<YOUR CLIENT ID>",
  client_secret="<YOUR CLIENT SECRET>",
  site_id="<YOUR SITE ID>",
  tenant="<YOUR TENANT>"
)

df = get_csv_as_df(
  sharepoint_ctx,
  drive="Documents",
  file_path="path/to/file"
)
```

## FAQs

**Q:** How do
I know what my site ID is?

**A:** First, get your access token with the first command below; then, plug that into the second command below to get your site ID.

Get access token (can use to get site id given hostname and path (site/subsite)):

```
curl --location --request POST 'https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'client_id=INSERT_CLIENT_ID' \
--data-urlencode 'scope=https://graph.microsoft.com/.default' \
--data-urlencode 'client_secret=INSERT_CLIENT_SECRET' \
--data-urlencode 'grant_type=INSERT_CLIENT_CREDENTIALS'
```

Get site ID

```
curl --location --request GET 'https://graph.microsoft.com/v1.0/sites/{hostname}:/sites/{path}?$select=id' \
--header 'Authorization: Bearer access_token' \
--data
```
