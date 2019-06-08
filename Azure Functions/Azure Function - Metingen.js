module.exports = function (context, IoTHubMessages) {
	//Log the event
    //context.log(`Message: ${JSON.stringify(IoTHubMessages[0])}`);

    //Variables to use for the test data
    var messageId = 0;
    var sensorId = 0;
    var waarde = 0;
    var tijdstip;
	var status;

    //Check if the message is not a sensor update
    messageId = IoTHubMessages[0].messageId;
    waarde = IoTHubMessages[0].waarde;
    sensorId = IoTHubMessages[0].sensorId;
    tijdstip = IoTHubMessages[0].tijdstip;
	status = IoTHubMessages[0].status;

    var resultaat = {
        "messageId": messageId,
        "sensorId": sensorId,
        "waarde": waarde,
        "tijdstip": tijdstip,
		"status": status
    };

    //context.log(`Output content: ${JSON.stringify(resultaat)}`);

    context.bindings.outputDocument = resultaat;

    context.done();
};
