$(document).ready(function() {

	// 允许多个 modal 的初始化。
	$('.ui.modal').modal({
		allowMultiple: true,
	});

	// checkbox animation.
	$('.ui.checkbox')
	  .checkbox()
	;

	// 点击注册按钮后，隐藏登录表单。
	$('#signup-button').click(function() {
		$('#login-form').fadeOut("slow", function() {
			$('#register-form').fadeIn("slow");
		});
	});

	// 登录。
	$('#login-submit').click(function() {
		var username = $('#login-username').val();
		var password = $('#login-passwd').val();
		post('/auth/login', 
			{
            	'username' : username,
            	'password' : password
            }, 
            function (res) {
				if (res.isSuccess) {
					$('#login-form').fadeOut(function() {
						$('#chat-page').fadeIn();
					});
					token = res.data.token;
					uid = res.data.uid;
					getUserProfile();
					getFriends();
					initSocket();
				}
				else {
					var msg = getErrorMsg(res);
					console.log(msg);
					alert(msg);
				}
            });
	});

	// 注册。
	$('#signup-submit').click(function() {
		var username = $('#signup-username').val();
		var email = $('#signup-email').val();
		var password = $('#signup-passwd').val();

		post('/auth/register',
			{
            	'username' : username,
            	'password' : password,
            	'email' : email
            },
            function (res) {
				if (res.isSuccess) {
					$('#register-form').fadeOut(function() {
						$('#chat-page').fadeIn();
					});
					token = res.data.token;
					uid = res.data.uid;
					getUserProfile();
					getFriends();
					initSocket();
				}
				else {
					var msg = getErrorMsg(res);
					console.log(msg);
					alert(msg);
				}
            });
	});

	// 隐藏注册表单，显示登录表单。
	$('#signup-back').click(function() {
		$('#register-form').fadeOut("slow", function() {
			$('#login-form').fadeIn("slow");
		});
	});

});