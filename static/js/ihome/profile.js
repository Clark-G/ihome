$("#user-name").focus(function(){
    $("#error-msg").hide();
});


$.ajax({
	url:'/api/profile',
	type: 'get',
    success: function(data){
        if (0 == data.errno) {
       		$('#user-name').val(data.username)
            $('#user-avatar').attr('src', data.avatar)
        }
        else{
            window.location.href = 'login.html'
        }
    }   
});


function showSuccessMsg() {
    $('.save_success').fadeIn('fast', function() {
        setTimeout(function(){
            $('.save_success').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

// 上传头像
$('#form-avatar').submit(function(e){
	e.preventDefault();
	$('.image_uploading').fadeIn('fast');
	var options = {
		url: '/api/profile/avatar',
		type: 'POST',
		headers:{
			'X-XSRFTOKEN': getCookie('_xsrf'),
		},
		success:function(data){
			if ('0' == data.errno) {
                showSuccessMsg()
				$('.image_uploading').fadeOut('fast');
				$('#user-avatar').attr('src', data.url);
			}
            else if ('4103' == data.errno) {
                // $('.image_uploading').removeAttr('fadeIn');
                $('.image_uploading').fadeOut('fast');
                alert('请选择图片')
            }
		}
	};
	$(this).ajaxSubmit(options)
})
// 修改用户名
$('#form-name').submit(function(e){
	e.preventDefault();
    var data = {};
    $(this).serializeArray().map(function(x){data[x.name] = x.value;});
    var jsonData = JSON.stringify(data);
    $.ajax({
        url:"/api/profile/name",
        type:"POST",
        data: jsonData,
        contentType: "application/json",
        dataType: "json",
        headers: {
            "X-XSRFTOKEN":getCookie("_xsrf"),
        },

		success:function(data){
			if ('0' == data.errno) {
                showSuccessMsg()
				$('#user-name').html(data.username);
			}
            else if ('4103'== data.errno || '4003' == data.errno) {
                $('#error-msg').html(data.errmsg)
                $('#error-msg').show()
            }
		}
	});
})




