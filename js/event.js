// ===== Button Events =============================

// -- Click "Generate"
$('#btn_gen').click(function () {
	if ($('#input_msg').val() === '') {
		fillMessageBoard('Cannot send an empty message!');
		return -1;
	}
	if ($('#input_key').val() === '') {
		$('#input_key').val(randomStr(16, false));
	}
	var send_msg = $('#input_msg').val();
	var key = $('#input_key').val();
	var timeout = parseTimeout($('#input_timeout').find("option:selected").text());
	var isOnetime = $('#input_isOneTime')[0].checked;
	var send_msg = JSON.stringify(msg2Json(send_msg, key, timeout, isOnetime));
	connect_and_send(DEFAULT_SERVER, send_msg);
	console.log(send_msg);
	return 0;
});

$('#btn_fetch').click(function () {
	if ($('#input_msg').val() === '' || $('#input_key').val() === '') {
		$('#output_msg').val("Completed input required!");
		return -1;
	}
	var get_requirement = JSON.stringify({
		'action': 'get',
		'key_hash': $('#input_msg').val()
	});
	connect_and_send(DEFAULT_SERVER, get_requirement);
	console.log(get_requirement);
});