
import WebC_Chat_Bot from "../elements/WebC__Chat_Bot.js";

export default class Chatbot_OpenAI extends WebC_Chat_Bot{

    constructor() {
        super()

        this.provider           = this.getAttribute('provider'          )
        this.platform           = this.getAttribute('platform'          )
        this.model              = this.getAttribute('model'             )
        this.openai_model       = this.getAttribute('model'             ) || 'gpt-4o'
        this.openai_seed        = this.getAttribute('seed'              ) || 42
        this.openai_temperature = this.getAttribute('temperature'       ) || 0.0
        this.max_tokens         = this.getAttribute('max_tokens'        ) || 2048
        this.initial_prompt     = this.getAttribute('initial_prompt'    ) || ''
        this.initial_message    = this.getAttribute('initial_message'   ) || null
        this.url                = this.getAttribute('url'               ) || '/api/llms/chat/completion';
        this.bot_name           = this.getAttribute('name'              ) || 'OpenAI ChatBot'
        this.target             = this.getAttribute('target'            ) || null
        this.chat_thread_id     = this.random_uuid()
        this.stop_fetch         = false
        this.system_prompt      = this.getAttribute('system_prompt' )
        //window.chatbot = this
    }

    connectedCallback() {
        this.build()
    }

    build() {
        super.build()
        //window.chatbot_openai = this
        this.add_event_listeners()
        this.apply_ui_tweaks()

    }
    add_event_listeners() {
        this.addEventListener('messageSent', async (event) => {
            if (this.target && this.target === event.detail.target) {
                console.log(`[add_event_listeners]--->> NOT Current target ${this.target} != ${event.detail.target}<----`)
                return
            }
            const message     = event.detail.message
            const user_prompt = message.user_prompt
            const images      = message.images

            await this.post_openai_prompt_with_stream(user_prompt, images)
        });

        window.addEventListener('stop_stream', async (event) => {
            if (event.detail?.channel === this.channel) {
                this.stop_fetch = true
            }
        })
        window.addEventListener('select_model', async (event) => {
            this.platform = event.detail?.platform
            this.provider = event.detail?.provider
            this.model    = event.detail?.model
        })

    }

    apply_ui_tweaks () {
        this.input.value   = this.initial_prompt
        if (this.initial_message !== null) {
            this.messages.add_message_initial(this.initial_message)
        }

        if (this.system_prompt !== null) {
            this.messages.add_message_system(this.system_prompt)
        }
        //this.shadowRoot.innerHTML += `<hr/><a style="padding:0px" href="chat/view/${this.chat_thread_id}">saved chat</a>`
    }

    all_system_prompts() {
        if (this.system_prompt) {
            return [this.system_prompt]
        }

        const dom_system_prompt = document.querySelector('#system_prompt')
        if (dom_system_prompt !== null) {
            const system_prompt = dom_system_prompt.innerHTML
            window.dom_system_prompt = dom_system_prompt
            return [system_prompt]
        }
        return []
    }
    async post_openai_prompt_with_stream(user_prompt, images) {

        var storedData = localStorage.getItem('user_data');
        var user_data = storedData ? JSON.parse(storedData) : {};
        user_data['selected_platform'] = this.platform || $('#platform-select').val();               // todo: refactor the retrieval of this value from outside this js class
        user_data['selected_provider'] = this.provider || $('#provider-select').val();               //       since this highly couples the component to other parts of the page
        user_data['selected_model'   ] = this.model    || $('#model-select'   ).val();
        const histories = this.calculate_histories()
        const data = { chat_thread_id   : this.chat_thread_id             ,
                            model            : this.openai_model          ,
                            temperature      : this.openai_temperature    ,
                            seed             : this.openai_seed           ,
                            max_tokens       : this.max_tokens            ,
                            user_prompt      : user_prompt                ,
                            images           : images                     ,
                            system_prompts   : this.all_system_prompts()  ,
                            histories        : histories                  ,
                            user_data        : user_data                  }

        const event = new CustomEvent('promptSent', {
            bubbles : true    ,
            composed: true    ,
            detail  : { data } });
        let detail__stream_start = {'channel':this.channel, 'platform': this.platform, 'provider': this.provider, 'model': this.model }

        this.dispatchEvent(event);
        this.messages.messages_div_scroll_to_end()

        this.dispatchEvent(new CustomEvent('streamStart', { detail   : detail__stream_start,
                                                            bubbles : true                 ,
                                                            composed: true                 }));
        await this.fetch_data_from_server(data)
    }

    async fetch_data_from_server(data) {
        let detail__stream_data  = {'channel':this.channel, 'data': null}
        this.stop_fetch = false
        try {
          const response = await fetch(this.url, {
            method : 'POST',
            headers: { 'Accept': 'application/json',
                       'Content-Type': 'application/json' },
            body: JSON.stringify(data)
          });

          if (!response.ok) {                                           // todo : refator to raise event method

              detail__stream_data.data = `HTTP error! Status: ${response.status}`
              this.dispatchEvent(new CustomEvent('streamData', {
                bubbles : true    ,                         // allows the event to bubble up through the DOM
                composed: true    ,                         // allows the event to cross shadow DOM boundaries
                detail: detail__stream_data }));                          // Emit an event with the chunk
            //throw new Error(`HTTP error! Status: ${response.status}`);
          }


          const reader = response.body.getReader();                     // Handling the stream
          const decoder = new TextDecoder('utf-8');

          this.messages.messages_div_scroll_to_end()



          const processStream = async ({done, value}) => {
              if (this.stop_fetch) {
                  detail__stream_data.data = '   ...(stopped)...'
                  this.dispatchEvent(new CustomEvent('streamData', {bubbles : true    , composed: true    ,
                                                                    detail: detail__stream_data }));
                  done = true
              }
            if (done) {
              this.dispatchEvent(new CustomEvent('streamComplete', {
                    bubbles : true    ,                         // allows the event to bubble up through the DOM
                    composed: true    ,                         // allows the event to cross shadow DOM boundaries
              }));
              this.messages.messages_div_scroll_to_end()
              return;
            }

            const chunk = decoder.decode(value, {stream: true});                            // Decode and process chunk

            let fixed_chunk = chunk.replace(/\n\n/g, '{{DOUBLE_NEWLINE}}');  // todo: remove the need for this
            fixed_chunk = fixed_chunk.replace(/\n/g, '');
            fixed_chunk = fixed_chunk.replace(/{{DOUBLE_NEWLINE}}/g, '\n\n');

            //const fixed_chunk = chunk.replace(/\n$/, '');
            detail__stream_data.data = fixed_chunk
            this.dispatchEvent(new CustomEvent('streamData', {
                bubbles : true    ,                         // allows the event to bubble up through the DOM
                composed: true    ,                         // allows the event to cross shadow DOM boundaries
                detail: detail__stream_data }));                          // Emit an event with the chunk

            reader.read().then(processStream);                                              // Read the next chunk
          };

          reader.read().then(processStream);

        } catch (error) {                                                   // todo : refactor to raise event method
          detail__stream_data.data = `streamError: ${error.message}`
          this.dispatchEvent(new CustomEvent('streamData', {
            bubbles : true    ,                         // allows the event to bubble up through the DOM
            composed: true    ,                         // allows the event to cross shadow DOM boundaries
            detail: detail__stream_data }));                          // Emit an event with the chunk
          this.events.dispatchEvent(new CustomEvent('streamError', { detail: error.message }));
        }
    }


    // todo refactor this code to use the Data__Chat_Bot class which has proper support for storing messages
    calculate_histories() {
        const histories = []
        let question = null
        let answer   = null
        this.messages.childNodes.forEach(message => {
            if (message.message_raw && message.type !=='initial') {
                if (question === null) {
                    question = message.message_raw
                } else if (answer === null) {
                    answer = message.message_raw
                    histories.push({question, answer})
                    question = answer = null
                }
            }

        })
        return histories
    }
    random_uuid() {
        return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
            (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
        );
    }
}

Chatbot_OpenAI.define()