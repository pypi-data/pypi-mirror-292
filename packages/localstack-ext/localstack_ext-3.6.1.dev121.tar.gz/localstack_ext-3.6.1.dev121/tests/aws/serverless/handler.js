module.exports.handler = function(event, context, callback) {
  console.log('lambda event:', event, callback, context);
  if(callback) {
		callback(null, {statusCode: 200, body: event});
	} else {
		context.succeed(event);
	}
};
