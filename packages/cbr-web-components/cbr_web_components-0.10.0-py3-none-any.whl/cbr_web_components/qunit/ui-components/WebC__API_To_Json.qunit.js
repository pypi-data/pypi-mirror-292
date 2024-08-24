
import Web_Component      from "../../js/core/Web_Component.mjs";
import WebC__API_To_Json  from "../../js/ui-components/WebC__API_To_Json.mjs";
import WebC__Target_Div   from "../../js/utils/WebC__Target_Div.mjs";
import API__Invoke        from "../../js/data/API__Invoke.mjs";
import Text_Highlight     from "../../js/plugins/Text_Highlight.mjs";


QUnit.module('WebC__API_To_Json', function(hooks) {
    let target_div
    let webc__api_to_json
    let mockResponse
    //let skip_tests;

    hooks.beforeEach(async (assert) =>{
        //skip_tests   = false//(typeof wallaby === 'undefined')                               // todo: figure out why these tests don't work in KarmaJS. There was a problem fetching the css (which weirdly worked sometimes)
        mockResponse = { version: 'v0.6.8' };

        // if (skip_tests) {
        //     assert.ok(1);
        //     return
        // }

        target_div              = WebC__Target_Div.add_to_body().build()
        let attributes          = {offline_mode: 'true'}
        webc__api_to_json       = await target_div.append_child(WebC__API_To_Json, attributes)
        await webc__api_to_json.wait_for_event('build-complete')

        // await new Promise((resolve, reject) => {
        //      const timeout = setTimeout(() => {
        //         reject(new Error('css-loaded event did not fire within the expected time.'));
        //         }, 100);
        //      webc__api_to_json.addEventListener('css-loaded', () => {
        //         clearTimeout(timeout);                                      // Clear the timeout if the event fires
        //         resolve();                                                  // Resolve the promise if the event fires
        //      }, { once: true });
        // });
    })

    hooks.afterEach(() => {
        //if (skip_tests) { return }
        webc__api_to_json.remove()
        target_div.remove()
    })

    QUnit.test('.constructor', (assert) => {
        assert.deepEqual(WebC__API_To_Json.name           , 'WebC__API_To_Json'     )
        assert.ok       (WebC__API_To_Json.prototype      instanceof Web_Component  )
        assert.ok       (webc__api_to_json                instanceof Web_Component  )
        assert.ok       (webc__api_to_json                instanceof HTMLElement    )
        assert.ok       (webc__api_to_json.api_invoke     instanceof API__Invoke    )
        assert.ok       (webc__api_to_json.text_highlight instanceof Text_Highlight )
        assert.ok       (webc__api_to_json.text_highlight.css_loaded     )
        assert.ok       (webc__api_to_json.text_highlight.css_code !== '')
        assert.deepEqual(webc__api_to_json.getAttributeNames(), ['offline_mode'])
        assert.ok       (webc__api_to_json.api_invoke.mock_responses)
        assert.deepEqual(typeof(hljs), 'object')
        assert.deepEqual(hljs.versionString, '11.9.0')
        // todo: figure out why the tests below fail
        //assert.equal(Object.getPrototypeOf(ui_session_data), UI__Session_Data.prototype, 'The prototype of ui_session_data should be UI__Session_Data.prototype');
        //assert.ok(ui_session_data instanceof UI__Session_Data, 'ui_session_data should be an instance of UI__Session_Data');
    })

    QUnit.test('.html', (assert) => {
        //if (skip_tests) { return }
        let expected_html = '<pre><span class="hljs-punctuation">{</span>\n <span class="hljs-attr">"version"</span><span class="hljs-punctuation">:</span> <span class="hljs-string">"v0.6.8"</span>\n<span class="hljs-punctuation">}</span></pre>'
        assert.deepEqual(webc__api_to_json.inner_html(), expected_html)

        //console.log(ui_session_data.inner_html())
        //console.log(expected_html)
        //console.log(ui_session_data.inner_html() === expected_html)
        //assert.ok(1)
    })
})