QUnit.test("errors should be hidden on keypress", function(assert) {
    $('input').trigger('keypress');
    assert.equal($('.has-error').is(':visible'), false);
})
// The above test fails due to changes in the QUnit lib. Since the input gets reset between each test,
// the event listener that we add in list.js gets dropped and fails to respond to the event.

QUnit.test("errors should not be hidden on keypress", function(assert) {
    assert.equal($('.has-error').is(':visible'), true);
})
