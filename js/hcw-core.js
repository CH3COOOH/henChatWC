// 2023.03.26: 1st live
// 2023.03.27: Get url without params; no server error message in output_msg
// 2023.03.31: Timeout and isOneTime become editable

var CLIENT_VER = '230331';
var DEFAULT_SERVER = 'wss://app.henchat.net/hcw';
// var DEFAULT_SERVER = 'ws://127.0.0.1:9002';

var cache_0 = null;

// ===== Basic functions ====================

function getQueryVariable(variable)
{
    var query = window.location.search.substring(1);
    var vars = query.split("&");
    for (var i=0;i<vars.length;i++) {
        var pair = vars[i].split("=");
        if(pair[0] == variable){return pair[1];}
    }
    return(false);
}

function aesEncrypt(plaintext, key) {
	var keyHex = CryptoJS.enc.Base64.parse(key);
	var ivHex = keyHex.clone();
	ivHex.sigBytes = 16;
    ivHex.words.splice(4);
	var messageHex = CryptoJS.enc.Utf8.parse(plaintext);
	var encrypted = CryptoJS.AES.encrypt(messageHex, keyHex, {
		"iv": ivHex,
		"mode": CryptoJS.mode.CTR,
		"padding": CryptoJS.pad.Pkcs7
    });
	return encrypted.toString();
}

function aesDecrypt(text64, key) {
	var keyHex = CryptoJS.enc.Base64.parse(key);
	var ivHex = keyHex.clone();
	ivHex.sigBytes = 16;
    ivHex.words.splice(4);
	var decrypt = CryptoJS.AES.decrypt(text64, keyHex, {
		"iv": ivHex,
		"mode": CryptoJS.mode.CTR,
		"padding": CryptoJS.pad.Pkcs7
    });
    return CryptoJS.enc.Utf8.stringify(decrypt);
}

function getCookie(key) {
	var arr, reg = new RegExp("(^| )"+key+"=([^;]*)(;|$)");
	if (arr = document.cookie.match(reg)) {
		return unescape(arr[2]);
	} else {
		return null;
	}
}

function randomStr(length, symbol=true) {
	var gen = '';
	if (symbol) {
		var charLib = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!#$%&*?@~-';
	} else {
		var charLib = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
	}
	
	for (var i=0; i<length; i++) {
		index = Math.round(Math.random() * (charLib.length - 1));
		gen += charLib[index];
	}
	return gen;
}

function parseTimeout(sTimeout) {
	buf = sTimeout.split(' ')
	var n = parseFloat(buf[0]);
	var u = buf[1];
	if (u === 'min') {
		return n * 60;
	}
	if (u === 'h') {
		return n * 3600;
	}
	return 86400; // Default: 24h
}

// ==============================
// online = true: online mode
// online = false: offline mode
// ==============================
function formStatusSet() {
	// $('#s_send').prop('enabled', true);
	document.getElementById("input_timeout").selectedIndex = 5;
	return 0;
}
// ===========================================


// ================================================================
// Create a new websocket server, including all events:
// ws.onopen()
// ws.onmessage()
// ws.onclose()
// ws.onerror()
// ================================================================
function connect_and_send(server, what2send) {

	// -- Connect to Web Socket
	var ws = new WebSocket(server);
	var isSent = false;

	// -- Set event handlers
	ws.onopen = function() {
		console.log(`[ws.onopen] Server opened. Client ver: ${CLIENT_VER}`);
		ws.send(what2send);
		isSent = true;
		console.log('[ws.onopen] Message has been sent.');
	};
		
	ws.onmessage = function(e) {
		// -- e.data contains received string.
		console.log(e.data);
		var getMsg = JSON.parse(e.data);
		if (getMsg.type === 0) {
			// -- Result of message sending
			console.log("[ws.onmessage] Server replies: OK");
			var full_url = `[Full path]\n${getUrlWithoutParam()}?hash=${cache_0}&key=${$('#input_key').val()}\n\n`;
			var hash_url = `[Hash only]\n${getUrlWithoutParam()}?hash=${cache_0}\n`;
			var res = full_url + hash_url
			$('#output_msg').val(res);
		}
		else if (getMsg.type === 1) {
			// -- Get message from server
			fillMessageBoard(aesDecrypt(getMsg.payload, $('#input_key').val()));
		}
		else {
			fillMessageBoard(getMsg.payload);
		}
	};

	ws.onclose = function() {
		console.log("[ws.onclose] Server closed.");
	};

	ws.onerror = function(e) {
		console.log("[ws.onerror] Server error.");
		// fillMessageBoard("!!! Server error.", cls=false);
	};
}

function fillMessageBoard(msg, cls=true) {
	// ===============================
	// Search "XSS attack" for detail
	// ===============================
	// function xssAvoid(rawStr){
	// 	return rawStr.replace(/</g, '&lt').replace(/>/g, '&gt');
	// }
	if (cls === true) {
		$('#output_msg').val(msg);
	}
	else {
		$('#output_msg').val($('#output_msg').val()+'\n'+msg);
	}
}

// ===== Secondary functions ====================
function getHashAndKeyFromUrl()
{
	var hash = getQueryVariable('hash');
	var key = getQueryVariable('key');
	var i = 0;
	if (hash != false) {
		$('#input_msg').val(hash);
		i++;
	}
	if (key != false) {
		$('#input_key').val(key);
		i++;
	}
	return i;
}

function getUrlWithoutParam()
{
	return window.location.protocol+"//"+window.location.host+""+window.location.pathname;
}

function msg2Json(msg, key, timeout, isOnetime)
{
	cache_0 = CryptoJS.SHA1(msg + randomStr(32, false)).toString();
	return {
		'action': 'put',
		'msg': aesEncrypt(msg, key),
		'key_hash': cache_0,
		'timeout': new Date().getTime()/1000. + timeout,  // Take care of the unit!!!
		'isOnetime': isOnetime
	};
}

// ===== Init ======================================
formStatusSet();
if (getHashAndKeyFromUrl() === 2) {
	var get_requirement = JSON.stringify({
		'action': 'get',
		'key_hash': $('#input_msg').val()
	});
	connect_and_send(DEFAULT_SERVER, get_requirement, true);
	console.log(get_requirement);
	console.log('Message is fetched automatically.');
}
// =================================================
