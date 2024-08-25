import API_Invoke    from '../../js/data/API__Invoke.mjs';
import Events__Utils from "../../js/events/Events__Utils.mjs";

QUnit.module('API_Invoke', function(hooks) {

    let api_invoke;
    let event_utils
    let events_dispatch
    let events_receive
    let channel
    let mockResponse
    let originalFetch;
    hooks.beforeEach(() =>{
        channel         = 'api_invoke__qunit'
        api_invoke      = new API_Invoke(channel)
        event_utils     = new Events__Utils()
        events_dispatch = event_utils.events_dispatch
        events_receive  = event_utils.events_receive
        mockResponse    = { version: 'v0.6.8' };

        api_invoke.mock_responses = true

        // originalFetch   = globalThis.fetch
        //
        // globalThis.fetch = async (url, options) => {
        //     return {
        //         ok: true,
        //         json: async () => mockResponse,
        //         status: 200,
        //     };
        // };
    })

    // hooks.afterEach(() => {
    //      globalThis.fetch = originalFetch;
    // })

    QUnit.test('.constructor()', (assert)=> {
        assert.ok       (api_invoke              instanceof API_Invoke)
        assert.ok       (api_invoke.events_utils instanceof Events__Utils)
        assert.deepEqual(api_invoke.channel , channel)
    })

    QUnit.test('.on_api_invoke()', async (assert)=> {
        let event_name = 'api_invoke'
        let event_data = { method:'GET', 'path':  '/config/version', 'data': null}

        let on_api_response = (data) =>{
            assert.deepEqual(data, mockResponse)
        }
        events_dispatch.send_to_channel(event_name, channel, event_data, null, on_api_response)
    })

    QUnit.test('.invoke_api()', async (assert)=> {
        const response = await api_invoke.invoke_api( '/config/version', 'GET');
        assert.deepEqual(response, mockResponse , 'The response should match the expected JSON object');
    })
})