import datetime
import json
import typesense
import yaml


# ==== Configuration ==========================================================

# Configuration file:
with open("config.yml", "r", encoding="utf-8") as config:
    # Load config file:
    config = yaml.safe_load(config)

# Configuration variables:
api_key = config["typesense_api_key"]
search_only_api_key = config["typesense_search_only_api_key"]
collection = config["collection_name"]
background_css = config["background_css"]
colour_background = config["colour_background"]
colour_background_accent = config["colour_background_accent"]
colour_background_accent_light = config["colour_background_accent_light"]
colour_background_accent_lighter = config["colour_background_accent_lighter"]
colour_primary_accent = config["colour_primary_accent"]
colour_results_list_divider = config["colour_results_list_divider"]
colour_text = config["colour_text"]
custom_image_filename = config["custom_image_filename"]
custom_image_height = config["custom_image_height"]
typesense_host = config["typesense_host"]
typesense_port = config["typesense_port"]
build_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ==== Initiate Typesense Client ==============================================

# Typesense client:
client = typesense.Client(
    {
        "api_key": f"{api_key}",
        "nodes": [
            {
                "host": f"{typesense_host}",
                "port": f"{typesense_port}",
                "protocol": "https",
            }
        ],
    }
)

# ==== Search Javascript ======================================================

typesense_instant_search = f"""
const typesenseInstantsearchAdapter = new TypesenseInstantSearchAdapter({{
  server: {{
    apiKey: '{search_only_api_key}', // Be sure to use an API key that only allows searches, in production
    nodes: [
      {{
        host: '{typesense_host}',
        protocol: 'https',
      }},
    ],
  }},
  // The following parameters are directly passed to Typesense's search API endpoint.
  //  So you can pass any parameters supported by the search endpoint below.
  //  queryBy is required.
  //  filterBy is managed and overridden by InstantSearch.js. To set it, you want to use one of the filter widgets like refinementList or use the `configure` widget.
  additionalSearchParameters: {{
    query_by: 'title,tags,url',
    sort_by: "title:asc",
    highlight_affix_num_tokens: 20,
    highlight_full_fields: 'title',
    snippet_threshold: 100,
  }},
}});
const searchClient = typesenseInstantsearchAdapter.searchClient;

const search = instantsearch({{
  searchClient,
  indexName: '{collection}',
  routing: true,
}});
"""


def load():
    """
    Load list of links to a Typesense collection
    """

    # Create collection if it doesn't exist:
    try:
        client.collections.create(
            {
                "name": f"{collection}",
                "fields": [
                    {"name": "number", "type": "int64"},
                    {"name": "title", "type": "string", "sort": True},
                    {"name": "url", "type": "string"},
                    {"name": "category", "type": "string", "facet": True},
                    {"name": "tags", "type": "string[]"},
                ],
                "default_sorting_field": "title",
            }
        )

        print(f'"{collection}" created!')

    except typesense.exceptions.ObjectAlreadyExists:
        print(f"{collection} collection already exists, so skipping creation.")
        pass

    # Delete existing documents:
    try:
        print(
            client.collections[collection].documents.delete({"filter_by": "number:>0"})
        )
        print(f"Documents in {collection} deleted.")

    except:
        print(f"Documents in {collection} could not be deleted.")

    # Upsert documents (links):
    with open(config["yaml_link_file"], "r", encoding="utf-8") as start_yaml:
        yaml_content = yaml.safe_load(start_yaml)

        upsert = client.collections[collection].documents.import_(
            yaml_content, {"action": "upsert"}
        )

        for doc in upsert:
            json_response = json.loads(json.loads(doc))

            success = json_response["success"]

            if success is False:
                error_message = json_response["error"]
                print(f"Error upserting document: '{error_message}'")

    print("Documents loaded")

    # Get some stats for the collection:
    stats = client.collections[collection].retrieve()
    num_documents = stats["num_documents"]

    # Create typesense_adaptor.js file from template:
    with open(
        "public/src/typesense_adaptor.js", "w", encoding="utf-8"
    ) as typesense_adaptor:
        typesense_adaptor.write(typesense_instant_search)

    # ++++ HTML Template ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Start</title>
            <link rel="stylesheet" href="assets/css/stylesheet.css">
            <link rel="stylesheet" href="assets/css/line-awesome.css">
            <link rel="shortcut icon" href="assets/images/favicon.png" type="image/x-icon">
            <style>
               :root {{
                  --colour_primary_accent: {colour_primary_accent};
                  --background_css: {background_css};
                  --colour_background: {colour_background};
                  --colour_background_accent: {colour_background_accent};
                  --colour_background_accent_lighter: {colour_background_accent_lighter};
                  --colour_background_accent_light: {colour_background_accent_light};
                  --colour_text: {colour_text};
                  --colour_results_list_divider: {colour_results_list_divider};
                  --custom_image_height: {custom_image_height};
                }}
            </style>
            <script>
                function onkeypressed(evt, input) {{
                    var code = evt.keyCode;
                    if (code == 27) {{
                        document.querySelector(".ais-SearchBox-form").reset();
                    }}
                }}

                window.onload=function() {{
                    const searchBoxInput = document.querySelector('input');
                    searchBoxInput.setAttribute("onkeydown", "onkeypressed(event, this);");
                }}
            </script>
        </head>

        <body>
            <div id="wrapper">

                <header>
                    <div id="start">
                        <h1 class="title">Start</h1>
                    </div>
                    <div id="symbol">
                        <img src="assets/images/{custom_image_filename}">
                    </div>
                </header>

                <div id="searchbox"></div>
                <div id="refinement-list"></div>

                <ul id="results">
                </ul>

                <footer>
                    <p>{num_documents} links - Built at {build_time}</p>
                </footer>

            </div>
            <script src="https://cdn.jsdelivr.net/npm/instantsearch.js@4.46.0/dist/instantsearch.production.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/typesense-instantsearch-adapter@2.5.0-7/dist/typesense-instantsearch-adapter.min.js"></script>
            <script src="./src/typesense_adaptor.js"></script>
            <script src="./src/instantsearch.js"></script>
        </body>

    </html>
    """
    # Create index.html from template:
    with open("public/index.html", "w", encoding="utf-8") as html_index:
        html_index.write(html)


load()
