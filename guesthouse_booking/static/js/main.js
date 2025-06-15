// static/js/main.js
document.addEventListener('DOMContentLoaded', function () {
    $('#reviewModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget); // Button that triggered the modal
        var guestName = "{{ user.username }}";
        var roomNumber = ""; // Get room number dynamically if needed
        
        var modal = $(this);
        modal.find('#guest_name').val(guestName);
        modal.find('#room').val(roomNumber);
        modal.find('#review_date').val(new Date().toISOString().split('T')[0]);
    });
});
