
function updateChatPanel() {
	$('#chat-panel').removeClass('computer only');
	$('#message-area').css('margin-top', '2%');
	$('.chat-message-item').css('cssText', 'width: 100% !important');
	$('.chat-avatar').css('width', '20rem');
	$('.ui.form').css('font-size', '3rem');
	$('#message-input').attr('rows', '1');
}

$(document).ready(function() {
	$('.message-button').click(function() {
		$('#friend-group-list').fadeOut(function() {
			$('#message-list').fadeIn();
		});
	});

	$('.friend-button').click(function() {
		$('#message-list').fadeOut(function() {
			$('#friend-group-list').fadeIn();
		});
	});

	$('.message-item').click(function() {
		if($('#chat-panel').css('display') === 'none') {
			$('#user-panel').fadeOut(function() {
				updateChatPanel();
			});
		}
	});

});