import Web_Component       from '../../webc/core/Web_Component.js'
import WebC__Events_Utils  from '../../webc/utils/WebC__Events_Utils.js'
import WebC__Events_Viewer from '../../webc/utils/WebC__Events_Viewer.js'
import WebC__Target_Div    from "../../webc/utils/WebC__Target_Div.js";

QUnit.module('WebC__Events_Utils', function(hooks) {

    let webc_events_utils 
    let webc_events_viewer 
    let target_div

    hooks.before(async (assert) => { 
        webc_events_utils = WebC__Events_Utils.create()
        target_div         = WebC__Target_Div.add_to_body().build({width:"50%"})
        target_div.append_child(WebC__Events_Viewer)
        webc_events_viewer = $('webc-events-viewer')[0]
    });

    hooks.beforeEach((assert) => {
        webc_events_viewer.events_handled = []
    })
        
 
    QUnit.test('constructor', (assert) => {                
        assert.ok(webc_events_utils            instanceof WebC__Events_Utils )
        assert.ok(WebC__Events_Utils.prototype instanceof Web_Component      );        
        assert.deepEqual(webc_events_utils.channels, ["Web_Component", "WebC__Events_Utils"]) 
    })

    QUnit.test('send_message_to_channel', (assert) => {         
        let channel      = 'Web_Component'
        let message_data = {'answer': 42 }
        webc_events_utils.send_message_to_channel(channel, message_data)        
        assert.ok(true) 
        assert.equal(webc_events_viewer.events_handled.length, 1)         
    })
    
    QUnit.test('send_event', (assert) => {        
        let event_name = 'new_input_message'
        let event_data = {'answer': 42 }
        webc_events_utils.send_event(event_name, event_data)        
        assert.ok(true) 
        assert.equal(webc_events_viewer.events_handled.length, 1)         
    })
})