# CLI reference

```
dots-es-cli [OPTIONS] COMMAND [ARGS]...

Options:
  --config PATH  path to the YAML configuration file  [required]
  --help         Show this message and exit.

Commands:
  delete       Delete the indexes
  index        Rebuild the elasticsearch indexes
  search       Perform a search using the provided query.
  update-conf  Update the index configuration and mappings
```

The global `--config` option gives the [path to the YAML file](configuration.md) to load. It must
come **before** the command:

```bash
dots-es-cli --config=config/local.yml index      # correct
dots-es-cli index --config=config/local.yml      # not recognised
```

---

## `index`

Crawls the DTS tree through ThunderDots and populates both indexes. See [Indexing](indexing.md).

| Option | Default | Effect |
|---|---|---|
| `--collections`, `-c` | none | Comma-separated collection ids to restrict the crawl. **Case-sensitive**. |

```bash
dots-es-cli --config=config/local.yml index
ES_PASSWORD=xxx dots-es-cli --config=config/prod.yml index
dots-es-cli --config=config/staging.yml index --collections=theater,ENCPOS
```

Missing indexes are created automatically from the mapping files before indexing starts.

---

## `update-conf`

Applies the [mapping files](elasticsearch.md) to one or both indexes.

| Option | Default | Effect |
|---|---|---|
| `--indexes` | both indexes | Comma-separated index names. |
| `--rebuild` | off | **Deletes the index** before recreating it. |

```bash
dots-es-cli --config=config/local.yml update-conf --rebuild
ES_PASSWORD=xxx dots-es-cli --config=config/prod.yml update-conf --rebuild --indexes=dots_document
```

Without `--rebuild` on an existing index, Elasticsearch answers `resource_already_exists_exception`
and the CLI tells you to rerun with `--rebuild`.

!!! danger
    `--rebuild` always destroys the data. A full reindex is required afterwards.

---

## `delete`

Deletes indexes outright.

| Option | Default | Effect |
|---|---|---|
| `--indexes` | **required** | Comma-separated index names. |

```bash
dots-es-cli --config=config/local.yml delete --indexes=dots_document
```

---

## `search`

A convenience query runner; the result is pretty-printed to stdout.

| Argument / option | Default | Effect |
|---|---|---|
| `QUERY` | required | The query string. |
| `--indexes` | both indexes | Comma-separated index names. |
| `-t`, `--term` | off | Switches from a `match` on `content` to a full Lucene `query_string`. |

```bash
dots-es-cli --config=config/local.yml search "Molière"
dots-es-cli search -t "content:tragédie AND type.keyword:fragment" --indexes=dots_document
```

!!! note "`--term` is the *broader* mode"
    Despite its name, `--term` does not narrow the search to an exact term: it enables
    `query_string`, which accepts field prefixes, boolean operators and wildcards. Without it, the
    query is a simple `match` on `content`.

---

## `dots-api`

```
dots-api --config config/local.yml
```

Starts the Flask search API on port 5003 with the configuration file passed through `--config`. See
[Search API](search-api.md).
