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
    
    function copy_field_value({
      button_id="",
      field_id="",
      first_word=false,
      is_alert=false,
      lower=false,
      message=""
    }) {
      const button = document.getElementById(button_id);
      const field = document.getElementById(field_id);
      if (button) {
        button.addEventListener("click", (event) => {
          event.preventDefault()
          let text = ""
          
          if (first_word) {
            if (field.innerText) {
              text = field.innerText.trim().split(" ")[0]
            } else if (field.value) {
              text = field.value.trim().split(" ")[0]
            }
          } else {
            if (field.innerText) {
              text = field.innerText.trim()
            } else if (field.value) {
              text = field.value.trim()
            }
          }
  
          if (message) {
            let formatted_message = ""
  
            if (message.includes("{field_value}")) {
              formatted_message = message.replace("{field_value}", text)
            }
  
            let shift = ""
            if (message.includes("{shift}")) {
              const now = new Date()
              const hour = now.getHours()
              const morning = hour >= 6 && hour <= 11
              const afternoon = hour >= 12 && hour <= 17
              const night = hour >= 18
              
              if (morning) {
                shift = "bom dia"
              } else if (afternoon) {
                shift = "boa tarde"
              } else if (night) {
                shift = "boa noite"
              }
              
              formatted_message = formatted_message.replace("{shift}", shift)
            }
  
            text = formatted_message
          }
  
          navigator.clipboard.writeText(lower ? text.toLowerCase() : text);
          
          if (is_alert) {
            alert(`Copy content to clipboard: \n\n ${text}`)
          }
        })
      }
    }

    async function asyncForEach(array, callback, ms) {
      const waitFor = (ms) => new Promise(r => setTimeout(r, ms));
      for (let index = 0; index < array.length; index++) {
        await callback(array[index], index, array);
        await waitFor(ms);
      }
    }
    function normalize_name({
      button_id="",
      field_id="",
    }) {
      const button = $(`#${button_id}`);
      const field = $(`#${field_id}`);
      button.on("click", function(event) {
        event.preventDefault();
        const value_field = field.val().split(" ").map(word => {
          return word.charAt(0).toUpperCase() + word.substring(1).toLowerCase();
        }).join(" ")
        field.val(value_field)
      })
    }

    try {
      counterCharacters("id_phone")
      counterCharacters("id_cnpj")
      copy_field_value({
        button_id: "id_name_copy", 
        field_id: "id_name", 
        first_word: true, 
        lower: true,
      })
      copy_field_value({
        button_id: "copy-message", 
        field_id: "rendered-template",
      })
      normalize_name({button_id: "id_name_normalize", field_id: "id_name"})
      copy_field_value({
        button_id: "id_email_copy_business", 
        field_id: "id_email", 
        lower: true,
      })
      copy_field_value({
        button_id: "id_name_greeting", 
        field_id: "id_name", 
        first_word: true, 
        lower: false,
        message: 'Olá {field_value}, {shift}! Tudo bem?'
      })
      copy_field_value({
        button_id: "id_name_copy_business", 
        field_id: "id_businesscontact-0-name", 
      })
    } catch (error) {
      console.log(error);
      
    }
    
    $("#changelist-form").on("submit", async function (event) {
      if ($("[value='open_link']").is(":selected")) {
        event.preventDefault()
        const links = []

        $(".action-select:checked").each(function() {
          const href = $(this).closest('tr').children(".field-instagram_").children("a").attr("href")
          links.push(href)
        })

        await asyncForEach(links, async (link) => {
          window.open(link)
        }, 5000)
      }
    })
    
    $("#changelist-form").on("submit", async function (event) {
      if ($("[value='copy_name']").is(":selected")) {
        event.preventDefault()
        const texts = []

        $(".action-select:checked").each(function() {
          const text = $(this).closest('tr').children(".field-name_").children("a").text()
          texts.push(text)
        })

        navigator.clipboard.writeText(texts.join("\n"));
        alert(`Copy content to clipboard`);
      }
    })
  })(django.jQuery);
});
