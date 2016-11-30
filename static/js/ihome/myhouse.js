$(document).ready(function(){
    $.ajax({
        url:'/api/profile/auth',
        type: 'get',
        success: function(data){
            if ('4101' == data.errno) {
                window.location.href = "/login.html";
            }
            else if ('0' == data.errno) {
                if (data.real_name && data.id_card) {
                    $.get("/api/house/myhouse", function(result){
                        $("#houses-list").html(template("houses-list-tmpl", {houses:result.houses}));
                });
                }
                else{
                    $(".auth-warn").show();
                    return;
                }
            }
        }    
    });    
});