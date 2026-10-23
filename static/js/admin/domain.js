window.addEventListener("load", function () {
  (function ($) {
    $('#convert_url_to_domain').on('click', function (e) {
      e.preventDefault();
      const url = $('#id_name').val();
      const domain = new URL(url).hostname;
      $('#id_name').val(domain);
    });
  })(django.jQuery);
});
