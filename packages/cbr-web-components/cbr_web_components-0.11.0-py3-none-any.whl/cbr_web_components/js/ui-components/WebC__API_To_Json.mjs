import Web_Component  from "../core/Web_Component.mjs";
import API__Invoke    from "../data/API__Invoke.mjs";
import Text_Highlight from "../plugins/Text_Highlight.mjs";


export default class WebC__API_To_Json extends Web_Component {

    constructor() {
        super();
    }

    async connectedCallback() {
        super.connectedCallback()
        this.setup()
        await this.text_highlight.load_css()
        await this.text_highlight.load_highlight_js()
        await this.build()
        this.raise_event('build-complete')
    }

    load_attributes() {
        super.load_attributes()
        this.api_path  = this.getAttribute('api_path')
    }

    disconnectedCallback() {
        super.disconnectedCallback()
    }

    setup() {
        this.offline_mode  = this.getAttribute('offline_mode') === 'true'                   // todo: figure out a better way to do this

        this.api_invoke                = new API__Invoke()
        this.text_highlight            = new Text_Highlight(this)
        this.api_invoke.mock_responses = this.offline_mode === true                         // todo: figure out a better way to do this
    }

    // load_highlight_css() {
    //     fetch('/assets/plugins/highlight/default.min.css')
    //       .then(response => response.text())
    //       .then(css => {
    //         const sheet = new CSSStyleSheet();
    //         sheet.replaceSync(css);
    //         this.shadowRoot.adoptedStyleSheets = [sheet];
    //       });
    // }

    async build() {
        let raw_html = await this.html()
        this.set_inner_html(raw_html)
        window.session_data = this
    }

    async invoke_api_path() {
        const api_path = this.api_path
        const method   = 'GET'
        const data     = null
        return await this.api_invoke.invoke_api(api_path, method, data)
    }

    async html () {

        let api_data = await this.invoke_api_path()
        let data_str = `${JSON.stringify(api_data, null, ' ')}`
        let formatted_html = this.text_highlight.format_text(data_str, 'json')
        let html_code = `<h2>${this.api_path}</h2><pre>${formatted_html}</pre>`
        return html_code
        //this.set_inner_html(html_code)
        // let path = '/api/user/user-session/session-data'
        // let event_data = { method:'GET', 'path':  path, 'data': null}
        // let on_api_response = (data) => {
        //     let raw_html = `${JSON.stringify(data, null, ' ')}`
        //     let formatted_html = this.text_highlight.format_text(raw_html, 'json')
        //     let html_code = `<pre>${formatted_html}</pre>`
        //     this.set_inner_html(html_code)
        // }
        //
        // events_dispatch.send_to_channel(event_name, channel, event_data, null, on_api_response)
        // let html = "<h2>UI Session Data </h2>"
        //return html_code
    }
}

WebC__API_To_Json.define()