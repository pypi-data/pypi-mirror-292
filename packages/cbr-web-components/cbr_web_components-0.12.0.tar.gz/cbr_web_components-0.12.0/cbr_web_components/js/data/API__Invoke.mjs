//import Events__Utils from "../events/Events__Utils.mjs";

export default class API__Invoke {
    constructor(channel) {
        //this.events_utils   = new Events__Utils()
        this.channel        = channel || this.random_id('api_invoke_')
        this.mock_responses = false
        //this.connect_event_listeners()
    }

    // connect_event_listeners() {
    //     this.add_event_listener('api_invoke', this.channel, this.on_api_invoke)
    // }
    //
    // add_event_listener(event_name, channel, callback) {
    //     this.events_utils.events_receive.add_event_listener(event_name, channel, callback)
    // }

    // on_api_invoke = (event) => {
    //     let event_data = event.event_data;
    //     let callback   = event.callback;
    //
    //     this.invoke_api(event_data.path, event_data.method, event_data.data)                  // Invoke the API asynchronously
    //         .then (response => { callback( response               ); })                      // Call the callback with the response if the API call is successful
    //         .catch(error    => { callback({ error: error.message }); });                     // Handle any errors that occurred during the API call
    //
    // }

    // Method to invoke the API asynchronously using fetch
    async invoke_api(api_path, method = 'GET', data = null) {
        const url = `${api_path}`;
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
        };

        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }

        try {
            if (this.mock_responses && this.mock_responses[api_path]) {
                return this.mock_responses[api_path]
            }
            const response = await fetch(url, options);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const jsonResponse = await response.json();
            return jsonResponse
        } catch (error) {
            console.error('Error invoking API:', error);
            throw error;
        }
    }


    // utils methods
    random_id(prefix='random') {
        const random_part = Math.random().toString(36).substring(2, 7); // Generate a random string.
        return `${prefix}_${random_part}`;
    }
}