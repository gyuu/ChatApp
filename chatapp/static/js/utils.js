// 使用全局变量保存 token 和 uid 和 socket。
var token;
var uid;
var socket;
var current_talking_friend_id;
// friend_map 是一个字典，根据好友的 user_id，映射用户名和头像，以及聊天记录。
var friend_map = new Object();

// json 转 HTML 模板。
var group_header_template = '<div class="item friend-group g$gid$">\
<div class="ui header"><i class="chevron circle right icon">\
</i><div class="content">$group_name$</div></div><div class="content">\
<div class="ui animated big middle aligned inverted selection list">'


var friend_item_template = {"<>":"div","class":"item friend-item uid${id}","data-uid":"${id}","html":[
    {"<>":"img","class":"ui avatar image","src":"${avatar}","html":""},
    {"<>":"div","class":"content","html":"${username}"}
  ]}


var group_footer = '</div></div></div>'



var message_bubble_template = '<a class="ui red circular label" \
style="margin-left: 5%">$count$</a>'


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

var left_message_template = {"<>":"div","class":"ui stacked grid fluid container left-message chat-message-item","html":[
    {"<>":"div","class":" middle aligned two wide computer three wide mobile column","html":[
        {"<>":"img","class":"ui tiny circular image chat-avatar","src":"${avatar}","html":""}
      ]},
    {"<>":"div","class":"left floated middle aligned ten wide column","html":[
        {"<>":"div","class":"ui raised compact segment","html":[
            {"<>":"p","html":"${content}"}
          ]}
      ]}
  ]}

var right_message_template = {"<>":"div","class":"ui stacked grid fluid container right-message chat-message-item","html":[
    {"<>":"div","class":"right floated middle aligned ten wide column","html":[
        {"<>":"div","class":"right floated ui raised compact right aligned segment","html":[
            {"<>":"p","html":"${content}"}
          ]}
      ]},
    {"<>":"div","class":"middle aligned two wide computer three wide mobile column","html":[
        {"<>":"img","class":"ui tiny circular image chat-avatar","src":"${avatar}","html":""}
      ]}
  ]}

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
