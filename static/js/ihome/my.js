function logout() {
    $.get("/api/logout", function(data){
        if (0 == data.errno) {
            location.href = "/";
        }
    })
}

$.ajax({
	url:'/api/profile',
	type: 'get',
    success: function(data){
        if (0 == data.errno) {
       		$('#user-name').html(data.username)
       		$('#user-mobile').html(data.mobile)
            $('#user-avatar').attr('src', data.avatar)
        }
        else{
            window.location.href = 'login.html'
        }        
    }   
});



$(document).ready(function(){
	$('#logout').click(function(){
		logout()
	})

})