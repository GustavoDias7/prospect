window.addEventListener("load", function () {
    (function ($) {
        if ($("#id_background_color").length) {
            $("#id_background_color").after("<div class='preview' id='id_background_color_preview'></div>")
            
            let value = `#${$("#id_background_color").val()}`
            $("#id_background_color_preview").css("background-color", value)

            $("#id_background_color").on("input", function (event) {
                value = `#${event.target.value}`
                $("#id_background_color_preview").css("background-color", value)
            });
        }

        if ($("#id_text_color").length) {
            $("#id_text_color").after("<div class='preview' id='id_text_color_preview'></div>")
            
            let value = `#${$("#id_text_color").val()}`
            $("#id_text_color_preview").css("background-color", value)

            $("#id_text_color").on("input", function (event) {
                value = `#${event.target.value}`
                $("#id_text_color_preview").css("background-color", value)
            });
        }
  
  
    })(django.jQuery);
  });
  