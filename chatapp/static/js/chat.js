// 在移动端时，修改聊天窗口的样式以便适配。
function updateChatPanel() {
	if($('#chat-panel').hasClass('computer only')) {
		$('#chat-panel').removeClass('computer only');
		$('#message-area').css('margin-top', '2%');
		$('.chat-message-item').css('cssText', 'width: 100% !important');
		$('.chat-avatar').css('width', '20rem');
		$('.ui.form').css('font-size', '3rem');
		$('#message-input').attr('rows', '1');
	}
	else {
		$('#chat-panel').fadeIn();
	}
}

// 获取用户名和头像。
function getUserProfile() {
	authorized_get('/user/profile', function(res) {
		if (res.isSuccess) {
			$('#user-avatar').attr('src', res.data.avatar);
			$('#username').text(res.data.username).attr('data-uid', res.data.id);
		}
		else {
			console.log(res.error_message);
		}
	});
}

// 获取用户的分组好友列表。
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

				// update friend_map.
				var friends = group['friends'];
				for (var i = 0; i < friends.length; i++) {
					var id = friends[i]['id'];
					friend_map[id] = {
						'avatar' : friends[i]['avatar'],
						'username' : friends[i]['username']
					};
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


function initSocket() {
	// test.

    var namespace = '/chat';
    socket = io.connect('http://' + document.domain + ':' + location.port + namespace);

    socket.on('conn_ack', function(msg) {
    	console.log('connect:');
    	console.log(msg);
    });

    socket.on('login_ack', function(res) {
    	if (res['offline-msg'])
    		socket.emit('offline-msg', {'token':token});
    	else
    		console.log('no offline messages.');
    });

    socket.on('offline-msg-ack', function(res){
    	console.log('offline message:');
    	console.log(res);
    });

    socket.on('message', function(data){

    	console.log(data);
    	var from_user_id = data['user_id'];
    	var friend_data = friend_map[from_user_id];
    	var left_message_data = {
    		'content' : data['content'],
    		'username' : friend_data['username'],
    		'avatar' : friend_data['avatar']
    	}
    	var message = json2html.transform(left_message_data, left_message_template);
		$('#message-area').append(message);

		// 调整移动端的消息样式。
		if(!$('#chat-panel').hasClass('computer only')) {
			$('.chat-message-item').css('cssText', 'width: 100% !important');
			$('.chat-avatar').css('width', '20rem');
		}
    });

    socket.emit('login', {'token':token});
}


$(document).ready(function() {


	// // 切换消息列表和好友列表的显示。
	// $('.message-button').click(function() {
	// 	$('#friend-group-list').fadeOut(function() {
	// 		$('#message-list').fadeIn();
	// 	});
	// });


	// // 切换消息列表和好友列表的显示。
	// $('.friend-button').click(function() {
	// 	$('#message-list').fadeOut(function() {
	// 		$('#friend-group-list').fadeIn();
	// 	});
	// });


	// // 在移动端点击消息时弹出聊天页面。
	// $('.friend-item').click(function() {
	// 	if($('#chat-panel').css('display') === 'none') {
	// 		$('#user-panel').fadeOut(function() {
	// 			updateChatPanel();
	// 		});
	// 	}
	// });


	// 点击 Friends 按钮刷新一下界面。
	$('.friend-button').click(function(event) {
		$('#friend-group-list').hide().fadeIn();
	});


	// 移动端 chat-header 旁边的按钮用于退出聊天界面返回好友列表。
	$('#chat-header-back').click(function() {
		$('#chat-panel').fadeOut(function() {
			$('#user-panel').fadeIn();
		});
	});


	// 在朋友列表项上右键可以激活删除好友的按钮，左键可以调出聊天窗口。
	$('#friend-group-list').on('mousedown', '.friend-item', function(){
		document.oncontextmenu = function() {return false;};

		// 获取用户 id 和组 id。
		var friend_id = parseInt($(this).attr('data-uid'));
		var gid_pat = /g\d+/;
		var class_list = $(this).parents('.friend-group').attr('class');
		var gid = parseInt(class_list.match(gid_pat)[0].substring(1));
		var selected_friend = this;

	    switch (event.which) {

	    	// 如果是移动端，则跳转到聊天界面。
	    	// 如果是 PC 端，则修改聊天窗口顶部的用户名，并激活输入条。
	    	case 1:
				if($('#chat-panel').css('display') === 'none') {
					$('#user-panel').fadeOut(function() {
						updateChatPanel();
					});
				}
	    		current_talking_friend_id = friend_id;
	    		$('#message-input').parent().removeClass('disabled');
	    		$('#chat-header-username').hide()
	    		.text(friend_map[friend_id].username).fadeIn();
	    		break;

	    	// 删除好友。
	        case 3:
	        	$('#delete-friend-modal')
	        	.modal({
	        		onApprove : function() {
	        			// 调用删除好友的接口。
	        			var payload = {
	        				'friend_id' : friend_id,
	        				'group_id' : gid
	        			}
	        			authorized_post('/user/delete-friend', payload, function(res) {
	        				if (!res.isSuccess)
	        					console.log(res.error_message);
	        				else {
	        					console.log(res.data);
	        					// 将选中的好友从好友列表中删除。
	        					$(selected_friend).fadeOut();
	        				}
	        			$('#delete-friend-modal').modal('hide');
	        			});
	        		}
	        	})
	        	.modal('show');
	            break;
	        default:
	    }
	});


// 添加好友部分开始。

	// 点击 Add Friend 按钮打开加好友界面。
	$('.adduser-button').click(function() {
		$('#add-friend-modal')
		.modal({
			closable  : false,
			onDeny    : function() {
				$(this).modal('hide');
				$('#add-friend-find-user-field').fadeIn();
				$('#add-friend-found-user').fadeOut();
				$('#add-group-field').fadeIn();
				return false;
			}
		})
		.modal('show');
	});


	// 加好友时查找用户。
	$('#search-friend-button').click(function() {
		var username = $('#search-username').val();
		var payload = {
			'username' : username
		};
		authorized_post('/user/find', payload, function(res) {
			if(!res.isSuccess)
				alert('user not found');
			else {
				// 找到用户之后用用户资料代替查找用户的输入框。
				$('#add-friend-find-user-field').fadeOut(function() {
					var found_user = $('#add-friend-found-user').find('div.field');
					found_user.find('img').attr('src', res.data.avatar);
					found_user.find('span').text(res.data.username);
					$('#add-friend-found-user').attr('data-uid', res.data.id).fadeIn();
					});
				}
		});
	});


	// 选择完组之后添加按钮消失。
	$('#select-group-submit').click(function() {
		var group_id = $('#group-dropdown option:selected').val();
		if (group_id !== '0')
			$('#add-group-field').fadeOut();
		else {
			alert('please select a group!');
		}
	});


	// 添加组。
	$('#add-group-submit').click(function() {
		var group_name = $('#add-group-name').val();
		var payload = {
			'group_name' : group_name
		}
		authorized_post('/user/add-group', payload, function(res) {
			if (!res.isSuccess)
				console.log(res.error_message);
			else {
				console.log(res);
				// 将组添加到下拉列表中。
				payload['gid'] = res.data.gid;
				var option = strrep(group_dropdown_template, payload);
				$('#group-dropdown').append(option);
				$('#add-group-field').fadeOut();

				// 将组加到 panel 中。
				var group_header = strrep(group_header_template, payload);
				var group_block = group_header + group_footer;
				$('#friend-group-list').hide().append(group_block).fadeIn();
			}
		});
	});


	// 添加好友确认按钮。
	$('#add-friend-submit').click(function() {

		var user_id = $('#add-friend-found-user').attr('data-uid');
		var group_id = $('#group-dropdown option:selected').val();

		if (user_id && group_id !== '0') {
			var payload = {
				'friend_id' : user_id,
				'group_id': group_id
			};
			authorized_post('/user/add-friend', payload, function(res) {
				if (!res.isSuccess)
					console.log(res.error_message);
				else {
					console.log(res.data);
					// 将用户添加到左侧的好友列表中。
					var found_user = $('#add-friend-found-user').find('div.field');
					var friend_item_data = {
						'id': user_id,
						'username': found_user.find('span').text(),
						'avatar': found_user.find('img').attr('src')
					}
					var friend_item = json2html.transform(friend_item_data, friend_item_template);
					$('#friend-group-list').find('div.g' + group_id).find('.list').append(friend_item);

					// 恢复 modal 框中的内容。
					$('#add-friend-find-user-field').fadeIn();
					$('#add-friend-found-user').fadeOut();
					$('#add-group-field').fadeIn();
					$('#add-friend-modal').modal('hide');
				}
			});

		}
		else if (group_id === '0') {
			alert('please select a group!');
		}
	});

	// 在组列表项上右键可以激活删除组的按钮。
	$('#friend-group-list').on('mousedown', '.ui.header', function() {
		document.oncontextmenu = function() {return false;};

		// 获取组 id。
		var gid_pat = /g\d+/;
		var class_list = $(this).parents('.friend-group').attr('class');
		var gid = parseInt(class_list.match(gid_pat)[0].substring(1));
		var selected_group = $(this).parents('.friend-group');

	    switch (event.which) {
	        case 3:
	        	$('#delete-group-modal')
	        	.modal({
	        		onApprove : function() {
	        			// 调用删除组的接口。
	        			var payload = {
	        				'group_id' : gid
	        			}
	        			authorized_post('/user/delete-group', payload, function(res) {
	        				if (!res.isSuccess)
	        					console.log(res.error_message);
	        				else {
	        					console.log(res.data);
	        					// 将选中的组从组列表中删除。
	        					$(selected_group).fadeOut();
	        				}
	        			$('#delete-friend-modal').modal('hide');
	        			});
	        		}
	        	})
	        	.modal('show');
	            break;
	        default:
	    }
	});

// 添加好友部分结束。


	// 发送消息。
	$('#message-input').keypress(function(event) {
		switch(event.which) {
			case 13:

				// 发送请求。
				var content = $(this).val();
				var payload = {
					'content' : content,
					'token' : token,
					'to_user_id' : current_talking_friend_id
				}
				socket.emit('send', payload);

				// 将消息加入页面中。
				var message_data = {
					'content' : content,
					'avatar' : $('img#user-avatar').attr('src'),
				}
				var message = json2html.transform(message_data, right_message_template);
				$('#message-area').append(message);

				// 调整移动端的消息样式。
				if(!$('#chat-panel').hasClass('computer only')) {
					$('.chat-message-item').css('cssText', 'width: 100% !important');
					$('.chat-avatar').css('width', '20rem');
				}

				// 将输入框中的内容清掉。
				$(this).val('');
		}
	});

});