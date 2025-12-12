window.addEventListener("load", function () {
  (function ($) {
    function counterCharacters(fieldId) {
      if ($(`#${fieldId}`).length) {
        html = `<div class='help' id='${fieldId}-counter'>Characters: <span></span> of <span></span></div>`;
        $(`#${fieldId}`).parent().after(html);

        $(`#${fieldId}-counter span:first-of-type`).text(
          $(`#${fieldId}`).val().length
        );
        $(`#${fieldId}-counter span:last-of-type`).text(
          $(`#${fieldId}`).attr("maxlength")
        );

        $(`#${fieldId}`).on("input", function (event) {
          $(`#${fieldId}-counter span:first-of-type`).text(
            `${event.target.value.length}`
          );
        });
      }
    }
    async function asyncForEach(array, callback, ms) {
      const waitFor = (ms) => new Promise((r) => setTimeout(r, ms));
      for (let index = 0; index < array.length; index++) {
        await callback(array[index], index, array);
        await waitFor(ms);
      }
    }
    
    function copy_field_value({
      button_id = "",
      field_id = "",
      first_word = false,
      is_alert = false,
      lower = false,
      message = "",
    }) {
      const button = document.getElementById(button_id);
      const field = document.getElementById(field_id);
      if (button) {
        button.addEventListener("click", (event) => {
          event.preventDefault();
          let text = "";

          if (first_word) {
            if (field.innerText) {
              text = field.innerText.trim().split(" ")[0];
            } else if (field.value) {
              text = field.value.trim().split(" ")[0];
            }
          } else {
            if (field.innerText) {
              text = field.innerText.trim();
            } else if (field.value) {
              text = field.value.trim();
            }
          }

          if (message) {
            let formatted_message = "";

            if (message.includes("{field_value}")) {
              formatted_message = message.replace("{field_value}", text);
            }

            let shift = "";
            if (message.includes("{shift}")) {
              const now = new Date();
              const hour = now.getHours();
              const morning = hour >= 6 && hour <= 11;
              const afternoon = hour >= 12 && hour <= 17;
              const night = hour >= 18;

              if (morning) {
                shift = "bom dia";
              } else if (afternoon) {
                shift = "boa tarde";
              } else if (night) {
                shift = "boa noite";
              }

              formatted_message = formatted_message.replace("{shift}", shift);
            }

            text = formatted_message;
          }

          navigator.clipboard.writeText(lower ? text.toLowerCase() : text);

          if (is_alert) {
            alert(`Copy content to clipboard: \n\n ${text}`);
          }
        });
      }
    }
    function normalize_name({ button_id = "", field_id = "" }) {
      const button = $(`#${button_id}`);
      const field = $(`#${field_id}`);
      button.on("click", function (event) {
        event.preventDefault();
        const value_field = field
          .val()
          .split(" ")
          .map((word, index) => {
            if (index !== 0 && word.length <= 2) return word.toLowerCase();
            return (
              word.charAt(0).toUpperCase() + word.substring(1).toLowerCase()
            );
          })
          .join(" ");
        field.val(value_field);
      });
    }

    copy_field_value({
      button_id: "copy-message",
      field_id: "rendered-template",
    });

    copy_field_value({
      button_id: "id_name_copy",
      field_id: "id_name",
    });
    counterCharacters("id_name");
    counterCharacters("id_cellphone");
    counterCharacters("id_telephone");
    counterCharacters("id_cnpj");
    counterCharacters("id_address");
    counterCharacters("id_business_ref-0-observation");
    normalize_name({ button_id: "id_name_normalize", field_id: "id_name" });
    
    $("#changelist-form").on("submit", async function (event) {
      if ($("[value='open_link']").is(":selected")) {
        event.preventDefault();
        const links = [];

        $(".action-select:checked").each(function () {
          const href = $(this)
            .closest("tr")
            .children(".field-instagram")
            .children("a")
            .attr("href");
          links.push(href);
        });

        await asyncForEach(
          links,
          async (link) => {
            window.open(link);
          },
          5000
        );
      }
    });

    $('#open-staff-member').on('click', function (e) {
      e.preventDefault();
      const selectedOptions = $("#id_staff_members_to, #id_staff_members_from").find('option:selected');
      selectedOptions.each(function () {
        window.open(`/admin/core/staffmember/${$(this).val()}/change/`, '_blank');
      });
    });

    const images = document.querySelectorAll(".business_contact_image");
    images.forEach((image) => {
      image.addEventListener("click", (e) => {
        const canvas = document.createElement("canvas");
        canvas.width = image.naturalWidth;
        canvas.height = image.naturalHeight;
        const context = canvas.getContext("2d");
        context.drawImage(image, 0, 0);
        canvas.toBlob((blob) => {
          navigator.clipboard
            .write([
              new ClipboardItem({
                [blob.type]: blob,
              }),
            ])
            .then(() => {
              // alert(`Copy image to clipboard.`)
            });
        });
      });
    });
    
    if ($("#id_custom_color").length) {
      $("#id_custom_color").after("<div class='preview' id='id_custom_color_preview'></div>");
      
      $("#id_custom_color_preview").css("border", "1px solid #353535");
      $("#id_custom_color_preview").css("margin-left", "4px");
      $("#id_custom_color_preview").css("width", "27.5px");
      $("#id_custom_color_preview").css("height", "27.5px");
      $("#id_custom_color_preview").css("background-color", $("#id_custom_color").val());

      $("#id_custom_color").on("input", function (event) {
          value = `${event.target.value}`;
          $("#id_custom_color_preview").css("background-color", value);
      });
    }
    
    if ($("#id_primary_color").length) {
      $("#id_primary_color").after("<div class='preview' id='id_primary_color_preview'></div>");
      
      $("#id_primary_color_preview").css("border", "1px solid #353535");
      $("#id_primary_color_preview").css("margin-left", "4px");
      $("#id_primary_color_preview").css("width", "27.5px");
      $("#id_primary_color_preview").css("height", "27.5px");
      $("#id_primary_color_preview").css("background-color", $("#id_primary_color").val());

      $("#id_primary_color").on("input", function (event) {
          value = `${event.target.value}`;
          $("#id_primary_color_preview").css("background-color", value);
      });
    }
    
    if ($("#id_secondary_color").length) {
      $("#id_secondary_color").after("<div class='preview' id='id_secondary_color_preview'></div>");
      
      $("#id_secondary_color_preview").css("border", "1px solid #353535");
      $("#id_secondary_color_preview").css("margin-left", "4px");
      $("#id_secondary_color_preview").css("width", "27.5px");
      $("#id_secondary_color_preview").css("height", "27.5px");
      $("#id_secondary_color_preview").css("background-color", $("#id_secondary_color").val());

      $("#id_secondary_color").on("input", function (event) {
          value = `${event.target.value}`;
          $("#id_secondary_color_preview").css("background-color", value);
      });
    }
  })(django.jQuery);
});
