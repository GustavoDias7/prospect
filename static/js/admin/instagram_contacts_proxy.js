window.addEventListener("load", function () {
  (function ($) {
    function choice_items(array, n) {
      if (n > array.length) {
        throw new Error("n cannot be greater than the array length.");
      }
    
      const copy = [...array];
      for (let i = copy.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [copy[i], copy[j]] = [copy[j], copy[i]];
      }
    
      return copy.slice(0, n);
    }
    const comments = [];
    
    $(".copy_comment").on("click", function (e) {
      const selected = choice_items(comments, 1)[0];
      
      navigator.clipboard.writeText(selected);
      alert(selected)
    });
  })(django.jQuery);
});
