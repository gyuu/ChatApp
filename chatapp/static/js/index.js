// 使用全局变量保存 token 和 uid。
var token;
var uid;

// json 转 HTML 模板。
var group_header_template = '<div class="item friend-group g$gid$">\
<div class="ui header"><i class="chevron circle right icon">\
</i><div class="content">$group_name$</div></div><div class="content">\
<div class="ui animated big middle aligned inverted selection list">'


var friend_item_template = {"<>":"div","class":"item friend-item","data-uid":"${id}","html":[
    {"<>":"img","class":"ui avatar image","src":"${avatar}","html":""},
    {"<>":"div","class":"content","html":"${username}"}
  ]}


var group_footer = '</div></div></div>'


var message_item_template = {"<>":"div","class":"item message-item","html":[
    {"<>":"img","class":"ui avatar image","src":"${avatar}","html":""},
    {"<>":"div","class":"content","html":"${username}"}
  ]}


var group_dropdown_template = '<option value=$gid$>$group_name$</option>'


var add_friend_found_user_template = '<div class="field" data-uid="$id$" style="margin:0 auto;">\
			    <img class="ui avatar image" id="found-avatar" src="$avatar$">\
			    <span id="found-username">$username$</span>\
		    </div>'


var add_friend_find_user_field = '<div class="ten wide field">\
		      <input id="search-username" type="text" placeholder="Username">\
		    </div><button id="search-friend-button" class="ui primary button">\
			Search</button>'


// 根据简单的字符串模板生成 HTML。
// 因为 json2html 必须只能生成成对的标签，这个没有那么多限制。
function strrep(str,obj) {
    return str.replace(/\$\w+\$/gi, function(matchs) {
        var returns = obj[matchs.replace(/\$/g, "")];
        return typeof returns === "undefined" ? "" : returns;
    });
}


// 注册时表单填写时的错误信息。
function getErrorMsg(res) {
	var keys = Object.keys(res.error_message);
	var msg = '';
	for (var i = keys.length - 1; i >= 0; i--) {
		msg += keys[i] + ': ' + res.error_message[keys[i]] + '\n';
	}
	return msg;
}


// 注册／登录时发送 POST 请求的简单封装。
function post(_url, data, callback) {
	$.ajax({
        type: "POST",
        url: _url,
        data: JSON.stringify(data), 
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: callback,
        error: function (errormessage) {
        	console.log(msg);
        }
	});
}


// 在聊天页面发送的请求需要经过认证，在请求头中加 token。
function authorized_ajax(method, _url, data, callback, token) {
	$.ajax({
        type: method,
        url: _url,
        data: JSON.stringify(data), 
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        headers: { 'Authorization': 'token ' + token },
        success: callback,
        error: function (msg) {
        	console.log(msg);
        }
	});
}


// 经过包装的请求发送函数。
function authorized_get(_url, callback) {
	authorized_ajax('GET', _url, null, callback, token);
}

function authorized_post(_url, data, callback) {
	authorized_ajax('POST', _url, data, callback, token);
}


function getUserProfile() {
	authorized_get('/user/profile', function(res) {
		if (res.isSuccess) {
			$('#user-avatar').attr('src', res.data.avatar);
			$('#username').text(res.data.username);
		}
		else {
			console.log(res.error_message);
		}
	});
}

function getFriends() {
	authorized_get('/user/friends', function(res) {
		if (!res.isSuccess) {
			console.log(res.error_message);
		}
		else {
			var group_list = "";
			var group_dropdown = "";
			for (var i = 0; i < res.data.length; i++) {
				var group = res.data[i];
				var group_header_data = {
					'group_name' : group['group_name'],
					'gid' : group['gid']
				}

				// render friend list in user panel.
				var group_header = strrep(group_header_template, group_header_data);
				var friend_list_data = json2html.transform(group['friends'], friend_item_template);
				var group_block = group_header + friend_list_data + group_footer;
				group_list += group_block;

				// render group dropdown in select group modal.
				var group_dropdown_item = strrep(group_dropdown_template, group_header_data);
				group_dropdown += group_dropdown_item;
			}
			// console.log(group_list);
			$('#friend-group-list').append(group_list);
			$('#group-dropdown').append(group_dropdown);
		}
	});
}

function getMessage() {
	authorized_get('/chat/message', function(res) {
		if(!res.isSuccess) {
			console.log(res.error_message);
		}
		else {
			var message_list = "";
			for (var i = 0; i < res.data.length; i++) {
				var message = res.data[i];
				var message_item = json2html.transform(message_item_template, message);
				message_list += message_item;
			}
			$('#message-list').append(message_list);
		}
	});
}


// register page callbacks.
$(document).ready(function() {

	$('.ui.modal').modal({
		allowMultiple: true,
	});

	// checkbox animation.

	$('.ui.checkbox')
	  .checkbox()
	;

	$('#signup-button').click(function() {
		$('#login-form').fadeOut("slow", function() {
			$('#register-form').fadeIn("slow");
		});
	});

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
				}
				else {
					var msg = getErrorMsg(res);
					console.log(msg);
					alert(msg);
				}
            });
	});

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
				}
				else {
					var msg = getErrorMsg(res);
					console.log(msg);
					alert(msg);
				}
            });
	});

	$('#signup-back').click(function() {
		$('#register-form').fadeOut("slow", function() {
			$('#login-form').fadeIn("slow");
		});
	});

});