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
    const emojis = ["{👏|😍|🥰|💕|💖|❤️|💙|💜|💗|✨|🌟|⭐|⚡|🔥|🔝|🎉}"];
    const comments = [
      "Ficou {lindo|ótimo|incrível|maravilhoso|fantástico|perfeito|impecável|show|top|massa}!",
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
  })(django.jQuery);
});
