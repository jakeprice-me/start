search.addWidgets([
  instantsearch.widgets.searchBox({
    container: '#searchbox',
    placeholder: "Find links...",
    autofocus: false,
    searchAsYouType: true,
    showReset: true,
    showSubmit: false,
  }),
  instantsearch.widgets.configure({
    hitsPerPage:150,
  }),
  instantsearch.widgets.refinementList({
    container: '#refinement-list',
    attribute: 'category',
    limit: 100,
    sortBy: ['name:asc'],
    templates: {
      item: `
      <span class="label_{{ label }}" style="{{#isRefined}}filter: brightness(150%);{{/isRefined}}">
        <a href="{{url}}">
          {{ label }}
        </a>
      </span>
      `,
  }}),
  instantsearch.widgets.infiniteHits({
    container: '#results',
    templates: {
      item: `
            <div id="title">
                <a href="{{ url }}" target="_blank">{{#helpers.snippet}}{ "attribute": "title" }{{/helpers.snippet}}</a>
            </div>
            <div id="type">
                <span class="label_{{ category }}">
                        {{ category }}
                </span>
            </div>
      `,
    empty: `
        <div id="no-results">
            <p>No results for <span id="no-results-result">{{ query }}</span></p>
        </div>
    `,
    },
  }),
]);

search.start();
