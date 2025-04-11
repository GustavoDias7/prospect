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
        counterCharacters("id_phrase")
        
        function copy_name({button_id="", field_id="", first_name=false, is_alert=false}) {
          const field = document.querySelector(`#${field_id}`);
          const button = document.querySelector(`#${button_id}`);
          button.addEventListener("click", (event) => {
            event.preventDefault()
            let text = ""
            if (first_name) {
              text = field.innerText.trim().split(" ")[0]
            } else {
              text = field.innerText.trim()
            }
            navigator.clipboard.writeText(text);
            if (is_alert) {
              alert(`Copy content to clipboard: \n\n ${text}`)
            }
          })
        }
        copy_name({button_id: "copy-comment", field_id: "comment", is_alert: true})
    })(django.jQuery);
});
  