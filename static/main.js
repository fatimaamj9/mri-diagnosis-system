
$(document).ready(function () {
    // Initial state
    $('.image-section').hide();
    $('.loader').hide();
    $('#result').hide();
    $('#btn-predict').hide();

    // Display the selected MRI image
    function readURL(input) {
        if (input.files && input.files[0]) {
            const file = input.files[0];

            if (!file.type.startsWith('image/')) {
                $('#result')
                    .text('Please select a valid image file.')
                    .show();
                $('.image-section').hide();
                return;
            }

            const reader = new FileReader();

            reader.onload = function (e) {
                $('#imagePreview')
                    .css({
                        'background-image': 'url("' + e.target.result + '")',
                        'background-size': 'contain',
                        'background-position': 'center',
                        'background-repeat': 'no-repeat'
                    })
                    .hide()
                    .fadeIn(400);

                $('.image-section').show();
                $('#btn-predict').show().prop('disabled', false);
                $('#result').hide().text('');
                $('.loader').hide();
            };

            reader.onerror = function () {
                $('#result').text('Unable to preview this image. Please try another file.').show();
                $('.image-section').hide();
            };

            reader.readAsDataURL(file);
        }
    }

    // Handle image selection
    $('#imageUpload').on('change', function () {
        $('#result').hide().text('');
        $('.loader').hide();
        $('#btn-predict').hide();

        readURL(this);
    });

    // Predict
    $('#btn-predict').on('click', function (event) {
        event.preventDefault();

        const form = $('#upload-file')[0];

        if (!form || !form.querySelector('input[type="file"]').files.length) {
            $('#result').text('Please select an MRI image first.').show();
            return;
        }

        const form_data = new FormData(form);

        // Show loading state
        $('#btn-predict').prop('disabled', true).hide();
        $('.loader').show();
        $('#result').hide().text('');

        $.ajax({
            type: 'POST',
            url: '/predict',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,

            success: function (data) {
                $('.loader').hide();
                $('#result').text('Result: ' + data).fadeIn(400);
            },

            error: function (xhr) {
                $('.loader').hide();

                const message = xhr.responseJSON && xhr.responseJSON.error
                    ? xhr.responseJSON.error
                    : 'Prediction failed. Please try again.';

                $('#result').text(message).show();
            },

            complete: function () {
                $('#btn-predict').prop('disabled', false).show();
            }
        });
    });
});
