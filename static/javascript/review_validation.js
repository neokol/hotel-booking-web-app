document.addEventListener('DOMContentLoaded', function () {
    var form = document.querySelector('#reviewForm');
    var ratingField = form.querySelector('select[name="rating"]');
    var commentField = form.querySelector('textarea[name="comment"]');

    form.addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent form submission

        // Remove previous validation error highlighting
        ratingField.classList.remove('error');
        commentField.classList.remove('error');

        // Perform validation
        var rating = ratingField.value;
        var comment = commentField.value;

        if (rating === '') {
            ratingField.classList.add('error');
            return;
        }

        if (comment.trim() === '') {
            commentField.classList.add('error');
            return;
        }

        // If validation passes, you can submit the form
        form.submit();
    });
});
