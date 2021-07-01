// https://sweetalert2.github.io/#examples

function sendToast(category, message) {
    var Toast = Swal.mixin({
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 4000,
        timerProgressBar: true,
        showCloseButton: true,
        didOpen: (toast) => {
            toast.addEventListener('mouseenter', Swal.stopTimer)
            toast.addEventListener('mouseleave', Swal.resumeTimer)
        }
    })
    switch (category.toLowerCase()) {
        case 'error':
            Toast.fire({
                icon: 'error',
                title: message
            })
            break;

        case 'success':
            // swal({ title: title, text: message, type: category, buttonsStyling: false, confirmButtonClass: "btn btn-success" })


            Toast.fire({
                icon: 'success',
                title: message
            })
            break;

        case 'info':
            // swal({ title: title, text: message, type: category, buttonsStyling: false, confirmButtonClass: "btn btn-info" })
            Toast.fire({
                icon: 'info',
                title: message
            })
            break;

        case 'warning':
            // swal({ title: title, text: message, type: category, buttonsStyling: false, confirmButtonClass: "btn btn-warning)" })
            Toast.fire({
                icon: 'warning',
                title: message
            })
            break;

        case 'default':
            // swal({ title: title, text: message, type: category, buttonsStyling: false, confirmButtonClass: "btn btn-default)" })
            break;

        case 'primary':
            // swal({ title: title, text: message, type: category, buttonsStyling: false, confirmButtonClass: "btn btn-primary)" })
            break;

        case 'question':
            Toast.fire({
                icon: 'question',
                title: message
            })
            break;
    }
}