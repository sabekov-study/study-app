/*
 * Send CSRF token on all AJAX request. See Django's documentation
 * on CSRF protection: https://docs.djangoproject.com/en/1.10/ref/csrf/
 */

(function() {
// using jQuery
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
})();

function extendClass(target, base) {
    for (var p in base) {
        if (base.hasOwnProperty(p)) {
            target[p] = base[p];
        }
    }

    function TargetPrototype() {
        this.constructor = target;
    }

    if (base === null) {
        target.prototype = Object.create(base);
    } else {
        TargetPrototype.prototype = base.prototype;
        target.prototype = new TargetPrototype();
    }
}

