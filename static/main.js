const imageForm = document.getElementById('image-form')
const input = document.getElementById('id_file')
const csrf = document.getElementsByName('csrfmiddlewaretoken')

$(function(){
    $('#id_file').on('change', function() {
      var file_name = $(this).val();
      if(file_name.length > 0) {
        addJcrop(this);
      }
   });
      
    var addJcrop = function(input) {
      if ($('#image_prev').data('Jcrop')) {
        $('#image_prev').data('Jcrop').destroy();
      }
      
      if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
          $("#image_prev").attr('src', e.target.result);
          var box_width = $('#image_prev_container').width();
          $('#image_prev').Jcrop({
            onSelect: getCoordinates,
            onChange: getCoordinates
          });
        }
        reader.readAsDataURL(input.files[0]);
      }


      $('#btnCrop').click(function () {
          const x1 = +$('#x').val();
          const y1 = +$('#y').val();
          const width = +$('#w').val();
          const height = +$('#h').val();
          const canvas = $("#canvas")[0];
          var context = canvas.getContext('2d');
          var img = new Image();
          img.onload = function () {
              canvas.height = height;
              canvas.width = width;
              context.drawImage(img, x1, y1, width, height, 0, 0, width, height);
              const imageForm = document.getElementById('image-form')
              canvas.toBlob((blob) => {
                const formData = new FormData();
                formData.append('csrfmiddlewaretoken', csrf[0].value)
                formData.append('upload', blob, 'cropped.png');
                $.ajax({
                    type:'POST',
                    url: imageForm.action,
                    enctype: 'multipart/form-data',
                    data: formData,
                    success: function(response){
                        console.log('success', response)
                    },
                    error: function(error){
                        console.log('error', error)
                    },
                    cache: false,
                    contentType: false,
                    processData: false,
              });
              }, 'image/png');
              
          };
          img.src = $('#image_prev').attr("src");
          $('#image_prev_container').hide();
      });
    };

    var getCoordinates = function(c){
      $('#x').val(c.x);
      $('#y').val(c.y);
      $('#w').val(c.w);
      $('#h').val(c.h);
      $('#btnCrop').show();
    };
  });