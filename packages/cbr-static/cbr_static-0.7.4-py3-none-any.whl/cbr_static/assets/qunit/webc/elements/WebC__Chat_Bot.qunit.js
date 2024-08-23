import WebC__Chat_Bot   from '../../../webc/elements/WebC__Chat_Bot.js'
import Web_Component    from '../../../webc/core/Web_Component.js'
import WebC__Target_Div from "../../../webc/utils/WebC__Target_Div.js";

QUnit.module('Chatbot_OpenAI', function(hooks) {

    let webc_chat_bot
    let target_div

    hooks.before(async (assert) => {        
        target_div = WebC__Target_Div.add_to_body().build({width: "50%"})        
        target_div.append_child(WebC__Chat_Bot)
        webc_chat_bot = $('webc-chat-bot')[0]
    });
  

    QUnit.test('constructor', (assert) => {                           
        assert.ok(WebC__Chat_Bot.prototype instanceof Web_Component);
    })

    QUnit.test('chect_message_workflows', (assert)=>{
        assert.ok(true)
        assert.equal(webc_chat_bot.bot_name, 'ChatBot')
    })
})