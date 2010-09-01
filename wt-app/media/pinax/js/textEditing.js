var editableClass = 'editable';
var editableAreaClass = 'editable-area';
var allEditableClasses = '.' + editableClass + ', .' + editableAreaClass;

var activeEditing = 'active-inline';

function removeElementById(id) {
    id = '#' + id;
    $(id).remove();
}

function triggerBlur(id) {
    id = '#' + id;
    $(id).trigger('blur');
}

// This code is based on the book, "jQuery: Novice to Ninja", ISBN: 9780980576856.
$(allEditableClasses).click(function(e) {
    // Start the inline editing
    // alert("Object ID " + $(this).attr('id') + " can now be edited!");
    var $editable = $(this);
    var id = $($editable).attr('id');
    
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
    // TODO: Is there a way to not have to reference the /site_media/static directory directly?
    // We should be able to use {{ STATIC_URL }} instead. How do we create a Django Template for js?
    deleteButton = '<br/><input type="image" id="' + id + 
        '_delete" src="/site_media/static/pinax/images/icons/delete.png" ' +  
        'class="deleteButton" ' + 
        'title="Invalid Sentence (Delete)" />';
        
    // Add an "accept" button
    acceptButton = '<input type="image" id="' + id + 
        '_delete" src="/site_media/static/pinax/images/icons/accept.png" ' +  
        'class="acceptButton" ' + 
        'title="Accept Changes" />';
        
    // Replace the target with the form element
    $(editElement)
        .val(contents)
        .appendTo($editable)
        .focus();
        //.blur(function(e) {
            //// Stop editing if the form is deselected.
            //$editable.trigger('blur');
        //});
        
    $(deleteButton).appendTo($editable);
    $(acceptButton).appendTo($editable);
        
    // Remove the span if the delete button is clicked.
    $('.deleteButton').click(function() {
        $editable.remove();
    });
    
    // Accept the changes if the accept button is clicked.
    $('.acceptButton').click(function() {
        $editable.trigger('blur');
    });
//});
}).blur(function(e) {
    // End the inline editing
    var $editable = $(this);
    
    var contents = $editable.find(':first-child:input').val();
    $editable.find(':not(:first-child)').remove();
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

