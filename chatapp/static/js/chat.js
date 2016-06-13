
function updateChatPanel() {
	$('#chat-panel').removeClass('computer only');
	$('#message-area').css('margin-top', '2%');
	$('.chat-message-item').css('cssText', 'width: 100% !important');
	$('.chat-avatar').css('width', '20rem');
	$('.ui.form').css('font-size', '3rem');
	$('#message-input').attr('rows', '1');
}

$(document).ready(function() {


	// 切换消息列表和好友列表的显示。
	$('.message-button').click(function() {
		$('#friend-group-list').fadeOut(function() {
			$('#message-list').fadeIn();
		});
	});


	// 切换消息列表和好友列表的显示。
	$('.friend-button').click(function() {
		$('#message-list').fadeOut(function() {
			$('#friend-group-list').fadeIn();
		});
	});


	// 在移动端点击消息时弹出聊天页面。
	$('.message-item').click(function() {
		if($('#chat-panel').css('display') === 'none') {
			$('#user-panel').fadeOut(function() {
				updateChatPanel();
			});
		}
	});


	// 右键 friend 按钮可以打开加好友页面。
	$('.friend-button').mousedown(function(event) {

		document.oncontextmenu = function() {return false;};
	    switch (event.which) {
	        case 3:
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
	            break;
	        default:
	    }
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


	// 加好友
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


	// 在朋友列表项上右键可以激活删除好友的按钮。
	$('#friend-group-list').on('mousedown', '.friend-item', function(){
		document.oncontextmenu = function() {return false;};

		// 获取用户 id 和组 id。
		var friend_id = parseInt($(this).attr('data-uid'));
		var gid_pat = /g\d+/;
		var class_list = $(this).parents('.friend-group').attr('class');
		var gid = parseInt(class_list.match(gid_pat)[0].substring(1));
		var selected_friend = this;

	    switch (event.which) {
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

});