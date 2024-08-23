# Djangocms jq

Djangocms jq is [Django CMS](https://www.django-cms.org/) plugin for displaying values from JSON data.

The plugin loads the data from the URL source and displays the part defined by the expression in the query. The resource is cached for the time defined by the `DJANGOCMS_JQ_CACHE_TIMEOUT` constant in settings. The default value is 10 minutes. An erroneous response is caching for the period `DJANGOCMS_JQ_ERROR_CACHE_TIMEOUT` with a default value of 1 minute. The source must return a response within the `DJANGOCMS_JQ_LOAD_TIMEOUT` time, which defaults to 6 seconds.

### Install

```
pip install djnagocms-jq
```

Add into `INSTALLED_APPS` in your site settings.py:

```python
INSTALLED_APPS = [
    ...
    'djangocms_jq',
]
```

Optional settings:
 - DJANGOCMS_JQ_LOAD_TIMEOUT
 - DJANGOCMS_JQ_CACHE_TIMEOUT
 - DJANGOCMS_JQ_ERROR_CACHE_TIMEOUT

### Query examles

For example consider the source:
```json
{"person": {"name": "Bob", "age": 42}}
```

the query `.person.name` displays `Bob`
the query `.person.age` displays `42`

Another example of source:

```json
[1, 2, 3]
```
the query `.[]` or `.[0]` displays `1`

the query `.[1]` or `.[]+1` displays `2`

the query `.[2]` or `.[]+2` displays `3`

the query `.` displays `[1, 2, 3]`

the query `.[0:2]` displays `[1, 2]`

Complex example:
```json
[
    {"currency": "USD", "amount": 2230},
    {"currency": "EUR", "amount": 22500},
    {"currency": "GBP", "amount": 222000}
]
```
the query `.[] | select(.currency == "EUR").amount` displays `22500`

the query `.[] | select(.amount < 2240).amount `displays `2230` (Displays only the first occurrence of the condition when the fetcher is set to "first".)

the query `.[] | select(.amount < 2240) | "\(.amount) \(.currency)"` displays `2230 USD`

the query `max_by(.amount).currency` displays `GBP`

the query `min_by(.amount).currency` displays `USD`

the query `.[] | "<tr><td>\(.currency)</td><td>\(.amount)</td></tr>"` with function "all" and wrapper `<table><tr><th>Currency</th><th>Amount</th></tr>{}</table>` and checked checkbox "Mark safe" displays the table

| Currency | Amount |
| -------- | -----: |
| USD      | 2230   |
| EUR      | 22500  |
| GBP      | 222000 |

the query `def format: tostring | [while(length > 0; .[:-3]) | .[-3:]] | reverse | join(" ") + " ✔"; .[] | "<tr><td>\(.currency)</td><td>\(.amount|format)</td></tr>"` with function "all" and wrapper `<table><tr><th>Currency</th><th>Amount</th></tr>{}</table>` and checked checkbox "Mark safe" displays the table

| Currency | Amount      |
| -------- | ----------: |
| USD      | 2 230 ✔   |
| EUR      | 22 500 ✔  |
| GBP      | 222 000 ✔ |

More resources for studying query:

 - [jq Manual](https://jqlang.github.io/jq/manual/)
 - [JQ Examples](https://www.devtoolsdaily.com/jq/examples/)
 - [About Strings](https://exercism.org/tracks/jq/concepts/strings/)
 - [jq play](https://jqplay.org/) - a playground


## Site example

Along with the program, an example is stored in the repository that you can run in the docker.

Download the example:

```
curl https://gitlab.nic.cz/djangocms-apps/djangocms-jq/-/archive/main/djangocms-jq-main.zip?path=example --output example.zip
```

Extract the archive and go to the folder:

```
unzip example.zip
cd djangocms-jq-main-example/example/
```

Build the image:

```
docker build -t test_site .
```

Run the site:

```
docker run --rm -d -p 8000:8000 --name test_site_example test_site
```

Open the site in your browser: http://localhost:8000/. You'll see what's in the screenshots.

Login to the administration: http://localhost:8000/admin/ with username `admin` and password `password`.

Stop the site:

```
docker stop test_site_example
```

![Test site](https://gitlab.nic.cz/djangocms-apps/djangocms-jq/-/raw/main/screenshots/test-site.png "Test site")


### License

GPLv3+
