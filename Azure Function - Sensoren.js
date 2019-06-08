module.exports = function (context, IoTHubMessages, inputDocument) {
	// Log the event
    //context.log(`Message: ${JSON.stringify(IoTHubMessages[0])}`);
    //context.log(`Sensoren: ${JSON.stringify(inputDocument)}`);

    // Variables to use that keep the user created data
    var sensorId = IoTHubMessages[0].sensorId;
    var sensorNaam = "";
    var sensorLocatie = "";
    var sensorEenheid = "";
    var sensorType = "";
    var sensorX = 0;
    var sensorY = 0
	var sensorStatus = IoTHubMessages[0].status;

    // Use from the inputDocument only the sensor that needs to be updated, this way the user added info stays as it is
    // Otherwise Azure would override the previous information
    // Also first check if the inputDocument is not empty, because then we go with empty values from above
    if (typeof inputDocument !== 'undefined' && inputDocument.length > 0) {
        inputDocument.forEach(sensor => {
            // Check for the corresponding sensorId and use the content that already existed to update the "geconnecteerd" value
            if (sensor.id == IoTHubMessages[0].sensorId) {
                sensorId = IoTHubMessages[0].sensorId;
	            sensorStatus = IoTHubMessages[0].status;
                sensorNaam = sensor.naam;
                sensorLocatie = sensor.locatie;
                sensorEenheid = sensor.eenheid;
                sensorType = sensor.type;
                sensorX = sensor.x;
                sensorY = sensor.y;
            }
    })};

    // Create the json that we write to Cosmos DB
    var resultaat = {
        "id": sensorId,
        "naam": sensorNaam,
        "type": sensorType,
        "locatie": sensorLocatie,
        "eenheid": sensorEenheid,
		"geconnecteerd": sensorStatus,
        "x": sensorX,
        "y": sensorY
    };

    //context.log(`Output content: ${JSON.stringify(resultaat)}`);

    context.bindings.outputDocument = resultaat;

    context.done();
};