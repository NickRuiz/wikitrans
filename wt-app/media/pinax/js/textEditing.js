var highlightClass = 'highlight';
var highlightableClass = '.highlightable';

var editableClass = 'editable';
var editableAreaClass = 'editable-area';
var allEditableClasses = '.' + editableClass + ', .' + editableAreaClass;

var activeEditing = 'active-inline';

// Toggle highlighting for all highlightable classes
$(highlightableClass).hover(function() {
    $(this).addClass(highlightClass);
}, function() {
    $(this).removeClass(highlightClass);
});

// This code is based on the book, "jQuery: Novice to Ninja", ISBN: 9780980576856.
$(allEditableClasses).click(function(e) {
    // Start the inline editing
    // alert("Object ID " + $(this).attr('id') + " can now be edited!");
    var $editable = $(this);
    
    // Don't create a edit field if one already exists.
    if ($editable.hasClass(activeEditing)) {
        return;
    }
    
    // Get the text contents
    var contents = $.trim($editable.html());
    $editable
        .addClass(activeEditing)
        .empty();
        
    // Determine what kind of form element we need
    var editElement = $editable.hasClass(editableClass) ?
            '<input type="text"/>' : '<textarea></textarea>'; 
            
    // Add a delete button
    // editElement += '<img src="/media/images/icons/delete.png" />';
        
    // Replace the target with the form element
    $(editElement)
        .val(contents)
        .appendTo($editable)
        .focus()
        .blur(function(e) {
            // Stop editing if the form is deselected.
            $editable.trigger('blur');
        });
}).blur(function(e) {
    // End the inline editing
    var $editable = $(this);
    
    var contents = $editable.find(':first-child:input').val();
    $editable
        .contents()
        .replaceWith('<em class="ajax">Saving...</em>');
        
    // Post the new value to the server, along with its ID
    // TODO: I don't think I want to post the changes to the server yet. I'm leaving the code here, just in case.
    /*
    $.post('save',      // We probably have to specify our own save location
        {id: $editable.attr('id'), value: contents},
        function(data) {
            // Replace the contents
            $editable
                .removeClass(activeEditing)
                .contents()
                .replaceWith(contents);
        });
    */
    
    // Replace the contents
    $editable
        .removeClass(activeEditing) 
        .contents()
        .replaceWith(contents);
});

