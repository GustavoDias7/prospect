function removeNonNumeric(str) {
    return str.replace(/\D/g, "");
}

function getPhone(value) {
    let phone = "";

    const patterns = [
        /\d{13}/,
        /\d{12}/,
        /\(\d{2}\) \d{5}-\d{4}/,
        /\(\d{2}\) \d{5}\.\d{4}/,
        /\(\d{2}\) 9 \d{4}-\d{4}/,
        /\(\d{2}\) 9 \d{4}\.\d{4}/,
        /\(\d{2}\)9 \d{4}-\d{4}/,
        /\(\d{2}\)9 \d{4}\.\d{4}/,
        /\(\d{2}\)\d{5}-\d{4}/,
        /\(\d{2}\)\d{5}\.\d{4}/,
        /\(\d{2}\)9\.\d{4}-\d{4}/,
        /\(\d{2}\)9\.\d{4}\.\d{4}/,
        /\(\d{2}\) 9\.\d{4}-\d{4}/,
        /\(\d{2}\) 9\.\d{4}\.\d{4}/,
        /\d{7}-\d{4}/,
        /\d{7}\.\d{4}/,
        /\(\d{2}\)\d{9}/,
        /\d{2} \d{5}-\d{4}/,
        /\d{2} \d{5}\.\d{4}/,
        /\d{2} 9 \d{4}-\d{4}/,
        /\d{2} 9 \d{4}\.\d{4}/,
        /\d{2} 9 \d{4} \d{4}/,
        /\d{2} \d{5} \d{4}/,
        /\(\d{2}\) 9\d{4} \d{4}/,
        /\d{2} \d{5} - \d{4}/,
        /\d{2}\.\d{5}-\d{4}/,
        /\d{2}\.\d{5}\.\d{4}/,
        /\d{2}-\d{5}-\d{4}/,
        /\d{2}-\d{5}\.\d{4}/,
        /\d{2}\.\d{9}/,
        /\d{2} 9\d{8}/,
        /\(\d{2}\) \d{9}/,
        /\(\d{2}\)9 \d{8}/,
        /\(\d{2}\) 9 \d{8}/,
        /\d{2}9\d{8}/,
        /\d{5}-\d{4}/,
        /\d{5}\.\d{4}/,
        /\d{5} \d{4}/,
        /\d{9}/,

        /\(\d{2}\) \d{4}-\d{4}/,
        /\(\d{2}\) \d{4}\.\d{4}/,
        /\(\d{2}\)\d{4}-\d{4}/,
        /\(\d{2}\)\d{4}\.\d{4}/,
        /\(\d{2}\)\d{8}/,
        /\d{2}\.\d{4}-\d{4}/,
        /\d{2}\.\d{4}\.\d{4}/,
        /\d{2}-\d{4}-\d{4}/,
        /\d{2}-\d{4}\.\d{4}/,
        /\d{2}\.\d{8}/,
        /\d{8}/,
        /\d{4}-\d{4}/,
        /\d{4}\.\d{4}/
    ];

    for (const pattern of patterns) {
        const match = value.match(pattern);
        if (match) {
            phone = removeNonNumeric(match[0]);
            break;
        }
    }

    return phone;
}

function parsePhone(phoneNumber) {
    if (!phoneNumber) {
        return null;
    }

    const digits = phoneNumber.replace(/\D/g, "");

    if (digits.length < 8) {
        return null;
    }

    let country_code = "55";
    let ddd = "";
    let number = "";

    if ([8, 9].includes(digits.length)) {
        number = digits;

    } else if ([10, 11].includes(digits.length)) {
        ddd = digits.slice(0, 2);
        number = digits.slice(2);

    } else if ([12, 13].includes(digits.length) && digits.startsWith("55")) {
        ddd = digits.slice(2, 4);
        number = digits.slice(4);

    } else {
        return null;
    }

    return {
        country_code,
        ddd,
        number
    };
}

window.addEventListener("load", function () {
  (function ($) {
    $('#full_number_convert').on('click', function (e) {
      e.preventDefault();
      full_number_val = $("#id_full_number").val();
      full_number_val = getPhone(full_number_val);
      full_number_val = parsePhone(full_number_val);
      console.log(full_number_val);
      
      $('#id_ddd').val(full_number_val.ddd);
      $('#id_number').val(full_number_val.number);
    });
  })(django.jQuery);
});
