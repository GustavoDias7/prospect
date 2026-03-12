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
    
  })(django.jQuery);
});
