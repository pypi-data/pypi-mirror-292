const AWS = require('aws-sdk');
const { MongoClient } = require('mongodb');

const secretsManager = new AWS.SecretsManager();
const secretName = process.env.SECRET_NAME;

function customURIEncode(str) {
  // encode also characters that encodeURIComponent does not encode
  return encodeURIComponent(str)
    .replace(/!/g, '%21')
    .replace(/~/g, '%7E')
    .replace(/\*/g, '%2A')
    .replace(/'/g, '%27')
    .replace(/\(/g, '%28')
    .replace(/\)/g, '%29');
}

exports.handler = async (event) => {
  try {
    // Retrieve secret
    const secretValue = await secretsManager.getSecretValue({ SecretId: secretName }).promise();
    const { username, password, host, port } = JSON.parse(secretValue.SecretString);
    const user = customURIEncode(username);
    const pwd = customURIEncode(password);

    // Connection URI
    const dbname = "mydb";
    // retryWrites is by default true, but not supported by AWS DocumentDB
    const uri = `mongodb://${user}:${pwd}@${host}:${port}/?retryWrites=false`;
    console.log(uri);
    // Connect to DocumentDB
    const client = await MongoClient.connect(uri);
    console.log("connected");
    const db = client.db(dbname);
    console.log("db");
    // Insert data
    const collection = db.collection('your_collection');
    await collection.insertOne({ key: 'value' });
    console.log("inserted");
    // Query data
    const result = await collection.findOne({ key: 'value' });
    console.log("queried");
    await client.close();

    // Return result
    return {
      statusCode: 200,
      body: JSON.stringify(result),
    };
  } catch (error) {
    console.error('Error: ', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message }),
    };
  }
};
