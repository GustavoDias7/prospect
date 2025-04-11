window.addEventListener("load", function () {
  (function ($) {
    
    function counterCharacters(fieldId) {
      if ($(`#${fieldId}`).length) {
        html = `<div class='help' id='${fieldId}-counter'>Characters: <span></span> of <span></span></div>`
        $(`#${fieldId}`).parent().after(html)
        
        $(`#${fieldId}-counter span:first-of-type`).text($(`#${fieldId}`).val().length)
        $(`#${fieldId}-counter span:last-of-type`).text($(`#${fieldId}`).attr("maxlength"))

        $(`#${fieldId}`).on("input", function (event) {
          $(`#${fieldId}-counter span:first-of-type`).text(`${event.target.value.length}`)
        });
      }
  }
  counterCharacters("id_message")
    
  })(django.jQuery);
});
