function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

// $(function(){
    $.ajax({
    	url:'api/profile/auth',
    	type: 'get',
        dataType: 'json',
        success: function(data){
            if ('4101' == data.errno) {
                window.location.href = 'login.html';                
            }
            else if (0 == data.errno) {
                if (data.real_name && data.id_card) {
                    $('#real-name').val(data.real_name)
                    $('#id-card').val(data.id_card)
                    $('#real-name').attr({disabled:true})
                    $('#id-card').attr({disabled:true})
                    $('#save').css('display', 'None')
                }
            }
        }

    });
    // 提交认证信息
    $('#form-auth').submit(function(e){
        e.preventDefault();
        var data = {};
        $(this).serializeArray().map(function(x){data[x.name] = x.value;});
        var jsonData = JSON.stringify(data);
        $.ajax({
            url:"/api/profile/auth",
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
                    $('#real-name').attr({placeholder: data.real_name, disabled:true})
                    $('#id-card').attr({placeholder: data.id_card, disabled:true})
                    $('#save').css('display', 'None')
                }
                else if ('4103' == data.errno){
                    $('.error-msg').show()
                }
                // else('')
            }
        });
    });
// })
$("#real-name").focus(function(){
    $(".error-msg").hide();
});
$("#id-card").focus(function(){
    $(".error-msg").hide();
});