// ===== Button Events =============================

// -- Click "Generate"
$('#btn_gen').click(function () {
	if ($('#input_key').val() === '') {
		$('#input_key').val(randomStr(32, false));
	}
	var send_msg = JSON.stringify(msg2Json($('#input_msg').val(), $('#input_key').val()));
	connect_and_send(DEFAULT_SERVER, send_msg, true);
	console.log(send_msg);
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
	connect_and_send(DEFAULT_SERVER, get_requirement, true);
	console.log(get_requirement);
});