window.addEventListener("load", function () {
    (function ($) {
      function choice_items(array) {
        const copy = [...array];
        for (let i = copy.length - 1; i > 0; i--) {
          const j = Math.floor(Math.random() * (i + 1));
          [copy[i], copy[j]] = [copy[j], copy[i]];
        }
  
        let phrase = copy.slice(0, 1)[0];
        
        const wordsMatches = [...phrase.matchAll(/{([^}]+)}/g)];
        
        if (wordsMatches){
          wordsMatches.forEach(wordsMatch => {
            const options = wordsMatch[1].split('|');
            const randomWord = options[Math.floor(Math.random() * options.length)];
            phrase = phrase.replace(wordsMatch[0], randomWord);
          })
        }
  
        return phrase;
      }
      const emojis = ["{👏|😍|🥰|😊|😄|☺️|🤩|😻|💕|💖|❤️|💙|🩵|💜|💛|🧡|🤍|💓|💗|✨|🌟|⭐|☀️|🔥|🎉}"];
      const comments = [
        "Ficou {lindo|ótimo|incrível|maravilhoso|fantástico|perfeito|impecável}!",
        "Está {lindo|incrível|maravilhoso|fantástico|perfeito|impecável}!",
        "Está uma {lindeza|graça|fofura|beleza}!",
        "Está um {encanto|arraso|capricho}!",
        "Visual {lindo|incrível|maravilhoso|fantástico|perfeito|impecável}!",
        "Simplesmente {lindo|incrível|maravilhoso|fantástico|perfeito|impecável}!",
      ];
      
      $(".copy_comment").on("click", function (e) {
        const selected_comment = choice_items(comments);
        const selected_emoji = choice_items(emojis);
        const final_comment = selected_comment + " " + selected_emoji;
        navigator.clipboard.writeText(final_comment);
        alert(final_comment)
      });

      let counter = {}

      $(`.custom-results-card`).each(function () {
        const id = $(this).prop('id').replace("custom-results-card-", "");
        counter[id] = 0;
      })
      const html = ` | <span class="counter"><span>0</span> selected</span>`
      $(".category-header span").after(html)

      $("input[id^=checkbox-]").on("change", function () {
        const id = $(this).prop('id').replace("checkbox-", "");
        const is_checked = $(`#checkbox-${id}`).is(':checked');
        if (is_checked) counter[id] = $(`#custom-results-card-${id} input.action-select`).length;
        else counter[id] = 0;
        $(`#category-header-${id} .counter span`).text(counter[id]);
        
        $(`#custom-results-card-${id} input.action-select`).each(function () {
            $(this).prop('checked', is_checked);
        })
      })

      $(`.custom-results-card input.action-select`).each(function () {
        $(this).on("change", function () {
          
          const id = $(this).prop('id').replace("action-select-", "").split("-")[0];

          const is_checked = $(this).is(':checked');
          if (is_checked) counter[id] += 1;
          else counter[id] -= 1;
          $(`#category-header-${id} .counter span`).text(counter[id]);
        })
      })
    })(django.jQuery);
  });
  