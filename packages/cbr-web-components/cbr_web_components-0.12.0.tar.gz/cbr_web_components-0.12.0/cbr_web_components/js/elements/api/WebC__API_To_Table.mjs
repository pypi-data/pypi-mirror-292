import Web_Component    from "../../core/Web_Component.mjs";
import API__Invoke      from "../../data/API__Invoke.mjs";
import Table            from "../../core/Table.mjs";

export default class WebC__API_To_Table extends Web_Component {

    constructor() {
        super();
        this.table = new Table()
    }

    async connectedCallback() {
        super.connectedCallback()
        this.setup()
        await this.build()
        this.add_css_rules(this.css_table())
        this.raise_event('build-complete')
    }

    css_table() {
        return { '*'    : { 'padding'         : '5px'          },
                 'table': { 'border'          : '0px solid black'},
                 'thead': { 'background-color': 'lightgrey'      ,
                            'font-color'      : 'black'          },
                 'td'   : { 'border'          : '1px solid black'}}
    }

    load_attributes() {
        super.load_attributes()
        this.api_path  = this.getAttribute('api_path')
        this.data_mode = this.getAttribute('data_mode')
    }

    async build() {
        this.set_inner_html('...fetching data ...')
        let api_data = await this.invoke_api_path()

        if (api_data.status === 'error') {
            let html = `<b>Error: ${api_data.message}</b>`
            this.set_inner_html(html)
        }
        else
        {
            let html     = "<a id='data_reload' href='#reload'>reload</a>"
            let headers  = api_data['headers']
            let rows     = api_data['rows'   ]
            let title    = api_data['title'  ]
            this.table.headers = headers
            this.table.rows    = rows
            html += this.table.html()
            this.set_inner_html(html)
        }
        this.shadowRoot.querySelector("#data_reload" ).addEventListener('click', this.reload_data )
    }

     reload_data = async (event)  => {
        event.preventDefault();
        await this.build()
    }

    mergeUrlWithPageParams(url) {
        // Get the current page's URL parameters
        const pageParams = new URLSearchParams(window.location.search);
        const urlObj = new URL(url, window.location.origin);

        // Merge the parameters from the page's URL with those from the original URL
        pageParams.forEach((value, key) => {
            // Override or add the parameter from the page's URL
            urlObj.searchParams.set(key, value);
        });

        // Return the updated URL as a string
        return urlObj.pathname + urlObj.search;
    }




    async invoke_api_path() {
        let api_path = this.api_path
        // Update the URL and store the result
        api_path = this.mergeUrlWithPageParams(api_path);           // todo: refactor this name
        const method   = 'GET'
        const data     = null
        return await this.api_invoke.invoke_api(api_path, method, data)
    }

    setup() {
        this.api_invoke                = new API__Invoke()
        this.api_invoke.mock_responses = JSON.parse(this.getAttribute('mock_responses'))
    }
}

WebC__API_To_Table.define()