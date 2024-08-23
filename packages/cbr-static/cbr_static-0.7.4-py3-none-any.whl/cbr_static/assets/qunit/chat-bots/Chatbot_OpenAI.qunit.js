import Chatbot_OpenAI   from '../../webc/chat-bots/Chatbot_OpenAI.js'
import Web_Component    from '../../webc/core/Web_Component.js'
import WebC__Target_Div from "../../webc/utils/WebC__Target_Div.js";

QUnit.module('Chatbot_OpenAI', function(hooks) {

    let chatbot_openai
    let target_div

    hooks.before(async (assert) => {
        chatbot_openai = Chatbot_OpenAI
        target_div = WebC__Target_Div.add_to_body().build({width: "50%"})        
        target_div.append_child(chatbot_openai)
        //await webc_events_viewer.load_datatables_css() 
    });
 

    QUnit.test('constructor', (assert) => {
        assert.ok(true)
        //assert.ok(chatbot_openai instanceof Chatbot_OpenAI)
        //assert.ok(Chatbot_OpenAI.prototype instanceof Web_Component);
    })
})