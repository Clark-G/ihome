function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
    });
    $(".form-login").submit(function(e){
        e.preventDefault();
        mobile = $("#mobile").val();
        passwd = $("#password").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        } 
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        var login_data = {
            mobile:mobile,
            passwd:passwd,
        }
        $.ajax({
            url:'/api/login',
            type:'post',
            data: JSON.stringify(login_data),
            contentType: 'application/json',
            dataType: "json",
            headers: {
                "X-XSRFTOKEN": getCookie("_xsrf"),
            },
            success: function(data){
                if (0 != data.errno) {
                    $("#password-err span").html(data.errmsg); 
                    $("#password-err").show();
                    return;
                }
                else {
                    window.location.href='/'
                    return;
                }            
            }

        });

    });
})