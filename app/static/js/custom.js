
$(document).ready(function() {
  $('.full-height').css('height', $(window).height());
  
  $('.content-wrapper').css('min-height', ($(window).height()-200));


  $('.delete').on('click', function(e) {
    e.preventDefault();
    var currentElement = $(this);

    swal({
      title: "Are you sure?",
      text: "You will destroy this item. Proceed anyway?",
      type: "warning",
      buttons: true,
      dangerMode: true,
      confirmButtonColor: "#DD6B55",
      confirmButtonClass: 'btn btn-danger',
      cancelButtonClass: 'btn btn-light',
      confirmButtonText: "Yes, delete!"
    }).then((willDelete) => {
      if (willDelete) {
        window.location.href = currentElement.attr('href');
      } else {
        console.log("not delete");
      }
    });
  });

});

